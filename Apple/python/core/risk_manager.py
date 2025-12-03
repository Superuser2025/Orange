"""
AppleTrader Pro - Risk Manager
Symbol position limits, risk calculations, and exposure tracking
"""

from typing import Dict, Tuple
from config import settings
from utils.logger import logger


class RiskManager:
    """
    Manages risk limits and position sizing

    Features:
    - Symbol-specific position limits
    - Daily/weekly loss limits
    - Risk per trade calculations
    - Exposure tracking
    """

    def __init__(self):
        # Symbol position limits (USER REQUESTED)
        self.max_lots_per_symbol = 0.10  # Maximum lots allowed per symbol
        self.symbol_exposure = {}  # Track current exposure per symbol

        # Account-level limits
        self.daily_loss_limit_percent = 2.0  # 2% daily loss limit
        self.weekly_loss_limit_percent = 5.0  # 5% weekly loss limit

        # Risk settings
        self.base_risk_percent = 0.5  # Base risk per trade
        self.current_risk_percent = 0.5  # Dynamic risk (adjusted based on conditions)

        # Tracking
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.account_balance = 10000.0  # Will be updated from MT5

        logger.info(f"Risk Manager initialized: Max {self.max_lots_per_symbol} lots per symbol")

    def check_symbol_limit(self, symbol: str, requested_lot: float) -> Tuple[bool, str]:
        """
        Check if adding requested lot size would exceed symbol limit

        Args:
            symbol: Trading symbol (e.g., 'GBPUSD')
            requested_lot: Lot size to add

        Returns:
            (allowed: bool, message: str)
        """
        current_exposure = self.symbol_exposure.get(symbol, 0.0)
        new_total = current_exposure + requested_lot

        if new_total > self.max_lots_per_symbol:
            return False, f"❌ Symbol limit exceeded: {current_exposure:.2f} + {requested_lot:.2f} = {new_total:.2f} > {self.max_lots_per_symbol:.2f}"

        return True, f"✓ Within limit: {new_total:.2f} / {self.max_lots_per_symbol:.2f} lots"

    def update_symbol_exposure(self, symbol: str, lot_size: float, is_opening: bool = True):
        """
        Update symbol exposure tracking

        Args:
            symbol: Trading symbol
            lot_size: Lot size to add/subtract
            is_opening: True if opening position, False if closing
        """
        current = self.symbol_exposure.get(symbol, 0.0)

        if is_opening:
            self.symbol_exposure[symbol] = current + lot_size
            logger.info(f"Symbol exposure updated: {symbol} = {self.symbol_exposure[symbol]:.2f} lots")
        else:
            self.symbol_exposure[symbol] = max(0.0, current - lot_size)
            logger.info(f"Symbol exposure reduced: {symbol} = {self.symbol_exposure[symbol]:.2f} lots")

    def get_symbol_exposure(self, symbol: str) -> Dict[str, float]:
        """Get current exposure for symbol"""
        current = self.symbol_exposure.get(symbol, 0.0)
        remaining = self.max_lots_per_symbol - current
        utilization_percent = (current / self.max_lots_per_symbol) * 100

        return {
            'current': current,
            'limit': self.max_lots_per_symbol,
            'remaining': remaining,
            'utilization_percent': utilization_percent
        }

    def check_daily_limit(self) -> Tuple[bool, str]:
        """Check if daily loss limit reached"""
        daily_loss_limit_dollars = self.account_balance * (self.daily_loss_limit_percent / 100)
        remaining = daily_loss_limit_dollars + self.daily_pnl  # daily_pnl is negative if losing

        if self.daily_pnl <= -daily_loss_limit_dollars:
            return False, f"❌ Daily loss limit reached: ${self.daily_pnl:.2f} / -${daily_loss_limit_dollars:.2f}"

        return True, f"✓ Daily limit OK: ${remaining:.2f} remaining"

    def check_weekly_limit(self) -> Tuple[bool, str]:
        """Check if weekly loss limit reached"""
        weekly_loss_limit_dollars = self.account_balance * (self.weekly_loss_limit_percent / 100)
        remaining = weekly_loss_limit_dollars + self.weekly_pnl

        if self.weekly_pnl <= -weekly_loss_limit_dollars:
            return False, f"❌ Weekly loss limit reached: ${self.weekly_pnl:.2f} / -${weekly_loss_limit_dollars:.2f}"

        return True, f"✓ Weekly limit OK: ${remaining:.2f} remaining"

    def calculate_position_size(self, symbol: str, entry_price: float, sl_price: float) -> Dict[str, float]:
        """
        Calculate position size based on risk parameters

        Args:
            symbol: Trading symbol
            entry_price: Entry price
            sl_price: Stop loss price

        Returns:
            Dict with lot_size, risk_amount, etc.
        """
        # Calculate risk amount in account currency
        risk_amount = self.account_balance * (self.current_risk_percent / 100)

        # Calculate pip risk
        pip_size = 0.0001  # For most pairs
        pips_risk = abs(entry_price - sl_price) / pip_size

        # Calculate lot size (simplified - would need proper pip value calculation)
        # For GBPUSD: 1 lot = $10/pip, 0.01 lot = $0.10/pip
        pip_value_per_lot = 10.0  # $10 per pip for 1 standard lot
        lot_size = risk_amount / (pips_risk * pip_value_per_lot)

        # Round to 0.01
        lot_size = round(lot_size, 2)

        # Check against symbol limit
        allowed, message = self.check_symbol_limit(symbol, lot_size)

        if not allowed:
            # Reduce to fit limit
            current_exposure = self.symbol_exposure.get(symbol, 0.0)
            lot_size = max(0.01, self.max_lots_per_symbol - current_exposure)
            logger.warning(f"Lot size reduced to fit symbol limit: {lot_size:.2f}")

        return {
            'lot_size': lot_size,
            'risk_amount': risk_amount,
            'pips_risk': pips_risk,
            'pip_value': pip_value_per_lot * lot_size,
            'allowed': allowed,
            'message': message
        }

    def adjust_risk_for_conditions(self, volatility: str, mtf_aligned: bool, confluence_score: int):
        """
        Adjust risk based on market conditions

        Args:
            volatility: 'LOW', 'NORMAL', 'HIGH'
            mtf_aligned: True if MTF confirmation present
            confluence_score: Number of confluence factors (0-5)
        """
        risk = self.base_risk_percent

        # Volatility adjustment
        if volatility == 'HIGH':
            risk *= 0.7  # Reduce by 30% in high volatility
        elif volatility == 'LOW':
            risk *= 1.3  # Increase by 30% in low volatility

        # MTF adjustment
        if not mtf_aligned:
            risk *= 0.8  # Reduce by 20% if no MTF confirmation

        # Confluence adjustment
        if confluence_score >= 4:
            risk *= 1.2  # Increase by 20% for high confluence
        elif confluence_score <= 2:
            risk *= 0.8  # Reduce by 20% for low confluence

        # Cap at reasonable limits
        risk = max(0.1, min(2.0, risk))  # Between 0.1% and 2.0%

        self.current_risk_percent = risk
        logger.info(f"Risk adjusted: {self.base_risk_percent:.2f}% → {self.current_risk_percent:.2f}%")

    def get_risk_status(self) -> Dict:
        """Get current risk status for display"""
        daily_ok, daily_msg = self.check_daily_limit()
        weekly_ok, weekly_msg = self.check_weekly_limit()

        return {
            'current_risk_percent': self.current_risk_percent,
            'base_risk_percent': self.base_risk_percent,
            'daily_limit_ok': daily_ok,
            'daily_limit_message': daily_msg,
            'weekly_limit_ok': weekly_ok,
            'weekly_limit_message': weekly_msg,
            'daily_pnl': self.daily_pnl,
            'weekly_pnl': self.weekly_pnl,
            'account_balance': self.account_balance,
            'symbol_limits': {
                symbol: self.get_symbol_exposure(symbol)
                for symbol in self.symbol_exposure.keys()
            }
        }


# Global instance
risk_manager = RiskManager()
