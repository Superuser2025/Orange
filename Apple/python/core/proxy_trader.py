"""
Guerilla Trader - Proxy Order Management Engine
Bypasses broker restrictions with virtual orders and tight stops

Features:
- Virtual pending orders (not sent to broker)
- Virtual tight SL/TP (bypasses broker minimum distance)
- Real-time price monitoring (<100ms execution)
- Instant order execution when levels hit
- Smart scalping with big volume
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from threading import Thread, Lock
import MetaTrader5 as mt5

from utils.logger import logger


class OrderType(Enum):
    """Order types"""
    BUY = "BUY"
    SELL = "SELL"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"


class OrderStatus(Enum):
    """Order status"""
    PENDING = "PENDING"  # Waiting for price
    ACTIVE = "ACTIVE"    # Position open
    CLOSED = "CLOSED"    # Closed by TP/SL/manual
    CANCELLED = "CANCELLED"


@dataclass
class ProxyOrder:
    """
    Virtual order held locally (NOT sent to broker)
    """
    id: str
    symbol: str
    order_type: OrderType
    volume: float
    entry_price: float  # For pending orders
    sl_price: float  # Virtual SL (tight!)
    tp_price: float  # Virtual TP
    status: OrderStatus = OrderStatus.PENDING

    # Execution tracking
    mt5_ticket: Optional[int] = None  # Only when position is open
    open_time: Optional[datetime] = None
    close_time: Optional[datetime] = None
    close_price: Optional[float] = None
    profit: float = 0.0

    # Metadata
    comment: str = "GUERILLA"
    created_at: datetime = field(default_factory=datetime.now)

    def is_pending(self) -> bool:
        """Check if order is still pending"""
        return self.status == OrderStatus.PENDING

    def is_active(self) -> bool:
        """Check if position is open"""
        return self.status == OrderStatus.ACTIVE

    def should_execute(self, bid: float, ask: float) -> bool:
        """Check if pending order should execute"""
        if not self.is_pending():
            return False

        if self.order_type == OrderType.BUY_STOP:
            return ask >= self.entry_price
        elif self.order_type == OrderType.SELL_STOP:
            return bid <= self.entry_price
        elif self.order_type == OrderType.BUY_LIMIT:
            return ask <= self.entry_price
        elif self.order_type == OrderType.SELL_LIMIT:
            return bid >= self.entry_price

        return False

    def should_close_sl(self, bid: float, ask: float) -> bool:
        """Check if position hit virtual SL"""
        if not self.is_active():
            return False

        if self.order_type in [OrderType.BUY, OrderType.BUY_STOP, OrderType.BUY_LIMIT]:
            return bid <= self.sl_price  # BUY closed at BID
        else:
            return ask >= self.sl_price  # SELL closed at ASK

    def should_close_tp(self, bid: float, ask: float) -> bool:
        """Check if position hit virtual TP"""
        if not self.is_active():
            return False

        if self.order_type in [OrderType.BUY, OrderType.BUY_STOP, OrderType.BUY_LIMIT]:
            return bid >= self.tp_price  # BUY closed at BID
        else:
            return ask <= self.tp_price  # SELL closed at ASK


class ProxyTraderEngine:
    """
    Guerilla Trader Engine
    Manages virtual orders and executes instantly when levels hit

    BYPASS BROKER RESTRICTIONS:
    - Tight stops (e.g., 5 pips) that broker would reject
    - Instant execution without broker validation delays
    - No pending orders visible to broker
    """

    def __init__(self):
        self.orders: Dict[str, ProxyOrder] = {}  # id -> ProxyOrder
        self.lock = Lock()  # Thread-safe operations
        self.running = False
        self.monitor_thread: Optional[Thread] = None

        self.update_interval = 0.1  # Check every 100ms (fast!)

        # Statistics
        self.total_orders = 0
        self.total_profit = 0.0
        self.win_count = 0
        self.loss_count = 0

        logger.info("✓ Guerilla Trader Engine initialized")

    def start(self):
        """Start real-time monitoring"""
        if self.running:
            logger.warning("Guerilla Trader already running")
            return

        self.running = True
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("🎯 Guerilla Trader STARTED - Monitoring active")

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

        logger.info("Guerilla Trader stopped")

    def place_market_order(self, symbol: str, order_type: str, volume: float,
                          sl_pips: float, tp_pips: float) -> Tuple[bool, str]:
        """
        Place GUERILLA market order with virtual tight stops

        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            order_type: "BUY" or "SELL"
            volume: Lot size
            sl_pips: Stop loss in pips (CAN BE TIGHT! e.g., 5 pips)
            tp_pips: Take profit in pips

        Returns:
            (success, message/order_id)
        """
        try:
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return False, f"Failed to get price for {symbol}"

            # Get symbol info for pip calculation
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return False, f"Symbol {symbol} not found"

            point = symbol_info.point
            digits = symbol_info.digits

            # Calculate pip value (1 pip = 10 points for 5-digit quotes)
            pip_value = point * 10 if digits == 5 or digits == 3 else point

            # Execute market order IMMEDIATELY (no broker validation)
            if order_type.upper() == "BUY":
                entry_price = tick.ask
                sl_price = entry_price - (sl_pips * pip_value)
                tp_price = entry_price + (tp_pips * pip_value)
                mt5_type = OrderType.BUY
            else:
                entry_price = tick.bid
                sl_price = entry_price + (sl_pips * pip_value)
                tp_price = entry_price - (tp_pips * pip_value)
                mt5_type = OrderType.SELL

            # Place order to MT5 WITHOUT SL/TP (we manage them locally!)
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if order_type.upper() == "BUY" else mt5.ORDER_TYPE_SELL,
                "price": entry_price,
                "sl": 0,  # NO SL on broker side!
                "tp": 0,  # NO TP on broker side!
                "deviation": 10,
                "magic": 999999,  # Guerilla magic number
                "comment": "GUERILLA",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)

            if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = result.comment if result else "Unknown error"
                return False, f"MT5 order failed: {error_msg}"

            # Create proxy order to manage virtual SL/TP
            order_id = f"GU_{int(time.time() * 1000)}"  # Unique ID

            proxy_order = ProxyOrder(
                id=order_id,
                symbol=symbol,
                order_type=mt5_type,
                volume=volume,
                entry_price=entry_price,
                sl_price=sl_price,
                tp_price=tp_price,
                status=OrderStatus.ACTIVE,
                mt5_ticket=result.order,
                open_time=datetime.now(),
                comment="GUERILLA"
            )

            with self.lock:
                self.orders[order_id] = proxy_order
                self.total_orders += 1

            logger.trade(f"🎯 GUERILLA {order_type} {symbol} @ {entry_price:.5f}")
            logger.trade(f"   SL: {sl_price:.5f} ({sl_pips} pips) | TP: {tp_price:.5f} ({tp_pips} pips)")
            logger.trade(f"   Ticket: {result.order} | Proxy ID: {order_id}")

            return True, order_id

        except Exception as e:
            logger.exception(f"Guerilla order error: {e}")
            return False, str(e)

    def place_pending_order(self, symbol: str, order_type: str, entry_price: float,
                           volume: float, sl_pips: float, tp_pips: float) -> Tuple[bool, str]:
        """
        Place GUERILLA pending order (held LOCALLY, not sent to broker)

        Args:
            symbol: Trading symbol
            order_type: "BUY_STOP", "SELL_STOP", "BUY_LIMIT", "SELL_LIMIT"
            entry_price: Entry price level
            volume: Lot size
            sl_pips: Stop loss in pips
            tp_pips: Take profit in pips

        Returns:
            (success, message/order_id)
        """
        try:
            # Parse order type
            try:
                mt5_order_type = OrderType[order_type.upper()]
            except KeyError:
                return False, f"Invalid order type: {order_type}"

            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return False, f"Symbol {symbol} not found"

            point = symbol_info.point
            digits = symbol_info.digits
            pip_value = point * 10 if digits == 5 or digits == 3 else point

            # Calculate SL/TP from entry
            if "BUY" in order_type.upper():
                sl_price = entry_price - (sl_pips * pip_value)
                tp_price = entry_price + (tp_pips * pip_value)
            else:
                sl_price = entry_price + (sl_pips * pip_value)
                tp_price = entry_price - (tp_pips * pip_value)

            # Create VIRTUAL pending order (NOT sent to broker!)
            order_id = f"GU_{int(time.time() * 1000)}"

            proxy_order = ProxyOrder(
                id=order_id,
                symbol=symbol,
                order_type=mt5_order_type,
                volume=volume,
                entry_price=entry_price,
                sl_price=sl_price,
                tp_price=tp_price,
                status=OrderStatus.PENDING,
                comment="GUERILLA_PENDING"
            )

            with self.lock:
                self.orders[order_id] = proxy_order

            logger.trade(f"🎯 GUERILLA PENDING: {order_type} {symbol} @ {entry_price:.5f}")
            logger.trade(f"   Will execute when price reaches level (proxy ID: {order_id})")

            return True, order_id

        except Exception as e:
            logger.exception(f"Guerilla pending order error: {e}")
            return False, str(e)

    def cancel_order(self, order_id: str) -> Tuple[bool, str]:
        """Cancel pending order or close active position"""
        with self.lock:
            if order_id not in self.orders:
                return False, f"Order {order_id} not found"

            order = self.orders[order_id]

            if order.is_pending():
                # Just mark as cancelled
                order.status = OrderStatus.CANCELLED
                logger.trade(f"Guerilla order {order_id} cancelled")
                return True, "Order cancelled"

            elif order.is_active():
                # Close MT5 position
                return self._close_position(order, "Manual close")

            else:
                return False, f"Order {order_id} already closed/cancelled"

    def get_active_orders(self) -> List[ProxyOrder]:
        """Get all active orders"""
        with self.lock:
            return [o for o in self.orders.values() if o.is_active() or o.is_pending()]

    def get_statistics(self) -> Dict:
        """Get trading statistics"""
        with self.lock:
            return {
                'total_orders': self.total_orders,
                'active_orders': len([o for o in self.orders.values() if o.is_active()]),
                'pending_orders': len([o for o in self.orders.values() if o.is_pending()]),
                'total_profit': self.total_profit,
                'win_count': self.win_count,
                'loss_count': self.loss_count,
                'win_rate': (self.win_count / (self.win_count + self.loss_count) * 100) if (self.win_count + self.loss_count) > 0 else 0
            }

    def _monitor_loop(self):
        """Real-time monitoring loop (runs in background thread)"""
        logger.info("Guerilla Trader monitor loop started")

        while self.running:
            try:
                self._check_all_orders()
                time.sleep(self.update_interval)  # 100ms = fast!

            except Exception as e:
                logger.exception(f"Monitor loop error: {e}")
                time.sleep(1.0)  # Slow down on errors

        logger.info("Guerilla Trader monitor loop stopped")

    def _check_all_orders(self):
        """Check all orders for execution/close conditions"""
        with self.lock:
            orders_to_check = list(self.orders.values())

        for order in orders_to_check:
            try:
                # Get current price
                tick = mt5.symbol_info_tick(order.symbol)
                if tick is None:
                    continue

                bid = tick.bid
                ask = tick.ask

                # Check pending orders for execution
                if order.is_pending() and order.should_execute(bid, ask):
                    self._execute_pending_order(order, bid, ask)

                # Check active positions for SL/TP
                elif order.is_active():
                    if order.should_close_sl(bid, ask):
                        self._close_position(order, f"SL hit @ {bid if 'BUY' in order.order_type.value else ask:.5f}")

                    elif order.should_close_tp(bid, ask):
                        self._close_position(order, f"TP hit @ {bid if 'BUY' in order.order_type.value else ask:.5f}")

            except Exception as e:
                logger.exception(f"Error checking order {order.id}: {e}")

    def _execute_pending_order(self, order: ProxyOrder, bid: float, ask: float):
        """Execute pending order when price hits"""
        try:
            # Determine execution price and MT5 order type
            if "BUY" in order.order_type.value:
                exec_price = ask
                mt5_type = mt5.ORDER_TYPE_BUY
            else:
                exec_price = bid
                mt5_type = mt5.ORDER_TYPE_SELL

            # Execute market order
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": order.symbol,
                "volume": order.volume,
                "type": mt5_type,
                "price": exec_price,
                "sl": 0,  # NO SL on broker!
                "tp": 0,  # NO TP on broker!
                "deviation": 10,
                "magic": 999999,
                "comment": "GUERILLA_EXEC",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)

            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                # Update order status
                with self.lock:
                    order.status = OrderStatus.ACTIVE
                    order.mt5_ticket = result.order
                    order.open_time = datetime.now()
                    order.entry_price = exec_price  # Update with actual execution price

                logger.trade(f"✓ GUERILLA PENDING EXECUTED: {order.order_type.value} {order.symbol} @ {exec_price:.5f}")

            else:
                error_msg = result.comment if result else "Unknown error"
                logger.error(f"Failed to execute pending order: {error_msg}")

        except Exception as e:
            logger.exception(f"Error executing pending order: {e}")

    def _close_position(self, order: ProxyOrder, reason: str) -> Tuple[bool, str]:
        """Close MT5 position"""
        try:
            if order.mt5_ticket is None:
                return False, "No MT5 ticket"

            # Get position
            positions = mt5.positions_get(ticket=order.mt5_ticket)
            if not positions:
                # Position already closed
                with self.lock:
                    order.status = OrderStatus.CLOSED
                return True, "Position already closed"

            position = positions[0]

            # Close order
            if position.type == mt5.ORDER_TYPE_BUY:
                close_type = mt5.ORDER_TYPE_SELL
                close_price = mt5.symbol_info_tick(order.symbol).bid
            else:
                close_type = mt5.ORDER_TYPE_BUY
                close_price = mt5.symbol_info_tick(order.symbol).ask

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": order.symbol,
                "volume": order.volume,
                "type": close_type,
                "position": order.mt5_ticket,
                "price": close_price,
                "deviation": 10,
                "magic": 999999,
                "comment": f"GUERILLA_CLOSE: {reason}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)

            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                # Update order
                with self.lock:
                    order.status = OrderStatus.CLOSED
                    order.close_time = datetime.now()
                    order.close_price = close_price
                    order.profit = position.profit

                    self.total_profit += position.profit
                    if position.profit > 0:
                        self.win_count += 1
                    else:
                        self.loss_count += 1

                logger.trade(f"✓ GUERILLA CLOSED: {order.symbol} | {reason} | Profit: ${position.profit:.2f}")
                return True, f"Position closed at {close_price:.5f}"

            else:
                error_msg = result.comment if result else "Unknown error"
                logger.error(f"Failed to close position: {error_msg}")
                return False, error_msg

        except Exception as e:
            logger.exception(f"Error closing position: {e}")
            return False, str(e)


# Global instance
proxy_trader = ProxyTraderEngine()
