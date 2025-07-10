"""ReportLab PDF Generation Service with Russian text support"""

import io
import base64
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Wedge
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

from app.core.logging import logger
from app.utils.exceptions import ServiceError

# Configure matplotlib for Russian text
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Arial']
plt.rcParams['axes.unicode_minus'] = False


class ReportLabPDFService:
    """ReportLab-based PDF generation service with Russian support"""
    
    def __init__(self):
        self.charts_dir = Path("temp_charts")
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        
        # Register fonts for Russian text
        self._register_fonts()
        
        # Create styles
        self.styles = self._create_styles()
    
    def _register_fonts(self):
        """Register fonts that support Russian text"""
        try:
            # Try to register DejaVu Sans font for Russian text
            import matplotlib.font_manager as fm
            
            # Find DejaVu Sans font
            dejavu_font = None
            for font in fm.fontManager.ttflist:
                if 'DejaVu Sans' in font.name and font.style == 'normal':
                    dejavu_font = font.fname
                    break
            
            if dejavu_font:
                pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_font))
                logger.info(f"Registered DejaVu Sans font: {dejavu_font}")
                self.russian_font = 'DejaVuSans'
            else:
                # Try to use built-in fonts that support some Cyrillic
                logger.warning("DejaVu Sans font not found, trying alternative fonts")
                
                # Try Arial Unicode MS if available
                try:
                    arial_unicode = None
                    for font in fm.fontManager.ttflist:
                        if 'Arial Unicode MS' in font.name:
                            arial_unicode = font.fname
                            break
                    
                    if arial_unicode:
                        pdfmetrics.registerFont(TTFont('ArialUnicodeMS', arial_unicode))
                        logger.info(f"Registered Arial Unicode MS font: {arial_unicode}")
                        self.russian_font = 'ArialUnicodeMS'
                    else:
                        logger.warning("No suitable Unicode font found, using Helvetica")
                        self.russian_font = 'Helvetica'
                except:
                    logger.warning("Font registration failed, using Helvetica")
                    self.russian_font = 'Helvetica'
                
        except Exception as e:
            logger.warning(f"Font registration failed: {e}, using Helvetica")
            self.russian_font = 'Helvetica'
    
    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create paragraph styles for the document"""
        styles = getSampleStyleSheet()
        
        # Use registered Russian font
        font_name = getattr(self, 'russian_font', 'Helvetica')
        
        custom_styles = {
            'CustomTitle': ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                textColor=HexColor('#FFFFFF'),
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName=font_name
            ),
            'CustomHeading1': ParagraphStyle(
                'CustomHeading1',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=HexColor('#667eea'),
                spaceAfter=12,
                spaceBefore=20,
                fontName=font_name
            ),
            'CustomHeading2': ParagraphStyle(
                'CustomHeading2',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=HexColor('#333333'),
                spaceAfter=10,
                spaceBefore=15,
                fontName=font_name
            ),
            'CustomNormal': ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                textColor=HexColor('#333333'),
                spaceAfter=6,
                leading=14,
                fontName=font_name
            ),
            'RiskScore': ParagraphStyle(
                'RiskScore',
                parent=styles['Normal'],
                fontSize=48,
                textColor=HexColor('#dc3545'),
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName=font_name
            ),
            'RedFlag': ParagraphStyle(
                'RedFlag',
                parent=styles['Normal'],
                fontSize=11,
                textColor=HexColor('#dc3545'),
                leftIndent=20,
                bulletIndent=10,
                spaceAfter=6,
                fontName=font_name
            )
        }
        
        return custom_styles
    
    async def generate_partner_report(
        self,
        analysis_data: Dict[str, Any],
        user_id: int,
        partner_name: str = "партнер"
    ) -> bytes:
        """Generate PDF report using ReportLab"""
        try:
            logger.info(f"Starting ReportLab PDF generation for user {user_id}")
            
            # Create PDF buffer
            buffer = io.BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            # Build content
            story = []
            
            # Cover page
            story.extend(self._create_cover_page(analysis_data, partner_name))
            
            # Risk assessment page
            story.extend(self._create_risk_assessment_page(analysis_data))
            
            # Psychological profile page
            story.extend(self._create_psychological_profile_page(analysis_data))
            
            # Red flags page
            story.extend(self._create_red_flags_page(analysis_data))
            
            # Recommendations page
            story.extend(self._create_recommendations_page(analysis_data))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            # Cleanup
            self._cleanup_temp_files(user_id)
            
            logger.info(f"ReportLab PDF generated successfully, size: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"ReportLab PDF generation failed: {e}")
            self._cleanup_temp_files(user_id)
            raise ServiceError(f"Failed to generate PDF report: {str(e)}")
    
    def _create_cover_page(self, analysis_data: Dict[str, Any], partner_name: str) -> List:
        """Create cover page"""
        story = []
        
        # Title
        story.append(Paragraph("ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ ПАРТНЕРА", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Partner name
        story.append(Paragraph(f'"{partner_name}"', self.styles['CustomTitle']))
        story.append(Spacer(1, 30))
        
        # Risk score
        risk_score = analysis_data.get('overall_risk_score', 0)
        story.append(Paragraph(f"{int(risk_score)}%", self.styles['RiskScore']))
        story.append(Spacer(1, 20))
        
        # Date
        current_date = datetime.now().strftime("%d.%m.%Y")
        story.append(Paragraph(f"Дата создания: {current_date}", self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Report ID
        story.append(Paragraph(f"ID отчета: RPT-{current_date.replace('.', '')}-{analysis_data.get('user_id', 'XXX')}", self.styles['CustomNormal']))
        
        story.append(PageBreak())
        return story
    
    def _create_risk_assessment_page(self, analysis_data: Dict[str, Any]) -> List:
        """Create risk assessment page"""
        story = []
        
        story.append(Paragraph("ОЦЕНКА РИСКА", self.styles['CustomHeading1']))
        story.append(Spacer(1, 20))
        
        # Overall risk
        risk_score = analysis_data.get('overall_risk_score', 0)
        urgency = analysis_data.get('urgency_level', 'UNKNOWN')
        
        # Risk level table
        risk_data = [
            ['Параметр', 'Значение'],
            ['Общий уровень риска', f'{int(risk_score)}%'],
            ['Уровень срочности', urgency],
            ['Оценка', self._get_risk_level_text(risk_score)]
        ]
        
        risk_table = Table(risk_data, colWidths=[3*inch, 2*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.russian_font),
            ('FONTNAME', (0, 1), (-1, -1), self.russian_font),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(risk_table)
        story.append(Spacer(1, 30))
        
        # Block scores
        block_scores = analysis_data.get('block_scores', {})
        if block_scores:
            story.append(Paragraph("Детальная оценка по блокам:", self.styles['CustomHeading2']))
            story.append(Spacer(1, 10))
            
            block_names = {
                'narcissism': 'Нарциссизм',
                'control': 'Контроль',
                'gaslighting': 'Газлайтинг',
                'emotion': 'Эмоциональное воздействие',
                'intimacy': 'Интимность',
                'social': 'Социальное влияние'
            }
            
            block_data = [['Блок', 'Оценка', 'Уровень']]
            for block_key, score in block_scores.items():
                if block_key in block_names:
                    block_data.append([
                        block_names[block_key],
                        f'{score:.1f}/10',
                        self._get_score_level_text(score)
                    ])
            
            block_table = Table(block_data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
            block_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.russian_font),
                ('FONTNAME', (0, 1), (-1, -1), self.russian_font),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(block_table)
        
        story.append(PageBreak())
        return story
    
    def _create_psychological_profile_page(self, analysis_data: Dict[str, Any]) -> List:
        """Create psychological profile page"""
        story = []
        
        story.append(Paragraph("ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ", self.styles['CustomHeading1']))
        story.append(Spacer(1, 20))
        
        # Profile text
        profile_text = analysis_data.get('psychological_profile', 'Профиль недоступен')
        story.append(Paragraph(profile_text, self.styles['CustomNormal']))
        story.append(Spacer(1, 30))
        
        # Dark Triad scores if available
        dark_triad = analysis_data.get('dark_triad', {})
        if dark_triad:
            story.append(Paragraph("Темная триада личности:", self.styles['CustomHeading2']))
            story.append(Spacer(1, 10))
            
            triad_names = {
                'narcissism': 'Нарциссизм',
                'psychopathy': 'Психопатия',
                'machiavellianism': 'Макиавеллизм'
            }
            
            triad_data = [['Черта', 'Оценка', 'Интерпретация']]
            for trait_key, score in dark_triad.items():
                if trait_key in triad_names:
                    triad_data.append([
                        triad_names[trait_key],
                        f'{score:.1f}/10',
                        self._get_triad_interpretation(score)
                    ])
            
            triad_table = Table(triad_data, colWidths=[2*inch, 1*inch, 2*inch])
            triad_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#764ba2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.russian_font),
                ('FONTNAME', (0, 1), (-1, -1), self.russian_font),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(triad_table)
        
        story.append(PageBreak())
        return story
    
    def _create_red_flags_page(self, analysis_data: Dict[str, Any]) -> List:
        """Create red flags page"""
        story = []
        
        story.append(Paragraph("КРАСНЫЕ ФЛАГИ", self.styles['CustomHeading1']))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Обнаруженные тревожные сигналы:", self.styles['CustomNormal']))
        story.append(Spacer(1, 10))
        
        red_flags = analysis_data.get('red_flags', [])
        if red_flags:
            for flag in red_flags:
                story.append(Paragraph(f"• {flag}", self.styles['RedFlag']))
        else:
            story.append(Paragraph("Критических красных флагов не обнаружено.", self.styles['CustomNormal']))
        
        story.append(PageBreak())
        return story
    
    def _create_recommendations_page(self, analysis_data: Dict[str, Any]) -> List:
        """Create recommendations page"""
        story = []
        
        story.append(Paragraph("РЕКОМЕНДАЦИИ И ПЛАН ДЕЙСТВИЙ", self.styles['CustomHeading1']))
        story.append(Spacer(1, 20))
        
        survival_guide = analysis_data.get('survival_guide', [])
        if survival_guide:
            story.append(Paragraph("Руководство по выживанию:", self.styles['CustomHeading2']))
            story.append(Spacer(1, 10))
            
            for i, recommendation in enumerate(survival_guide, 1):
                story.append(Paragraph(f"{i}. {recommendation}", self.styles['CustomNormal']))
                story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 20))
        story.append(Paragraph("Методология:", self.styles['CustomHeading2']))
        story.append(Paragraph(
            "Данный анализ основан на научных методах психологической оценки и включает "
            "анализ паттернов поведения, эмоциональных реакций и межличностных взаимодействий. "
            "Рекомендации разработаны с учетом современных подходов к психологической безопасности.",
            self.styles['CustomNormal']
        ))
        
        return story
    
    def _get_risk_level_text(self, risk_score: float) -> str:
        """Get risk level text"""
        if risk_score < 25:
            return "НИЗКИЙ РИСК"
        elif risk_score < 50:
            return "УМЕРЕННЫЙ РИСК"
        elif risk_score < 75:
            return "ВЫСОКИЙ РИСК"
        else:
            return "КРИТИЧЕСКИЙ РИСК"
    
    def _get_score_level_text(self, score: float) -> str:
        """Get score level text"""
        if score < 3:
            return "Низкий"
        elif score < 6:
            return "Средний"
        elif score < 8:
            return "Высокий"
        else:
            return "Критический"
    
    def _get_triad_interpretation(self, score: float) -> str:
        """Get Dark Triad interpretation"""
        if score < 3:
            return "Норма"
        elif score < 6:
            return "Умеренно"
        elif score < 8:
            return "Повышенно"
        else:
            return "Критично"
    
    def _cleanup_temp_files(self, user_id: int):
        """Clean up temporary files"""
        try:
            for file_path in self.charts_dir.glob(f"*_{user_id}.*"):
                file_path.unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}") 