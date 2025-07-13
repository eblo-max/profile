"""HTML to PDF conversion service using CloudLayer.io API"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
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
        logger.info("🎨 Initializing HTMLPDFService")
        self._cloudlayer_available = None
        self.template = None
        self.api_key = settings.CLOUDLAYER_API_KEY
        self.api_url = "https://api.cloudlayer.io"
        if not self.api_key:
            logger.warning("⚠️ CloudLayer.io API key not configured! Set CLOUDLAYER_API_KEY environment variable.")
    
    def reset_cloudlayer_check(self):
        """Reset CloudLayer availability check (for testing)"""
        pass
    
    def _decline_name(self, name: str, case: str = "nominative") -> str:
        """
        Склоняет имя по падежам
        
        Args:
            name: имя для склонения
            case: падеж (nominative, genitive, dative, accusative, instrumental, prepositional)
        
        Returns:
            склоненное имя
        """
        if not name or not isinstance(name, str):
            return name or "партнер"
        
        name = name.strip()
        if not name:
            return "партнер"
        
        # Словарь популярных женских имен
        female_names = {
            "анна": {
                "nominative": "Анна", "genitive": "Анны", "dative": "Анне",
                "accusative": "Анну", "instrumental": "Анной", "prepositional": "Анне"
            },
            "мария": {
                "nominative": "Мария", "genitive": "Марии", "dative": "Марии", 
                "accusative": "Марию", "instrumental": "Марией", "prepositional": "Марии"
            },
            "елена": {
                "nominative": "Елена", "genitive": "Елены", "dative": "Елене",
                "accusative": "Елену", "instrumental": "Еленой", "prepositional": "Елене"
            },
            "татьяна": {
                "nominative": "Татьяна", "genitive": "Татьяны", "dative": "Татьяне",
                "accusative": "Татьяну", "instrumental": "Татьяной", "prepositional": "Татьяне"
            },
            "ольга": {
                "nominative": "Ольга", "genitive": "Ольги", "dative": "Ольге",
                "accusative": "Ольгу", "instrumental": "Ольгой", "prepositional": "Ольге"
            },
            "наталья": {
                "nominative": "Наталья", "genitive": "Натальи", "dative": "Наталье",
                "accusative": "Наталью", "instrumental": "Натальей", "prepositional": "Наталье"
            },
            "ирина": {
                "nominative": "Ирина", "genitive": "Ирины", "dative": "Ирине",
                "accusative": "Ирину", "instrumental": "Ириной", "prepositional": "Ирине"
            },
            "светлана": {
                "nominative": "Светлана", "genitive": "Светланы", "dative": "Светлане",
                "accusative": "Светлану", "instrumental": "Светланой", "prepositional": "Светлане"
            },
            "юлия": {
                "nominative": "Юлия", "genitive": "Юлии", "dative": "Юлии",
                "accusative": "Юлию", "instrumental": "Юлией", "prepositional": "Юлии"
            },
            "екатерина": {
                "nominative": "Екатерина", "genitive": "Екатерины", "dative": "Екатерине",
                "accusative": "Екатерину", "instrumental": "Екатериной", "prepositional": "Екатерине"
            }
        }
        
        # Словарь популярных мужских имен
        male_names = {
            "александр": {
                "nominative": "Александр", "genitive": "Александра", "dative": "Александру",
                "accusative": "Александра", "instrumental": "Александром", "prepositional": "Александре"
            },
            "алексей": {
                "nominative": "Алексей", "genitive": "Алексея", "dative": "Алексею",
                "accusative": "Алексея", "instrumental": "Алексеем", "prepositional": "Алексее"
            },
            "андрей": {
                "nominative": "Андрей", "genitive": "Андрея", "dative": "Андрею",
                "accusative": "Андрея", "instrumental": "Андреем", "prepositional": "Андрее"
            },
            "дмитрий": {
                "nominative": "Дмитрий", "genitive": "Дмитрия", "dative": "Дмитрию",
                "accusative": "Дмитрия", "instrumental": "Дмитрием", "prepositional": "Дмитрии"
            },
            "сергей": {
                "nominative": "Сергей", "genitive": "Сергея", "dative": "Сергею",
                "accusative": "Сергея", "instrumental": "Сергеем", "prepositional": "Сергее"
            },
            "владимир": {
                "nominative": "Владимир", "genitive": "Владимира", "dative": "Владимиру",
                "accusative": "Владимира", "instrumental": "Владимиром", "prepositional": "Владимире"
            },
            "михаил": {
                "nominative": "Михаил", "genitive": "Михаила", "dative": "Михаилу",
                "accusative": "Михаила", "instrumental": "Михаилом", "prepositional": "Михаиле"
            },
            "николай": {
                "nominative": "Николай", "genitive": "Николая", "dative": "Николаю",
                "accusative": "Николая", "instrumental": "Николаем", "prepositional": "Николае"
            },
            "игорь": {
                "nominative": "Игорь", "genitive": "Игоря", "dative": "Игорю",
                "accusative": "Игоря", "instrumental": "Игорем", "prepositional": "Игоре"
            },
            "евгений": {
                "nominative": "Евгений", "genitive": "Евгения", "dative": "Евгению",
                "accusative": "Евгения", "instrumental": "Евгением", "prepositional": "Евгении"
            }
        }
        
        name_lower = name.lower()
        
        # Проверяем точное совпадение с известными именами
        if name_lower in female_names:
            return female_names[name_lower].get(case, name)
        elif name_lower in male_names:
            return male_names[name_lower].get(case, name)
        
        # Эвристические правила для неизвестных имен
        return self._decline_name_heuristic(name, case)
    
    def _decline_name_heuristic(self, name: str, case: str) -> str:
        """Склонение имен по эвристическим правилам"""
        if case == "nominative":
            return name
        
        name_lower = name.lower()
        
        # Женские имена на -а/-я
        if name_lower.endswith(('а', 'я')):
            if case == "genitive":
                if name_lower.endswith('я'):
                    return name[:-1] + 'и'
                else:
                    return name[:-1] + 'ы'
            elif case == "dative":
                return name[:-1] + 'е'
            elif case == "accusative":
                if name_lower.endswith('я'):
                    return name[:-1] + 'ю'
                else:
                    return name[:-1] + 'у'
            elif case == "instrumental":
                if name_lower.endswith('я'):
                    return name[:-1] + 'ей'
                else:
                    return name[:-1] + 'ой'
            elif case == "prepositional":
                return name[:-1] + 'е'
        
        # Мужские имена на согласную
        elif not name_lower.endswith(('а', 'я', 'ь')):
            if case in ["genitive", "accusative"]:
                return name + 'а'
            elif case == "dative":
                return name + 'у'
            elif case == "instrumental":
                return name + 'ом'
            elif case == "prepositional":
                return name + 'е'
        
        # Имена на -ь (могут быть мужскими или женскими)
        elif name_lower.endswith('ь'):
            if case == "genitive":
                return name[:-1] + 'я'
            elif case == "dative":
                return name[:-1] + 'ю'
            elif case == "accusative":
                return name[:-1] + 'я'
            elif case == "instrumental":
                return name[:-1] + 'ем'
            elif case == "prepositional":
                return name[:-1] + 'е'
        
        # Если не удалось определить, возвращаем исходное имя
        return name
    
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
            analysis_data: Analysis results from psychological assessment
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
        
        # EXPAND psychological profile for detailed analysis
        expanded_profile = self._expand_psychological_profile(
            psychological_profile, 
            partner_name, 
            overall_risk, 
            analysis_data
        )
        
        # Generate assessment details
        risk_level, risk_color, risk_badge_color = self._determine_risk_level(overall_risk)
        
        # Current date
        current_date = datetime.now().strftime("%d.%m.%Y")
        report_id = f"RPT-{datetime.now().strftime('%d%m%Y')}-{user_id:03d}"
        
        # Generate personality type based on risk
        personality_type = self._determine_personality_type(overall_risk)
        
        # Extract Dark Triad scores from analysis data
        dark_triad_scores = self._extract_dark_triad_scores(analysis_data, overall_risk)
        
        # Generate personalized insights based on analysis
        personalized_insights = self._generate_personalized_insights(analysis_data, partner_name, overall_risk)
        
        # Prepare template data
        # Generate enhanced data for blocks
        personality_traits = self._get_personality_traits(personality_type, overall_risk)
        personality_description = self._get_personality_description(personality_type, overall_risk)
        risk_detailed_description = self._get_risk_detailed_description(overall_risk)
        risk_recommendations = self._get_risk_recommendations(overall_risk)
        
        template_data = {
            'partner_name': partner_name,
            'partner_name_genitive': self._decline_name(partner_name, "genitive"),      # кого? чего? - анализ Анны
            'partner_name_dative': self._decline_name(partner_name, "dative"),          # кому? чему? - советы Анне
            'partner_name_accusative': self._decline_name(partner_name, "accusative"),  # кого? что? - анализирую Анну
            'partner_name_instrumental': self._decline_name(partner_name, "instrumental"), # кем? чем? - работа с Анной
            'partner_name_prepositional': self._decline_name(partner_name, "prepositional"), # о ком? о чем? - о Анне
            'date': current_date,
            'report_id': report_id,
            'risk_score': int(overall_risk),
            'risk_level': self._get_risk_level(overall_risk),
            'urgency': 'CRITICAL' if overall_risk > 70 else 'HIGH' if overall_risk > 40 else 'MEDIUM' if overall_risk > 20 else 'LOW',
            'personality_type': personality_type,
            'personality_description': personality_description,
            'personality_traits': personality_traits,
            'risk_detailed_description': risk_detailed_description,
            'risk_recommendations': risk_recommendations,
            'psychological_profile': expanded_profile,  # Using expanded version
            'red_flags': red_flags[:6] if len(red_flags) > 6 else red_flags,  # Limit to 6 for display
            'recommendations': '\n'.join(recommendations) if isinstance(recommendations, list) else str(recommendations),
            'population_percentile': min(95, int(overall_risk * 1.2)),  # Conservative estimate
            'total_questions': 28,
            'blocks': self._generate_blocks_data(analysis_data, overall_risk),
            
            # Dynamic Dark Triad scores
            'narcissism_score': dark_triad_scores['narcissism'],
            'machiavellianism_score': dark_triad_scores['machiavellianism'], 
            'psychopathy_score': dark_triad_scores['psychopathy'],
            
            # Personalized insights instead of static content
            'warning_signs': personalized_insights['warning_signs'],
            'behavioral_patterns': personalized_insights['behavioral_patterns'],
            'development_prognosis': personalized_insights['development_prognosis'],
            'protective_mechanisms': personalized_insights['protective_mechanisms'],
            'help_resources': personalized_insights['help_resources'],
            
            # AI analysis
            'ai_analysis': analysis_data.get('psychological_profile', ''),
            
            # Additional data for new sections
            'manipulation_tactics': analysis_data.get('manipulation_tactics', []),
            'escalation_triggers': analysis_data.get('escalation_triggers', []),
            'emotional_patterns': analysis_data.get('emotional_patterns', []),
            'violence_indicators': analysis_data.get('violence_indicators', []),
            'control_mechanisms': analysis_data.get('control_mechanisms', []),
            'behavioral_evidence': analysis_data.get('behavioral_evidence', []),
            'personalized_insights': analysis_data.get('personalized_insights', [])
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
            raise Exception(f"HTML генерация не удалась: {str(e)}")

    def _extract_dark_triad_scores(self, analysis_data: Dict[str, Any], overall_risk: float) -> Dict[str, int]:
        """Extract Dark Triad scores from analysis data or calculate based on risk and block scores"""
        
        # Try to get from block_scores if available
        block_scores = analysis_data.get('block_scores', {})
        
        # Calculate Dark Triad based on psychological research and user responses
        narcissism_base = block_scores.get('narcissism', overall_risk / 10)
        control_score = block_scores.get('control', overall_risk / 10)
        emotion_score = block_scores.get('emotion', overall_risk / 10)
        social_score = block_scores.get('social', overall_risk / 10)
        
        # Narcissism: Based on grandiosity, need for admiration, lack of empathy
        narcissism = min(10, max(1, int(narcissism_base + (control_score * 0.3) + (social_score * 0.2))))
        
        # Machiavellianism: Based on manipulation, cunning, strategic thinking
        gaslighting_score = block_scores.get('gaslighting', overall_risk / 10)
        machiavellianism = min(10, max(1, int(control_score + (gaslighting_score * 0.4) + (social_score * 0.3))))
        
        # Psychopathy: Based on callousness, impulsivity, antisocial behavior
        intimacy_score = block_scores.get('intimacy', overall_risk / 10)
        psychopathy = min(10, max(1, int(emotion_score + (intimacy_score * 0.4) + (gaslighting_score * 0.3))))
        
        return {
            'narcissism': narcissism,
            'machiavellianism': machiavellianism,
            'psychopathy': psychopathy
        }

    def _generate_personalized_insights(self, analysis_data: Dict[str, Any], partner_name: str, overall_risk: float) -> Dict[str, List[str]]:
        """Generate personalized insights based on analysis data instead of static content"""
        
        block_scores = analysis_data.get('block_scores', {})
        red_flags = analysis_data.get('red_flags', [])
        key_concerns = analysis_data.get('key_concerns', [])
        
        # Generate personalized warning signs based on highest scoring blocks
        warning_signs = []
        if block_scores.get('control', 0) > 6:
            warning_signs.extend([
                "Контроль над финансами и временем партнера",
                "Ограничение социальных контактов и изоляция",
                "Принятие решений без учета мнения партнера"
            ])
        
        if block_scores.get('emotion', 0) > 6:
            warning_signs.extend([
                "Эмоциональные качели и непредсказуемость",
                "Агрессивные реакции на критику или несогласие",
                "Использование эмоций для манипулирования"
            ])
            
        if block_scores.get('gaslighting', 0) > 6:
            warning_signs.extend([
                "Газлайтинг и искажение реальности",
                "Отрицание собственных слов и действий",
                "Перекладывание вины на партнера"
            ])
            
        if block_scores.get('narcissism', 0) > 6:
            warning_signs.extend([
                "Постоянная потребность в восхищении",
                "Обесценивание достижений партнера",
                "Неспособность к эмпатии и сочувствию"
            ])
            
        # If no specific patterns, use general warning signs
        if not warning_signs:
            warning_signs = [
                "Нарушение личных границ",
                "Двойные стандарты в поведении", 
                "Отказ брать ответственность за свои действия"
            ]
        
        # Generate behavioral patterns based on analysis
        behavioral_patterns = []
        if block_scores.get('social', 0) > 6:
            behavioral_patterns.append("Различное поведение наедине и в обществе")
        if block_scores.get('intimacy', 0) > 6:
            behavioral_patterns.append("Нарушение интимных границ и принуждение")
        if overall_risk > 70:
            behavioral_patterns.append("Эскалация агрессивного поведения при сопротивлении")
        if block_scores.get('control', 0) > 7:
            behavioral_patterns.append("Систематическое подрывание самооценки партнера")
            
        # Development prognosis based on risk level
        if overall_risk > 80:
            prognosis = "Критический прогноз: без профессионального вмешательства поведение будет усиливаться и может привести к серьезным последствиям"
        elif overall_risk > 60:
            prognosis = "Неблагоприятный прогноз: паттерны поведения будут усиливаться без изменений в динамике отношений"
        elif overall_risk > 40:
            prognosis = "Осторожный прогноз: возможны улучшения при работе с квалифицированным специалистом"
        else:
            prognosis = "Относительно благоприятный прогноз при соблюдении здоровых границ в отношениях"
            
        # Protective mechanisms based on specific risks
        protective_mechanisms = [
            "Документирование инцидентов и ведение дневника событий",
            "Поддержание связей с поддерживающим окружением"
        ]
        
        if block_scores.get('gaslighting', 0) > 6:
            protective_mechanisms.append("Развитие навыков распознавания газлайтинга")
        if block_scores.get('control', 0) > 6:
            protective_mechanisms.append("Создание финансовой независимости и автономии")
        if overall_risk > 70:
            protective_mechanisms.append("Разработка плана безопасности на случай эскалации")
            
        # Help resources based on risk level
        if overall_risk > 80:
            help_resources = [
                "Немедленное обращение в кризисные центры поддержки",
                "Консультация с психологом, специализирующимся на абьюзивных отношениях",
                "Обращение к юристу для защиты прав"
            ]
        elif overall_risk > 60:
            help_resources = [
                "Консультация семейного психолога",
                "Групповая терапия для жертв эмоционального насилия",
                "Телефоны доверия и онлайн-поддержка"
            ]
        else:
            help_resources = [
                "Семейное консультирование для работы с парой",
                "Индивидуальная терапия для укрепления границ",
                "Образовательные ресурсы по здоровым отношениям"
            ]
        
        return {
            'warning_signs': warning_signs[:8],  # Limit to 8 items
            'behavioral_patterns': behavioral_patterns,
            'development_prognosis': prognosis,
            'protective_mechanisms': protective_mechanisms,
            'help_resources': help_resources
        }

    def _generate_blocks_data(self, analysis_data: Dict[str, Any], overall_risk: float) -> list:
        """Generate blocks data for template using real block_scores if available"""
        
        # Try to use real block_scores from analysis
        block_scores = analysis_data.get('block_scores', {})
        
        # If we have real block_scores, use them
        if block_scores:
            blocks = []
            
            # Map block names with emojis and calculate scores
            block_mapping = {
                'narcissism': {'name': 'Нарциссизм', 'emoji': '👑'},
                'control': {'name': 'Контроль', 'emoji': '🎛️'},
                'gaslighting': {'name': 'Газлайтинг', 'emoji': '🌪️'},
                'emotion': {'name': 'Эмоции', 'emoji': '💥'},
                'intimacy': {'name': 'Интимность', 'emoji': '💔'},
                'social': {'name': 'Социальность', 'emoji': '🎭'}
            }
            
            for block_key, block_info in block_mapping.items():
                score = int(block_scores.get(block_key, overall_risk / 10))
                blocks.append({
                    'name': block_info['name'],
                    'emoji': block_info['emoji'],
                    'score': min(10, max(0, score)),
                    'level': self._get_level_description(score)
                })
            
            return blocks
        else:
            # Fallback to calculated scores based on overall risk
            emotion_score = min(10, int(overall_risk / 10))
            manipulation_score = min(10, int((overall_risk + 10) / 12))
            empathy_score = max(1, 10 - int(overall_risk / 10))
            aggression_score = min(10, int(overall_risk / 8))
            control_score = min(10, int(overall_risk / 9))
            narcissism_score = min(10, int(overall_risk / 11))

            blocks = [
                {
                    'name': 'Эмоциональный контроль',
                    'emoji': '💥',
                    'score': emotion_score,
                    'level': self._get_level_description(emotion_score)
                },
                {
                    'name': 'Манипулятивность', 
                    'emoji': '🎭',
                    'score': manipulation_score,
                    'level': self._get_level_description(manipulation_score)
                },
                {
                    'name': 'Эмпатия',
                    'emoji': '💝',
                    'score': empathy_score,
                    'level': self._get_level_description(empathy_score)
                },
                {
                    'name': 'Агрессивность',
                    'emoji': '⚡',
                    'score': aggression_score,
                    'level': self._get_level_description(aggression_score)
                },
                {
                    'name': 'Контроль',
                    'emoji': '🎛️',
                    'score': control_score,
                    'level': self._get_level_description(control_score)
                },
                {
                    'name': 'Нарциссизм',
                    'emoji': '👑',
                    'score': narcissism_score,
                    'level': self._get_level_description(narcissism_score)
                }
            ]
            return blocks
    

    
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
        elif risk_score >= 25:
            return "Эмоционально зрелая личность"
        elif risk_score >= 15:
            return "Гармоничная личность с развитой эмпатией"
        else:
            return "Эмоционально здоровая и поддерживающая личность"
    
    def _get_personality_description(self, personality_type: str) -> str:
        """Get description for personality type"""
        descriptions = {
            "Критический токсичный нарцисс": "Крайне опасная комбинация нарциссических черт с садистскими наклонностями и полным отсутствием эмпатии",
            "Контролирующий нарцисс": "Выраженные нарциссические черты с потребностью в доминировании и контроле над партнером",
            "Манипулятивная личность": "Склонность к систематическим манипуляциям и эмоциональному воздействию",
            "Эмоционально нестабильный": "Непредсказимые эмоциональные реакции с элементами контролирующего поведения",
            "Эмоционально зрелая личность": "Развитые навыки эмоциональной регуляции с основами здорового общения",
            "Гармоничная личность с развитой эмпатией": "Высокий эмоциональный интеллект, способность к эмпатии и поддержке партнера",
            "Эмоционально здоровая и поддерживающая личность": "Выдающиеся качества партнера: эмоциональная зрелость, уважение к границам и безусловная поддержка"
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
        elif risk_score >= 25:
            traits = [
                "🟡 Некоторые коммуникационные сложности",
                "🟢 В целом здоровое поведение",
                "🟢 Способность к самоанализу",
                "🟢 Эмоциональная стабильность"
            ]
        elif risk_score >= 15:
            traits = [
                "🟢 Высокая эмпатия и понимание",
                "🟢 Уважение к личным границам",
                "🟢 Поддержка и забота",
                "🟢 Здоровая коммуникация"
            ]
        else:
            traits = [
                "🟢 Выдающиеся навыки эмоциональной поддержки",
                "🟢 Безусловное уважение к партнеру",
                "🟢 Открытость и честность",
                "🟢 Способность к здоровой близости"
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
            elif risk_score >= 25:
                red_flags = [
                    ("Коммуникационные моменты", "Иногда возникают небольшие сложности в общении, которые успешно решаются"),
                    ("Эмоциональная отзывчивость", "Здоровые эмоциональные реакции на важные ситуации")
                ]
            elif risk_score >= 15:
                red_flags = [
                    ("Открытая коммуникация", "Партнер всегда готов к честному и открытому диалогу"),
                    ("Эмоциональная поддержка", "Проявляет искреннюю заботу и понимание ваших потребностей"),
                    ("Уважение границ", "Всегда спрашивает разрешения и уважает ваше личное пространство")
                ]
            else:
                red_flags = [
                    ("Исключительная эмпатия", "Демонстрирует глубокое понимание и сочувствие к вашим переживаниям"),
                    ("Безусловная поддержка", "Поддерживает ваши цели, мечты и личностный рост"),
                    ("Здоровые отношения", "Создает атмосферу доверия, уважения и взаимной заботы"),
                    ("Эмоциональная зрелость", "Способен к конструктивному решению конфликтов и самоанализу")
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
        elif risk_score >= 25:
            urgency = "развивающих"
            short_term = [
                "Продолжать развивать навыки здорового общения",
                "Поддерживать открытый диалог с партнером",
                "Изучать литературу по укреплению отношений"
            ]
        elif risk_score >= 15:
            urgency = "поддерживающих"
            short_term = [
                "Поддерживать существующие здоровые паттерны",
                "Практиковать благодарность за качества партнера",
                "Развивать совместные интересы и активности",
                "Продолжать открытое и честное общение"
            ]
        else:
            urgency = "укрепляющих"
            short_term = [
                "Наслаждаться здоровыми отношениями",
                "Быть примером для других пар",
                "Делиться опытом здоровой коммуникации",
                "Продолжать взаимную поддержку и рост"
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
            
    def _expand_psychological_profile(
        self, 
        original_profile: str, 
        partner_name: str, 
        risk_score: float, 
        analysis_data: Dict[str, Any]
    ) -> str:
        """Expand psychological profile to detailed multi-page analysis"""
        
        # Extract additional data
        block_scores = analysis_data.get('block_scores', {})
        red_flags = analysis_data.get('red_flags', [])
        personality_type = self._determine_personality_type(risk_score)
        dark_triad = analysis_data.get('dark_triad', {})
        
        # ПРИОРИТЕТ: Использовать реальный ИИ-анализ!
        if original_profile and len(original_profile.strip()) > 100:
            # Форматируем реальный ИИ-анализ в HTML
            expanded = self._format_ai_analysis_to_html(
                original_profile, 
                partner_name, 
                risk_score, 
                analysis_data
            )
        else:
            # Используем статичные шаблоны если AI-анализ отсутствует
            logger.warning(f"No AI analysis found, using static templates")
            if risk_score >= 70:
                expanded = self._generate_high_risk_analysis(partner_name, risk_score, block_scores, red_flags, dark_triad)
            elif risk_score >= 50:
                expanded = self._generate_medium_risk_analysis(partner_name, risk_score, block_scores, red_flags, dark_triad)
            else:
                expanded = self._generate_low_risk_analysis(partner_name, risk_score, block_scores, analysis_data)
        
        # Возвращаем объединенный профиль
        return f"""
        <div class="analysis-section">
            <div class="analysis-content">
                {expanded}
            </div>
        </div>
        """
    
    def _format_ai_analysis_to_html(
        self,
        ai_analysis: str,
        partner_name: str,
        risk_score: float,
        analysis_data: Dict[str, Any]
    ) -> str:
        """Форматирует реальный ИИ-анализ в красивый HTML"""
        
        # Убираем дублирующий заголовок в начале
        lines = ai_analysis.split('\n')
        filtered_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            
            # Пропускаем дублирующие заголовки
            if 'ПЕРСОНАЛИЗИРОВАННЫЙ ПСИХОЛОГИЧЕСКИЙ АНАЛИЗ' in line_clean:
                continue
            if line_clean == '':
                # Не добавляем лишние пустые строки подряд
                if filtered_lines and filtered_lines[-1] != '':
                    filtered_lines.append('')
                continue
                
            filtered_lines.append(line)
        
        # Объединяем обратно
        cleaned_analysis = '\n'.join(filtered_lines).strip()
        
        # Разбиваем на блоки по заголовкам
        sections = []
        current_section = {'title': '', 'content': []}
        
        paragraphs = cleaned_analysis.split('\n\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # Проверяем, является ли это заголовком блока
            is_section_title = (
                paragraph.isupper() and 
                len(paragraph) < 150 and
                any(keyword in paragraph.lower() for keyword in [
                    'портрет', 'характеристика', 'паттерн', 'контрол', 
                    'манипул', 'эмоциональн', 'интимность', 'социальн',
                    'прогноз', 'рекомендац'
                ])
            )
            
            if is_section_title:
                # Сохраняем предыдущую секцию
                if current_section['title'] or current_section['content']:
                    sections.append(current_section)
                
                # Начинаем новую секцию
                current_section = {'title': paragraph, 'content': []}
            else:
                # Добавляем содержимое в текущую секцию
                current_section['content'].append(paragraph)
        
        # Добавляем последнюю секцию
        if current_section['title'] or current_section['content']:
            sections.append(current_section)
        
        # Форматируем в HTML
        formatted_sections = []
        
        for section in sections:
            if section['title']:
                formatted_sections.append(f'<h4 class="analysis-section-title">{section["title"]}</h4>')
            
            for content in section['content']:
                if content.strip():
                    formatted_sections.append(f'<p class="analysis-text">{content}</p>')
        
        # Обертываем в структуру
        html_analysis = f"""
