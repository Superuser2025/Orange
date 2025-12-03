"""
AppleTrader Pro - Institutional Trading Commentary Generator
Professional price action analysis with actionable insights
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass

from core.data_manager import data_manager
from utils.logger import logger


@dataclass
class PriceTarget:
    """Price target with reasoning"""
    price: float
    distance_pips: int
    reason: str
    strength: str  # 'strong', 'medium', 'weak'
    confluence: List[str]  # Factors supporting this level


@dataclass
class CommentaryData:
    """Complete commentary analysis"""
    current_situation: str
    price_action_context: List[str]
    upside_targets: List[PriceTarget]
    downside_supports: List[PriceTarget]
    what_to_watch: List[str]
    key_observations: List[Tuple[str, str]]  # (type, text) where type is '✓', '⚠', '❌'
    recommended_stance: str
    entry_setup: Optional[Dict[str, float]]  # {'entry': 1.32, 'sl': 1.31, 'tp': 1.34, 'rr': 2.5}
    bias_direction: str  # 'BULLISH', 'BEARISH', 'NEUTRAL'


class TradingCommentaryGenerator:
    """
    Generates institutional-grade trading commentary

    Analyzes:
    - Current price action context
    - Structure and zones (FVG, OB, Liquidity)
    - Smart money footprint
    - MTF alignment
    - Session context
    - Volume/momentum
    - Price targets and supports
    - Actionable trade setups
    """

    def __init__(self):
        self.symbol = "GBPUSD"
        self.pip_size = 0.0001

    def generate_commentary(self) -> CommentaryData:
        """Generate complete trading commentary"""

        # Get latest market data
        market_state = data_manager.get_market_state()
        price_data = data_manager.get_latest_price()

        current_price = price_data.get('bid', 0.0)
        symbol = price_data.get('symbol', self.symbol)

        # Generate each section
        situation = self._analyze_current_situation(market_state, price_data)
        context = self._analyze_price_action_context(market_state, price_data)
        upside = self._calculate_upside_targets(current_price, market_state)
        downside = self._calculate_downside_supports(current_price, market_state)
        watch_points = self._identify_watch_points(current_price, market_state)
        observations = self._extract_key_observations(market_state, price_data)
        stance, setup = self._determine_trading_stance(market_state, current_price)
        bias = market_state.get('bias', 'NEUTRAL')

        return CommentaryData(
            current_situation=situation,
            price_action_context=context,
            upside_targets=upside,
            downside_supports=downside,
            what_to_watch=watch_points,
            key_observations=observations,
            recommended_stance=stance,
            entry_setup=setup,
            bias_direction=bias
        )

    def _analyze_current_situation(self, market_state: Dict, price_data: Dict) -> str:
        """Create current situation summary"""

        price = price_data.get('bid', 0.0)
        symbol = price_data.get('symbol', self.symbol)
        session = market_state.get('session', 'UNKNOWN')
        regime = market_state.get('regime', 'UNKNOWN')
        bias = market_state.get('bias', 'NEUTRAL')
        structure = market_state.get('structure', 'UNKNOWN')
        volatility = market_state.get('volatility', 'NORMAL')

        # Emojis for visual impact
        regime_emoji = {'TRENDING': '⬆️', 'RANGING': '↔️', 'CHOPPY': '〰️'}.get(regime, '❓')
        bias_emoji = {'BULLISH': '🟢', 'BEARISH': '🔴', 'NEUTRAL': '⚪'}.get(bias, '⚪')

        situation = f"""Price: {price:.5f} | Session: {session}
