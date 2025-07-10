"""PDF Report Generation Service"""

import os
import io
import base64
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Wedge
import numpy as np

# Configure matplotlib for Russian text
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

from app.core.logging import logger
from app.utils.exceptions import ServiceError

# Always import ReportLab as fallback
from app.services.reportlab_pdf_service import ReportLabPDFService


class PDFReportService:
    """Service for generating PDF reports from partner analysis"""
    
    def __init__(self):
        self.templates_dir = Path("app/templates/pdf")
        self.output_dir = Path("reports")
        self.charts_dir = Path("temp_charts")
        
        # Create directories if they don't exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        
        # Always initialize ReportLab service
        self.reportlab_service = ReportLabPDFService()
        
        # Check WeasyPrint availability
        self.weasyprint_available = self._check_weasyprint_availability()
        
        # Initialize WeasyPrint components only if available
        if self.weasyprint_available:
            self._setup_weasyprint()
            logger.info("WeasyPrint PDF service initialized")
        else:
            logger.info("Using ReportLab PDF service as primary engine")
    
    def _check_weasyprint_availability(self) -> bool:
        """Check if WeasyPrint is available"""
        try:
            from jinja2 import Environment, FileSystemLoader
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            logger.info("WeasyPrint available for PDF generation")
            return True
        except ImportError as e:
            logger.warning(f"WeasyPrint not available: {e}")
            logger.info("Using ReportLab fallback for PDF generation")
            return False
    
    def _setup_weasyprint(self):
        """Setup WeasyPrint components"""
        if not self.weasyprint_available:
            return
            
        try:
            from jinja2 import Environment, FileSystemLoader
            from weasyprint.text.fonts import FontConfiguration
            
            # Initialize Jinja2 environment for WeasyPrint
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=True
            )
            
            # Font configuration for WeasyPrint with Russian support
            self.font_config = FontConfiguration()
            self._setup_fonts()
        except Exception as e:
            logger.error(f"WeasyPrint setup failed: {e}")
            self.weasyprint_available = False
    
    def _setup_fonts(self):
        """Setup fonts for Russian text support"""
        if not self.weasyprint_available:
            return
            
        try:
            # Try to find system fonts that support Cyrillic
            import font_roboto
            logger.info("Roboto font available for Russian text")
        except ImportError:
            logger.warning("Roboto font not available, using system defaults")
        
    async def generate_partner_report(
        self,
        analysis_data: Dict[str, Any],
        user_id: int,
        partner_name: str = "партнер"
    ) -> bytes:
        """
        Generate comprehensive PDF report for partner analysis
        
        Args:
            analysis_data: Analysis results from AI service
            user_id: User ID for file naming
            partner_name: Partner's name
            
        Returns:
            PDF bytes
        """
        try:
            logger.info(f"Starting PDF generation for user {user_id}, partner: {partner_name}")
            
            # Use ReportLab if WeasyPrint not available
            if not self.weasyprint_available:
                logger.info("Using ReportLab PDF service")
                return await self.reportlab_service.generate_partner_report(
                    analysis_data, user_id, partner_name
                )
            
            # Try WeasyPrint implementation first
            try:
                # Generate charts
                charts = await self._generate_charts(analysis_data, user_id)
                
                # Prepare template data
                template_data = self._prepare_template_data(analysis_data, charts, partner_name)
                
                # Render HTML template
                html_content = self._render_html_template(template_data)
                
                # Generate PDF
                pdf_bytes = self._html_to_pdf(html_content)
                
                # Cleanup temporary files
                self._cleanup_temp_files(user_id)
                
                logger.info(f"WeasyPrint PDF generated successfully for user {user_id}, size: {len(pdf_bytes)} bytes")
                return pdf_bytes
                
            except Exception as weasy_error:
                logger.warning(f"WeasyPrint generation failed: {weasy_error}")
                logger.info("Falling back to ReportLab")
                
                # Fallback to ReportLab
                return await self.reportlab_service.generate_partner_report(
                    analysis_data, user_id, partner_name
                )
            
        except Exception as e:
            logger.error(f"PDF generation failed for user {user_id}: {e}")
            self._cleanup_temp_files(user_id)
            raise ServiceError(f"Failed to generate PDF report: {str(e)}")

    async def _generate_charts(self, analysis_data: Dict[str, Any], user_id: int) -> Dict[str, str]:
        """Generate charts and return base64 encoded images"""
        charts = {}
        
        try:
            # Risk circle chart
            charts['risk_circle'] = self._create_risk_circle_chart(
                analysis_data.get('overall_risk_score', 0), user_id
            )
            
            # Block scores bar chart
            charts['blocks_chart'] = self._create_blocks_bar_chart(
                analysis_data.get('block_scores', {}), user_id
            )
            
            # Dark Triad radar chart
            charts['dark_triad_chart'] = self._create_dark_triad_chart(
                analysis_data, user_id
            )
            
            return charts
            
        except Exception as e:
            logger.error(f"Chart generation failed: {e}")
            return {}
    
    def _create_risk_circle_chart(self, risk_score: float, user_id: int) -> str:
        """Create risk score circle chart"""
        fig, ax = plt.subplots(figsize=(4, 4), facecolor='white')
        
        # Calculate angle for risk percentage
        angle = (risk_score / 100) * 360
        
        # Create circle chart
        circle_bg = patches.Circle((0.5, 0.5), 0.4, facecolor='#e9ecef', edgecolor='none')
        ax.add_patch(circle_bg)
        
        # Risk arc
        if risk_score > 0:
            risk_color = self._get_risk_color(risk_score)
            wedge = Wedge(
                (0.5, 0.5), 0.4, -90, -90 + angle,
                facecolor=risk_color, edgecolor='none'
            )
            ax.add_patch(wedge)
        
        # Inner white circle
        inner_circle = patches.Circle((0.5, 0.5), 0.25, facecolor='white', edgecolor='none')
        ax.add_patch(inner_circle)
        
        # Risk score text
        ax.text(0.5, 0.5, f'{int(risk_score)}', 
                ha='center', va='center', fontsize=24, fontweight='bold',
                color=self._get_risk_color(risk_score))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Save to base64
        return self._save_chart_to_base64(fig, f'risk_circle_{user_id}')
    
    def _create_blocks_bar_chart(self, block_scores: Dict[str, float], user_id: int) -> str:
        """Create block scores bar chart"""
        if not block_scores:
            return ""
            
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
        
        # Block names in Russian
        block_names = {
            'narcissism': 'Нарциссизм',
            'control': 'Контроль',
            'gaslighting': 'Газлайтинг',
            'emotion': 'Эмоции',
            'intimacy': 'Интимность',
            'social': 'Социальное'
        }
        
        # Prepare data
        blocks = []
        scores = []
        colors = []
        
        for block_key, score in block_scores.items():
            if block_key in block_names:
                blocks.append(block_names[block_key])
                scores.append(score)
                colors.append(self._get_score_color(score))
        
        if not blocks:
            return ""
        
        # Create bar chart
        bars = ax.bar(blocks, scores, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
        
        # Add score labels on bars
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{score:.1f}', ha='center', va='bottom', fontweight='bold', color='white')
        
        ax.set_ylim(0, 10)
        ax.set_ylabel('Оценка (0-10)', fontsize=12, fontweight='bold')
        ax.set_title('Оценка по ключевым параметрам', fontsize=14, fontweight='bold', pad=20)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        
        # Grid
        ax.grid(True, alpha=0.3, axis='y')
        
        # Tight layout
        plt.tight_layout()
        
        # Save to base64
        return self._save_chart_to_base64(fig, f'blocks_chart_{user_id}')
    
    def _create_dark_triad_chart(self, analysis_data: Dict[str, Any], user_id: int) -> str:
        """Create Dark Triad radar chart"""
        dark_triad = analysis_data.get('dark_triad', {})
        if not dark_triad:
            return ""
            
        fig, ax = plt.subplots(figsize=(6, 6), facecolor='white', subplot_kw=dict(projection='polar'))
        
        # Dark Triad components
        categories = ['Нарциссизм', 'Психопатия', 'Макиавеллизм']
        values = [
            dark_triad.get('narcissism', 0),
            dark_triad.get('psychopathy', 0),
            dark_triad.get('machiavellianism', 0)
        ]
        
        # Add first point at the end to close the polygon
        values.append(values[0])
        
        # Angles for each category
        angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
        angles.append(angles[0])
        
        # Plot
        ax.plot(angles, values, 'o-', linewidth=2, color='#dc3545')
        ax.fill(angles, values, alpha=0.25, color='#dc3545')
        
        # Add category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        
        # Set y-axis limits
        ax.set_ylim(0, 10)
        
        # Add grid
        ax.grid(True)
        
        # Title
        ax.set_title('Темная триада личности', size=14, fontweight='bold', pad=20)
        
        # Save to base64
        return self._save_chart_to_base64(fig, f'dark_triad_{user_id}')
    
    def _prepare_template_data(
        self, 
        analysis_data: Dict[str, Any], 
        charts: Dict[str, str],
        partner_name: str
    ) -> Dict[str, Any]:
        """Prepare data for template rendering"""
        
        # Get risk score and level
        risk_score = analysis_data.get('overall_risk_score', 0)
        urgency_level = analysis_data.get('urgency_level', 'UNKNOWN')
        
        # Get block scores
        block_scores = analysis_data.get('block_scores', {})
        
        # Block names mapping
        block_names = {
            'narcissism': 'Нарциссизм',
            'control': 'Контроль',
            'gaslighting': 'Газлайтинг',
            'emotion': 'Эмоциональное воздействие',
            'intimacy': 'Интимность',
            'social': 'Социальное влияние'
        }
        
        # Prepare block data for template
        blocks_data = []
        for block_key, score in block_scores.items():
            if block_key in block_names:
                blocks_data.append({
                    'name': block_names[block_key],
                    'score': score,
                    'level': self._get_score_level(score),
                    'width_percent': int((score / 10) * 100)
                })
        
        # Current date
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        template_data = {
            'partner_name': partner_name,
            'risk_score': int(risk_score),
            'urgency_level': urgency_level,
            'risk_level': self._get_risk_level(risk_score),
            'risk_color': self._get_risk_color(risk_score),
            'psychological_profile': analysis_data.get('psychological_profile', ''),
            'survival_guide': analysis_data.get('survival_guide', []),
            'red_flags': analysis_data.get('red_flags', []),
            'blocks': blocks_data,
            'charts': charts,
            'date': current_date,
            'report_id': f"RPT-{current_date.replace('.', '')}-{analysis_data.get('user_id', 'XXX')}"
        }
        
        return template_data
    
    def _render_html_template(self, template_data: Dict[str, Any]) -> str:
        """Render HTML template with data"""
        if not self.weasyprint_available:
            return ""
            
        try:
            template = self.jinja_env.get_template('partner_report.html')
            return template.render(**template_data)
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return self._create_simple_html_report(template_data)
    
    def _html_to_pdf(self, html_content: str) -> bytes:
        """Convert HTML to PDF"""
        if not self.weasyprint_available:
            raise ServiceError("WeasyPrint not available for HTML to PDF conversion")
            
        try:
            from weasyprint import HTML, CSS
            
            # Create CSS for styling
            css_content = self._get_pdf_css()
            css = CSS(string=css_content, font_config=self.font_config)
            
            # Generate PDF
            html_doc = HTML(string=html_content)
            pdf_bytes = html_doc.write_pdf(
                stylesheets=[css],
                font_config=self.font_config
            )
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"HTML to PDF conversion failed: {e}")
            raise ServiceError(f"PDF conversion failed: {str(e)}")
    
    def _save_chart_to_base64(self, fig, filename: str) -> str:
        """Save matplotlib figure to base64 string"""
        try:
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            buffer.seek(0)
            
            # Convert to base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            plt.close(fig)
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Chart to base64 conversion failed: {e}")
            plt.close(fig)
            return ""
    
    def _cleanup_temp_files(self, user_id: int):
        """Clean up temporary chart files"""
        try:
            for file_path in self.charts_dir.glob(f"*_{user_id}.*"):
                file_path.unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")
    
    def _get_risk_color(self, risk_score: float) -> str:
        """Get color based on risk score"""
        if risk_score < 25:
            return '#28a745'  # Green
        elif risk_score < 50:
            return '#ffc107'  # Yellow
        elif risk_score < 75:
            return '#fd7e14'  # Orange
        else:
            return '#dc3545'  # Red
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score"""
        if score < 3:
            return '#28a745'  # Green
        elif score < 6:
            return '#ffc107'  # Yellow
        elif score < 8:
            return '#fd7e14'  # Orange
        else:
            return '#dc3545'  # Red
    
    def _get_score_level(self, score: float) -> str:
        """Get level text based on score"""
        if score < 3:
            return 'Низкий'
        elif score < 6:
            return 'Средний'
        elif score < 8:
            return 'Высокий'
        else:
            return 'Критический'
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level text"""
        if risk_score < 25:
            return 'НИЗКИЙ'
        elif risk_score < 50:
            return 'УМЕРЕННЫЙ'
        elif risk_score < 75:
            return 'ВЫСОКИЙ'
        else:
            return 'КРИТИЧЕСКИЙ'
    
    def _get_pdf_css(self) -> str:
        """Get CSS styles for PDF"""
        return """
        @page {
            size: A4;
            margin: 20mm;
        }
        
        body {
            font-family: 'Roboto', 'DejaVu Sans', 'Arial Unicode MS', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 12px;
        }
        
        .cover-page {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 80px 20px;
            page-break-after: always;
        }
        
        .cover-title {
            font-size: 32px;
            font-weight: 300;
            margin-bottom: 20px;
        }
        
        .risk-score {
            font-size: 48px;
            font-weight: bold;
            margin: 20px 0;
        }
        
        .section {
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #667eea;
        }
        
        .red-flag {
            background: #fff5f5;
            border-left: 4px solid #dc3545;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        
        .chart-container {
            text-align: center;
            margin: 20px 0;
        }
        
        .chart-container img {
            max-width: 100%;
            height: auto;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }
        """
    
    def _create_simple_html_report(self, data: Dict[str, Any]) -> str:
        """Create simple HTML report as fallback"""
        partner_name = data.get('partner_name', 'партнер')
        risk_score = data.get('risk_score', 0)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Психологический профиль партнера</title>
        </head>
        <body>
            <div class="cover-page">
                <h1 class="cover-title">ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ ПАРТНЕРА</h1>
                <h2>"{partner_name}"</h2>
                <div class="risk-score">{risk_score}%</div>
                <p>Дата создания: {data.get('date', 'Неизвестно')}</p>
            </div>
            
            <div class="page-break">
                <h2>Результаты анализа</h2>
                <p>Общий уровень риска: {risk_score}%</p>
                
                <h3>Психологический профиль:</h3>
                <p>{data.get('psychological_profile', 'Данные недоступны')}</p>
                
                <h3>Рекомендации:</h3>
                <p>{data.get('survival_guide', 'Данные недоступны')}</p>
            </div>
        </body>
        </html>
        """ 