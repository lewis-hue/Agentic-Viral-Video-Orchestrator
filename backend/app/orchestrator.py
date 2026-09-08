import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os
import json

# Import existing agents
from agents.trend_discovery.trend_discovery_agent import TrendDiscoveryAgent
from agents.story_ideation.story_ideation_agent import StoryIdeationAgent
from agents.documentation.documentation_agent import DocumentationAgent

# Import new expert-level agents
from agents.predictive_intelligence.predictive_intelligence_agent import PredictiveIntelligenceAgent
from agents.optimization_feedback.reinforcement_strategy_engine import ReinforcementStrategyEngine
from agents.brand_safety.ethical_guardian_agent import BrandSafetyGuardian
from agents.video_generation.dynamic_shot_orchestrator import DynamicShotOrchestrator

class EnhancedOrchestrator:
    """
    Enhanced orchestrator that integrates all expert-level AVVO agents
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize existing agents
        gemini_key = os.getenv("GEMINI_API_KEY")
        self.trend_agent = TrendDiscoveryAgent(gemini_api_key=gemini_key)
        self.story_agent = StoryIdeationAgent(gemini_api_key=gemini_key)
        langsmith_key = os.getenv("LANGCHAIN_API_KEY")
        github_token = os.getenv("GITHUB_TOKEN")
        self.doc_agent = DocumentationAgent(
            langsmith_api_key=langsmith_key,
            github_token=github_token
        )

        # Initialize new expert-level agents
        self.predictive_agent = PredictiveIntelligenceAgent()
        self.strategy_engine = ReinforcementStrategyEngine()
        self.safety_guardian = BrandSafetyGuardian()
        self.video_orchestrator = DynamicShotOrchestrator()

        # Pipeline state
        self.pipeline_state = {
            'current_run_id': None,
            'start_time': None,
            'current_stage': None,
            'results': {},
            'errors': []
        }

    async def run_enhanced_pipeline(self, target_platform: str = 'tiktok') -> Dict:
        """
        Run the complete enhanced AVVO pipeline with all expert-level features
        """
        run_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.pipeline_state['current_run_id'] = run_id
        self.pipeline_state['start_time'] = datetime.now()
        self.pipeline_state['results'] = {}
        self.pipeline_state['errors'] = []

        try:
            self.logger.info(f"Starting enhanced AVVO pipeline run: {run_id}")

            # Stage 1: Predictive Intelligence & Trend Discovery
            await self._execute_stage("predictive_intelligence", self._run_predictive_intelligence)

            # Stage 2: Enhanced Trend Discovery with Anomaly Detection
            await self._execute_stage("enhanced_trend_discovery", self._run_enhanced_trend_discovery)

            # Stage 3: Intelligent Story Ideation with Strategy Optimization
            await self._execute_stage("intelligent_story_ideation", self._run_intelligent_story_ideation)

            # Stage 4: Brand Safety & Ethical Vetting
            await self._execute_stage("brand_safety_vetting", self._run_brand_safety_vetting)

            # Stage 5: Advanced Video Generation with Shot Orchestration
            await self._execute_stage("advanced_video_generation", self._run_advanced_video_generation)

            # Stage 6: Strategy Learning & Optimization
            await self._execute_stage("strategy_optimization", self._run_strategy_optimization)

            # Stage 7: Documentation & Versioning
            await self._execute_stage("documentation", self._run_documentation)

            # Pipeline completed successfully
            completion_time = datetime.now()
            duration = completion_time - self.pipeline_state['start_time']

            result = {
                'run_id': run_id,
                'status': 'completed',
                'duration_seconds': duration.total_seconds(),
                'stages_completed': len(self.pipeline_state['results']),
                'results': self.pipeline_state['results'],
                'errors': self.pipeline_state['errors'],
                'completed_at': completion_time
            }

            self.logger.info(f"Enhanced AVVO pipeline completed successfully in {duration.total_seconds()}s")
            return result

        except Exception as e:
            self.logger.error(f"Error in enhanced pipeline: {e}")
            self.pipeline_state['errors'].append(str(e))

            return {
                'run_id': run_id,
                'status': 'failed',
                'error': str(e),
                'results': self.pipeline_state['results'],
                'errors': self.pipeline_state['errors']
            }

    async def _execute_stage(self, stage_name: str, stage_function) -> None:
        """Execute a pipeline stage with error handling"""
        try:
            self.pipeline_state['current_stage'] = stage_name
            self.logger.info(f"Executing stage: {stage_name}")

            result = await stage_function()
            self.pipeline_state['results'][stage_name] = result

        except Exception as e:
            error_msg = f"Stage {stage_name} failed: {str(e)}"
            self.logger.error(error_msg)
            self.pipeline_state['errors'].append(error_msg)
            raise

    async def _run_predictive_intelligence(self) -> Dict:
        """Run predictive intelligence and anomaly detection"""
        # Run comprehensive predictive analysis
        predictive_results = await self.predictive_agent.run_predictive_analysis()

        return {
            'forecasts_count': len(predictive_results.get('forecasts', [])),
            'anomalies_detected': len(predictive_results.get('anomalies', [])),
            'arbitrage_opportunities': len(predictive_results.get('arbitrage_opportunities', [])),
            'analysis_timestamp': predictive_results.get('analysis_timestamp'),
            'total_trends_analyzed': predictive_results.get('total_trends_analyzed', 0)
        }

    async def _run_enhanced_trend_discovery(self) -> Dict:
        """Run enhanced trend discovery with anomaly insights"""
        # Get traditional trends
        traditional_trends = await self.trend_agent.discover_trends()

        # Get predictive insights
        predictive_results = await self.predictive_agent.run_predictive_analysis()

        # Combine and enhance trends with predictive data
        enhanced_trends = self._enhance_trends_with_predictive_insights(
            traditional_trends, predictive_results
        )

        return {
            'traditional_trends_count': len(traditional_trends),
            'enhanced_trends_count': len(enhanced_trends),
            'anomalies_detected': len(predictive_results.get('anomalies', [])),
            'breakout_potential_trends': len([t for t in enhanced_trends if t.get('breakout_potential', 0) > 0.7])
        }

    async def _run_intelligent_story_ideation(self) -> Dict:
        """Run intelligent story ideation with strategy optimization"""
        # Get enhanced trends
        enhanced_trends = self.pipeline_state['results'].get('enhanced_trend_discovery', {}).get('enhanced_trends', [])

        if not enhanced_trends:
            return {'error': 'No enhanced trends available for story ideation'}

        # Select optimal trends for content creation
        selected_trends = self._select_optimal_trends(enhanced_trends)

        # Generate context for strategy engine
        context = {
            'topic': selected_trends[0].get('keyword', 'trending_topic'),
            'platform': 'tiktok',
            'past_performance': {'avg_views': 10000, 'avg_engagement': 0.05}
        }

        # Get optimal creative strategy
        optimal_strategy = await self.strategy_engine.select_optimal_strategy(context)

        # Generate scripts using story agent with strategy guidance
        scripts = self.story_agent.generate_scripts(selected_trends[:3])  # Top 3 trends
        ranked_scripts = self.story_agent.rank_scripts(scripts)

        # Enhance top scripts with optimal strategy
        enhanced_scripts = self._enhance_scripts_with_strategy(ranked_scripts[:2], optimal_strategy)

        return {
            'selected_trends_count': len(selected_trends),
            'scripts_generated': len(scripts),
            'top_scripts_count': len(enhanced_scripts),
            'optimal_strategy': optimal_strategy,
            'enhanced_scripts': enhanced_scripts
        }

    async def _run_brand_safety_vetting(self) -> Dict:
        """Run comprehensive brand safety and ethical vetting"""
        # Get scripts from previous stage
        enhanced_scripts = self.pipeline_state['results'].get('intelligent_story_ideation', {}).get('enhanced_scripts', [])

        if not enhanced_scripts:
            return {'error': 'No scripts available for safety vetting'}

        vetting_results = []

        for script in enhanced_scripts:
            # Prepare content for vetting
            content_data = {
                'content_id': script.get('id', 'unknown'),
                'script': script.get('content', ''),
                'topic': script.get('topic', 'general')
            }

            # Run comprehensive safety analysis
            safety_analysis = await self.safety_guardian.vet_content(content_data)

            vetting_results.append({
                'script_id': script.get('id'),
                'safety_score': safety_analysis.overall_safety_score,
                'brand_alignment_score': safety_analysis.brand_alignment_score,
                'requires_human_review': safety_analysis.requires_human_review,
                'risk_flags': safety_analysis.risk_flags,
                'recommendations': safety_analysis.recommendations
            })

        # Filter safe content
        safe_scripts = [r for r in vetting_results if r['safety_score'] > 0.7 and not r['requires_human_review']]

        return {
            'scripts_vetted': len(vetting_results),
            'safe_scripts_count': len(safe_scripts),
            'flagged_scripts_count': len(vetting_results) - len(safe_scripts),
            'vetting_results': vetting_results
        }

    async def _run_advanced_video_generation(self) -> Dict:
        """Run advanced video generation with shot orchestration"""
        # Get safe scripts from previous stage
        safe_scripts = self.pipeline_state['results'].get('brand_safety_vetting', {}).get('safe_scripts', [])

        if not safe_scripts:
            return {'error': 'No safe scripts available for video generation'}

        video_generation_results = []

        for script_result in safe_scripts[:1]:  # Generate video for top safe script
            # Get script content
            script_content = next(
                (s['content'] for s in self.pipeline_state['results']['intelligent_story_ideation']['enhanced_scripts']
                 if s['id'] == script_result['script_id']),
                'Default script content'
            )

            # Prepare script data for video generation
            script_data = {
                'script': script_content,
                'topic': 'trending',
                'tone': 'engaging'
            }

            # Generate video using advanced orchestrator
            video_package = await self.video_orchestrator.orchestrate_video_creation(
                script_data, target_platform='tiktok'
            )

            video_generation_results.append({
                'script_id': script_result['script_id'],
                'video_path': video_package.get('video_path', ''),
                'storyboard_shots': len(video_package.get('storyboard', {}).get('shots', [])),
                'total_duration': video_package.get('metadata', {}).get('total_duration', 0),
                'generation_success': bool(video_package.get('video_path'))
            })

        return {
            'videos_generated': len(video_generation_results),
            'generation_results': video_generation_results
        }

    async def _run_strategy_optimization(self) -> Dict:
        """Run strategy learning and optimization"""
        # Get performance data from current pipeline run
        performance_data = {
            'content_id': self.pipeline_state['current_run_id'],
            'metrics': {
                'trends_analyzed': self.pipeline_state['results'].get('enhanced_trend_discovery', {}).get('enhanced_trends_count', 0),
                'scripts_generated': self.pipeline_state['results'].get('intelligent_story_ideation', {}).get('scripts_generated', 0),
                'safe_content_rate': (
                    self.pipeline_state['results'].get('brand_safety_vetting', {}).get('safe_scripts_count', 0) /
                    max(self.pipeline_state['results'].get('brand_safety_vetting', {}).get('scripts_vetted', 1), 1)
                ),
                'videos_generated': self.pipeline_state['results'].get('advanced_video_generation', {}).get('videos_generated', 0)
            },
            'metadata': {
                'strategy': 'enhanced_pipeline',
                'platform': 'tiktok',
                'experiment_id': None,
                'variant_id': None
            }
        }

        # Process performance feedback
        reward_signal = await self.strategy_engine.process_performance_feedback(
            content_id=performance_data['content_id'],
            metrics=performance_data['metrics'],
            content_metadata=performance_data['metadata']
        )

        # Get strategy recommendations
        strategy_recommendations = self.strategy_engine.get_strategy_recommendations()

        return {
            'reward_signal': reward_signal.total_reward,
            'strategy_performance': strategy_recommendations,
            'learning_progress': strategy_recommendations.get('learning_progress', {})
        }

    async def _run_documentation(self) -> Dict:
        """Run enhanced documentation and versioning"""
        # Compile comprehensive system data
        system_data = {
            'overview': 'Enhanced AVVO pipeline run completed successfully',
            'pipeline_run': {
                'run_id': self.pipeline_state['current_run_id'],
                'duration': self.pipeline_state['start_time'],
                'stages_completed': len(self.pipeline_state['results']),
                'errors': len(self.pipeline_state['errors'])
            },
            'agent_performance': {
                'predictive_intelligence': self.pipeline_state['results'].get('predictive_intelligence', {}),
                'trend_discovery': self.pipeline_state['results'].get('enhanced_trend_discovery', {}),
                'story_ideation': self.pipeline_state['results'].get('intelligent_story_ideation', {}),
                'brand_safety': self.pipeline_state['results'].get('brand_safety_vetting', {}),
                'video_generation': self.pipeline_state['results'].get('advanced_video_generation', {}),
                'strategy_optimization': self.pipeline_state['results'].get('strategy_optimization', {})
            },
            'system_capabilities': [
                'Predictive Intelligence & Anomaly Detection',
                'Reinforcement & Strategy Engine',
                'Brand Safety & Ethical Guardian',
                'Dynamic Shot & Composition Orchestrator'
            ]
        }

        # Generate comprehensive documentation
        docs = self.doc_agent.generate_docs(system_data)

        # Update version control
        version_message = f"Enhanced AVVO pipeline run {self.pipeline_state['current_run_id']} completed"
        self.doc_agent.version_control(version_message)

        return {
            'documentation_generated': True,
            'version_control_updated': True,
            'system_data_summary': {
                'total_agents': 7,  # Including new agents
                'expert_features': 4,
                'pipeline_stages': len(self.pipeline_state['results'])
            }
        }

    def _enhance_trends_with_predictive_insights(self, traditional_trends: List, predictive_results: Dict) -> List:
        """Enhance traditional trends with predictive insights"""
        enhanced_trends = []

        for trend in traditional_trends:
            # Add predictive insights
            trend['predictive_insights'] = {
                'forecasts': predictive_results.get('forecasts', []),
                'anomalies': predictive_results.get('anomalies', []),
                'arbitrage_opportunities': predictive_results.get('arbitrage_opportunities', [])
            }

            # Calculate breakout potential
            trend['breakout_potential'] = self._calculate_breakout_potential(trend, predictive_results)

            enhanced_trends.append(trend)

        return enhanced_trends

    def _calculate_breakout_potential(self, trend: Dict, predictive_results: Dict) -> float:
        """Calculate breakout potential for a trend"""
        score = 0.5  # Base score

        # Factor in anomaly detection
        anomalies = predictive_results.get('anomalies', [])
        trend_anomalies = [a for a in anomalies if a.keyword in trend.get('summary', '')]
        if trend_anomalies:
            score += 0.3

        # Factor in forecasts
        forecasts = predictive_results.get('forecasts', [])
        trend_forecasts = [f for f in forecasts if f.keyword in trend.get('summary', '')]
        if trend_forecasts:
            # Higher confidence forecasts increase breakout potential
            avg_confidence = sum(f.confidence_score for f in trend_forecasts) / len(trend_forecasts)
            score += avg_confidence * 0.2

        return min(1.0, score)

    def _select_optimal_trends(self, enhanced_trends: List) -> List:
        """Select optimal trends for content creation"""
        # Sort by breakout potential and return top trends
        sorted_trends = sorted(enhanced_trends, key=lambda x: x.get('breakout_potential', 0), reverse=True)
        return sorted_trends[:3]  # Return top 3 trends

    def _enhance_scripts_with_strategy(self, scripts: List, strategy: Dict) -> List:
        """Enhance scripts with optimal creative strategy"""
        enhanced_scripts = []

        for script in scripts:
            enhanced_script = script.copy()
            enhanced_script['creative_strategy'] = strategy
            enhanced_script['strategy_enhancements'] = {
                'voiceover_style': strategy.get('voiceover_style', 'energetic_young'),
                'music_genre': strategy.get('music_genre', 'electronic_upbeat'),
                'narrative_structure': strategy.get('narrative_structure', 'storytelling'),
                'visual_style': strategy.get('visual_style', 'modern')
            }
            enhanced_scripts.append(enhanced_script)

        return enhanced_scripts

    def get_pipeline_status(self) -> Dict:
        """Get current pipeline status"""
        return {
            'current_run_id': self.pipeline_state['current_run_id'],
            'current_stage': self.pipeline_state['current_stage'],
            'start_time': self.pipeline_state['start_time'],
            'stages_completed': len(self.pipeline_state['results']),
            'total_stages': 7,
            'errors_count': len(self.pipeline_state['errors']),
            'progress_percentage': (len(self.pipeline_state['results']) / 7) * 100
        }

# Backward compatibility - keep original Orchestrator class
class Orchestrator(EnhancedOrchestrator):
    """Backward compatibility wrapper"""

    async def run_pipeline(self):
        """Legacy pipeline method"""
        return await self.run_enhanced_pipeline()