<div class="detailed-profile ai-generated">
    <div class="ai-analysis-content">
        {''.join(formatted_sections)}
    </div>
</div>"""
        
        return html_analysis
    
    def _generate_additional_insights(self, analysis_data: Dict[str, Any]) -> str:
        """Генерирует дополнительные инсайты из данных анализа"""
        
        insights = []
        
        # Добавляем экспертные мнения если есть
        if 'experts' in analysis_data:
            experts = analysis_data['experts']
            if isinstance(experts, dict):
                for expert_name, expert_opinion in experts.items():
                    insights.append(f'''
                    <div class="expert-insight">
                        <h4>{expert_name}</h4>
                        <p>{expert_opinion}</p>
                    </div>
                    ''')
        
        # Добавляем персонализированные инсайты
        if 'personalized_insights' in analysis_data:
            personalized = analysis_data['personalized_insights']
            if isinstance(personalized, list):
                for insight in personalized:
                    insights.append(f'<div class="personalized-insight"><p>{insight}</p></div>')
        
        # Добавляем поведенческие доказательства
        if 'behavioral_evidence' in analysis_data:
            evidence = analysis_data['behavioral_evidence']
            if isinstance(evidence, list):
                insights.append('<div class="behavioral-evidence"><h4>Поведенческие доказательства:</h4><ul>')
                for item in evidence:
                    insights.append(f'<li>{item}</li>')
                insights.append('</ul></div>')
        
        return ''.join(insights) if insights else '<p>Дополнительные инсайты не найдены</p>'
    
    def _generate_high_risk_analysis(
        self, 
        partner_name: str, 
        risk_score: float, 
        block_scores: Dict[str, float], 
        red_flags: list,
        dark_triad: Dict[str, float]
    ) -> str:
        """Generate detailed analysis for high-risk cases (70%+)"""
        
        analysis = f"""
