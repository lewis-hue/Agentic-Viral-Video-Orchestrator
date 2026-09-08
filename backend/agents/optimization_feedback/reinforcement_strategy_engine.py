import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import hashlib
import random
from enum import Enum
import statistics

try:
    import vowpal_wabbit
    VOWPAL_WABBIT_AVAILABLE = True
except ImportError:
    VOWPAL_WABBIT_AVAILABLE = False

class CreativeVariable(Enum):
    """Enumeration of creative variables for A/B testing"""
    VOICEOVER_STYLE = "voiceover_style"
    MUSIC_GENRE = "music_genre"
    VIDEO_PACING = "video_pacing"
    NARRATIVE_STRUCTURE = "narrative_structure"
    OPENING_HOOK = "opening_hook"
    CALL_TO_ACTION = "call_to_action"
    VISUAL_STYLE = "visual_style"
    CONTENT_LENGTH = "content_length"

@dataclass
class ExperimentVariant:
    """Data class for A/B test variants"""
    variant_id: str
    creative_variables: Dict[CreativeVariable, Any]
    traffic_allocation: float
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    impression_count: int = 0
    conversion_count: int = 0

@dataclass
class ContextualBanditArm:
    """Data class for contextual bandit arms"""
    arm_id: str
    context_features: Dict[str, float]
    reward_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    pull_count: int = 0
    total_reward: float = 0
    average_reward: float = 0.0

@dataclass
class RewardSignal:
    """Data class for sophisticated reward modeling"""
    base_reward: float
    engagement_bonus: float
    retention_bonus: float
    virality_bonus: float
    brand_alignment_score: float
    total_reward: float
    timestamp: datetime
    content_id: str

class ContextualBandit:
    """
    Implementation of contextual multi-armed bandit for creative optimization
    """

    def __init__(self, n_arms: int = 10, epsilon: float = 0.1, decay_rate: float = 0.99):
        self.n_arms = n_arms
        self.epsilon = epsilon  # Exploration rate
        self.decay_rate = decay_rate
        self.arms = {}
        self.context_history = []
        self.reward_history = []

        # Upper Confidence Bound parameters
        self.ucb_c = 1.0
        self.total_pulls = 0

        # Initialize arms
        for i in range(n_arms):
            self.arms[f"arm_{i}"] = ContextualBanditArm(
                arm_id=f"arm_{i}",
                context_features={}
            )

    def _extract_context_features(self, context: Dict) -> Dict[str, float]:
        """Extract numerical features from context"""
        features = {}

        # Content features
        if 'topic_category' in context:
            features['topic_tech'] = 1.0 if context['topic_category'] == 'technology' else 0.0
            features['topic_entertainment'] = 1.0 if context['topic_category'] == 'entertainment' else 0.0
            features['topic_education'] = 1.0 if context['topic_category'] == 'education' else 0.0

        # Platform features
        if 'platform' in context:
            features['platform_tiktok'] = 1.0 if context['platform'] == 'tiktok' else 0.0
            features['platform_youtube'] = 1.0 if context['platform'] == 'youtube' else 0.0
            features['platform_twitter'] = 1.0 if context['platform'] == 'twitter' else 0.0

        # Temporal features
        if 'hour' in context:
            features['hour_sin'] = np.sin(2 * np.pi * context['hour'] / 24)
            features['hour_cos'] = np.cos(2 * np.pi * context['hour'] / 24)

        if 'day_of_week' in context:
            features['day_sin'] = np.sin(2 * np.pi * context['day_of_week'] / 7)
            features['day_cos'] = np.cos(2 * np.pi * context['day_of_week'] / 7)

        # Historical performance features
        if 'past_performance' in context:
            features['avg_views'] = context['past_performance'].get('avg_views', 0)
            features['avg_engagement'] = context['past_performance'].get('avg_engagement', 0)

        return features

    def select_arm(self, context: Dict) -> str:
        """Select arm using epsilon-greedy with UCB"""
        features = self._extract_context_features(context)

        # Epsilon-greedy exploration
        if np.random.random() < self.epsilon:
            # Explore: random arm
            selected_arm = np.random.choice(list(self.arms.keys()))
        else:
            # Exploit: use UCB to select best arm
            best_arm = None
            best_ucb = -float('inf')

            for arm_id, arm in self.arms.items():
                if arm.pull_count == 0:
                    ucb_value = float('inf')  # Always try untested arms
                else:
                    # UCB formula
                    confidence = self.ucb_c * np.sqrt(np.log(self.total_pulls) / arm.pull_count)
                    ucb_value = arm.average_reward + confidence

                if ucb_value > best_ucb:
                    best_ucb = ucb_value
                    best_arm = arm_id

            selected_arm = best_arm

        # Update arm context and pull count
        self.arms[selected_arm].context_features = features
        self.arms[selected_arm].pull_count += 1
        self.total_pulls += 1

        return selected_arm

    def update_reward(self, arm_id: str, reward: float):
        """Update arm with received reward"""
        if arm_id in self.arms:
            arm = self.arms[arm_id]
            arm.reward_history.append(reward)
            arm.total_reward += reward
            arm.pull_count += 1
            arm.average_reward = arm.total_reward / arm.pull_count

            # Store in history
            self.reward_history.append({
                'arm_id': arm_id,
                'reward': reward,
                'timestamp': datetime.now()
            })

    def get_arm_performance(self) -> Dict:
        """Get performance statistics for all arms"""
        performance = {}

        for arm_id, arm in self.arms.items():
            if arm.pull_count > 0:
                performance[arm_id] = {
                    'pull_count': arm.pull_count,
                    'average_reward': arm.average_reward,
                    'total_reward': arm.total_reward,
                    'recent_performance': list(arm.reward_history)[-10:]  # Last 10 rewards
                }

        return performance

