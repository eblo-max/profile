"""HTML to PDF service using Playwright for PDF conversion with beautiful design"""

import asyncio
import logging
from typing import Dict, Any
import os
from datetime import datetime

from app.utils.exceptions import ServiceError

logger = logging.getLogger(__name__)


class HTMLPDFService:
    """Service for generating beautiful PDF reports via HTML using Playwright"""
    
    def __init__(self):
        self.playwright_available = None  # Will be checked on first use
        self.playwright_checked = False
        
        logger.info("🚀 HTMLPDFService initialized - Playwright ONLY (no fallbacks)")
    
    def reset_playwright_check(self):
        """Force re-check of Playwright availability"""
        logger.info("🔄 Resetting Playwright availability check")
        self.playwright_checked = False
        self.playwright_available = None
    
    async def _ensure_playwright_available(self) -> bool:
        """Ensure Playwright is available and working"""
        if self.playwright_checked:
            return self.playwright_available
        
        try:
            logger.info("🔍 Checking Playwright availability...")
            from playwright.async_api import async_playwright
            
            # Try to launch browser to verify availability
            async with async_playwright() as p:
                try:
                    logger.info("🚀 Attempting to launch Chromium browser...")
                    browser = await p.chromium.launch(
                        headless=True,
                        args=[
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-accelerated-2d-canvas',
                            '--no-first-run',
                            '--no-zygote',
                            '--single-process',
                            '--disable-gpu'
                        ]
                    )
                    await browser.close()
                    logger.info("✅ Playwright Chromium is available and working")
                    self.playwright_available = True
                    self.playwright_checked = True
                    return True
                except Exception as browser_error:
                    logger.warning(f"❌ Playwright browser launch failed: {browser_error}")
                    # Try to install browser automatically
                    logger.info("🔧 Attempting to install Playwright browser...")
                    success = await self._install_playwright_browser_async()
                    
                    if success:
                        logger.info("✅ Playwright installation successful, rechecking availability...")
                        # Recheck availability after installation
                        try:
                            async with async_playwright() as p_new:
                                browser = await p_new.chromium.launch(
                                    headless=True,
                                    args=[
                                        '--no-sandbox',
                                        '--disable-setuid-sandbox',
                                        '--disable-dev-shm-usage',
                                        '--disable-accelerated-2d-canvas',
                                        '--no-first-run',
                                        '--no-zygote',
                                        '--single-process',
                                        '--disable-gpu'
                                    ]
                                )
                                await browser.close()
                                logger.info("✅ Playwright Chromium verified after installation")
                                self.playwright_available = True
                                self.playwright_checked = True
                                return True
                        except Exception as verify_error:
                            logger.error(f"❌ Playwright verification failed after installation: {verify_error}")
                            self.playwright_available = False
                            self.playwright_checked = True
                            return False
                    else:
                        logger.error("❌ Playwright installation failed")
                        self.playwright_available = False
                        self.playwright_checked = True
                        return False
                        
        except Exception as e:
            logger.error(f"💥 Playwright availability check failed: {e}")
            self.playwright_available = False
            self.playwright_checked = True
            return False
    
    async def _install_playwright_browser_async(self) -> bool:
        """Try to install Playwright browser automatically using async API"""
        try:
            logger.info("Attempting to install Playwright Chromium browser...")
            import subprocess
            import os
            
            # Set environment for headless installation
            env = os.environ.copy()
            env['PLAYWRIGHT_BROWSERS_PATH'] = '/ms-playwright'
            
            # Run subprocess asynchronously  
            process = await asyncio.create_subprocess_exec(
                'python', '-m', 'playwright', 'install', 'chromium', '--with-deps',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            if process.returncode == 0:
                logger.info("Playwright Chromium installed successfully")
                # Verify installation by actually launching browser
                try:
                    from playwright.async_api import async_playwright
                    async with async_playwright() as p:
                        browser = await p.chromium.launch(
                            headless=True,
                            args=[
                                '--no-sandbox',
                                '--disable-setuid-sandbox',
                                '--disable-dev-shm-usage',
                                '--disable-accelerated-2d-canvas',
                                '--no-first-run',
                                '--no-zygote',
                                '--single-process',
                                '--disable-gpu'
                            ]
                        )
                        await browser.close()
                        logger.info("✅ Playwright Chromium verified by successful launch")
                        return True
                except Exception as e:
                    logger.error(f"Failed to verify Playwright browser by launch: {e}")
                    return False
            else:
                logger.error(f"Failed to install Playwright browser: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error installing Playwright browser: {e}")
            return False
    
    async def generate_partner_report_html(
        self,
        analysis_data: Dict[str, Any],
        user_id: int,
        partner_name: str
    ) -> bytes:
        """
        Generate beautiful partner analysis PDF report using ONLY Playwright
        
        Args:
            analysis_data: Analysis results from AI
            user_id: User ID
            partner_name: Partner name
            
        Returns:
            PDF bytes
        """
        try:
            logger.info(f"Starting PROFESSIONAL PDF generation for user {user_id}, partner: {partner_name}")
            logger.debug(f"Analysis data keys: {list(analysis_data.keys())}")
            
            # Check Playwright availability first using async method
            logger.info("🔄 About to check Playwright availability...")
            playwright_available = await self._ensure_playwright_available()
            logger.info(f"🎯 Playwright availability result: {playwright_available}")
            
            if not playwright_available:
                logger.error("❌ Playwright is required for professional PDF generation!")
                raise ServiceError("Playwright browser is required for PDF generation. Please ensure Docker environment has proper Playwright setup.")
            
            logger.info("✅ Using Playwright for beautiful PDF generation")
            # Generate complete HTML report matching mockup
            html_content = self._generate_beautiful_html_report(analysis_data, partner_name, user_id)
            
            # Convert HTML to PDF using Playwright
            pdf_bytes = await self._convert_html_to_pdf_playwright(html_content)
            
            logger.info(f"✅ Professional PDF generated successfully! Size: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"💥 Professional PDF generation failed: {e}")
            raise ServiceError(f"Failed to generate professional PDF: {str(e)}")
    
    def _generate_beautiful_html_report(
        self,
        analysis_data: Dict[str, Any],
        partner_name: str,
        user_id: int = 123
    ) -> str:
        """Generate beautiful HTML report using Jinja2 template"""
        
        # Extract data safely
        overall_risk = self._extract_risk_score(analysis_data)
        red_flags = analysis_data.get('red_flags', [])
        recommendations = analysis_data.get('survival_guide', analysis_data.get('recommendations', []))
        psychological_profile = analysis_data.get('psychological_profile', 'Анализ личности партнера показывает сложные поведенческие паттерны')
        
        # Generate assessment details
        risk_level, risk_color, risk_badge_color = self._determine_risk_level(overall_risk)
        
        # Current date
        current_date = datetime.now().strftime("%d.%m.%Y")
        report_id = f"RPT-{datetime.now().strftime('%d%m%Y')}-{user_id:03d}"
        
        # Generate personality type based on risk
        personality_type = self._determine_personality_type(overall_risk)
        
        # Prepare template data
        template_data = {
            'partner_name': partner_name,
            'date': current_date,
            'report_id': report_id,
            'risk_score': int(overall_risk),
            'urgency': 'CRITICAL' if overall_risk > 70 else 'HIGH' if overall_risk > 40 else 'MEDIUM' if overall_risk > 20 else 'LOW',
            'personality_type': personality_type,
            'psychological_profile': psychological_profile,
            'red_flags': red_flags[:6] if len(red_flags) > 6 else red_flags,  # Limit to 6 for display
            'recommendations': '\n'.join(recommendations) if isinstance(recommendations, list) else str(recommendations),
            'population_percentile': min(95, int(overall_risk * 1.2)),  # Conservative estimate
            'blocks': self._generate_blocks_data(analysis_data, overall_risk),
            'charts': {
                'blocks_chart': None,  # Could be generated dynamically
                'dark_triad_chart': None,
                'risk_circle': None
            }
        }
        
        # Load and render template
        try:
            from jinja2 import Environment, FileSystemLoader
            import os
            
            # Get template directory
            template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'pdf')
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template('partner_report.html')
            
            # Render template with data
            html_content = template.render(**template_data)
            logger.info("✅ HTML template rendered successfully")
            return html_content
            
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            # Fallback to simple HTML if template fails
            return self._generate_simple_fallback_html(template_data)
    
    def _generate_blocks_data(self, analysis_data: Dict[str, Any], overall_risk: float) -> list:
        """Generate blocks data for template"""
        blocks = [
            {
                'name': 'Эмоциональный контроль',
                'emoji': '😠',
                'score': min(10, int(overall_risk / 10)),
                'level': 'КРИТИЧНО' if overall_risk > 70 else 'ВЫСОКО' if overall_risk > 40 else 'УМЕРЕННО'
            },
            {
                'name': 'Манипулятивность',
                'emoji': '🎭',
                'score': min(10, int((overall_risk + 10) / 12)),
                'level': 'КРИТИЧНО' if overall_risk > 70 else 'ВЫСОКО' if overall_risk > 40 else 'УМЕРЕННО'
            },
            {
                'name': 'Эмпатия',
                'emoji': '💝',
                'score': max(1, 10 - int(overall_risk / 10)),  # Inverse correlation
                'level': 'НИЗКО' if overall_risk > 70 else 'УМЕРЕННО' if overall_risk > 40 else 'НОРМАЛЬНО'
            },
            {
                'name': 'Агрессивность',
                'emoji': '⚡',
                'score': min(10, int(overall_risk / 8)),
                'level': 'КРИТИЧНО' if overall_risk > 70 else 'ВЫСОКО' if overall_risk > 40 else 'УМЕРЕННО'
            }
        ]
        return blocks
    
    def _generate_simple_fallback_html(self, data: dict) -> str:
        """Simple fallback HTML if template fails"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Профиль партнера - {data['partner_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .header {{ background: #667eea; color: white; padding: 20px; text-align: center; }}
        .risk-score {{ font-size: 48px; color: red; text-align: center; margin: 20px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ ПАРТНЕРА</h1>
        <p>Партнер: {data['partner_name']} | Дата: {data['date']}</p>
            </div>
            
    <div class="risk-score">Оценка риска: {data['risk_score']}</div>
            
            <div class="section">
        <h3>Тип личности</h3>
        <p>{data['personality_type']}</p>
            </div>
            
            <div class="section">
        <h3>Красные флаги</h3>
        <ul>{''.join(f'<li>{flag}</li>' for flag in data['red_flags'])}</ul>
            </div>
            
            <div class="section">
        <h3>Рекомендации</h3>
        <p>{data['recommendations']}</p>
    </div>
</body>
</html>"""
    
    def _generate_red_flags_html(self, red_flags: list) -> str:
        """Generate HTML for red flags section"""
        if not red_flags:
            return '<div class="red-flag">Красные флаги не обнаружены</div>'
        
        html_parts = []
        for flag in red_flags:
            html_parts.append(f'<div class="red-flag">• {flag}</div>')
        
        return '\\n'.join(html_parts)
    
    def _generate_recommendations_html(self, recommendations: list) -> str:
        """Generate HTML for recommendations section"""
        if not recommendations:
            return '<div class="recommendation">Специфических рекомендаций не требуется</div>'
        
        html_parts = []
        for rec in recommendations:
            html_parts.append(f'<div class="recommendation">• {rec}</div>')
        
        return '\\n'.join(html_parts)
    
    def _extract_risk_score(self, analysis_data: Dict[str, Any]) -> float:
        """Extract risk score from analysis data"""
        # Try different field names
        for field in ['overall_risk_score', 'manipulation_risk', 'risk_score', 'toxicity_score']:
            if field in analysis_data:
                value = analysis_data[field]
                if isinstance(value, (int, float)):
                    # Convert to percentage if needed
                    if field == 'manipulation_risk' and value <= 10:
                        return value * 10  # Convert 0-10 scale to 0-100
                    return min(value, 100)
        
        # Default if no risk score found
        return 50.0
    
    def _determine_risk_level(self, risk_score: float) -> tuple:
        """Determine risk level text and colors"""
        if risk_score >= 80:
            return "КРИТИЧЕСКИЙ РИСК", "#dc3545", "#dc3545"
        elif risk_score >= 60:
            return "ВЫСОКИЙ РИСК", "#fd7e14", "#fd7e14"
        elif risk_score >= 40:
            return "СРЕДНИЙ РИСК", "#ffc107", "#ffc107"
        else:
            return "НИЗКИЙ РИСК", "#28a745", "#28a745"
    
    async def _convert_html_to_pdf_playwright(self, html_content: str) -> bytes:
        """Convert HTML to PDF using Playwright"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                # Launch browser with Docker-friendly settings
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--single-process',
                        '--disable-gpu',
                        '--disable-background-timer-throttling',
                        '--disable-renderer-backgrounding',
                        '--disable-backgrounding-occluded-windows'
                    ]
                )
                page = await browser.new_page()
                
                # Set content and wait for it to load
                await page.set_content(html_content, wait_until="networkidle")
                
                # Generate PDF with high quality settings
                pdf_bytes = await page.pdf(
                    format='A4',
                    print_background=True,
                    margin={
                        'top': '0.5in',
                        'right': '0.5in',
                        'bottom': '0.5in',
                        'left': '0.5in'
                    },
                    prefer_css_page_size=True
                )
                
                await browser.close()
                
                return pdf_bytes
                
        except Exception as e:
            logger.error(f"Playwright PDF conversion failed: {e}")
            raise ServiceError(f"Failed to convert HTML to PDF: {str(e)}")
    
    def _determine_personality_type(self, risk_score: float) -> str:
        """Determine personality type based on risk score"""
        if risk_score >= 80:
            return "Критический токсичный нарцисс"
        elif risk_score >= 70:
            return "Контролирующий нарцисс"
        elif risk_score >= 60:
            return "Манипулятивная личность"
        elif risk_score >= 40:
            return "Эмоционально нестабильный"
        else:
            return "Условно стабильный"
    
    def _get_personality_description(self, personality_type: str) -> str:
        """Get description for personality type"""
        descriptions = {
            "Критический токсичный нарцисс": "Крайне опасная комбинация нарциссических черт с садистскими наклонностями и полным отсутствием эмпатии",
            "Контролирующий нарцисс": "Выраженные нарциссические черты с потребностью в доминировании и контроле над партнером",
            "Манипулятивная личность": "Склонность к систематическим манипуляциям и эмоциональному воздействию",
            "Эмоционально нестабильный": "Непредсказимые эмоциональные реакции с элементами контролирующего поведения",
            "Условно стабильный": "В целом стабильная личность с некоторыми проблемными паттернами поведения"
        }
        return descriptions.get(personality_type, "Анализ личностных особенностей")
    
    def _generate_key_traits(self, analysis_data: Dict[str, Any], risk_score: float) -> str:
        """Generate key traits HTML list"""
        if risk_score >= 70:
            traits = [
                "🔴 Систематический контроль поведения",
                "🔴 Газлайтинг и искажение реальности", 
                "🔴 Эмоциональное насилие",
                "🔴 Отсутствие эмпатии"
            ]
        elif risk_score >= 50:
            traits = [
                "🟡 Элементы контролирующего поведения",
                "🟡 Эмоциональная нестабильность",
                "🟡 Проблемы с границами",
                "🟡 Склонность к манипуляциям"
            ]
        else:
            traits = [
                "🟢 Некоторые проблемные паттерны",
                "🟡 Эмоциональные реакции",
                "🟡 Коммуникационные сложности",
                "🟢 В целом адекватное поведение"
            ]
        
        return '\n'.join([f'<li>{trait}</li>' for trait in traits])
    
    def _generate_detailed_red_flags(self, red_flags: list, risk_score: float) -> str:
        """Generate detailed red flags HTML"""
        if not red_flags or len(red_flags) == 0:
            # Generate default red flags based on risk score
            if risk_score >= 70:
                red_flags = [
                    ("Систематический контроль поведения", "Партнер пытается контролировать ваше расписание, общение с друзьями и принятие решений"),
                    ("Газлайтинг и переписывание реальности", "Отрицание произошедших событий, обесценивание ваших воспоминаний и чувств"),
                    ("Эмоциональный шантаж", "Использование чувства вины и любви для получения желаемого поведения"),
                    ("Изоляция от поддержки", "Попытки ограничить ваше общение с семьей, друзьями и другими источниками поддержки")
                ]
            elif risk_score >= 50:
                red_flags = [
                    ("Контролирующие тенденции", "Попытки влиять на ваши решения и выборы"),
                    ("Эмоциональное давление", "Использование эмоций для получения желаемого"),
                    ("Нарушение границ", "Неуважение к вашим личным границам и пространству")
                ]
            else:
                red_flags = [
                    ("Коммуникационные проблемы", "Сложности в открытом и честном общении"),
                    ("Эмоциональные реакции", "Непропорциональные эмоциональные ответы на ситуации")
                ]
        else:
            # Convert simple list to tuples with descriptions
            red_flags = [(flag, f"Анализ показывает наличие данного паттерна поведения: {flag.lower()}") for flag in red_flags[:4]]
        
        html_parts = []
        for title, description in red_flags:
            html_parts.append(f'''
                <div class="red-flag">
                    <div class="red-flag-title">{title}</div>
                    <p>{description}</p>
                </div>
            ''')
        
        return '\n'.join(html_parts)
    
    def _generate_protection_strategies(self, recommendations: list) -> str:
        """Generate protection strategies HTML"""
        strategies = [
            "<strong>Установка четких границ:</strong> Определите неприемлемое поведение и последствия за его нарушение",
            "<strong>Техника \"Серый камень\":</strong> Минимизируйте эмоциональные реакции, отвечайте нейтрально и кратко",
            "<strong>Документирование инцидентов:</strong> Ведите дневник случаев проблемного поведения с датами и деталями",
            "<strong>Поддержание связей:</strong> Восстановите и укрепите отношения с семьей и друзьями"
        ]
        
        if recommendations:
            # Add custom recommendations
            for rec in recommendations[:2]:
                strategies.append(f"<strong>Персональная рекомендация:</strong> {rec}")
        
        return '\n'.join([f'<li>{strategy}</li>' for strategy in strategies])
    
    def _generate_action_plan(self, risk_score: float) -> str:
        """Generate action plan HTML"""
        if risk_score >= 70:
            urgency = "немедленных"
            short_term = [
                "Немедленно обратиться к психологу для консультации",
                "Создать список доверенных контактов для экстренной связи",
                "Начать ведение дневника взаимодействий",
                "Изучить техники защиты от манипуляций",
                "Рассмотреть временное изменение места проживания"
            ]
        elif risk_score >= 50:
            urgency = "скорейших"
            short_term = [
                "Обратиться к психологу для консультации",
                "Создать список поддерживающих контактов",
                "Начать ведение дневника взаимодействий",
                "Изучить техники защиты от манипуляций"
            ]
        else:
            urgency = "планомерных"
            short_term = [
                "Рассмотреть возможность парной терапии",
                "Работать над навыками коммуникации",
                "Изучить литературу по здоровым отношениям"
            ]
        
        return f'''
            <h4 style="color: #667eea; margin-bottom: 15px;">Краткосрочные действия (1-2 недели):</h4>
            <ul style="margin-left: 20px; margin-bottom: 25px;">
                {''.join([f'<li>{action}</li>' for action in short_term])}
            </ul>
            
            <h4 style="color: #667eea; margin-bottom: 15px;">Среднесрочные действия (1-3 месяца):</h4>
            <ul style="margin-left: 20px; margin-bottom: 25px;">
                <li>Развивать навыки ассертивности и установки границ</li>
                <li>Восстановить социальные связи и поддерживающую сеть</li>
                <li>Работать над повышением самооценки и уверенности</li>
                <li>Рассмотреть варианты изменения жизненной ситуации</li>
            </ul>
            
            <h4 style="color: #667eea; margin-bottom: 15px;">Долгосрочные цели (3+ месяца):</h4>
            <ul style="margin-left: 20px;">
                <li>Принять обоснованное решение о будущем отношений</li>
                <li>Развить устойчивость к манипулятивному воздействию</li>
                <li>Восстановить психологическое благополучие</li>
                <li>Создать здоровые паттерны взаимоотношений</li>
            </ul>
        '''
    
    def _get_level_description(self, score: float) -> str:
        """Get level description for score"""
        if score >= 8:
            return "Критический уровень"
        elif score >= 6:
            return "Высокий уровень"
        elif score >= 4:
            return "Средний уровень"
        else:
            return "Низкий уровень"
    
    def _generate_personality_characteristics(self, risk_score: float) -> str:
        """Generate personality characteristics HTML"""
        if risk_score >= 70:
            characteristics = [
                "Грандиозное самовосприятие и потребность в постоянном восхищении",
                "Полное отсутствие эмпатии к переживаниям партнера",
                "Систематическое манипулятивное поведение для достижения целей",
                "Категорическая неспособность принимать критику и признавать ошибки",
                "Эмоциональная нестабильность с агрессивными вспышками",
                "Патологическая потребность в контроле над партнером"
            ]
        elif risk_score >= 50:
            characteristics = [
                "Повышенное самовосприятие и потребность в одобрении",
                "Ограниченная эмпатия к переживаниям партнера",
                "Склонность к манипулятивному поведению",
                "Сложности с принятием критики",
                "Эмоциональная нестабильность",
                "Контролирующие тенденции"
            ]
        else:
            characteristics = [
                "Некоторые нарциссические черты",
                "Периодические проблемы с эмпатией",
                "Эмоциональные реакции на стресс",
                "Сложности в коммуникации"
            ]
        
        return '\n'.join([f'<li>{char}</li>' for char in characteristics])
    
    def _generate_behavior_patterns(self, risk_score: float) -> str:
        """Generate behavior patterns HTML"""
        if risk_score >= 70:
            patterns = [
                "Цикл \"любовные бомбардировки\" → обесценивание → контроль",
                "Использование молчания как формы психологического наказания",
                "Систематическая проекция собственных недостатков на партнера",
                "Двойные стандарты в отношении правил и ожиданий",
                "Эскалация агрессии при попытках установить границы"
            ]
        elif risk_score >= 50:
            patterns = [
                "Периодические циклы близости и отдаления",
                "Использование эмоций для контроля ситуации",
                "Проекция вины на партнера",
                "Непоследовательность в поведении и обещаниях"
            ]
        else:
            patterns = [
                "Эмоциональные реакции на конфликты",
                "Сложности в выражении чувств",
                "Периодические коммуникационные проблемы"
            ]
        
        return '\n'.join([f'<li>{pattern}</li>' for pattern in patterns]) 