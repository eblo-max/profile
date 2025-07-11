"""HTML to PDF conversion service using CloudLayer.io API"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
import base64
import json

from app.core.config import settings
from app.utils.exceptions import ServiceError

logger = logging.getLogger(__name__)


class HTMLPDFService:
    """Service for generating PDF reports from HTML using CloudLayer.io API"""
    
    def __init__(self):
        self.api_key = settings.CLOUDLAYER_API_KEY
        self.api_url = "https://api.cloudlayer.io"
        if not self.api_key:
            logger.warning("⚠️ CloudLayer.io API key not configured! Set CLOUDLAYER_API_KEY environment variable.")
    
    def reset_cloudlayer_check(self):
        """Reset CloudLayer availability check (for testing)"""
        pass
    
    async def _ensure_cloudlayer_available(self) -> bool:
        """Ensure CloudLayer.io API is available"""
        if not self.api_key:
            logger.error("❌ CloudLayer.io API key not configured!")
            return False
        
        try:
            logger.info("🔍 Checking CloudLayer.io API availability...")
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'x-api-key': self.api_key,
                    'Content-Type': 'application/json'
                }
                
                # Test with minimal HTML (base64 encoded)
                test_html = '<html><body><h1>Test</h1></body></html>'
                test_html_b64 = base64.b64encode(test_html.encode('utf-8')).decode('utf-8')
                
                test_data = {
                    'html': test_html_b64
                }
                
                async with session.post(
                    f'{self.api_url}/v2/html/pdf',
                    headers=headers,
                    json=test_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status in [200, 202]:  # 202 = async processing
                        logger.info("✅ CloudLayer.io API is available and working")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ CloudLayer.io API test failed with status {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"💥 CloudLayer.io API availability check failed: {e}")
            return False

    async def _wait_for_job_completion(self, session: aiohttp.ClientSession, job_id: str) -> str:
        """Wait for CloudLayer.io job completion and return download URL"""
        max_attempts = 30  # Max 30 attempts (30 seconds with 1 second delay)
        attempt = 0
        
        while attempt < max_attempts:
            try:
                headers = {'x-api-key': self.api_key}
                
                async with session.get(
                    f'{self.api_url}/v2/jobs/{job_id}',
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        job_data = await response.json()
                        status = job_data.get('status')
                        
                        if status in ['completed', 'success']:
                            # Log full response to understand structure
                            logger.debug(f"📋 CloudLayer.io job response: {job_data}")
                            
                            # First check for assetUrl specifically
                            download_url = job_data.get('assetUrl')
                            logger.debug(f"🔍 Checking assetUrl: {download_url}")
                            
                            # If not found, try other fields
                            if not download_url:
                                download_url = job_data.get('url')
                                logger.debug(f"🔍 Checking url: {download_url}")
                            
                            if not download_url:
                                download_url = job_data.get('download_url')
                                logger.debug(f"🔍 Checking download_url: {download_url}")
                            
                            if not download_url:
                                download_url = job_data.get('file_url')
                                logger.debug(f"🔍 Checking file_url: {download_url}")
                            
                            if download_url:
                                logger.info(f"✅ CloudLayer.io job {job_id} completed successfully! URL: {download_url}")
                                return download_url
                            else:
                                logger.error(f"Job completed but no download URL found in response: {job_data}")
                                raise ServiceError(f"Job completed but no download URL provided")
                        
                        elif status == 'failed':
                            error_message = job_data.get('error', 'Unknown error')
                            raise ServiceError(f"CloudLayer.io job failed: {error_message}")
                        
                        elif status in ['processing', 'pending']:
                            logger.debug(f"🔄 CloudLayer.io job {job_id} is {status}, waiting...")
                            await asyncio.sleep(1)
                            attempt += 1
                            continue
                        
                        else:
                            raise ServiceError(f"Unknown job status: {status}")
                    
                    else:
                        error_text = await response.text()
                        raise ServiceError(f"Failed to check job status: {response.status} - {error_text}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"⏰ Timeout checking job {job_id} status, retrying...")
                await asyncio.sleep(1)
                attempt += 1
                continue
        
        raise ServiceError(f"Job {job_id} did not complete within {max_attempts} seconds")

    async def generate_partner_report_html(
        self,
        analysis_data: Dict[str, Any],
        user_id: int,
        partner_name: str
    ) -> bytes:
        """
        Generate professional partner analysis PDF report using CloudLayer.io API
        
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
            
            # Check CloudLayer.io availability
            logger.info("🔄 Checking CloudLayer.io API availability...")
            cloudlayer_available = await self._ensure_cloudlayer_available()
            
            if not cloudlayer_available:
                logger.error("❌ CloudLayer.io API is required for professional PDF generation!")
                raise ServiceError("CloudLayer.io API is not available. Please check your API key and internet connection.")
            
            logger.info("✅ Using CloudLayer.io for professional PDF generation")
            
            # Generate complete HTML report
            html_content = self._generate_beautiful_html_report(analysis_data, partner_name, user_id)
            
            # Convert HTML to PDF using CloudLayer.io
            pdf_bytes = await self._convert_html_to_pdf_cloudlayer(html_content)
            
            logger.info(f"✅ Professional PDF generated successfully! Size: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"💥 Professional PDF generation failed: {e}")
            raise ServiceError(f"Failed to generate professional PDF: {str(e)}")

    async def _convert_html_to_pdf_cloudlayer(self, html_content: str) -> bytes:
        """Convert HTML to PDF using CloudLayer.io API"""
        try:
            logger.info("🔄 Converting HTML to PDF using CloudLayer.io...")
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'x-api-key': self.api_key,
                    'Content-Type': 'application/json'
                }
                
                # Encode HTML to base64 as required by CloudLayer.io
                html_b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
                
                # CloudLayer.io API v2 payload
                payload = {
                    'html': html_b64,
                    'viewPort': {
                        'width': 1200,
                        'height': 800
                    },
                    'format': 'A4',
                    'landscape': False,
                    'printBackground': True,
                    'margin': {
                        'top': '0.5in',
                        'right': '0.5in',
                        'bottom': '0.5in',
                        'left': '0.5in'
                    },
                    'preferCSSPageSize': True
                }
                
                logger.debug(f"📤 Sending request to CloudLayer.io API v2...")
                
                async with session.post(
                    f'{self.api_url}/v2/html/pdf',
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status == 200:
                        # Synchronous response - PDF ready immediately
                        response_data = await response.json()
                        file_url = response_data.get('url')
                        
                        if file_url:
                            # Download PDF file
                            async with session.get(file_url) as file_response:
                                if file_response.status == 200:
                                    pdf_bytes = await file_response.read()
                                    logger.info(f"✅ PDF generated successfully via CloudLayer.io! Size: {len(pdf_bytes)} bytes")
                                    return pdf_bytes
                                else:
                                    raise ServiceError(f"Failed to download PDF from CloudLayer.io CDN: {file_response.status}")
                        else:
                            raise ServiceError("CloudLayer.io response missing file URL")
                    
                    elif response.status == 202:
                        # Asynchronous response - need to wait for job completion
                        job_data = await response.json()
                        job_id = job_data.get('id')
                        
                        if not job_id:
                            raise ServiceError("CloudLayer.io did not return job ID")
                        
                        logger.info(f"🔄 CloudLayer.io job {job_id} started, waiting for completion...")
                        
                        # Wait for job completion
                        download_url = await self._wait_for_job_completion(session, job_id)
                        
                        # Download the completed PDF
                        async with session.get(download_url) as file_response:
                            if file_response.status == 200:
                                pdf_bytes = await file_response.read()
                                logger.info(f"✅ PDF generated successfully via CloudLayer.io! Size: {len(pdf_bytes)} bytes")
                                return pdf_bytes
                            else:
                                raise ServiceError(f"Failed to download PDF from CloudLayer.io CDN: {file_response.status}")
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ CloudLayer.io API error {response.status}: {error_text}")
                        raise ServiceError(f"CloudLayer.io API error {response.status}: {error_text}")
                        
        except aiohttp.ClientError as e:
            logger.error(f"❌ CloudLayer.io API request failed: {e}")
            raise ServiceError(f"CloudLayer.io API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"💥 CloudLayer.io PDF conversion failed: {e}")
            raise ServiceError(f"Failed to convert HTML to PDF: {str(e)}")

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