class ABTestManager:
    """
    Manages automated A/B testing for creative variables
    """

    def __init__(self):
        self.active_experiments = {}
        self.completed_experiments = []
        self.variant_performance = defaultdict(dict)

    def create_experiment(self, experiment_name: str, variants: List[ExperimentVariant],
                         traffic_split: List[float] = None) -> str:
        """Create a new A/B test experiment"""
        experiment_id = hashlib.md5(f"{experiment_name}_{datetime.now()}".encode()).hexdigest()

        if traffic_split is None:
            # Equal traffic split by default
            traffic_split = [1.0 / len(variants)] * len(variants)

        # Normalize traffic allocation
        total_traffic = sum(traffic_split)
        normalized_allocation = [split / total_traffic for split in traffic_split]

        # Create variants with normalized allocation
        experiment_variants = []
        for i, variant in enumerate(variants):
            variant.traffic_allocation = normalized_allocation[i]
            variant.variant_id = f"{experiment_id}_variant_{i}"
            experiment_variants.append(variant)

        self.active_experiments[experiment_id] = {
            'name': experiment_name,
            'variants': experiment_variants,
            'start_time': datetime.now(),
            'status': 'active'
        }

        return experiment_id

    def assign_variant(self, experiment_id: str, context: Dict) -> Optional[ExperimentVariant]:
        """Assign user to experiment variant based on traffic allocation"""
        if experiment_id not in self.active_experiments:
            return None

        experiment = self.active_experiments[experiment_id]
        variants = experiment['variants']

        # Simple random assignment based on traffic allocation
        rand = np.random.random()
        cumulative_prob = 0.0

        for variant in variants:
            cumulative_prob += variant.traffic_allocation
            if rand <= cumulative_prob:
                variant.impression_count += 1
                return variant

        # Fallback to first variant
        variants[0].impression_count += 1
        return variants[0]

    def record_conversion(self, experiment_id: str, variant_id: str, reward_signal: RewardSignal):
        """Record conversion event for variant"""
        if experiment_id not in self.active_experiments:
            return

        experiment = self.active_experiments[experiment_id]
        for variant in experiment['variants']:
            if variant.variant_id == variant_id:
                variant.conversion_count += 1
                variant.performance_metrics = self._update_performance_metrics(
                    variant.performance_metrics, reward_signal
                )
                break

    def _update_performance_metrics(self, current_metrics: Dict, reward_signal: RewardSignal) -> Dict:
        """Update performance metrics with new reward signal"""
        updated_metrics = current_metrics.copy()

        # Calculate running averages
        if 'total_reward' not in updated_metrics:
            updated_metrics['total_reward'] = 0
            updated_metrics['count'] = 0

        updated_metrics['total_reward'] += reward_signal.total_reward
        updated_metrics['count'] += 1
        updated_metrics['average_reward'] = updated_metrics['total_reward'] / updated_metrics['count']

        # Track recent performance (last 100 samples)
        if 'recent_rewards' not in updated_metrics:
            updated_metrics['recent_rewards'] = deque(maxlen=100)

        updated_metrics['recent_rewards'].append(reward_signal.total_reward)
        updated_metrics['recent_average'] = sum(updated_metrics['recent_rewards']) / len(updated_metrics['recent_rewards'])

        return updated_metrics

    def get_experiment_results(self, experiment_id: str) -> Dict:
        """Get results for completed experiment"""
        if experiment_id not in self.active_experiments:
            return {}

        experiment = self.active_experiments[experiment_id]
        variants = experiment['variants']

        results = {
            'experiment_id': experiment_id,
            'experiment_name': experiment['name'],
            'start_time': experiment['start_time'],
            'duration': datetime.now() - experiment['start_time'],
            'variants': []
        }

        for variant in variants:
            variant_results = {
                'variant_id': variant.variant_id,
                'creative_variables': variant.creative_variables,
                'traffic_allocation': variant.traffic_allocation,
                'impressions': variant.impression_count,
                'conversions': variant.conversion_count,
                'conversion_rate': variant.conversion_count / max(variant.impression_count, 1),
                'performance_metrics': variant.performance_metrics
            }
            results['variants'].append(variant_results)

        return results