<div class="detailed-profile">
    <div class="profile-section">
        <h3 class="section-title">Детальная психологическая характеристика</h3>
        <p>Анализ выявляет крайне опасный паттерн абьюзивного поведения с множественными признаками нарциссического расстройства личности и склонностью к манипуляциям. Набранный балл риска <strong>{risk_score}%</strong> указывает на критическую ситуацию, требующую немедленного вмешательства.</p>
        
        <p>В рамках модели "Темной триады" профиль показывает тревожные показатели: нарциссизм <strong>{dark_triad.get('narcissism', 0)}/10</strong>, макиавеллизм <strong>{dark_triad.get('machiavellianism', 0)}/10</strong>, психопатия <strong>{dark_triad.get('psychopathy', 0)}/10</strong>. Эта комбинация создает токсичную личность, неспособную к здоровым отношениям.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">Нарциссические проявления в отношениях</h3>
        <p><strong>{partner_name}</strong> демонстрирует классические признаки нарциссического расстройства личности. Его самооценка критически зависит от постоянного подтверждения собственной исключительности. Любой разговор он мастерски переводит на себя, обесценивая достижения и переживания партнера.</p>
        
        <p>Характерны фразы типа <em>"я не такой, как все"</em>, <em>"обычные люди меня не понимают"</em>, <em>"у меня особый взгляд на вещи"</em>. При этом он болезненно реагирует на любую критику, даже конструктивную, воспринимая ее как личное оскорбление.</p>
        
        <p>Особенно показательно его поведение при успехах партнера: вместо искренней радости он либо обесценивает достижение, либо сразу начинает рассказывать о своих более значительных успехах, переключая внимание на себя.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">🎯 Контролирующее поведение: эскалация власти</h3>
        <p>Контроль развивается постепенно, как затягивающаяся петля. Начиная с "заботы" - предложений встретить после работы, интереса к планам, советов по одежде - он постепенно переходит к требованиям детального отчета о каждом шаге.</p>
        
        <p>Блок "Контроль" показывает критический уровень <strong>{block_scores.get('control', 0)}/10</strong>. Это проявляется в:</p>
        <ul class="behavior-list">
            <li>Систематической проверке телефона и переписок</li>
            <li>Контроле финансов под видом "заботы о семье"</li>
            <li>Ограничении социальных контактов через эмоциональный шантаж</li>
            <li>Требованиях постоянной отчетности о местонахождении</li>
        </ul>
        
        <p>Финансовый контроль - особенно коварный инструмент. Начиная с благородных предложений "оплатить все расходы", он создает зависимость, при которой партнер не может купить даже кофе без разрешения.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">🔄 Мастерство газлайтинга и искажения реальности</h3>
        <p>Блок "Газлайтинг" достигает тревожного уровня <strong>{block_scores.get('gaslighting', 0)}/10</strong>. {partner_name} - мастер переписывания реальности. Он никогда не говорит прямо "ты лжешь", используя более тонкие формулировки: <em>"ты что-то путаешь"</em>, <em>"у тебя странная память"</em>, <em>"ты слишком эмоционально все воспринимаешь"</em>.</p>
        
        <p>После каждого конфликта у него своя версия произошедшего, где он - жертва, а партнер - агрессор. Особенно коварно он использует эмоции партнера против него: плач становится "истерикой", злость - "неуравновешенностью", спокойное объяснение - "холодностью".</p>
        
        <p><strong>Классический прием:</strong> перенос встреч с последующим утверждением, что "мы же договаривались на другое время", заставляя партнера сомневаться в собственной памяти.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">💭 Эмоциональная нестабильность и двойные стандарты</h3>
        <p>Несмотря на внешнюю маску контроля, эмоциональная регуляция {partner_name} крайне нарушена (блок "Эмоция": <strong>{block_scores.get('emotion', 0)}/10</strong>). Переход от спокойного тона к крику происходит мгновенно, если что-то идет не по его плану.</p>
        
        <p>Характерна диспропорциональность реакций: опоздание на 10 минут вызывает часовую лекцию, забытая покупка становится доказательством "неуважения к семье". При этом собственные ошибки он объясняет "важными обстоятельствами".</p>
        
        <p>После вспышек гнева извинений не следует. Вместо этого включается режим жертвы: <em>"До чего ты меня довела"</em>, <em>"Я не хотел кричать, но ты заставила"</em>. Ответственность всегда перекладывается на партнера.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">💕 Интимность как инструмент власти</h3>
        <p>Блок "Интимность" показывает <strong>{block_scores.get('intimacy', 0)}/10</strong>, что указывает на использование близости как средства контроля. {partner_name} рассматривает интимность не как взаимное удовольствие, а как подтверждение власти над партнером.</p>
        
        <p>Отказ воспринимается как личное оскорбление и становится поводом для эмоционального шантажа: <em>"Если ты меня любишь..."</em>, <em>"Все нормальные пары..."</em>, <em>"Я же не многого прошу"</em>.</p>
        
        <p>Интимность используется как награда и наказание: после ссор может неделями демонстративно отстраняться, а затем требовать близости как "доказательство прощения". При этом он единолично контролирует когда и как происходит близость.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">Социальная маска против истинного лица</h3>
        <p>Одна из самых травматичных черт - кардинальная разница между публичным образом и поведением наедине. В обществе он обаятельный, внимательный, галантный. Может произнести речь о равенстве в отношениях, пошутить об эгоистичных мужчинах.</p>
        
        <p>Эта двойственность особенно болезненна для партнера, создавая когнитивный диссонанс. Окружающие видят "замечательного мужчину", а дома разворачивается совсем другая реальность. Это заставляет жертву винить себя и сомневаться в адекватности собственного восприятия.</p>
    </div>

    <div class="profile-section critical-section">
        <h3 class="section-title">Прогноз и критические рекомендации</h3>
        <p>При таком уровне риска (<strong>{risk_score}%</strong>) отношения представляют серьезную угрозу для психического и физического здоровья партнера. Паттерны поведения ригидны и глубоко укоренены, изменения маловероятны без интенсивной психотерапии.</p>
        
        <div class="critical-actions">
            <h4>⚠️ КРИТИЧЕСКИ ВАЖНО:</h4>
            <ul class="critical-list">
                <li>Обратиться за профессиональной помощью немедленно</li>
                <li>Создать план безопасности и определить поддерживающую сеть</li>
                <li>Рассмотреть возможность временного раздельного проживания</li>
                <li>Документировать инциденты для возможного правового вмешательства</li>
            </ul>
        </div>
        
        <p><strong>Важно понимать:</strong> отношения характеризуются цикличностью с возрастающей интенсивностью. Без радикальных изменений ситуация будет только ухудшаться. Партнер не может "исправить" такого человека любовью или изменением собственного поведения.</p>
    </div>
