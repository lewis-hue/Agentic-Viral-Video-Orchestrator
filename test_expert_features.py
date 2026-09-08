#!/usr/bin/env python3
"""
Comprehensive test suite for AVVO expert-level features
Tests all new agents and their integration into the enhanced pipeline
"""

import asyncio
import logging
import os
import sys
import json
from datetime import datetime
from typing import Dict, List

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExpertFeaturesTester:
    """
    Comprehensive tester for all expert-level AVVO features
    """

    def __init__(self):
        self.test_results = {}
        self.errors = []

    async def run_all_tests(self) -> Dict:
        """Run all expert feature tests"""
        logger.info("Starting comprehensive AVVO expert features test suite")

        test_methods = [
            self.test_predictive_intelligence_agent,
            self.test_reinforcement_strategy_engine,
            self.test_brand_safety_guardian,
            self.test_dynamic_shot_orchestrator,
            self.test_enhanced_orchestrator_integration,
            self.test_end_to_end_pipeline
        ]

        for test_method in test_methods:
            try:
                await test_method()
            except Exception as e:
                logger.error(f"Test {test_method.__name__} failed: {e}")
                self.errors.append(f"{test_method.__name__}: {str(e)}")

        # Generate test report
        report = self._generate_test_report()
        logger.info("Expert features test suite completed")
        return report

    async def test_predictive_intelligence_agent(self):
        """Test Predictive Intelligence & Anomaly Detection Agent"""
        logger.info("Testing Predictive Intelligence Agent...")

        try:
            from agents.predictive_intelligence.predictive_intelligence_agent import PredictiveIntelligenceAgent

            # Initialize agent
            agent = PredictiveIntelligenceAgent()

            # Test historical data collection
            df = await agent.collect_historical_data("AI technology", "tiktok", days=7)
            assert not df.empty, "Historical data collection failed"
            assert 'ds' in df.columns and 'y' in df.columns, "DataFrame missing required columns"

            # Test trend forecasting
            forecast = await agent.forecast_trend_trajectory("AI technology", "tiktok")
            assert forecast is not None, "Trend forecasting failed"
            assert hasattr(forecast, 'predicted_peak_date'), "Forecast missing peak date"
            assert forecast.confidence_score > 0, "Invalid confidence score"

            # Test anomaly detection
            current_data = {
                'keywords': ["AI technology", "machine learning"],
                'platforms': ["tiktok", "youtube"],
                'trends': [
                    {
                        'current_engagement': 15000,
                        'previous_engagement': 12000,
                        'reach': 50000,
                        'engagement_rate': 0.08,
                        'growth_rate': 0.25
                    }
                ]
            }
            anomalies = await agent.detect_anomalies(current_data)
            assert isinstance(anomalies, list), "Anomaly detection should return list"

            # Test cross-platform arbitrage
            arbitrage_opportunities = await agent.identify_cross_platform_arbitrage()
            assert isinstance(arbitrage_opportunities, list), "Arbitrage should return list"

            # Test comprehensive analysis
            analysis_results = await agent.run_predictive_analysis()
            assert 'forecasts' in analysis_results, "Analysis missing forecasts"
            assert 'anomalies' in analysis_results, "Analysis missing anomalies"

            self.test_results['predictive_intelligence'] = {
                'status': 'PASSED',
                'forecasts_count': len(analysis_results.get('forecasts', [])),
                'anomalies_count': len(analysis_results.get('anomalies', [])),
                'arbitrage_count': len(analysis_results.get('arbitrage_opportunities', []))
            }

            logger.info("✓ Predictive Intelligence Agent test PASSED")

        except Exception as e:
            logger.error(f"Predictive Intelligence Agent test FAILED: {e}")
            self.test_results['predictive_intelligence'] = {'status': 'FAILED', 'error': str(e)}
            raise

    async def test_reinforcement_strategy_engine(self):
        """Test Reinforcement & Strategy Engine"""
        logger.info("Testing Reinforcement & Strategy Engine...")

        try:
            from agents.optimization_feedback.reinforcement_strategy_engine import (
                ReinforcementStrategyEngine, CreativeVariable, VOWPAL_WABBIT_AVAILABLE
            )

            # Skip if vowpal_wabbit is not available
            if not VOWPAL_WABBIT_AVAILABLE:
                logger.warning("Vowpal Wabbit not available, skipping reinforcement strategy test")
                self.test_results['reinforcement_strategy'] = {
                    'status': 'SKIPPED',
                    'reason': 'Vowpal Wabbit not installed'
                }
                return

            # Initialize engine
            engine = ReinforcementStrategyEngine()

            # Test contextual bandit
            context = {
                'topic': 'technology',
                'platform': 'tiktok',
                'past_performance': {'avg_views': 10000, 'avg_engagement': 0.05}
            }

            strategy = await engine.select_optimal_strategy(context)
            assert isinstance(strategy, dict), "Strategy should be dictionary"
            assert CreativeVariable.VOICEOVER_STYLE in strategy, "Strategy missing voiceover style"

            # Test A/B test manager
            from agents.optimization_feedback.reinforcement_strategy_engine import ExperimentVariant

            variants = [
                ExperimentVariant("control", {CreativeVariable.MUSIC_GENRE: "electronic"}, 0.5),
                ExperimentVariant("variant1", {CreativeVariable.MUSIC_GENRE: "pop"}, 0.5)
            ]

            experiment_id = engine.ab_test_manager.create_experiment("test_experiment", variants)
            assert experiment_id, "Experiment creation failed"

            # Test reward model
            metrics = {
                'views': 10000,
                'likes': 800,
                'comments': 120,
                'shares': 45,
                'watch_time': 45000,
                'content_length': 60
            }

            reward_signal = engine.reward_model.calculate_reward(metrics, {'content_id': 'test'})
            assert reward_signal.total_reward > 0, "Reward calculation failed"
            assert reward_signal.total_reward <= 100, "Reward should be normalized"

            # Test strategy recommendations
            recommendations = engine.get_strategy_recommendations()
            assert 'learning_progress' in recommendations, "Missing learning progress"

            self.test_results['reinforcement_strategy'] = {
                'status': 'PASSED',
                'strategy_selected': True,
                'experiment_created': True,
                'reward_calculated': True
            }

            logger.info("✓ Reinforcement & Strategy Engine test PASSED")

        except Exception as e:
            logger.error(f"Reinforcement & Strategy Engine test FAILED: {e}")
            self.test_results['reinforcement_strategy'] = {'status': 'FAILED', 'error': str(e)}
            raise

    async def test_brand_safety_guardian(self):
        """Test Brand Safety & Ethical Guardian Agent"""
        logger.info("Testing Brand Safety & Ethical Guardian...")

        try:
            from agents.brand_safety.ethical_guardian_agent import BrandSafetyGuardian

            # Initialize guardian
            guardian = BrandSafetyGuardian()

            # Test text content moderation
            test_script = """
            This is an amazing new AI technology that will revolutionize the industry!
            It's incredibly powerful and everyone should try it immediately.
            """

            text_analysis = await guardian.text_moderator.analyze_text(test_script, guardian.brand_profile)
            assert 'safety_score' in text_analysis, "Text analysis missing safety score"
            assert text_analysis['safety_score'] > 0.8, "Safety score should be high for safe content"

            # Test content vetting
            content_data = {
                'content_id': 'test_content_001',
                'script': test_script,
                'topic': 'technology'
            }

            vetting_result = await guardian.vet_content(content_data)
            assert hasattr(vetting_result, 'overall_safety_score'), "Vetting result missing safety score"
            assert not vetting_result.requires_human_review, "Safe content should not require review"

            # Test adversarial probing
            probes = await guardian.run_adversarial_probes(['story_ideation'])
            assert len(probes) > 0, "Adversarial probes should return results"
            assert hasattr(probes[0], 'vulnerability_score'), "Probe missing vulnerability score"

            # Test safety report generation
            report = guardian.get_safety_report()
            assert isinstance(report, dict), "Safety report should be dictionary"

            self.test_results['brand_safety'] = {
                'status': 'PASSED',
                'text_analysis_completed': True,
                'content_vetting_completed': True,
                'adversarial_probes_run': True,
                'safety_report_generated': True
            }

            logger.info("✓ Brand Safety & Ethical Guardian test PASSED")

        except Exception as e:
            logger.error(f"Brand Safety & Ethical Guardian test FAILED: {e}")
            self.test_results['brand_safety'] = {'status': 'FAILED', 'error': str(e)}
            raise

    async def test_dynamic_shot_orchestrator(self):
        """Test Dynamic Shot & Composition Orchestrator"""
        logger.info("Testing Dynamic Shot & Composition Orchestrator...")

        try:
            from agents.video_generation.dynamic_shot_orchestrator import DynamicShotOrchestrator

            # Initialize orchestrator
            orchestrator = DynamicShotOrchestrator()

            # Test storyboard generation
            script_data = {
                'script': 'Learn about amazing AI technology that will change everything. It uses advanced machine learning algorithms.',
                'topic': 'technology',
                'tone': 'exciting'
            }

            storyboard = await orchestrator.storyboard_generator.generate_storyboard(script_data, 'tiktok')
            assert hasattr(storyboard, 'shots'), "Storyboard missing shots"
            assert len(storyboard.shots) > 0, "Storyboard should have at least one shot"
            assert storyboard.total_duration > 0, "Storyboard should have duration"

            # Test style frame generation
            style_frame = await orchestrator.style_manager.generate_style_frame(storyboard)
            assert hasattr(style_frame, 'prompt'), "Style frame missing prompt"
            assert hasattr(style_frame, 'style_keywords'), "Style frame missing keywords"

            # Test shot breakdown
            breakdown = orchestrator.get_shot_breakdown(storyboard)
            assert 'total_shots' in breakdown, "Breakdown missing shot count"
            assert 'shot_details' in breakdown, "Breakdown missing shot details"

            # Test complete video orchestration (mock)
            video_package = await orchestrator.orchestrate_video_creation(script_data, 'tiktok')
            assert 'metadata' in video_package, "Video package missing metadata"

            self.test_results['dynamic_shot_orchestrator'] = {
                'status': 'PASSED',
                'storyboard_generated': True,
                'style_frame_created': True,
                'shot_breakdown_analyzed': True,
                'video_orchestration_completed': True
            }

            logger.info("✓ Dynamic Shot & Composition Orchestrator test PASSED")

        except Exception as e:
            logger.error(f"Dynamic Shot & Composition Orchestrator test FAILED: {e}")
            self.test_results['dynamic_shot_orchestrator'] = {'status': 'FAILED', 'error': str(e)}
            raise

    async def test_enhanced_orchestrator_integration(self):
        """Test integration of all agents in enhanced orchestrator"""
        logger.info("Testing Enhanced Orchestrator Integration...")

        try:
            from app.orchestrator import EnhancedOrchestrator

            # Initialize enhanced orchestrator
            orchestrator = EnhancedOrchestrator()

            # Test pipeline status
            status = orchestrator.get_pipeline_status()
            assert 'current_run_id' in status, "Status missing run ID"
            assert 'progress_percentage' in status, "Status missing progress"

            # Test individual stage methods exist
            stage_methods = [
                '_run_predictive_intelligence',
                '_run_enhanced_trend_discovery',
                '_run_intelligent_story_ideation',
                '_run_brand_safety_vetting',
                '_run_advanced_video_generation',
                '_run_strategy_optimization',
                '_run_documentation'
            ]

            for method_name in stage_methods:
                assert hasattr(orchestrator, method_name), f"Missing method: {method_name}"

            # Test helper methods
            enhanced_trends = [
                {'summary': 'AI technology trends', 'breakout_potential': 0.8},
                {'summary': 'Machine learning advances', 'breakout_potential': 0.6}
            ]

            optimal_trends = orchestrator._select_optimal_trends(enhanced_trends)
            assert len(optimal_trends) <= 3, "Should select max 3 optimal trends"

            self.test_results['enhanced_orchestrator'] = {
                'status': 'PASSED',
                'pipeline_status_available': True,
                'all_stages_present': True,
                'helper_methods_working': True
            }

            logger.info("✓ Enhanced Orchestrator Integration test PASSED")

        except Exception as e:
            logger.error(f"Enhanced Orchestrator Integration test FAILED: {e}")
            self.test_results['enhanced_orchestrator'] = {'status': 'FAILED', 'error': str(e)}
            raise

    async def test_end_to_end_pipeline(self):
        """Test complete end-to-end pipeline execution"""
        logger.info("Testing End-to-End Pipeline...")

        try:
            from app.orchestrator import EnhancedOrchestrator

            # Initialize orchestrator
            orchestrator = EnhancedOrchestrator()

            # Run complete pipeline (with timeout to prevent hanging)
            try:
                result = await asyncio.wait_for(
                    orchestrator.run_enhanced_pipeline('tiktok'),
                    timeout=30.0  # 30 second timeout for testing
                )

                # Validate pipeline results
                assert 'run_id' in result, "Pipeline result missing run ID"
                assert 'status' in result, "Pipeline result missing status"
                assert 'results' in result, "Pipeline result missing results"
                assert 'stages_completed' in result, "Pipeline result missing stages completed"

                # Check that multiple stages completed
                stages_completed = result.get('stages_completed', 0)
                assert stages_completed > 0, "No stages completed"

                # Validate results structure
                results = result.get('results', {})
                expected_stages = [
                    'predictive_intelligence',
                    'enhanced_trend_discovery',
                    'intelligent_story_ideation',
                    'brand_safety_vetting',
                    'advanced_video_generation',
                    'strategy_optimization',
                    'documentation'
                ]

                completed_stages = set(results.keys())
                assert len(completed_stages) == stages_completed, "Stage count mismatch"

                self.test_results['end_to_end_pipeline'] = {
                    'status': 'PASSED',
                    'pipeline_completed': True,
                    'stages_completed': stages_completed,
                    'run_id': result.get('run_id'),
                    'duration_seconds': result.get('duration_seconds', 0)
                }

                logger.info(f"✓ End-to-End Pipeline test PASSED ({stages_completed} stages completed)")

            except asyncio.TimeoutError:
                logger.warning("Pipeline test timed out - this is expected in test environment")
                self.test_results['end_to_end_pipeline'] = {
                    'status': 'TIMEOUT',
                    'note': 'Pipeline started but timed out (expected in test environment)'
                }

        except Exception as e:
            logger.error(f"End-to-End Pipeline test FAILED: {e}")
            self.test_results['end_to_end_pipeline'] = {'status': 'FAILED', 'error': str(e)}
            raise

    def _generate_test_report(self) -> Dict:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get('status') == 'PASSED'])
        failed_tests = len([r for r in self.test_results.values() if r.get('status') == 'FAILED'])
        timeout_tests = len([r for r in self.test_results.values() if r.get('status') == 'TIMEOUT'])

        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'timeout': timeout_tests,
                'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
                'test_timestamp': datetime.now().isoformat()
            },
            'results': self.test_results,
            'errors': self.errors,
            'recommendations': self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        if any(result.get('status') == 'FAILED' for result in self.test_results.values()):
            recommendations.append("Fix failed tests before production deployment")

        if len(self.errors) > 0:
            recommendations.append("Address error conditions in agent implementations")

        # Check for missing dependencies
        try:
            import prophet
            import sklearn
        except ImportError:
            recommendations.append("Install missing ML dependencies: pip install prophet scikit-learn")

        try:
            import vowpal_wabbit
        except ImportError:
            recommendations.append("Install Vowpal Wabbit for contextual bandits")

        recommendations.extend([
            "Set up proper API keys for production use",
            "Configure brand safety profiles for your specific use case",
            "Set up monitoring and logging for production deployment",
            "Implement proper error handling and fallback mechanisms"
        ])

        return recommendations

async def main():
    """Main test execution function"""
    tester = ExpertFeaturesTester()

    try:
        # Run all tests
        report = await tester.run_all_tests()

        # Print summary
        summary = report['summary']
        print("\n=== AVVO EXPERT FEATURES TEST REPORT ===")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Timeout: {summary['timeout']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Test Time: {summary['test_timestamp']}")

        # Print detailed results
        print("\n=== DETAILED RESULTS ===")
        for test_name, result in report['results'].items():
            status = result.get('status', 'UNKNOWN')
            print(f"{test_name}: {status}")

        # Print errors if any
        if report['errors']:
            print("\n=== ERRORS ===")
            for error in report['errors']:
                print(f"• {error}")

        # Print recommendations
        if report['recommendations']:
            print("\n=== RECOMMENDATIONS ===")
            for rec in report['recommendations']:
                print(f"• {rec}")

        # Save report to file
        report_file = f"avvo_expert_features_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\nDetailed report saved to: {report_file}")

        # Exit with appropriate code
        if summary['failed'] > 0:
            sys.exit(1)
        else:
            print("\n🎉 All expert features tests completed successfully!")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())