class RewardModel:
    """
    Sophisticated reward modeling for content optimization
    """

    def __init__(self):
        self.weights = {
            'view_duration': 0.3,
            'engagement_rate': 0.25,
            'virality_score': 0.2,
            'brand_alignment': 0.15,
            'retention_score': 0.1
        }

        self.performance_history = deque(maxlen=10000)

    def calculate_reward(self, metrics: Dict, content_metadata: Dict) -> RewardSignal:
        """Calculate sophisticated reward signal from performance metrics"""

        # Base engagement metrics
        views = metrics.get('views', 0)
        likes = metrics.get('likes', 0)
        comments = metrics.get('comments', 0)
        shares = metrics.get('shares', 0)
        watch_time = metrics.get('watch_time', 0)
        content_length = content_metadata.get('length_seconds', 60)

        # Calculate component scores
        engagement_rate = (likes + comments + shares) / max(views, 1)
        view_duration_rate = watch_time / max(content_length, 1)
        virality_score = self._calculate_virality_score(metrics)
        retention_score = self._calculate_retention_score(metrics, content_length)
        brand_alignment_score = content_metadata.get('brand_alignment_score', 0.5)

        # Weighted reward components
        base_reward = engagement_rate * 100  # Normalize to 0-100 scale
        engagement_bonus = min(engagement_rate * 50, 25)  # Cap at 25
        retention_bonus = view_duration_rate * 20  # Up to 20 points
        virality_bonus = min(virality_score * 30, 30)  # Cap at 30
        brand_bonus = brand_alignment_score * 15  # Up to 15 points

        total_reward = (
            base_reward +
            engagement_bonus +
            retention_bonus +
            virality_bonus +
            brand_bonus
        )

        return RewardSignal(
            base_reward=base_reward,
            engagement_bonus=engagement_bonus,
            retention_bonus=retention_bonus,
            virality_bonus=virality_bonus,
            brand_alignment_score=brand_alignment_score,
            total_reward=total_reward,
            timestamp=datetime.now(),
            content_id=content_metadata.get('content_id', 'unknown')
        )

    def _calculate_virality_score(self, metrics: Dict) -> float:
        """Calculate how viral the content is"""
        try:
            shares = metrics.get('shares', 0)
            views = metrics.get('views', 1)

            # Virality ratio (shares per view)
            virality_ratio = shares / views

            # Normalize to 0-1 scale (typical viral content gets 0.01-0.05 shares per view)
            normalized_score = min(virality_ratio / 0.05, 1.0)

            return normalized_score

        except:
            return 0.0

    def _calculate_retention_score(self, metrics: Dict, content_length: int) -> float:
        """Calculate content retention score"""
        try:
            watch_time = metrics.get('watch_time', 0)
            views = metrics.get('views', 1)

            # Average watch time per view
            avg_watch_time = watch_time / views

            # Retention rate (how much of content is watched on average)
            retention_rate = avg_watch_time / content_length

            # Boost for longer content that retains well
            if content_length > 30:  # Longer than 30 seconds
                retention_rate *= 1.2

            return min(retention_rate, 1.0)

        except:
            return 0.0