</div>"""
        return analysis
    
    def _generate_medium_risk_analysis(
        self, 
        partner_name: str, 
        risk_score: float, 
        block_scores: Dict[str, float], 
        red_flags: list,
        dark_triad: Dict[str, float]
    ) -> str:
        """Generate analysis for medium-risk cases (40-70%)"""
        
        analysis = f"""
<div class="detailed-profile">
    <div class="profile-section">
        <h3 class="section-title">Психологическая характеристика личности</h3>
        <p>Анализ выявляет проблемные паттерны поведения, требующие серьезного внимания. Уровень риска <strong>{risk_score}%</strong> указывает на значительные сложности в отношениях, которые могут эскалировать без соответствующих мер.</p>
        
        <p><strong>{partner_name}</strong> демонстрирует смешанные черты личности с выраженными элементами нарциссизма (<strong>{dark_triad.get('narcissism', 0)}/10</strong>) и склонностью к манипулятивному поведению (<strong>{dark_triad.get('machiavellianism', 0)}/10</strong>).</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">Проявления нарциссических черт</h3>
        <p>Партнер проявляет повышенную потребность во внимании и одобрении. Часто переводит разговоры на себя, особенно когда обсуждаются достижения или проблемы других. Болезненно реагирует на критику, даже конструктивную.</p>
        
        <p>Характерна тенденция к обесцениванию чужих успехов через сравнение со своими достижениями. При этом собственные неудачи объясняются внешними обстоятельствами, а ответственность перекладывается на других.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">🎯 Элементы контролирующего поведения</h3>
        <p>Блок "Контроль" показывает <strong>{block_scores.get('control', 0)}/10</strong>. Проявляется в постепенном ограничении автономии партнера под видом заботы и любви. Начинается с "невинных" вопросов о планах и местонахождении, перерастает в требования постоянной отчетности.</p>
        
        <p>Характерны попытки влиять на социальные связи через негативные комментарии о друзьях и коллегах партнера. Финансовые решения также стремится контролировать, представляя это как "совместное планирование".</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">🔄 Искажения в коммуникации</h3>
        <p>Уровень газлайтинга <strong>{block_scores.get('gaslighting', 0)}/10</strong> проявляется в попытках переписать историю конфликтов. После ссор настаивает на своей версии событий, где его поведение выглядит оправданным.</p>
        
        <p>Использует эмоциональные реакции партнера против него: <em>"Ты слишком чувствительная"</em>, <em>"Ты все неправильно понимаешь"</em>, <em>"Я же не это имел в виду"</em>. Эти фразы заставляют сомневаться в адекватности собственных реакций.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">💭 Эмоциональная нестабильность</h3>
        <p>Проблемы с эмоциональной регуляцией (блок "Эмоция": <strong>{block_scores.get('emotion', 0)}/10</strong>) проявляются в непропорциональных реакциях на стресс. Мелкие неудобства могут вызвать значительную злость или обиду.</p>
        
        <p>После эмоциональных вспышек редко извиняется искренне. Чаще объясняет свое поведение усталостью, стрессом или действиями партнера: <em>"Ты же знаешь, как я устал"</em>, <em>"Ты меня спровоцировала"</em>.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">💕 Интимность и границы</h3>
        <p>В интимной сфере (блок "Интимность": <strong>{block_scores.get('intimacy', 0)}/10</strong>) иногда проявляет нечувствительность к потребностям и настроению партнера. Может использовать близость как способ "помириться" после конфликтов.</p>
        
        <p>Не всегда уважает отказы, склонен к эмоциональному давлению: <em>"Если ты меня любишь..."</em>, <em>"Мы давно не были близки"</em>. Границы партнера воспринимает как отвержение себя лично.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">Социальное поведение</h3>
        <p>В обществе старается произвести хорошее впечатление, может быть обаятельным и внимательным. Однако наедине поведение часто кардинально меняется. Эта двойственность создает путаницу и сомнения у партнера.</p>
    </div>

    <div class="profile-section warning-section">
        <h3 class="section-title">Прогноз и рекомендации</h3>
        <p>Уровень риска <strong>{risk_score}%</strong> требует активных мер по изменению ситуации. При отсутствии работы над проблемами высока вероятность эскалации конфликтов и ухудшения отношений.</p>
        
        <div class="recommendations">
            <h4>📋 Рекомендации:</h4>
            <ul class="recommendation-list">
                <li>Парная терапия с квалифицированным специалистом</li>
                <li>Установление четких границ в отношениях</li>
                <li>Развитие навыков здоровой коммуникации</li>
                <li>Индивидуальная работа над эмоциональной регуляцией</li>
            </ul>
        </div>
        
        <p><strong>Важно:</strong> изменения возможны при условии признания проблем и активной работы обеих сторон. Важно не игнорировать тревожные сигналы и обращаться за профессиональной помощью.</p>
    </div>
