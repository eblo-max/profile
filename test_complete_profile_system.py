"""
Комплексный тест системы профилирования партнера
Тестирует весь процесс от создания профиля до генерации PDF
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_session
from app.models.user import User
from app.models.profile import PartnerProfile
from app.services.ai_service import AIService
from app.services.html_pdf_service import HTMLPDFService
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

class CompleteProfileSystemTest:
    """Комплексный тест системы профилирования партнера"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.pdf_service = HTMLPDFService()
        self.test_results = {}
        
    async def create_test_user(self, db: AsyncSession) -> User:
        """Создает тестового пользователя"""
        import random
        telegram_id = random.randint(900000000, 999999999)
        
        user = User(
            telegram_id=telegram_id,
            username="test_user",
            first_name="Тестовый",
            last_name="Пользователь",
            name="Тестовый Пользователь",
            gender="male",
            age_group="26-35",
            personality_type="ENFP",
            timezone="Europe/Moscow",
            bio="Тестовый пользователь для проверки системы",
            interests='["психология", "отношения", "саморазвитие"]',
            goals='["найти совместимость", "улучшить отношения"]'
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
        
    async def create_test_partner_profile(self, db: AsyncSession, user_id: int) -> PartnerProfile:
        """Создает полный профиль партнера с детальными ответами"""
        # Создаем детальные ответы для анкеты
        questionnaire_answers = {
            "partner_name": "Анна Петрова",
            "partner_age": 28,
            "partner_gender": "female",
            "relationship_history": "Была в двух серьезных отношениях. Первые длились 3 года, закончились из-за разных жизненных целей. Вторые - 2 года, партнер оказался нечестным в финансовых вопросах. Сейчас очень осторожна в выборе партнера.",
            "communication_style": "Очень эмоциональна в общении, любит делиться чувствами. Иногда может быть слишком прямолинейной, что обижает окружающих. В конфликтах становится очень возбужденной, может повышать голос. Предпочитает решать проблемы сразу, а не откладывать.",
            "conflict_resolution": "В конфликтах сначала эмоционально реагирует, может наговорить лишнего. Потом остывает и готова к диалогу. Любит, когда партнер первым идет на примирение. Иногда может дуться несколько дней, если чувствует себя обиженной.",
            "emotional_patterns": "Очень чувствительна к критике, может расплакаться от резкого слова. Настроение меняется быстро - от радости к грусти. Нуждается в постоянном подтверждении любви и внимания. Ревнива, но старается это скрывать.",
            "family_dynamics": "Из неполной семьи, воспитывалась мамой и бабушкой. Отца практически не видела. Очень близка с мамой, советуется по всем вопросам. Иногда мнение мамы важнее мнения партнера. Хочет большую семью с детьми.",
            "financial_behavior": "Импульсивна в тратах, может потратить всю зарплату за неделю на одежду и косметику. Не умеет планировать бюджет. Считает, что мужчина должен обеспечивать семью. Любит дорогие подарки и воспринимает их как проявление любви.",
            "social_interactions": "Очень общительная, душа компании. Любит быть в центре внимания. Имеет много подруг, с которыми постоянно общается. Иногда может рассказать личные детали отношений подругам. Ревнует партнера к его друзьям.",
            "intimacy_approach": "Рассматривает близость как способ укрепления отношений. Очень романтична, любит свечи, лепестки роз. Нуждается в долгих прелюдиях и эмоциональной близости. Может использовать близость для манипуляций или помирения после ссор.",
            "stress_management": "Под стрессом становится очень нервной, может срываться на близких. Заедает стресс сладким или идет за покупками. Любит, когда ее жалеют и утешают. Иногда может придумывать проблемы, чтобы получить внимание.",
            "future_planning": "Мечтает о красивой свадьбе и счастливой семье. Планирует детей в ближайшие 2-3 года. Хочет переехать в большую квартиру. Не очень реалистично оценивает финансовые возможности для осуществления планов.",
            "personal_growth": "Посещает психолога, читает книги по саморазвитию. Пытается работать над своими эмоциями и ревностью. Хочет научиться быть более независимой. Иногда начинает новые хобби, но быстро бросает.",
            "red_flags": "Может быть очень ревнивой, проверяет телефон партнера. Иногда устраивает сцены ревности без повода. Слишком зависима от мнения мамы. Импульсивна в тратах. Может манипулировать через слезы и обиды.",
            "partner_background": "Работает менеджером в торговой компании. Зарабатывает средне, но хочет большего. Активна в социальных сетях, много фотографируется. Любит путешествия и красивую жизнь. Из семьи со средним достатком.",
            "behavioral_observations": "Часто меняет настроение в течение дня. Может быть очень милой и нежной, а через час устроить скандал. Любит быть в центре внимания на публике. Очень следит за внешностью, тратит много времени на уход за собой.",
            "goals_aspirations": "Хочет стать успешной в карьере, но не готова много работать. Мечтает о статусной жизни. Планирует рожать детей, но боится потерять фигуру. Хочет, чтобы партнер был успешным и обеспечивал семью.",
            "additional_notes": "Очень эмоциональна и импульсивна. Нуждается в постоянном внимании и подтверждении. Может быть замечательной партнершей, если научится контролировать эмоции. Требует терпеливого и понимающего партнера."
        }
        
        from app.utils.enums import UrgencyLevel
        
        profile = PartnerProfile(
            user_id=user_id,
            partner_name="Анна Петрова",
            partner_description="Тестовый профиль партнера для комплексного анализа",
            questionnaire_answers=questionnaire_answers,
            manipulation_risk=0.0,  # Будет вычислен AI
            urgency_level=UrgencyLevel.LOW,  # Будет обновлен AI
            is_completed=False
        )
        
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile
        
    async def test_ai_analysis(self, profile: PartnerProfile) -> dict:
        """Тестирует AI анализ профиля"""
        print("🧠 Начинаю AI анализ профиля...")
        
        try:
            # Преобразуем questionnaire_answers в формат для AIService
            answers_list = []
            for key, value in profile.questionnaire_answers.items():
                answers_list.append({
                    'question': key.replace('_', ' ').title(),
                    'answer': str(value)
                })
            
            # Получаем анализ через Tree of Thoughts
            analysis = await self.ai_service.profile_partner_advanced(
                answers=answers_list,
                user_id=profile.user_id,
                partner_name=profile.partner_name,
                partner_description=profile.partner_description or "",
                technique="tree_of_thoughts",
                use_cache=False
            )
            
            print(f"✅ AI анализ завершен")
            print(f"📊 Размер ответа: {len(str(analysis))} символов")
            
            # Проверяем структуру ответа
            required_fields = [
                'psychological_profile', 'experts', 'personalized_insights',
                'behavioral_evidence', 'survival_guide', 'overall_risk_score',
                'dark_triad'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in analysis:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Отсутствуют поля: {missing_fields}")
            else:
                print("✅ Все обязательные поля присутствуют")
                
            # Проверяем экспертов
            if 'experts' in analysis and len(analysis['experts']) == 3:
                print("✅ Найдены все 3 эксперта Tree of Thoughts")
            else:
                print(f"❌ Найдено экспертов: {len(analysis.get('experts', []))}")
                
            # Проверяем персонализацию
            insights_count = len(analysis.get('personalized_insights', []))
            evidence_count = len(analysis.get('behavioral_evidence', []))
            
            print(f"📈 Персонализированных инсайтов: {insights_count}")
            print(f"🔍 Поведенческих доказательств: {evidence_count}")
            
            # Проверяем размер психологического профиля
            profile_text = analysis.get('psychological_profile', '')
            word_count = len(profile_text.split())
            
            print(f"📝 Слов в психологическом профиле: {word_count}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Ошибка AI анализа: {str(e)}")
            raise
            
    async def test_pdf_generation(self, analysis: dict, partner_name: str) -> str:
        """Тестирует генерацию PDF"""
        print("📄 Начинаю генерацию PDF...")
        
        try:
            # Генерируем PDF
            pdf_bytes = await self.pdf_service.generate_partner_report_html(
                analysis_data=analysis,
                user_id=12345,
                partner_name=partner_name
            )
            
            # Сохраняем в файл
            pdf_path = f"partner_analysis_{partner_name.replace(' ', '_')}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(pdf_bytes)
            
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"✅ PDF сгенерирован: {pdf_path}")
                print(f"📊 Размер файла: {file_size} байт ({file_size/1024:.1f} KB)")
                
                return pdf_path
            else:
                print("❌ PDF файл не найден")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка генерации PDF: {str(e)}")
            raise
            
    def evaluate_quality(self, analysis: dict) -> dict:
        """Оценивает качество анализа"""
        print("🎯 Оцениваю качество анализа...")
        
        quality_score = 0
        max_score = 100
        
        # Проверяем структуру (20 баллов)
        required_fields = [
            'psychological_profile', 'experts', 'personalized_insights',
            'behavioral_evidence', 'survival_guide', 'overall_risk_score',
            'dark_triad'
        ]
        
        structure_score = 0
        for field in required_fields:
            if field in analysis:
                structure_score += 20 / len(required_fields)
        
        quality_score += structure_score
        
        # Проверяем экспертов Tree of Thoughts (20 баллов)
        experts_count = len(analysis.get('experts', []))
        if experts_count == 3:
            quality_score += 20
        elif experts_count > 0:
            quality_score += 10
            
        # Проверяем персонализацию (30 баллов)
        insights_count = len(analysis.get('personalized_insights', []))
        evidence_count = len(analysis.get('behavioral_evidence', []))
        
        personalization_score = 0
        if insights_count >= 8:
            personalization_score += 15
        elif insights_count >= 4:
            personalization_score += 10
        elif insights_count >= 1:
            personalization_score += 5
            
        if evidence_count >= 10:
            personalization_score += 15
        elif evidence_count >= 6:
            personalization_score += 10
        elif evidence_count >= 3:
            personalization_score += 5
            
        quality_score += personalization_score
        
        # Проверяем размер профиля (30 баллов)
        profile_text = analysis.get('psychological_profile', '')
        word_count = len(profile_text.split())
        
        if word_count >= 1500:
            quality_score += 30
        elif word_count >= 1000:
            quality_score += 20
        elif word_count >= 500:
            quality_score += 10
            
        # Определяем оценку
        if quality_score >= 90:
            grade = "A+"
        elif quality_score >= 80:
            grade = "A"
        elif quality_score >= 70:
            grade = "B+"
        elif quality_score >= 60:
            grade = "B"
        else:
            grade = "C"
            
        quality_report = {
            'total_score': quality_score,
            'max_score': max_score,
            'percentage': (quality_score / max_score) * 100,
            'grade': grade,
            'structure_score': structure_score,
            'experts_count': experts_count,
            'insights_count': insights_count,
            'evidence_count': evidence_count,
            'word_count': word_count
        }
        
        print(f"📊 Общий балл: {quality_score}/{max_score} ({quality_report['percentage']:.1f}%)")
        print(f"🎓 Оценка: {grade}")
        print(f"🏗️ Структура: {structure_score:.1f}/20")
        print(f"👥 Экспертов: {experts_count}/3")
        print(f"💡 Инсайтов: {insights_count}")
        print(f"🔍 Доказательств: {evidence_count}")
        print(f"📝 Слов: {word_count}")
        
        return quality_report
        
    async def run_complete_test(self):
        """Запускает полный комплексный тест"""
        print("🚀 Запускаю комплексный тест системы профилирования партнера")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Получаем сессию БД
            async with get_session() as db:
                # 1. Создаем тестового пользователя
                print("👤 Создаю тестового пользователя...")
                user = await self.create_test_user(db)
                print(f"✅ Пользователь создан: {user.first_name} {user.last_name}")
                
                # 2. Создаем профиль партнера
                print("💝 Создаю профиль партнера...")
                profile = await self.create_test_partner_profile(db, user.id)
                print(f"✅ Профиль создан для партнера: {profile.partner_name}")
                
                # 3. Тестируем AI анализ
                analysis = await self.test_ai_analysis(profile)
                
                # 4. Оцениваем качество
                quality_report = self.evaluate_quality(analysis)
                
                # 5. Генерируем PDF
                pdf_path = await self.test_pdf_generation(analysis, profile.partner_name)
                
                # 6. Сохраняем результаты
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                self.test_results = {
                    'timestamp': start_time.isoformat(),
                    'duration_seconds': duration,
                    'user_id': user.id,
                    'partner_name': profile.partner_name,
                    'quality_report': quality_report,
                    'pdf_path': pdf_path,
                    'pdf_generated': pdf_path is not None,
                    'analysis_size': len(str(analysis)),
                    'success': True
                }
                
                # Сохраняем результаты в файл
                with open('test_results.json', 'w', encoding='utf-8') as f:
                    json.dump(self.test_results, f, ensure_ascii=False, indent=2)
                    
                print("\n" + "=" * 60)
                print("🎉 КОМПЛЕКСНЫЙ ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
                print(f"⏱️ Время выполнения: {duration:.1f} секунд")
                print(f"🎯 Итоговая оценка: {quality_report['grade']} ({quality_report['percentage']:.1f}%)")
                print(f"📄 PDF файл: {'✅ Создан' if pdf_path else '❌ Не создан'}")
                print(f"💾 Результаты сохранены в: test_results.json")
                
                if pdf_path:
                    print(f"🔗 PDF файл: {pdf_path}")
                    
                # Очищаем тестовые данные
                print("\n🧹 Очищаю тестовые данные...")
                await db.delete(profile)
                await db.delete(user)
                await db.commit()
                print("✅ Тестовые данные очищены")
            
        except Exception as e:
            print(f"\n❌ ОШИБКА В ТЕСТЕ: {str(e)}")
            import traceback
            traceback.print_exc()
            
            self.test_results = {
                'timestamp': start_time.isoformat(),
                'duration_seconds': (datetime.now() - start_time).total_seconds(),
                'error': str(e),
                'success': False
            }
            
            # Сохраняем результаты с ошибкой
            with open('test_results.json', 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)

async def main():
    """Основная функция для запуска теста"""
    test = CompleteProfileSystemTest()
    await test.run_complete_test()

if __name__ == "__main__":
    asyncio.run(main()) 