class ReinforcementStrategyEngine:
    """
    Main engine that combines contextual bandits, A/B testing, and sophisticated reward modeling
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.contextual_bandit = ContextualBandit(
            n_arms=self.config.get('n_bandit_arms', 10),
            epsilon=self.config.get('exploration_rate', 0.1)
        )

        self.ab_test_manager = ABTestManager()
        self.reward_model = RewardModel()

        # Strategy state
        self.current_strategy = {}
        self.strategy_performance = defaultdict(list)
        self.learning_history = []

        # Creative variable options
        self.creative_options = self._initialize_creative_options()

    def _initialize_creative_options(self) -> Dict[CreativeVariable, List[Any]]:
        """Initialize possible values for each creative variable"""
        return {
            CreativeVariable.VOICEOVER_STYLE: [
                "energetic", "calm", "professional", "casual", "enthusiastic",
                "authoritative", "friendly", "dramatic"
            ],
            CreativeVariable.MUSIC_GENRE: [
                "electronic", "pop", "hip_hop", "classical", "ambient",
                "rock", "jazz", "folk", "orchestral"
            ],
            CreativeVariable.VIDEO_PACING: [
                "fast", "moderate", "slow", "variable"
            ],
            CreativeVariable.NARRATIVE_STRUCTURE: [
                "storytelling", "tutorial", "listicle", "interview",
                "documentary", "review", "comparison"
            ],
            CreativeVariable.OPENING_HOOK: [
                "question", "statistic", "story", "controversial_statement",
                "surprise", "humor", "pain_point"
            ],
            CreativeVariable.CALL_TO_ACTION: [
                "subscribe", "comment", "share", "visit_link", "follow",
                "save", "like", "tag_friend"
            ],
            CreativeVariable.VISUAL_STYLE: [
                "minimalist", "colorful", "vintage", "modern", "artistic",
                "corporate", "trendy", "classic"
            ],
            CreativeVariable.CONTENT_LENGTH: [
                "15s", "30s", "60s", "90s", "2min", "3min"
            ]
        }

    async def select_optimal_strategy(self, context: Dict) -> Dict[CreativeVariable, Any]:
        """Select optimal creative strategy using contextual bandits"""
        try:
            # Use contextual bandit to select strategy
            arm_id = self.contextual_bandit.select_arm(context)

            # Convert arm selection to creative variables
            strategy = self._arm_to_strategy(arm_id, context)

            # Store current strategy for tracking
            self.current_strategy = {
                'arm_id': arm_id,
                'strategy': strategy,
                'context': context,
                'timestamp': datetime.now()
            }

            return strategy

        except Exception as e:
            self.logger.error(f"Error selecting optimal strategy: {e}")
            return self._get_default_strategy()

    def _arm_to_strategy(self, arm_id: str, context: Dict) -> Dict[CreativeVariable, Any]:
        """Convert bandit arm selection to creative strategy"""
        # Use arm_id as seed for reproducible strategy selection
        random.seed(hash(arm_id + str(context.get('topic', ''))))

        strategy = {}
        for variable in CreativeVariable:
            options = self.creative_options[variable]
            strategy[variable] = random.choice(options)

        return strategy

    async def run_automated_ab_test(self, base_strategy: Dict, context: Dict) -> str:
        """Create and run automated A/B test for strategy optimization"""
        try:
            # Generate variants based on base strategy
            variants = []

            # Control variant (original strategy)
            control_variant = ExperimentVariant(
                variant_id="control",
                creative_variables=base_strategy,
                traffic_allocation=0.5
            )
            variants.append(control_variant)

            # Generate test variants by modifying creative variables
            for i in range(3):  # Create 3 test variants
                test_strategy = self._generate_variant_strategy(base_strategy, i)
                variant = ExperimentVariant(
                    variant_id=f"variant_{i}",
                    creative_variables=test_strategy,
                    traffic_allocation=1/6  # Equal split for 3 variants + control
                )
                variants.append(variant)

            # Create experiment
            experiment_name = f"strategy_test_{context.get('topic', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            experiment_id = self.ab_test_manager.create_experiment(experiment_name, variants)

            return experiment_id

        except Exception as e:
            self.logger.error(f"Error creating A/B test: {e}")
            return ""

    def _generate_variant_strategy(self, base_strategy: Dict, variant_index: int) -> Dict:
        """Generate a variant strategy by modifying base strategy"""
        variant_strategy = base_strategy.copy()

        # Modify different variables based on variant index
        modifications = {
            0: [CreativeVariable.VOICEOVER_STYLE, CreativeVariable.MUSIC_GENRE],
            1: [CreativeVariable.VIDEO_PACING, CreativeVariable.OPENING_HOOK],
            2: [CreativeVariable.NARRATIVE_STRUCTURE, CreativeVariable.CALL_TO_ACTION]
        }

        variables_to_modify = modifications.get(variant_index, [CreativeVariable.VISUAL_STYLE])

        for variable in variables_to_modify:
            options = self.creative_options[variable]
            current_value = variant_strategy.get(variable)

            # Select different option from current
            available_options = [opt for opt in options if opt != current_value]
            if available_options:
                variant_strategy[variable] = np.random.choice(available_options)

        return variant_strategy

    async def process_performance_feedback(self, content_id: str, metrics: Dict,
                                         content_metadata: Dict) -> RewardSignal:
        """Process performance feedback and update learning models"""
        try:
            # Calculate sophisticated reward signal
            reward_signal = self.reward_model.calculate_reward(metrics, content_metadata)

            # Update contextual bandit with reward
            if hasattr(self, 'current_strategy') and self.current_strategy.get('content_id') == content_id:
                arm_id = self.current_strategy['arm_id']
                self.contextual_bandit.update_reward(arm_id, reward_signal.total_reward)

            # Update A/B test results if applicable
            experiment_id = content_metadata.get('experiment_id')
            if experiment_id:
                variant_id = content_metadata.get('variant_id')
                if variant_id:
                    self.ab_test_manager.record_conversion(experiment_id, variant_id, reward_signal)

            # Store performance data
            self.performance_history.append({
                'content_id': content_id,
                'reward_signal': reward_signal,
                'metrics': metrics,
                'metadata': content_metadata,
                'timestamp': datetime.now()
            })

            # Update strategy performance tracking
            self._update_strategy_performance(reward_signal, content_metadata)

            return reward_signal

        except Exception as e:
            self.logger.error(f"Error processing performance feedback: {e}")
            # Return default reward signal
            return RewardSignal(
                base_reward=0, engagement_bonus=0, retention_bonus=0,
                virality_bonus=0, brand_alignment_score=0.5, total_reward=0,
                timestamp=datetime.now(), content_id=content_id
            )

    def _update_strategy_performance(self, reward_signal: RewardSignal, content_metadata: Dict):
        """Update strategy performance tracking"""
        strategy_key = str(content_metadata.get('strategy', {}))

        if strategy_key not in self.strategy_performance:
            self.strategy_performance[strategy_key] = []

        self.strategy_performance[strategy_key].append(reward_signal.total_reward)

        # Keep only recent performance data (last 100 samples per strategy)
        if len(self.strategy_performance[strategy_key]) > 100:
            self.strategy_performance[strategy_key] = self.strategy_performance[strategy_key][-100:]

    def get_strategy_recommendations(self) -> Dict:
        """Get current strategy recommendations based on learning"""
        try:
            # Get best performing arms from contextual bandit
            bandit_performance = self.contextual_bandit.get_arm_performance()

            # Get best performing strategies from A/B tests
            ab_test_results = {}
            for exp_id, experiment in self.ab_test_manager.active_experiments.items():
                results = self.ab_test_manager.get_experiment_results(exp_id)
                ab_test_results[exp_id] = results

            # Calculate overall strategy performance
            strategy_stats = {}
            for strategy_key, rewards in self.strategy_performance.items():
                if rewards:
                    strategy_stats[strategy_key] = {
                        'average_reward': statistics.mean(rewards),
                        'reward_std': statistics.stdev(rewards) if len(rewards) > 1 else 0,
                        'sample_count': len(rewards),
                        'recent_performance': rewards[-10:] if len(rewards) >= 10 else rewards
                    }

            return {
                'bandit_performance': bandit_performance,
                'ab_test_results': ab_test_results,
                'strategy_statistics': strategy_stats,
                'learning_progress': {
                    'total_interactions': len(self.performance_history),
                    'unique_strategies': len(self.strategy_performance),
                    'exploration_rate': self.contextual_bandit.epsilon
                },
                'timestamp': datetime.now()
            }

        except Exception as e:
            self.logger.error(f"Error getting strategy recommendations: {e}")
            return {}

    def _get_default_strategy(self) -> Dict[CreativeVariable, Any]:
        """Get default creative strategy when learning fails"""
        return {
            CreativeVariable.VOICEOVER_STYLE: "enthusiastic",
            CreativeVariable.MUSIC_GENRE: "electronic",
            CreativeVariable.VIDEO_PACING: "moderate",
            CreativeVariable.NARRATIVE_STRUCTURE: "storytelling",
            CreativeVariable.OPENING_HOOK: "question",
            CreativeVariable.CALL_TO_ACTION: "subscribe",
            CreativeVariable.VISUAL_STYLE: "modern",
            CreativeVariable.CONTENT_LENGTH: "60s"
        }