</div>"""
        return analysis
        
    def _generate_low_risk_analysis(
        self, 
        partner_name: str, 
        risk_score: float, 
        block_scores: Dict[str, float], 
        analysis_data: Dict[str, Any]
    ) -> str:
        """Generate analysis for low-risk cases (<40%)"""
        
        analysis = f"""
<div class="detailed-profile positive-profile">
    <div class="profile-section">
        <h3 class="section-title">Характеристика эмоционально зрелой личности</h3>
        <p>Анализ показывает здоровые паттерны поведения с высоким потенциалом для гармоничных отношений. Уровень риска <strong>{risk_score}%</strong> указывает на эмоционально зрелую личность с развитыми навыками межличностного взаимодействия.</p>
        
        <p><strong>{partner_name}</strong> демонстрирует стабильные проявления эмпатии, уважения к границам и способность к конструктивному общению. Это создает основу для здоровых, поддерживающих отношений.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">🌟 Эмоциональный интеллект и эмпатия</h3>
        <p>Партнер проявляет высокий уровень эмоционального интеллекта, способен понимать и учитывать чувства других. В разговорах активно слушает, задает уточняющие вопросы, проявляет искренний интерес к переживаниям партнера.</p>
        
        <p>Характерна способность разделять радость за успехи близких без зависти или конкуренции. Поддерживает начинания партнера, даже если они требуют временного отдаления или изменения планов.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">🤝 Здоровые коммуникативные навыки</h3>
        <p>Демонстрирует развитые навыки конструктивного общения. Конфликты решает через открытый диалог, избегая повышения голоса или личных оскорблений. Способен признавать ошибки и искренне извиняться.</p>
        
        <p>В спорных ситуациях стремится понять точку зрения другой стороны, ищет компромиссы. Не использует молчание или эмоциональные манипуляции как способы воздействия на партнера.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">🎯 Уважение к автономии и границам</h3>
        <p>Блок "Контроль" показывает здоровый уровень <strong>{block_scores.get('control', 0)}/10</strong>, что указывает на уважение к независимости партнера. Поддерживает социальные связи, не ревнует к друзьям и коллегам.</p>
        
        <p>В финансовых вопросах проявляет разумность: обсуждает крупные траты, но не контролирует каждую покупку. Уважает право партнера на личные расходы и хобби.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">🔄 Конструктивное разрешение конфликтов</h3>
        <p>Низкий уровень газлайтинга (<strong>{block_scores.get('gaslighting', 0)}/10</strong>) говорит о честности в общении. Не пытается переписать историю конфликтов или свести все к "неправильному пониманию".</p>
        
        <p>После ссор готов обсуждать произошедшее, анализировать причины и искать способы избежать повторения. Берет ответственность за свои слова и действия.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">💚 Эмоциональная стабильность и поддержка</h3>
        <p>Блок "Эмоция" (<strong>{block_scores.get('emotion', 0)}/10</strong>) демонстрирует развитые навыки эмоциональной регуляции. Реакции пропорциональны ситуации, способен сохранять спокойствие в стрессовых обстоятельствах.</p>
        
        <p>Служит эмоциональной опорой для партнера в трудные моменты. Умеет выслушать, поддержать, предложить практическую помощь без попыток "решить все за другого".</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">💕 Здоровая интимность</h3>
        <p>В интимной сфере (блок "Интимность": <strong>{block_scores.get('intimacy', 0)}/10</strong>) проявляет чуткость к потребностям и настроению партнера. Близость строится на взаимном желании и уважении.</p>
        
        <p>Никогда не принуждает к интимности, уважает отказы. Рассматривает близость как способ выражения любви и укрепления связи, а не как обязанность или инструмент воздействия.</p>
    </div>

    <div class="profile-section">
        <h3 class="section-title">Искренность и последовательность</h3>
        <p>Поведение в обществе и наедине остается последовательным. Не надевает "маски" для окружающих, демонстрирует искренность в отношениях. Это создает атмосферу доверия и безопасности.</p>
        
        <p>Готов открыто обсуждать отношения с близкими, не скрывает проблем под видом "все прекрасно". При этом уважает приватность пары и не выносит личные вопросы на публичное обсуждение.</p>
    </div>

    <div class="profile-section positive-section">
        <h3 class="section-title">Прогноз и перспективы</h3>
        <p>При уровне риска <strong>{risk_score}%</strong> прогноз для отношений крайне благоприятный. Такая личность способна создать стабильные, поддерживающие отношения с высоким уровнем удовлетворенности для обеих сторон.</p>
        
        <div class="positive-recommendations">
            <h4>🌱 Рекомендации для укрепления отношений:</h4>
            <ul class="positive-list">
                <li>Продолжать развивать навыки открытого общения</li>
                <li>Практиковать благодарность за качества партнера</li>
                <li>Совместно изучать литературу по психологии отношений</li>
                <li>Регулярно проводить время для откровенных разговоров</li>
            </ul>
        </div>
        
        <p><strong>Выводы:</strong> такие отношения служат примером здоровой привязанности и могут стать источником роста и поддержки для обеих сторон на протяжении долгих лет.</p>
    </div>
