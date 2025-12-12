"""
AppleTrader Pro - Subscription Plans Configuration
Defines all subscription tiers, features, and pricing
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class PlanTier(str, Enum):
    """Subscription plan tiers"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ELITE = "elite"


class BillingPeriod(str, Enum):
    """Billing cycle periods"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


@dataclass
class PlanFeatures:
    """Features available in each plan tier"""
    # Trading Features
    max_symbols: int  # Maximum symbols to trade simultaneously
    max_daily_trades: int  # Maximum trades per day
    max_position_size: float  # Maximum position size in lots

    # Filters & Analysis
    basic_filters: bool  # Trend, HTF alignment, market structure
    advanced_filters: bool  # Volume, session, news, volatility
    institutional_filters: bool  # Correlation, regime, confluence

    # Pattern Recognition
    basic_patterns: bool  # Double tops/bottoms, H&S
    advanced_patterns: bool  # Triangles, wedges, channels

    # Smart Money Concepts
    fair_value_gaps: bool
    order_blocks: bool
    liquidity_zones: bool

    # ML Features
    ml_predictions: bool
    ml_pattern_scoring: bool
    ml_custom_models: bool

    # Additional Features
    multi_timeframe_analysis: bool
    correlation_heatmap: bool
    volatility_position_sizing: bool
    session_momentum_scanner: bool
    order_flow_footprint: bool
    risk_reward_optimizer: bool
    equity_curve_analyzer: bool
    automated_trade_journal: bool
    ai_trade_insights: bool
    news_impact_predictor: bool

    # Support & Limits
    support_level: str  # "community", "email", "priority", "dedicated"
    api_access: bool
    custom_indicators: bool
    data_export: bool
    backtesting_years: int


@dataclass
class PlanPricing:
    """Pricing information for a plan"""
    tier: PlanTier
    name: str
    description: str
    monthly_price: float
    quarterly_price: float  # Total for 3 months
    annual_price: float  # Total for 12 months
    currency: str = "USD"
    stripe_monthly_price_id: Optional[str] = None
    stripe_quarterly_price_id: Optional[str] = None
    stripe_annual_price_id: Optional[str] = None

    @property
    def quarterly_monthly_equivalent(self) -> float:
        """Monthly equivalent price for quarterly billing"""
        return self.quarterly_price / 3

    @property
    def annual_monthly_equivalent(self) -> float:
        """Monthly equivalent price for annual billing"""
        return self.annual_price / 12

    @property
    def quarterly_discount_pct(self) -> float:
        """Discount percentage for quarterly vs monthly"""
        if self.monthly_price == 0:
            return 0.0
        return (1 - (self.quarterly_monthly_equivalent / self.monthly_price)) * 100

    @property
    def annual_discount_pct(self) -> float:
        """Discount percentage for annual vs monthly"""
        if self.monthly_price == 0:
            return 0.0
        return (1 - (self.annual_monthly_equivalent / self.monthly_price)) * 100


# Define features for each plan tier
PLAN_FEATURES: Dict[PlanTier, PlanFeatures] = {
    PlanTier.FREE: PlanFeatures(
        # Trading Features
        max_symbols=1,
        max_daily_trades=3,
        max_position_size=0.1,

        # Filters & Analysis
        basic_filters=True,
        advanced_filters=False,
        institutional_filters=False,

        # Pattern Recognition
        basic_patterns=True,
        advanced_patterns=False,

        # Smart Money Concepts
        fair_value_gaps=True,
        order_blocks=False,
        liquidity_zones=False,

        # ML Features
        ml_predictions=False,
        ml_pattern_scoring=False,
        ml_custom_models=False,

        # Additional Features
        multi_timeframe_analysis=False,
        correlation_heatmap=False,
        volatility_position_sizing=False,
        session_momentum_scanner=False,
        order_flow_footprint=False,
        risk_reward_optimizer=False,
        equity_curve_analyzer=False,
        automated_trade_journal=False,
        ai_trade_insights=False,
        news_impact_predictor=False,

        # Support & Limits
        support_level="community",
        api_access=False,
        custom_indicators=False,
        data_export=False,
        backtesting_years=1,
    ),

    PlanTier.BASIC: PlanFeatures(
        # Trading Features
        max_symbols=3,
        max_daily_trades=10,
        max_position_size=1.0,

        # Filters & Analysis
        basic_filters=True,
        advanced_filters=True,
        institutional_filters=False,

        # Pattern Recognition
        basic_patterns=True,
        advanced_patterns=True,

        # Smart Money Concepts
        fair_value_gaps=True,
        order_blocks=True,
        liquidity_zones=False,

        # ML Features
        ml_predictions=True,
        ml_pattern_scoring=False,
        ml_custom_models=False,

        # Additional Features
        multi_timeframe_analysis=True,
        correlation_heatmap=True,
        volatility_position_sizing=True,
        session_momentum_scanner=False,
        order_flow_footprint=False,
        risk_reward_optimizer=True,
        equity_curve_analyzer=True,
        automated_trade_journal=True,
        ai_trade_insights=False,
        news_impact_predictor=False,

        # Support & Limits
        support_level="email",
        api_access=False,
        custom_indicators=False,
        data_export=True,
        backtesting_years=3,
    ),

    PlanTier.PRO: PlanFeatures(
        # Trading Features
        max_symbols=10,
        max_daily_trades=50,
        max_position_size=10.0,

        # Filters & Analysis
        basic_filters=True,
        advanced_filters=True,
        institutional_filters=True,

        # Pattern Recognition
        basic_patterns=True,
        advanced_patterns=True,

        # Smart Money Concepts
        fair_value_gaps=True,
        order_blocks=True,
        liquidity_zones=True,

        # ML Features
        ml_predictions=True,
        ml_pattern_scoring=True,
        ml_custom_models=False,

        # Additional Features
        multi_timeframe_analysis=True,
        correlation_heatmap=True,
        volatility_position_sizing=True,
        session_momentum_scanner=True,
        order_flow_footprint=True,
        risk_reward_optimizer=True,
        equity_curve_analyzer=True,
        automated_trade_journal=True,
        ai_trade_insights=True,
        news_impact_predictor=True,

        # Support & Limits
        support_level="priority",
        api_access=True,
        custom_indicators=True,
        data_export=True,
        backtesting_years=5,
    ),

    PlanTier.ELITE: PlanFeatures(
        # Trading Features
        max_symbols=999,  # Unlimited
        max_daily_trades=999,  # Unlimited
        max_position_size=100.0,

        # Filters & Analysis
        basic_filters=True,
        advanced_filters=True,
        institutional_filters=True,

        # Pattern Recognition
        basic_patterns=True,
        advanced_patterns=True,

        # Smart Money Concepts
        fair_value_gaps=True,
        order_blocks=True,
        liquidity_zones=True,

        # ML Features
        ml_predictions=True,
        ml_pattern_scoring=True,
        ml_custom_models=True,

        # Additional Features
        multi_timeframe_analysis=True,
        correlation_heatmap=True,
        volatility_position_sizing=True,
        session_momentum_scanner=True,
        order_flow_footprint=True,
        risk_reward_optimizer=True,
        equity_curve_analyzer=True,
        automated_trade_journal=True,
        ai_trade_insights=True,
        news_impact_predictor=True,

        # Support & Limits
        support_level="dedicated",
        api_access=True,
        custom_indicators=True,
        data_export=True,
        backtesting_years=10,
    ),
}


# Define pricing for each plan tier
PLAN_PRICING: Dict[PlanTier, PlanPricing] = {
    PlanTier.FREE: PlanPricing(
        tier=PlanTier.FREE,
        name="Free Trial",
        description="Perfect for getting started with basic trading features",
        monthly_price=0.00,
        quarterly_price=0.00,
        annual_price=0.00,
    ),

    PlanTier.BASIC: PlanPricing(
        tier=PlanTier.BASIC,
        name="Basic",
        description="Essential tools for serious traders",
        monthly_price=49.99,
        quarterly_price=134.99,  # 10% discount
        annual_price=499.99,  # 17% discount
        stripe_monthly_price_id="price_basic_monthly",
        stripe_quarterly_price_id="price_basic_quarterly",
        stripe_annual_price_id="price_basic_annual",
    ),

    PlanTier.PRO: PlanPricing(
        tier=PlanTier.PRO,
        name="Pro",
        description="Advanced features for professional traders",
        monthly_price=149.99,
        quarterly_price=404.99,  # 10% discount
        annual_price=1499.99,  # 17% discount
        stripe_monthly_price_id="price_pro_monthly",
        stripe_quarterly_price_id="price_pro_quarterly",
        stripe_annual_price_id="price_pro_annual",
    ),

    PlanTier.ELITE: PlanPricing(
        tier=PlanTier.ELITE,
        name="Elite",
        description="Unlimited access with dedicated support for institutional traders",
        monthly_price=499.99,
        quarterly_price=1349.99,  # 10% discount
        annual_price=4999.99,  # 17% discount
        stripe_monthly_price_id="price_elite_monthly",
        stripe_quarterly_price_id="price_elite_quarterly",
        stripe_annual_price_id="price_elite_annual",
    ),
}


def get_plan_features(tier: PlanTier) -> PlanFeatures:
    """Get features for a specific plan tier"""
    return PLAN_FEATURES[tier]


def get_plan_pricing(tier: PlanTier) -> PlanPricing:
    """Get pricing for a specific plan tier"""
    return PLAN_PRICING[tier]


def get_all_plans() -> List[Dict]:
    """Get all plans with features and pricing combined"""
    plans = []
    for tier in PlanTier:
        features = get_plan_features(tier)
        pricing = get_plan_pricing(tier)
        plans.append({
            'tier': tier.value,
            'pricing': pricing,
            'features': features,
        })
    return plans


def can_access_feature(tier: PlanTier, feature_name: str) -> bool:
    """Check if a plan tier has access to a specific feature"""
    features = get_plan_features(tier)
    return getattr(features, feature_name, False)


def compare_plans(current_tier: PlanTier, new_tier: PlanTier) -> Dict[str, any]:
    """Compare two plans and return upgrade/downgrade information"""
    current_features = get_plan_features(current_tier)
    new_features = get_plan_features(new_tier)
    current_pricing = get_plan_pricing(current_tier)
    new_pricing = get_plan_pricing(new_tier)

    # Determine if upgrade or downgrade
    tier_order = [PlanTier.FREE, PlanTier.BASIC, PlanTier.PRO, PlanTier.ELITE]
    current_idx = tier_order.index(current_tier)
    new_idx = tier_order.index(new_tier)

    is_upgrade = new_idx > current_idx

    # Find feature differences
    added_features = []
    removed_features = []

    for attr in dir(new_features):
        if not attr.startswith('_'):
            current_value = getattr(current_features, attr)
            new_value = getattr(new_features, attr)

            if isinstance(current_value, bool) and isinstance(new_value, bool):
                if not current_value and new_value:
                    added_features.append(attr)
                elif current_value and not new_value:
                    removed_features.append(attr)

    return {
        'is_upgrade': is_upgrade,
        'price_change': new_pricing.monthly_price - current_pricing.monthly_price,
        'added_features': added_features,
        'removed_features': removed_features,
        'current_tier': current_tier.value,
        'new_tier': new_tier.value,
    }