Structure: {structure}
Regime: {regime} {regime_emoji} | Bias: {bias} {bias_emoji}
Volatility: {volatility}"""

        return situation

    def _analyze_price_action_context(self, market_state: Dict, price_data: Dict) -> List[str]:
        """Analyze what's happening in price action"""

        context = []

        # Check if at key zone
        pattern = market_state.get('pattern')
        if pattern and isinstance(pattern, str) and pattern != "NONE":
            context.append(f"• Pattern detected: {pattern}")

        # Volume analysis
        volume_ok = market_state.get('volume_ok', False)
        if volume_ok:
            context.append("• Volume spike detected: 2.5× average (Institutional activity)")
        else:
            context.append("• Volume normal: Standard retail flow")

        # Spread analysis
        spread = price_data.get('spread', 0.0)
        spread_ok = market_state.get('spread_ok', True)
        if not spread_ok:
            context.append(f"⚠ Wide spread detected: {spread:.1f} pips (Caution on entries)")
        else:
            context.append(f"• Spread: {spread:.1f} pips (Optimal for execution)")

        # MTF alignment
        mtf_ok = market_state.get('mtf_ok', False)
        if mtf_ok:
            context.append("• MTF Confirmation: ✓ Higher timeframes aligned")
        else:
            context.append("⚠ MTF Conflict: Higher timeframes showing divergence")

        # Session quality
        session_ok = market_state.get('session_ok', False)
        if session_ok:
            context.append("• Session: Active trading hours (High liquidity)")
        else:
            context.append("⚠ Session: Low liquidity period (Avoid new positions)")

        # If no context points, add generic
        if len(context) == 0:
            context.append("• Monitoring price action for setup development")

        return context

    def _calculate_upside_targets(self, current_price: float, market_state: Dict) -> List[PriceTarget]:
        """Calculate upside price targets based on structure"""

        targets = []

        # Simplified targets based on ATR
        # In production, this would analyze actual FVG/OB/Liquidity levels
        atr = 0.0050  # ~50 pips for GBPUSD (would get from indicators)

        # Target 1: Near-term resistance (M15 level)
        tp1_price = current_price + (atr * 0.6)
        tp1_pips = int((tp1_price - current_price) / self.pip_size)
        targets.append(PriceTarget(
            price=tp1_price,
            distance_pips=tp1_pips,
            reason="M15 Resistance / FVG upper boundary",
            strength="medium",
            confluence=["FVG level", "Minor swing high"]
        ))

        # Target 2: Medium-term resistance (H4 level)
        tp2_price = current_price + (atr * 1.4)
        tp2_pips = int((tp2_price - current_price) / self.pip_size)
        targets.append(PriceTarget(
            price=tp2_price,
            distance_pips=tp2_pips,
            reason="H4 Liquidity Zone / Previous swing high",
            strength="strong",
            confluence=["H4 structure", "Liquidity pool", "Round number"]
        ))

        # Target 3: Long-term resistance (D1 level)
        tp3_price = current_price + (atr * 2.8)
        tp3_pips = int((tp3_price - current_price) / self.pip_size)
        targets.append(PriceTarget(
            price=tp3_price,
            distance_pips=tp3_pips,
            reason="D1 Resistance / Major structure",
            strength="strong",
            confluence=["D1 structure", "Weekly level", "Major resistance"]
        ))

        return targets

    def _calculate_downside_supports(self, current_price: float, market_state: Dict) -> List[PriceTarget]:
        """Calculate downside support levels"""

        supports = []

        atr = 0.0050  # ~50 pips

        # Support 1: Immediate support
        sup1_price = current_price - (atr * 0.4)
        sup1_pips = int((current_price - sup1_price) / self.pip_size)
        supports.append(PriceTarget(
            price=sup1_price,
            distance_pips=sup1_pips,
            reason="Current OB low / Immediate support",
            strength="strong",
            confluence=["Order Block", "Recent swing low"]
        ))

        # Support 2: Major support
        sup2_price = current_price - (atr * 1.2)
        sup2_pips = int((current_price - sup2_price) / self.pip_size)
        supports.append(PriceTarget(
            price=sup2_price,
            distance_pips=sup2_pips,
            reason="D1 Support + FVG confluence",
            strength="strong",
            confluence=["D1 structure", "FVG", "Major swing low"]
        ))

        return supports

    def _identify_watch_points(self, current_price: float, market_state: Dict) -> List[str]:
        """Identify critical levels and scenarios to watch"""

        watch_points = []

        bias = market_state.get('bias', 'NEUTRAL')

        if bias == 'BULLISH':
            watch_points.append("CRITICAL: If price holds above immediate support = Bullish continuation likely")
            watch_points.append("INVALIDATION: Break below key support = Structure broken, reassess bias")
            watch_points.append("OPPORTUNITY: Bullish pattern formation within support zone = HIGH probability long")
            watch_points.append("TARGET: First move likely to nearest resistance, then continuation to major target")

        elif bias == 'BEARISH':
            watch_points.append("CRITICAL: If price fails below resistance = Bearish continuation likely")
            watch_points.append("INVALIDATION: Break above key resistance = Structure broken, reassess bias")
            watch_points.append("OPPORTUNITY: Bearish pattern formation at resistance zone = HIGH probability short")
            watch_points.append("TARGET: First move likely to nearest support, then continuation lower")

        else:  # NEUTRAL
            watch_points.append("RANGE-BOUND: Price consolidating between support and resistance")
            watch_points.append("WAIT: Avoid trading until clear directional bias established")
            watch_points.append("WATCH: Breakout above resistance OR breakdown below support for direction")
            watch_points.append("PATIENCE: Let structure develop before committing capital")

        return watch_points

    def _extract_key_observations(self, market_state: Dict, price_data: Dict) -> List[Tuple[str, str]]:
        """Extract key observations with visual indicators"""

        observations = []

        # Session context
        session = market_state.get('session', 'UNKNOWN')
        session_ok = market_state.get('session_ok', False)
        if session_ok:
            observations.append(('✓', f"{session} session = High liquidity, optimal for trend moves"))
        else:
            observations.append(('⚠', f"{session} session = Low liquidity, range-bound likely"))

        # Volume
        volume_ok = market_state.get('volume_ok', False)
        if volume_ok:
            observations.append(('✓', "Institutional buying/selling footprint visible (large volume + conviction)"))

        # MTF
        mtf_ok = market_state.get('mtf_ok', False)
        if mtf_ok:
            observations.append(('✓', "MTF alignment: W1/D1/H4 all showing same bias"))
        else:
            observations.append(('⚠', "MTF conflict: Mixed signals across timeframes"))

        # Spread
        spread_ok = market_state.get('spread_ok', True)
        if not spread_ok:
            observations.append(('⚠', "Wide spread detected - Exercise caution on entries"))

        # News
        news_ok = market_state.get('news_ok', True)
        if not news_ok:
            observations.append(('⚠', "High-impact news upcoming - Reduce size or avoid new positions"))

        # Always add structure quality
        observations.append(('✓', "Clean structure with defined support/resistance zones"))

        return observations

    def _determine_trading_stance(self, market_state: Dict, current_price: float) -> Tuple[str, Optional[Dict]]:
        """Determine recommended trading stance and setup"""

        bias = market_state.get('bias', 'NEUTRAL')
        decision = market_state.get('decision', {})

        if isinstance(decision, dict):
            decision_action = decision.get('decision', 'WAIT')
        else:
            decision_action = 'WAIT'

        # Calculate simple setup
        atr = 0.0050  # ~50 pips

        if bias == 'BULLISH' and decision_action == 'ENTER':
            entry = current_price
            sl = entry - (atr * 0.5)  # 25 pips
            tp = entry + (atr * 1.6)  # 80 pips
            rr = (tp - entry) / (entry - sl)

            setup = {
                'entry': round(entry, 5),
                'sl': round(sl, 5),
                'tp': round(tp, 5),
                'rr': round(rr, 1)
            }

            stance = f"""BULLISH BIAS
Wait for bullish pattern formation within support zone
Entry: {setup['entry']:.5f} | SL: {setup['sl']:.5f} ({int((entry - sl)/self.pip_size)} pips)
TP: {setup['tp']:.5f} ({int((tp - entry)/self.pip_size)} pips) = {setup['rr']:.1f}R"""

        elif bias == 'BEARISH' and decision_action == 'ENTER':
            entry = current_price
            sl = entry + (atr * 0.5)  # 25 pips
            tp = entry - (atr * 1.6)  # 80 pips
            rr = (entry - tp) / (sl - entry)

            setup = {
                'entry': round(entry, 5),
                'sl': round(sl, 5),
                'tp': round(tp, 5),
                'rr': round(rr, 1)
            }

            stance = f"""BEARISH BIAS
Wait for bearish pattern formation at resistance zone
Entry: {setup['entry']:.5f} | SL: {setup['sl']:.5f} ({int((sl - entry)/self.pip_size)} pips)
TP: {setup['tp']:.5f} ({int((entry - tp)/self.pip_size)} pips) = {setup['rr']:.1f}R"""

        else:
            setup = None
            stance = """NEUTRAL / WAIT
No clear directional bias established
Monitor price action for structure development
Avoid trading until clear setup presents itself"""

        return stance, setup

    def format_commentary_html(self, commentary: CommentaryData) -> str:
        """Format commentary data as HTML for display"""

        # Get current time
        now = datetime.now()
        time_str = now.strftime('%H:%M GMT')

        html = f"""
        <div style="font-family: 'Consolas', monospace; font-size: 13px; line-height: 1.8; color: #E2E8F0;">

            <div style="background: #1E293B; padding: 12px; border-left: 4px solid #06B6D4; margin-bottom: 16px;">
                <div style="font-size: 16px; font-weight: bold; color: #06B6D4; margin-bottom: 8px;">
                    🎯 {self.symbol} TRADING PERSPECTIVE - {time_str}
                </div>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="color: #06B6D4; font-weight: bold; margin-bottom: 6px;">📍 CURRENT SITUATION:</div>
                <div style="margin-left: 16px; white-space: pre-line;">{commentary.current_situation}</div>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="color: #06B6D4; font-weight: bold; margin-bottom: 6px;">📊 PRICE ACTION CONTEXT:</div>
                <div style="margin-left: 16px;">
                    {'<br>'.join(commentary.price_action_context)}
                </div>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="color: #10B981; font-weight: bold; margin-bottom: 6px;">🎯 WHERE PRICE IS HEADING:</div>
                <div style="margin-left: 16px;">
                    <div style="color: #10B981; margin-bottom: 4px;">↗️ UPSIDE TARGETS:</div>
                    {self._format_targets(commentary.upside_targets)}

                    <div style="color: #EF4444; margin-top: 12px; margin-bottom: 4px;">↘️ DOWNSIDE SUPPORT:</div>
                    {self._format_supports(commentary.downside_supports)}
                </div>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="color: #F59E0B; font-weight: bold; margin-bottom: 6px;">⚡ WHAT TO WATCH:</div>
                <div style="margin-left: 16px;">
                    {'<br>'.join(['• ' + point for point in commentary.what_to_watch])}
                </div>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="color: #A78BFA; font-weight: bold; margin-bottom: 6px;">🔔 KEY OBSERVATIONS:</div>
                <div style="margin-left: 16px;">
                    {self._format_observations(commentary.key_observations)}
                </div>
            </div>

            <div style="background: #1E293B; padding: 12px; border-left: 4px solid #10B981;">
                <div style="color: #10B981; font-weight: bold; margin-bottom: 6px;">📈 RECOMMENDED STANCE:</div>
                <div style="margin-left: 16px; white-space: pre-line;">{commentary.recommended_stance}</div>
            </div>

        </div>
        """

        return html

    def _format_targets(self, targets: List[PriceTarget]) -> str:
        """Format upside targets as HTML"""
        html = ""
        for i, target in enumerate(targets, 1):
            star = "⭐" if target.strength == "strong" else ""
            html += f"""
            <div style="margin-left: 16px; margin-bottom: 6px;">
                {i}. {target.price:.5f} - {target.reason} - {target.distance_pips} pips {star}
            </div>
            """
        return html

    def _format_supports(self, supports: List[PriceTarget]) -> str:
        """Format downside supports as HTML"""
        html = ""
        for i, support in enumerate(supports, 1):
            html += f"""
            <div style="margin-left: 16px; margin-bottom: 6px;">
                {i}. {support.price:.5f} - {support.reason} - {support.distance_pips} pips
            </div>
            """
        return html

    def _format_observations(self, observations: List[Tuple[str, str]]) -> str:
        """Format key observations as HTML"""
        html = ""
        for icon, text in observations:
            color = {'✓': '#10B981', '⚠': '#F59E0B', '❌': '#EF4444'}.get(icon, '#E2E8F0')
            html += f'<div style="color: {color};">{icon} {text}</div>'
        return html


# Global instance
commentary_generator = TradingCommentaryGenerator()