</div>"""
        return analysis
    
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
        elif risk_score >= 25:
            characteristics = [
                "Развитые навыки эмоциональной регуляции",
                "Способность к эмпатии и пониманию",
                "Здоровые реакции на стрессовые ситуации",
                "Навыки конструктивной коммуникации"
            ]
        elif risk_score >= 15:
            characteristics = [
                "Высокий эмоциональный интеллект",
                "Глубокая эмпатия к переживаниям партнера",
                "Стрессоустойчивость и эмоциональная стабильность",
                "Открытость и честность в общении",
                "Способность к компромиссам и взаимопониманию",
                "Уважение к личным границам и автономии партнера"
            ]
        else:
            characteristics = [
                "Исключительный эмоциональный интеллект",
                "Безусловная эмпатия и понимание",
                "Выдающаяся эмоциональная стабильность",
                "Мастерство в здоровой коммуникации",
                "Способность к глубокой эмоциональной близости",
                "Абсолютное уважение к партнеру как к личности"
            ]
        
        return '\n'.join([f'<li>{char}</li>' for char in characteristics])
    
    def _generate_behavior_patterns(self, risk_score: float) -> str:
        """Generate behavior patterns based on risk score"""
        patterns = [
            f"Эмоциональная нестабильность - {min(100, int(risk_score * 1.2))}%",
            f"Контролирующее поведение - {min(100, int(risk_score * 1.1))}%",
            f"Манипулятивные техники - {min(100, int(risk_score * 0.9))}%",
            f"Нарушение границ - {min(100, int(risk_score * 1.0))}%"
        ]
        
        return "\n".join(patterns)

    def _get_personality_traits(self, personality_type: str, risk_score: float) -> list:
        """Generate personality traits based on type and risk score"""
        base_traits = {
            'Нарциссическая личность': [
                'Грандиозное самомнение',
                'Потребность в восхищении', 
                'Отсутствие эмпатии',
                'Эксплуатация отношений'
            ],
            'Пограничная личность': [
                'Эмоциональная нестабильность',
                'Страх покинутости',
                'Импульсивность',
                'Нарушенная самоидентичность'
            ],
            'Антисоциальная личность': [
                'Игнорирование прав других',
                'Обман и манипуляции',
                'Импульсивность',
                'Отсутствие раскаяния'
            ],
            'Токсичная личность': [
                'Контролирующее поведение',
                'Эмоциональные качели',
                'Газлайтинг',
                'Нарушение границ'
            ]
        }
        
        # Get base traits for personality type
        traits = base_traits.get(personality_type, base_traits['Токсичная личность'])
        
        # Add risk-specific traits
        if risk_score >= 70:
            traits.extend(['Высокая агрессивность', 'Деструктивные паттерны'])
        elif risk_score >= 40:
            traits.extend(['Проблемные паттерны', 'Эмоциональная нестабильность'])
            
        return traits[:6]  # Limit to 6 traits

    def _get_personality_description(self, personality_type: str, risk_score: float) -> str:
        """Generate detailed personality description"""
        descriptions = {
            'Нарциссическая личность': f"Личность с выраженными нарциссическими чертами (риск {risk_score:.0f}%). Характеризуется грандиозным самомнением, потребностью в постоянном восхищении и отсутствием эмпатии к партнеру.",
            'Пограничная личность': f"Пограничное расстройство личности (риск {risk_score:.0f}%). Отличается эмоциональной нестабильностью, страхом покинутости и импульсивным поведением в отношениях.",
            'Антисоциальная личность': f"Антисоциальные черты личности (риск {risk_score:.0f}%). Проявляется в игнорировании прав партнера, обмане, манипуляциях и отсутствии раскаяния.",
            'Токсичная личность': f"Токсичные паттерны поведения (риск {risk_score:.0f}%). Включают контролирующее поведение, эмоциональные качели и систематическое нарушение границ партнера."
        }
        
        return descriptions.get(personality_type, descriptions['Токсичная личность'])

    def _get_risk_detailed_description(self, risk_score: float) -> str:
        """Generate detailed risk description"""
        if risk_score >= 70:
            return f"Критически высокий уровень токсичности ({risk_score:.0f}%). Обнаружены серьезные признаки эмоционального абьюза, контролирующего поведения и манипуляций. Отношения представляют значительную угрозу для психологического и возможно физического благополучия."
        elif risk_score >= 40:
            return f"Высокий уровень проблемных паттернов ({risk_score:.0f}%). Выявлены множественные красные флаги токсичного поведения, включая нарушение границ, эмоциональную нестабильность и элементы контроля."
        else:
            return f"Умеренный уровень риска ({risk_score:.0f}%). Некоторые проблемные моменты в поведении, которые требуют внимания, но в целом отношения находятся в допустимых рамках."

    def _get_risk_recommendations(self, risk_score: float) -> str:
        """Generate risk-specific recommendations"""
        if risk_score >= 70:
            return "Немедленно обратитесь к специалисту. Рассмотрите план безопасности. Установите четкие границы и поддержку близких."
        elif risk_score >= 40:
            return "Обратитесь к психологу для работы с отношениями. Укрепите личные границы. Развивайте поддерживающие отношения."
        else:
            return "Продолжайте наблюдение за динамикой отношений. При необходимости обратитесь за консультацией специалиста."

    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level string"""
        if risk_score >= 70:
            return "critical"
        elif risk_score >= 40:
            return "high"
        elif risk_score >= 20:
            return "medium"
        else:
            return "low"