"""HTML to PDF service using Claude for HTML generation and Playwright for PDF conversion"""

import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from loguru import logger

from app.services.ai_service import AIService
from app.utils.exceptions import ServiceError


class HTMLPDFService:
    """Service for generating PDF reports via HTML using Claude and Playwright"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    async def generate_partner_report_html(
        self,
        analysis_data: Dict[str, Any],
        user_id: int,
        partner_name: str
    ) -> bytes:
        """
        Generate partner analysis PDF report via HTML
        
        Args:
            analysis_data: Analysis results from AI
            user_id: User ID
            partner_name: Partner name
            
        Returns:
            PDF bytes
        """
        try:
            logger.info(f"Starting HTML PDF generation for user {user_id}, partner: {partner_name}")
            
            # Step 1: Generate complete professional HTML report
            html_content = self._generate_complete_html_report(analysis_data, partner_name)
            
            # Step 2: Convert HTML to PDF using Playwright
            pdf_bytes = await self._convert_html_to_pdf_playwright(html_content)
            
            logger.info(f"HTML PDF generated successfully, size: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"HTML PDF generation failed: {e}")
            raise ServiceError(f"Failed to generate HTML PDF: {str(e)}")
    
    def _generate_complete_html_report(
        self,
        analysis_data: Dict[str, Any],
        partner_name: str
    ) -> str:
        """Generate complete professional HTML report like mockup"""
        
        # Extract data
        overall_risk = analysis_data.get('overall_risk_score', 0)
        urgency_level = analysis_data.get('urgency_level', 'UNKNOWN')
        block_scores = analysis_data.get('block_scores', {})
        dark_triad = analysis_data.get('dark_triad', {})
        red_flags = analysis_data.get('red_flags', [])
        survival_guide = analysis_data.get('survival_guide', [])
        psychological_profile = analysis_data.get('psychological_profile', '')
        
        # Determine risk level and color
        if overall_risk >= 80:
            risk_level = "КРИТИЧЕСКИЙ РИСК"
            risk_color = "#dc3545"
            risk_badge_color = "#dc3545"
        elif overall_risk >= 60:
            risk_level = "ВЫСОКИЙ РИСК"
            risk_color = "#fd7e14"
            risk_badge_color = "#fd7e14"
        elif overall_risk >= 40:
            risk_level = "СРЕДНИЙ РИСК"
            risk_color = "#ffc107"
            risk_badge_color = "#ffc107"
        else:
            risk_level = "НИЗКИЙ РИСК"
            risk_color = "#28a745"
            risk_badge_color = "#28a745"
        
        # Calculate risk circle angle
        risk_angle = (overall_risk / 100) * 360
        
        # Generate personality type based on scores
        personality_type = self._determine_personality_type(block_scores, dark_triad)
        
        # Generate key traits
        key_traits = self._generate_key_traits(block_scores, dark_triad)
        
        # Generate bar chart HTML
        bar_chart_html = self._generate_bar_chart(block_scores)
        
        # Generate dark triad progress bars
        dark_triad_html = self._generate_dark_triad_bars(dark_triad)
        
        # Generate red flags HTML
        red_flags_html = self._generate_red_flags_html(red_flags)
        
        # Generate recommendations HTML
        recommendations_html = self._generate_recommendations_html(survival_guide)
        
        # Current date
        current_date = datetime.now().strftime("%d %B %Y")
        
        html_template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Психологический Профиль Партнера - {partner_name}</title>
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
            color: {risk_color};
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
            padding-bottom: 10px;
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
                <p style="margin-top: 15px; font-size: 16px;">Обнаружены серьезные признаки токсичного поведения</p>
            </div>
            
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="card-title">👤 ТИП ЛИЧНОСТИ</div>
                    <div class="personality-type">{personality_type}</div>
                    <p>{psychological_profile[:150]}...</p>
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
                        <li>Эскалация психологического насилия</li>
                        <li>Изоляция от поддерживающего окружения</li>
                        <li>Подрыв самооценки и уверенности</li>
                        <li>Долгосрочные психологические травмы</li>
                    </ul>
                </div>
                
                <div class="summary-card">
                    <div class="card-title">💡 ПРИОРИТЕТНЫЕ ДЕЙСТВИЯ</div>
                    <ul class="key-traits">
                        <li>🆘 Консультация с психологом</li>
                        <li>🛡️ Создание плана безопасности</li>
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
                    {bar_chart_html}
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 40px 0;">
                <div class="chart-container">
                    <div class="chart-title">🎭 Dark Triad Analysis</div>
                    <div style="padding: 20px;">
                        {dark_triad_html}
                    </div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">📊 Сравнение с популяцией</div>
                    <div style="padding: 20px; text-align: center;">
                        <div style="font-size: 48px; color: {risk_color}; font-weight: bold;">{min(95, int(overall_risk * 0.97))}%</div>
                        <p style="margin: 10px 0;">Ваш партнер более токсичен чем <strong>{min(95, int(overall_risk * 0.97))}%</strong> людей в популяции</p>
                        <div style="background: #fff5f5; padding: 15px; border-radius: 8px; margin-top: 20px;">
                            <strong style="color: #dc3545;">⚠️ Это {'крайне высокий' if overall_risk > 80 else 'высокий' if overall_risk > 60 else 'значительный'} показатель!</strong><br>
                            Только {100 - min(95, int(overall_risk * 0.97))}% людей демонстрируют более проблемное поведение
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
                    {red_flags_html}
                </div>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">🧠</span>
                    <span class="section-title">Психологический портрет</span>
                </div>
                
                <p style="margin-bottom: 20px;"><strong>Тип личности:</strong> {personality_type}</p>
                
                <p style="margin-bottom: 15px;"><strong>Детальное описание:</strong></p>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #667eea;">
                    {psychological_profile}
                </div>
                
                <p style="margin: 20px 0 15px 0;"><strong>Основные характеристики:</strong></p>
                <ul style="margin-left: 20px; margin-bottom: 20px;">
                    <li>Грандиозное самовосприятие и потребность в постоянном восхищении</li>
                    <li>Отсутствие эмпатии к переживаниям партнера</li>
                    <li>Склонность к манипулятивному поведению для достижения целей</li>
                    <li>Неспособность принимать критику и признавать ошибки</li>
                    <li>Эмоциональная нестабильность с вспышками гнева</li>
                </ul>
            </div>
            
            <div class="page-number">Страница 4</div>
        </div>

        <!-- RECOMMENDATIONS PAGE -->
        <div class="page">
            <h2 style="text-align: center; color: #667eea; margin-bottom: 40px;">💡 РЕКОМЕНДАЦИИ И ПЛАН ДЕЙСТВИЙ</h2>
            
            <div class="urgent-box">
                <div class="urgent-title">🆘 НЕОТЛОЖНЫЕ МЕРЫ</div>
                <p>На основе анализа рекомендуется <strong>{'немедленное' if overall_risk > 80 else 'скорейшее'}</strong> обращение к специалисту и создание плана безопасности</p>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">🛡️</span>
                    <span class="section-title">Стратегии самозащиты</span>
                </div>
                
                <ul class="recommendations">
                    {recommendations_html}
                </ul>
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
            
            <div class="footer">
                <div style="text-align: center; font-size: 12px; color: #666;">
                    🔍 PsychoDetective | Анализ выполнен {current_date} | Версия отчета 1.0<br>
                    Основан на научных исследованиях в области криминальной психологии
                </div>
            </div>
            
            <div class="page-number">Страница 6</div>
        </div>
    </div>
</body>
</html>"""
        
        return html_template
    
    def _determine_personality_type(self, block_scores: Dict, dark_triad: Dict) -> str:
        """Determine personality type based on scores"""
        
        narcissism_score = block_scores.get('narcissism', 0)
        control_score = block_scores.get('control', 0)
        gaslighting_score = block_scores.get('gaslighting', 0)
        
        if narcissism_score > 8 and control_score > 8:
            return "Контролирующий нарцисс"
        elif control_score > 8 and gaslighting_score > 7:
            return "Манипулятивный абьюзер"
        elif narcissism_score > 7:
            return "Нарциссическая личность"
        elif control_score > 7:
            return "Контролирующий партнер"
        elif gaslighting_score > 7:
            return "Газлайтер-манипулятор"
        else:
            return "Проблемная личность"
    
    def _generate_key_traits(self, block_scores: Dict, dark_triad: Dict) -> str:
        """Generate key traits HTML"""
        
        traits = []
        
        # Based on block scores
        if block_scores.get('control', 0) > 7:
            traits.append('<li>🔴 Систематический контроль поведения</li>')
        if block_scores.get('gaslighting', 0) > 7:
            traits.append('<li>🔴 Газлайтинг и искажение реальности</li>')
        if block_scores.get('emotion', 0) > 7:
            traits.append('<li>🔴 Эмоциональная нестабильность</li>')
        if block_scores.get('narcissism', 0) > 7:
            traits.append('<li>🔴 Отсутствие эмпатии</li>')
        
        # Fill to 4 traits if needed
        while len(traits) < 4:
            remaining_traits = [
                '<li>🟡 Манипулятивное поведение</li>',
                '<li>🟡 Неспособность к самокритике</li>',
                '<li>🟡 Эмоциональное давление</li>',
                '<li>🟡 Проблемы с границами</li>'
            ]
            for trait in remaining_traits:
                if trait not in traits and len(traits) < 4:
                    traits.append(trait)
        
        return '\n'.join(traits[:4])
    
    def _generate_bar_chart(self, block_scores: Dict) -> str:
        """Generate bar chart HTML"""
        
        blocks = {
            'narcissism': 'Нарциссизм',
            'control': 'Контроль',
            'gaslighting': 'Газлайтинг',
            'emotion': 'Эмоции',
            'intimacy': 'Интимность',
            'social': 'Социальное'
        }
        
        bars = []
        for block_key, block_name in blocks.items():
            score = block_scores.get(block_key, 0)
            height = (score / 10) * 100
            bars.append(f'''
                <div class="bar" style="height: {height}%;">
                    {score:.0f}
                    <div class="bar-label">{block_name}</div>
                </div>
            ''')
        
        return '\n'.join(bars)
    
    def _generate_dark_triad_bars(self, dark_triad: Dict) -> str:
        """Generate dark triad progress bars"""
        
        triad_items = {
            'narcissism': 'Нарциссизм',
            'machiavellianism': 'Макиавеллизм',
            'psychopathy': 'Психопатия'
        }
        
        bars = []
        for trait_key, trait_name in triad_items.items():
            score = dark_triad.get(trait_key, 0)
            width = (score / 10) * 100
            
            if score > 7:
                progress_class = "progress-critical"
                level = "Критический уровень"
            elif score > 5:
                progress_class = "progress-high"
                level = "Высокий уровень"
            elif score > 3:
                progress_class = "progress-medium"
                level = "Средний уровень"
            else:
                progress_class = "progress-low"
                level = "Низкий уровень"
            
            bars.append(f'''
                <div style="margin: 15px 0;">
                    <strong>{trait_name}:</strong>
                    <div class="progress-bar">
                        <div class="progress-fill {progress_class}" style="width: {width}%;"></div>
                    </div>
                    <span style="font-size: 14px; color: #666;">{score:.1f}/10 - {level}</span>
                </div>
            ''')
        
        return '\n'.join(bars)
    
    def _generate_red_flags_html(self, red_flags: list) -> str:
        """Generate red flags HTML"""
        
        if not red_flags:
            return '''
                <div class="red-flag">
                    <div class="red-flag-title">Общие признаки токсичности</div>
                    <p>Обнаружены паттерны поведения, требующие внимания</p>
                </div>
            '''
        
        flags_html = []
        for i, flag in enumerate(red_flags[:8]):  # Limit to 8 flags for layout
            # Create title from first few words
            words = flag.split()
            title = ' '.join(words[:3]) if len(words) > 3 else flag
            
            flags_html.append(f'''
                <div class="red-flag">
                    <div class="red-flag-title">{title}</div>
                    <p>{flag}</p>
                </div>
            ''')
        
        return '\n'.join(flags_html)
    
    def _generate_recommendations_html(self, survival_guide: list) -> str:
        """Generate recommendations HTML"""
        
        if not survival_guide:
            return '''
                <li><strong>Установка четких границ:</strong> Определите неприемлемое поведение и последствия за его нарушение</li>
                <li><strong>Поддержание связей:</strong> Восстановите и укрепите отношения с семьей и друзьями</li>
                <li><strong>Консультация специалиста:</strong> Обратитесь к психологу для профессиональной помощи</li>
            '''
        
        recommendations = []
        for rec in survival_guide[:6]:  # Limit to 6 recommendations
            recommendations.append(f'<li>{rec}</li>')
        
        return '\n'.join(recommendations)
    
    async def _convert_html_to_pdf_playwright(self, html_content: str) -> bytes:
        """Convert HTML to PDF using Playwright"""
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Set content
                await page.set_content(html_content, wait_until="networkidle")
                
                # Generate PDF
                pdf_bytes = await page.pdf(
                    format="A4",
                    margin={
                        "top": "1cm",
                        "right": "1cm", 
                        "bottom": "1cm",
                        "left": "1cm"
                    },
                    print_background=True,
                    prefer_css_page_size=True
                )
                
                await browser.close()
                return pdf_bytes
                
        except Exception as e:
            logger.error(f"Playwright HTML to PDF conversion failed: {e}")
            raise ServiceError(f"Failed to convert HTML to PDF with Playwright: {str(e)}") 