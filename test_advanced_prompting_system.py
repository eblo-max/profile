"""
Comprehensive test for Advanced Prompt Engineering techniques
Tests all implemented techniques: CoT, ToT, Meta-prompting, Self-refining, Context Engineering
"""

import asyncio
import json
import time
from typing import Dict, Any, List

from app.services.ai_service import AIService
from app.core.config import settings


class AdvancedPromptingTester:
    """Test all advanced prompting techniques"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.test_results = {}
        
    async def run_comprehensive_test(self):
        """Run comprehensive test of all advanced techniques"""
        
        print("🚀 COMPREHENSIVE ADVANCED PROMPT ENGINEERING TEST")
        print("=" * 60)
        
        # Test data
        test_text = """
        Если ты еще раз поговоришь с этими своими подругами, я тебе покажу!
        Ты всегда все делаешь назло мне. Никогда не можешь понять, что я хочу.
        Без меня ты никто и ничто. Запомни это!
        """
        
        test_answers = [
            {"question_id": 1, "question": "Контролирует ли партнер ваше общение с друзьями?", "answer": "Да, постоянно"},
            {"question_id": 2, "question": "Угрожает ли партнер вам?", "answer": "Да, часто"},
            {"question_id": 3, "question": "Критикует ли партнер вас?", "answer": "Постоянно унижает"},
            {"question_id": 4, "question": "Изолирует ли партнер вас от семьи?", "answer": "Запрещает видеться"},
            {"question_id": 5, "question": "Контролирует ли финансы?", "answer": "Полностью контролирует деньги"}
        ]
        
        # Test all techniques
        techniques_to_test = [
            ("chain_of_thought", "Chain-of-Thought Reasoning"),
            ("meta_prompting", "Meta-Prompting Optimization"),
            ("field_aware", "Field-Aware Context Engineering"),
            ("self_refining", "Constitutional AI Self-Refining")
        ]
        
        profiling_techniques = [
            ("tree_of_thoughts", "Tree of Thoughts Multi-Expert"),
            ("cognitive_tools", "Recursive Cognitive Tools"),
            ("multi_perspective", "Multi-Perspective Analysis")
        ]
        
        # Test text analysis techniques
        print("\n📝 TESTING TEXT ANALYSIS TECHNIQUES")
        print("-" * 40)
        
        for technique, name in techniques_to_test:
            await self._test_text_analysis_technique(technique, name, test_text)
        
        # Test profiling techniques
        print("\n👥 TESTING PARTNER PROFILING TECHNIQUES")
        print("-" * 40)
        
        for technique, name in profiling_techniques:
            await self._test_profiling_technique(technique, name, test_answers)
        
        # Performance comparison
        print("\n📊 PERFORMANCE ANALYSIS")
        print("-" * 40)
        self._analyze_performance()
        
        # Quality assessment
        print("\n🎯 QUALITY ASSESSMENT")
        print("-" * 40)
        self._assess_quality()
        
        # Generate recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 40)
        self._generate_recommendations()
        
    async def _test_text_analysis_technique(self, technique: str, name: str, text: str):
        """Test specific text analysis technique"""
        try:
            print(f"\n🔍 Testing {name} ({technique})")
            start_time = time.time()
            
            result = await self.ai_service.analyze_text_advanced(
                text=text,
                user_id=999,
                context="Тестирование продвинутых техник",
                technique=technique,
                use_cache=False
            )
            
            processing_time = time.time() - start_time
            
            # Store results
            self.test_results[f"text_{technique}"] = {
                "technique": technique,
                "name": name,
                "processing_time": processing_time,
                "toxicity_score": result.get("toxicity_score", 0),
                "urgency_level": result.get("urgency_level", "unknown"),
                "red_flags_count": len(result.get("red_flags", [])),
                "confidence_level": result.get("confidence_level", 0),
                "has_step_by_step": "step_by_step_analysis" in result,
                "result": result
            }
            
            print(f"   ✅ Completed in {processing_time:.2f}s")
            print(f"   📊 Toxicity: {result.get('toxicity_score', 0)}/10")
            print(f"   ⚠️  Urgency: {result.get('urgency_level', 'unknown')}")
            print(f"   🚩 Red flags: {len(result.get('red_flags', []))}")
            
            if technique == "chain_of_thought" and "step_by_step_analysis" in result:
                print(f"   🧠 CoT Analysis: Present")
            
            if technique == "meta_prompting":
                print(f"   🔧 Meta-optimization: Applied")
                
            if technique == "field_aware":
                print(f"   🎯 Field Management: Active")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            self.test_results[f"text_{technique}"] = {"error": str(e)}
    
    async def _test_profiling_technique(self, technique: str, name: str, answers: List[Dict]):
        """Test specific profiling technique"""
        try:
            print(f"\n🔍 Testing {name} ({technique})")
            start_time = time.time()
            
            result = await self.ai_service.profile_partner_advanced(
                answers=answers,
                user_id=999,
                partner_name="Тестовый партнер",
                partner_description="Контролирующее поведение",
                technique=technique,
                use_cache=False
            )
            
            processing_time = time.time() - start_time
            
            # Store results
            self.test_results[f"profile_{technique}"] = {
                "technique": technique,
                "name": name,
                "processing_time": processing_time,
                "manipulation_risk": result.get("manipulation_risk", 0),
                "urgency_level": result.get("urgency_level", "unknown"),
                "red_flags_count": len(result.get("red_flags", [])),
                "profile_length": len(result.get("psychological_profile", "")),
                "has_expert_analyses": "expert_analyses" in result,
                "expert_agreement": result.get("expert_agreement", 0),
                "result": result
            }
            
            print(f"   ✅ Completed in {processing_time:.2f}s")
            print(f"   📊 Manipulation Risk: {result.get('manipulation_risk', 0)}/10")
            print(f"   ⚠️  Urgency: {result.get('urgency_level', 'unknown')}")
            print(f"   🚩 Red flags: {len(result.get('red_flags', []))}")
            print(f"   📝 Profile length: {len(result.get('psychological_profile', ''))} chars")
            
            if technique == "tree_of_thoughts" and "expert_analyses" in result:
                print(f"   👥 Expert consensus: {result.get('expert_agreement', 0):.2f}")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            self.test_results[f"profile_{technique}"] = {"error": str(e)}
    
    def _analyze_performance(self):
        """Analyze performance across techniques"""
        
        # Text analysis performance
        text_results = {k: v for k, v in self.test_results.items() if k.startswith("text_") and "error" not in v}
        if text_results:
            print("\n📈 TEXT ANALYSIS PERFORMANCE:")
            avg_time = sum(r["processing_time"] for r in text_results.values()) / len(text_results)
            print(f"   Average processing time: {avg_time:.2f}s")
            
            fastest = min(text_results.items(), key=lambda x: x[1]["processing_time"])
            slowest = max(text_results.items(), key=lambda x: x[1]["processing_time"])
            print(f"   Fastest: {fastest[1]['name']} ({fastest[1]['processing_time']:.2f}s)")
            print(f"   Slowest: {slowest[1]['name']} ({slowest[1]['processing_time']:.2f}s)")
        
        # Profiling performance
        profile_results = {k: v for k, v in self.test_results.items() if k.startswith("profile_") and "error" not in v}
        if profile_results:
            print("\n📈 PROFILING PERFORMANCE:")
            avg_time = sum(r["processing_time"] for r in profile_results.values()) / len(profile_results)
            print(f"   Average processing time: {avg_time:.2f}s")
            
            fastest = min(profile_results.items(), key=lambda x: x[1]["processing_time"])
            slowest = max(profile_results.items(), key=lambda x: x[1]["processing_time"])
            print(f"   Fastest: {fastest[1]['name']} ({fastest[1]['processing_time']:.2f}s)")
            print(f"   Slowest: {slowest[1]['name']} ({slowest[1]['processing_time']:.2f}s)")
    
    def _assess_quality(self):
        """Assess quality of different techniques"""
        
        # Text analysis quality
        text_results = {k: v for k, v in self.test_results.items() if k.startswith("text_") and "error" not in v}
        if text_results:
            print("\n🎯 TEXT ANALYSIS QUALITY:")
            
            # Check consistency in toxicity scoring
            toxicity_scores = [r["toxicity_score"] for r in text_results.values()]
            if toxicity_scores:
                avg_toxicity = sum(toxicity_scores) / len(toxicity_scores)
                toxicity_variance = sum((score - avg_toxicity) ** 2 for score in toxicity_scores) / len(toxicity_scores)
                print(f"   Average toxicity score: {avg_toxicity:.1f}/10")
                print(f"   Toxicity variance: {toxicity_variance:.2f} (lower is more consistent)")
            
            # Check red flags detection
            red_flags_counts = [r["red_flags_count"] for r in text_results.values()]
            if red_flags_counts:
                avg_flags = sum(red_flags_counts) / len(red_flags_counts)
                print(f"   Average red flags detected: {avg_flags:.1f}")
        
        # Profiling quality
        profile_results = {k: v for k, v in self.test_results.items() if k.startswith("profile_") and "error" not in v}
        if profile_results:
            print("\n🎯 PROFILING QUALITY:")
            
            # Check manipulation risk consistency
            risk_scores = [r["manipulation_risk"] for r in profile_results.values()]
            if risk_scores:
                avg_risk = sum(risk_scores) / len(risk_scores)
                risk_variance = sum((score - avg_risk) ** 2 for score in risk_scores) / len(risk_scores)
                print(f"   Average manipulation risk: {avg_risk:.1f}/10")
                print(f"   Risk variance: {risk_variance:.2f}")
            
            # Check profile detail
            profile_lengths = [r["profile_length"] for r in profile_results.values()]
            if profile_lengths:
                avg_length = sum(profile_lengths) / len(profile_lengths)
                print(f"   Average profile length: {avg_length:.0f} characters")
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        
        print("\n💡 TECHNIQUE RECOMMENDATIONS:")
        
        # Best performing techniques
        successful_results = {k: v for k, v in self.test_results.items() if "error" not in v}
        
        if successful_results:
            # Speed recommendations
            fastest_overall = min(successful_results.items(), key=lambda x: x[1]["processing_time"])
            print(f"   🚀 Fastest technique: {fastest_overall[1]['name']}")
            
            # Quality recommendations for text analysis
            text_results = {k: v for k, v in successful_results.items() if k.startswith("text_")}
            if text_results:
                # Find technique with best red flag detection
                best_detection = max(text_results.items(), key=lambda x: x[1]["red_flags_count"])
                print(f"   🎯 Best red flag detection: {best_detection[1]['name']}")
            
            # Quality recommendations for profiling
            profile_results = {k: v for k, v in successful_results.items() if k.startswith("profile_")}
            if profile_results:
                # Find technique with most detailed analysis
                most_detailed = max(profile_results.items(), key=lambda x: x[1]["profile_length"])
                print(f"   📝 Most detailed analysis: {most_detailed[1]['name']}")
                
                # Find technique with highest expert agreement (if available)
                expert_results = {k: v for k, v in profile_results.items() if v.get("expert_agreement", 0) > 0}
                if expert_results:
                    best_consensus = max(expert_results.items(), key=lambda x: x[1]["expert_agreement"])
                    print(f"   👥 Best expert consensus: {best_consensus[1]['name']} ({best_consensus[1]['expert_agreement']:.2f})")
        
        print("\n🔧 IMPLEMENTATION RECOMMENDATIONS:")
        print("   • Use Chain-of-Thought for standard text analysis")
        print("   • Use Tree-of-Thoughts for complex partner profiling")
        print("   • Use Meta-prompting for domain-specific optimization")
        print("   • Use Field-aware prompting for token-constrained scenarios")
        print("   • Use Self-refining for critical safety assessments")
        
        print("\n⚡ PRODUCTION DEPLOYMENT:")
        print("   • Implement technique selection based on complexity")
        print("   • Use caching for expensive techniques like ToT")
        print("   • Monitor performance metrics in real-time")
        print("   • A/B test techniques for quality optimization")


async def main():
    """Run the comprehensive test"""
    tester = AdvancedPromptingTester()
    await tester.run_comprehensive_test()
    
    # Save detailed results
    with open("advanced_prompting_test_results.json", "w", encoding="utf-8") as f:
        json.dump(tester.test_results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: advanced_prompting_test_results.json")
    print("🎉 COMPREHENSIVE TEST COMPLETED!")


if __name__ == "__main__":
    asyncio.run(main()) 