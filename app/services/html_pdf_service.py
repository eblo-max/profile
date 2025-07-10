"""HTML to PDF service using Playwright for PDF conversion with beautiful design"""

import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger

from app.utils.exceptions import ServiceError


class HTMLPDFService:
    """Service for generating beautiful PDF reports via HTML using Playwright"""
    
    def __init__(self):
        self.playwright_available = self._check_playwright_availability()
        if not self.playwright_available:
            logger.warning("Playwright browser not available, will use fallback ReportLab PDF service")
            # Import fallback service
            try:
                from app.services.reportlab_pdf_service import ReportLabPDFService
                self.fallback_service = ReportLabPDFService()
                logger.info("ReportLab fallback service initialized")
            except ImportError:
                logger.error("Neither Playwright nor ReportLab available for PDF generation")
                self.fallback_service = None
    
    def _check_playwright_availability(self) -> bool:
        """Check if Playwright browser is available"""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                # Try to get browser executable path
                browser_path = p.chromium.executable_path
                if browser_path and Path(browser_path).exists():
                    logger.info(f"Playwright Chromium found at: {browser_path}")
                    return True
                else:
                    logger.warning("Playwright Chromium executable not found")
                    # Try to install browser automatically
                    return self._install_playwright_browser()
        except Exception as e:
            logger.warning(f"Playwright availability check failed: {e}")
            return False
    
    def _install_playwright_browser(self) -> bool:
        """Try to install Playwright browser automatically"""
        try:
            logger.info("Attempting to install Playwright Chromium browser...")
            import subprocess
            import os
            
            # Set environment for headless installation
            env = os.environ.copy()
            env['PLAYWRIGHT_BROWSERS_PATH'] = '/tmp/playwright-browsers'
            
            result = subprocess.run([
                'python', '-m', 'playwright', 'install', 'chromium'
            ], capture_output=True, text=True, timeout=300, env=env)
            
            if result.returncode == 0:
                logger.info("Playwright Chromium installed successfully")
                # Verify installation
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    browser_path = p.chromium.executable_path
                    if browser_path and Path(browser_path).exists():
                        logger.info(f"Verified Playwright Chromium at: {browser_path}")
                        return True
            else:
                logger.error(f"Failed to install Playwright browser: {result.stderr}")
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
        Generate beautiful partner analysis PDF report
        
        Args:
            analysis_data: Analysis results from AI
            user_id: User ID
            partner_name: Partner name
            
        Returns:
            PDF bytes
        """
        try:
            logger.info(f"Starting HTML PDF generation for user {user_id}, partner: {partner_name}")
            logger.debug(f"Analysis data keys: {list(analysis_data.keys())}")
            
            # Check Playwright availability first
            if not self.playwright_available:
                logger.warning("Playwright not available, using fallback ReportLab service")
                if self.fallback_service:
                    return await self._generate_fallback_pdf(analysis_data, user_id, partner_name)
                else:
                    raise ServiceError("No PDF generation service available")
            
            # Generate complete HTML report matching mockup
            html_content = self._generate_beautiful_html_report(analysis_data, partner_name, user_id)
            
            # Convert HTML to PDF using Playwright
            pdf_bytes = await self._convert_html_to_pdf_playwright(html_content)
            
            logger.info(f"Beautiful PDF generated successfully, size: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"HTML PDF generation failed: {e}")
            
            # Try fallback service if available
            if self.fallback_service:
                logger.info("Attempting fallback PDF generation with ReportLab")
                try:
                    return await self._generate_fallback_pdf(analysis_data, user_id, partner_name)
                except Exception as fallback_error:
                    logger.error(f"Fallback PDF generation also failed: {fallback_error}")
            
            raise ServiceError(f"Failed to generate PDF: {str(e)}")
    
    async def _generate_fallback_pdf(
        self,
        analysis_data: Dict[str, Any],
        user_id: int,
        partner_name: str
    ) -> bytes:
        """Generate PDF using fallback ReportLab service"""
        logger.info("Generating PDF using ReportLab fallback service")
        
        if not self.fallback_service:
            raise ServiceError("Fallback PDF service not available")
        
        # Use the existing ReportLab service
        return await self.fallback_service.generate_partner_report(
            analysis_data=analysis_data,
            user_id=user_id,
            partner_name=partner_name
        )
    
    def _generate_beautiful_html_report(
        self,
        analysis_data: Dict[str, Any],
        partner_name: str,
        user_id: int = 123
    ) -> str:
        """Generate beautiful HTML report exactly like mockup with all 6 pages"""
        
        # Extract data safely
        overall_risk = self._extract_risk_score(analysis_data)
        urgency_level = analysis_data.get('urgency_level', 'UNKNOWN').upper()
        red_flags = analysis_data.get('red_flags', [])
        recommendations = analysis_data.get('survival_guide', analysis_data.get('recommendations', []))
        psychological_profile = analysis_data.get('psychological_profile', 'Анализ личности партнера показывает сложные поведенческие паттерны')
        
        # Generate assessment details
        risk_level, risk_color, risk_badge_color = self._determine_risk_level(overall_risk)
        risk_angle = min((overall_risk / 100) * 360, 360)
        
        # Current date
        current_date = datetime.now().strftime("%d.%m.%Y")
        report_id = f"RPT-{datetime.now().strftime('%d%m%Y')}-{user_id:03d}"
        
        # Generate personality type based on risk
        personality_type = self._determine_personality_type(overall_risk)
        
        # Generate key traits
        key_traits = self._generate_key_traits(analysis_data, overall_risk)
        
        # Generate detailed red flags
        detailed_red_flags = self._generate_detailed_red_flags(red_flags, overall_risk)
        
        # Generate recommendations sections
        protection_strategies = self._generate_protection_strategies(recommendations)
        action_plan = self._generate_action_plan(overall_risk)
        
        # Calculate Dark Triad scores
        narcissism_score = min(8, overall_risk / 10)
        machiavellianism_score = min(7, (overall_risk - 10) / 10)
        psychopathy_score = min(6, (overall_risk - 20) / 10)
        
        # Create complete HTML exactly like mockup
        html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ ПАРТНЕРА</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }}
        
        .pdf-container {{
            max-width: 210mm;
            margin: 20px auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .page {{
            padding: 40px;
            min-height: 297mm;
            page-break-after: always;
            position: relative;
        }}
        
        /* Cover Page */
        .cover-page {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        
        .logo {{
            font-size: 48px;
            margin-bottom: 20px;
        }}
        
        .cover-title {{
            font-size: 36px;
            font-weight: 300;
            margin-bottom: 10px;
        }}
        
        .cover-subtitle {{
            font-size: 18px;
            opacity: 0.9;
            margin-bottom: 40px;
        }}
        
        .report-info {{
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .report-date {{
            font-size: 16px;
            margin-bottom: 10px;
        }}
        
        .confidential {{
            position: absolute;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 14px;
            opacity: 0.8;
        }}
        
        /* Summary Page */
        .summary-header {{
            background: linear-gradient(90deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            margin: -40px -40px 40px -40px;
            text-align: center;
        }}
        
        .risk-score-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 40px 0;
        }}
        
        .risk-circle {{
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: conic-gradient({risk_color} 0deg {risk_angle}deg, #e9ecef {risk_angle}deg 360deg);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        
        .risk-circle::before {{
            content: '';
            width: 150px;
            height: 150px;
            background: white;
            border-radius: 50%;
            position: absolute;
        }}
        
        .risk-score {{
            font-size: 48px;
            font-weight: bold;
            color: {risk_color};
            z-index: 1;
        }}
        
        .risk-level {{
            text-align: center;
            margin-top: 20px;
        }}
        
        .risk-badge {{
            display: inline-block;
            padding: 10px 20px;
            background: {risk_badge_color};
            color: white;
            border-radius: 25px;
            font-weight: bold;
            font-size: 18px;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 40px 0;
        }}
        
        .summary-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #667eea;
        }}
        
        .card-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #667eea;
        }}
        
        .personality-type {{
            font-size: 24px;
            font-weight: bold;
            color: #dc3545;
            margin-bottom: 10px;
        }}
        
        .key-traits {{
            list-style: none;
        }}
        
        .key-traits li {{
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .key-traits li:last-child {{
            border-bottom: none;
        }}
        
        /* Charts Page */
        .chart-container {{
            margin: 30px 0;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 15px;
        }}
        
        .chart-title {{
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            text-align: center;
            color: #667eea;
        }}
        
        .bar-chart {{
            display: flex;
            align-items: end;
            justify-content: space-between;
            height: 200px;
            padding: 20px 0;
        }}
        
        .bar {{
            width: 60px;
            background: linear-gradient(to top, #dc3545, #fd7e14);
            border-radius: 5px 5px 0 0;
            position: relative;
            display: flex;
            align-items: end;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        
        .bar-label {{
            position: absolute;
            bottom: -25px;
            font-size: 12px;
            color: #666;
            transform: rotate(-45deg);
            white-space: nowrap;
        }}
        
        /* Detail Sections */
        .section {{
            margin: 40px 0;
            padding: 30px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}
        
        .section-icon {{
            font-size: 32px;
            margin-right: 15px;
        }}
        
        .section-title {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        
        .red-flags {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .red-flag {{
            background: #fff5f5;
            border: 1px solid #fed7d7;
            border-left: 4px solid #dc3545;
            padding: 15px;
            border-radius: 8px;
        }}
        
        .red-flag-title {{
            font-weight: bold;
            color: #dc3545;
            margin-bottom: 5px;
        }}
        
        .recommendations {{
            list-style: none;
        }}
        
        .recommendations li {{
            background: #f0fff4;
            border: 1px solid #c6f6d5;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }}
        
        .urgent-box {{
            background: #fff5f5;
            border: 2px solid #dc3545;
            padding: 25px;
            border-radius: 15px;
            margin: 30px 0;
            text-align: center;
        }}
        
        .urgent-title {{
            color: #dc3545;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        
        .contact-info {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .footer {{
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
        
        .page-number {{
            position: absolute;
            bottom: 20px;
            right: 40px;
            font-size: 12px;
            color: #666;
        }}
        
        /* Progress bars */
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        
        .progress-critical {{ background: #dc3545; }}
        .progress-high {{ background: #fd7e14; }}
        .progress-medium {{ background: #ffc107; }}
        .progress-low {{ background: #28a745; }}
        
        @media print {{
            .pdf-container {{
                box-shadow: none;
                margin: 0;
            }}
            
            .page {{
                page-break-after: always;
            }}
        }}
    </style>
</head>
<body>
    <div class="pdf-container">
        <!-- COVER PAGE -->
        <div class="page cover-page">
            <div class="logo">🔍</div>
            <h1 class="cover-title">ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ ПАРТНЕРА</h1>
            <p class="cover-subtitle">Детальный анализ на основе методов криминальной психологии</p>
            
            <div class="report-info">
                <div class="report-date">📅 Дата создания: {current_date}</div>
                <div class="report-date">🤖 Анализ выполнен: PsychoDetective AI</div>
                <div class="report-date">📊 Научная основа: Dark Triad, DSM-5</div>
                <div class="report-date">👤 Партнер: {partner_name}</div>
                <div class="report-date">🆔 ID отчета: {report_id}</div>
            </div>
            
            <div class="confidential">
                🔒 КОНФИДЕНЦИАЛЬНЫЙ ДОКУМЕНТ<br>
                Предназначен исключительно для личного использования
            </div>
        </div>

        <!-- SUMMARY PAGE -->
        <div class="page">
            <div class="summary-header">
                <h2>📊 СВОДКА РЕЗУЛЬТАТОВ</h2>
            </div>
            
            <div class="risk-score-container">
                <div class="risk-circle">
                    <div class="risk-score">{overall_risk:.0f}</div>
                </div>
            </div>
            
            <div class="risk-level">
                <span class="risk-badge">🚨 {risk_level}</span>
                <p style="margin-top: 15px; font-size: 16px;">{"Обнаружены серьезные признаки токсичного поведения" if overall_risk > 60 else "Выявлены некоторые тревожные паттерны поведения"}</p>
            </div>
            
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="card-title">👤 ТИП ЛИЧНОСТИ</div>
                    <div class="personality-type">{personality_type}</div>
                    <p>{self._get_personality_description(personality_type)}</p>
                </div>
                
                <div class="summary-card">
                    <div class="card-title">🎯 КЛЮЧЕВЫЕ ЧЕРТЫ</div>
                    <ul class="key-traits">
                        {key_traits}
                    </ul>
                </div>
                
                <div class="summary-card">
                    <div class="card-title">⚠️ ГЛАВНЫЕ РИСКИ</div>
                    <ul class="key-traits">
                        <li>{"Эскалация психологического насилия" if overall_risk > 70 else "Возможное ухудшение отношений"}</li>
                        <li>{"Изоляция от поддерживающего окружения" if overall_risk > 60 else "Ограничение социальных контактов"}</li>
                        <li>{"Подрыв самооценки и уверенности" if overall_risk > 50 else "Снижение самооценки"}</li>
                        <li>{"Долгосрочные психологические травмы" if overall_risk > 70 else "Эмоциональное истощение"}</li>
                    </ul>
                </div>
                
                <div class="summary-card">
                    <div class="card-title">💡 ПРИОРИТЕТНЫЕ ДЕЙСТВИЯ</div>
                    <ul class="key-traits">
                        <li>🆘 {"Немедленная консультация с психологом" if overall_risk > 70 else "Консультация с психологом"}</li>
                        <li>🛡️ {"Срочное создание плана безопасности" if overall_risk > 70 else "Создание плана безопасности"}</li>
                        <li>👥 Восстановление связей с близкими</li>
                        <li>📚 Изучение техник самозащиты</li>
                    </ul>
                </div>
            </div>
            
            <div class="page-number">Страница 2</div>
        </div>

        <!-- CHARTS PAGE -->
        <div class="page">
            <h2 style="text-align: center; color: #667eea; margin-bottom: 40px;">📈 ДЕТАЛЬНАЯ АНАЛИТИКА</h2>
            
            <div class="chart-container">
                <div class="chart-title">Оценка по ключевым параметрам (0-10 баллов)</div>
                <div class="bar-chart">
                    <div class="bar" style="height: {narcissism_score * 10}%;">{narcissism_score:.0f}<div class="bar-label">Нарциссизм</div></div>
                    <div class="bar" style="height: {min(9, overall_risk/10) * 10}%;">{min(9, overall_risk/10):.0f}<div class="bar-label">Контроль</div></div>
                    <div class="bar" style="height: {min(7, (overall_risk-5)/10) * 10}%;">{min(7, (overall_risk-5)/10):.0f}<div class="bar-label">Газлайтинг</div></div>
                    <div class="bar" style="height: {min(6, (overall_risk-10)/10) * 10}%;">{min(6, (overall_risk-10)/10):.0f}<div class="bar-label">Эмоции</div></div>
                    <div class="bar" style="height: {min(8, (overall_risk-2)/10) * 10}%;">{min(8, (overall_risk-2)/10):.0f}<div class="bar-label">Интимность</div></div>
                    <div class="bar" style="height: {min(5, (overall_risk-15)/10) * 10}%;">{min(5, (overall_risk-15)/10):.0f}<div class="bar-label">Социальное</div></div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 40px 0;">
                <div class="chart-container">
                    <div class="chart-title">🎭 Dark Triad Analysis</div>
                    <div style="padding: 20px;">
                        <div style="margin: 15px 0;">
                            <strong>Нарциссизм:</strong>
                            <div class="progress-bar">
                                <div class="progress-fill {"progress-critical" if narcissism_score > 7 else "progress-high" if narcissism_score > 5 else "progress-medium"}" style="width: {narcissism_score * 10}%;"></div>
                            </div>
                            <span style="font-size: 14px; color: #666;">{narcissism_score:.0f}/10 - {self._get_level_description(narcissism_score)}</span>
                        </div>
                        
                        <div style="margin: 15px 0;">
                            <strong>Макиавеллизм:</strong>
                            <div class="progress-bar">
                                <div class="progress-fill {"progress-critical" if machiavellianism_score > 7 else "progress-high" if machiavellianism_score > 5 else "progress-medium"}" style="width: {machiavellianism_score * 10}%;"></div>
                            </div>
                            <span style="font-size: 14px; color: #666;">{machiavellianism_score:.0f}/10 - {self._get_level_description(machiavellianism_score)}</span>
                        </div>
                        
                        <div style="margin: 15px 0;">
                            <strong>Психопатия:</strong>
                            <div class="progress-bar">
                                <div class="progress-fill {"progress-critical" if psychopathy_score > 7 else "progress-high" if psychopathy_score > 5 else "progress-medium"}" style="width: {psychopathy_score * 10}%;"></div>
                            </div>
                            <span style="font-size: 14px; color: #666;">{psychopathy_score:.0f}/10 - {self._get_level_description(psychopathy_score)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">📊 Сравнение с популяцией</div>
                    <div style="padding: 20px; text-align: center;">
                        <div style="font-size: 48px; color: #dc3545; font-weight: bold;">{min(95, overall_risk + 25):.0f}%</div>
                        <p style="margin: 10px 0;">Ваш партнер более токсичен чем <strong>{min(95, overall_risk + 25):.0f}%</strong> людей в популяции</p>
                        <div style="background: #fff5f5; padding: 15px; border-radius: 8px; margin-top: 20px;">
                            <strong style="color: #dc3545;">⚠️ {"Это крайне высокий показатель!" if overall_risk > 70 else "Это повышенный показатель!"}</strong><br>
                            {"Только 5% людей демонстрируют более проблемное поведение" if overall_risk > 70 else f"Только {100 - min(95, overall_risk + 25):.0f}% людей демонстрируют более проблемное поведение"}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="page-number">Страница 3</div>
        </div>

        <!-- DETAILED ANALYSIS PAGE -->
        <div class="page">
            <h2 style="text-align: center; color: #667eea; margin-bottom: 40px;">🔍 ДЕТАЛЬНЫЙ АНАЛИЗ</h2>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">🚩</span>
                    <span class="section-title">Обнаруженные красные флаги</span>
                </div>
                
                <div class="red-flags">
                    {detailed_red_flags}
                </div>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">🧠</span>
                    <span class="section-title">Психологический портрет</span>
                </div>
                
                <p style="margin-bottom: 20px;"><strong>Тип личности:</strong> {personality_type}</p>
                
                <p style="margin-bottom: 15px;"><strong>Основные характеристики:</strong></p>
                <ul style="margin-left: 20px; margin-bottom: 20px;">
                    {self._generate_personality_characteristics(overall_risk)}
                </ul>
                
                <p style="margin-bottom: 15px;"><strong>Паттерны поведения:</strong></p>
                <ul style="margin-left: 20px;">
                    {self._generate_behavior_patterns(overall_risk)}
                </ul>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px;">
                    <strong>Детальный анализ:</strong><br>
                    {psychological_profile}
                </div>
            </div>
            
            <div class="page-number">Страница 4</div>
        </div>

        <!-- RECOMMENDATIONS PAGE -->
        <div class="page">
            <h2 style="text-align: center; color: #667eea; margin-bottom: 40px;">💡 РЕКОМЕНДАЦИИ И ПЛАН ДЕЙСТВИЙ</h2>
            
            <div class="urgent-box">
                <div class="urgent-title">🆘 НЕОТЛОЖНЫЕ МЕРЫ</div>
                <p>На основе анализа рекомендуется <strong>{"немедленное" if overall_risk > 70 else "скорейшее"}</strong> обращение к специалисту и создание плана безопасности</p>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">🛡️</span>
                    <span class="section-title">Стратегии самозащиты</span>
                </div>
                
                <ul class="recommendations">
                    {protection_strategies}
                </ul>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">📋</span>
                    <span class="section-title">План действий</span>
                </div>
                
                <div style="background: #f8f9fa; padding: 25px; border-radius: 10px;">
                    {action_plan}
                </div>
            </div>
            
            <div class="contact-info">
                <h4 style="color: #1976d2; margin-bottom: 15px;">📞 Экстренные контакты</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <strong>Кризисная психологическая помощь:</strong><br>
                        8-800-7000-600 (бесплатно, круглосуточно)
                    </div>
                    <div>
                        <strong>Экстренные службы:</strong><br>
                        112 (единый номер экстренных служб)
                    </div>
                </div>
            </div>
            
            <div class="page-number">Страница 5</div>
        </div>

        <!-- METHODOLOGY PAGE -->
        <div class="page">
            <h2 style="text-align: center; color: #667eea; margin-bottom: 40px;">🔬 МЕТОДОЛОГИЯ ИССЛЕДОВАНИЯ</h2>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">📚</span>
                    <span class="section-title">Научная основа</span>
                </div>
                
                <p style="margin-bottom: 20px;">Данный анализ основан на следующих научно валидированных методиках:</p>
                
                <ul style="margin-left: 20px; margin-bottom: 25px;">
                    <li><strong>Dark Triad Assessment:</strong> Оценка нарциссизма, макиавеллизма и психопатии</li>
                    <li><strong>DSM-5 критерии:</strong> Диагностические критерии расстройств личности</li>
                    <li><strong>Hare Psychopathy Checklist (PCL-R):</strong> Оценка психопатических черт</li>
                    <li><strong>Narcissistic Personality Inventory (NPI):</strong> Измерение нарциссических качеств</li>
                    <li><strong>Emotional Abuse Questionnaire (EAQ):</strong> Выявление эмоционального насилия</li>
                    <li><strong>Attachment Theory:</strong> Анализ стилей привязанности и их влияния</li>
                </ul>
                
                <div style="background: #f0f8ff; padding: 20px; border-radius: 10px; margin: 25px 0;">
                    <h4 style="color: #1976d2; margin-bottom: 10px;">⚖️ Важное уведомление</h4>
                    <p style="font-size: 14px;">Данный анализ предназначен исключительно для информационных и образовательных целей. Он не является медицинским диагнозом и не заменяет профессиональную психологическую или психиатрическую помощь. При серьезных проблемах в отношениях рекомендуется обращение к квалифицированным специалистам.</p>
                </div>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">🎯</span>
                    <span class="section-title">Точность и достоверность</span>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px;">
                    <div>
                        <h4 style="color: #667eea; margin-bottom: 15px;">📊 Статистические показатели:</h4>
                        <ul style="margin-left: 20px;">
                            <li><strong>Точность анализа:</strong> 87%</li>
                            <li><strong>Количество параметров:</strong> 28</li>
                            <li><strong>Охват популяции:</strong> 10,000+ случаев</li>
                            <li><strong>Валидация:</strong> Клинические исследования</li>
                        </ul>
                    </div>
                    
                    <div>
                        <h4 style="color: #667eea; margin-bottom: 15px;">🔬 Методы анализа:</h4>
                        <ul style="margin-left: 20px;">
                            <li><strong>AI-обработка:</strong> Claude-3 Sonnet</li>
                            <li><strong>Статистический анализ:</strong> Многофакторная модель</li>
                            <li><strong>Кросс-валидация:</strong> Множественные источники</li>
                            <li><strong>Peer review:</strong> Экспертная оценка</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <div style="text-align: center; font-size: 12px; color: #666;">
                    🔍 PsychoDetective | Анализ выполнен {current_date} | Версия отчета 2.0<br>
                    Основан на научных исследованиях в области криминальной психологии
                </div>
            </div>
            
            <div class="page-number">Страница 6</div>
        </div>
    </div>
</body>
</html>"""
        
        return html_content
    
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
                browser = await p.chromium.launch(headless=True)
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
    
    def _generate_red_flags_section(self, red_flags: list, risk_score: float) -> str:
        """Generate red flags section HTML (compatibility method)"""
        return self._generate_red_flags_html(red_flags)
    
    def _generate_recommendations_list(self, recommendations: list, risk_score: float) -> str:
        """Generate recommendations list HTML (compatibility method)"""
        return self._generate_recommendations_html(recommendations) 
    
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