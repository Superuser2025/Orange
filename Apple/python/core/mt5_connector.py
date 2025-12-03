"""
AppleTrader Pro - MT5 Connector
Handles all communication with MetaTrader 5
"""

import json
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import pandas as pd
import pytz

from config import MARKET_DATA_FILE, COMMANDS_FILE, STATUS_FILE, TIMEFRAMES
from utils.logger import logger


class MT5Connector:
    """
    MetaTrader 5 connection and data management
    Provides both direct MT5 API access and file-based IPC
    """

    def __init__(self):
        self.connected = False
        self.account_info = None
        self.symbol = "EURUSD"
        self.timeframe = "H4"
        self.timezone = pytz.UTC

        # Initialize MT5 connection
        self.initialize()

    def initialize(self) -> bool:
        """Initialize MT5 connection"""
        try:
            if not mt5.initialize():
                logger.error(f"MT5 initialize() failed, error code: {mt5.last_error()}")
                return False

            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                return False

            self.account_info = account_info
            self.connected = True

            logger.connection(f"✓ Connected to MT5 - Account: {account_info.login}")
            logger.connection(f"  Server: {account_info.server}")
            logger.connection(f"  Balance: {account_info.balance} {account_info.currency}")

            return True

        except Exception as e:
            logger.exception(f"MT5 connection error: {e}")
            return False

    def shutdown(self):
        """Shutdown MT5 connection"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.connection("MT5 connection closed")

    def is_connected(self) -> bool:
        """Check if connected to MT5"""
        return self.connected and mt5.terminal_info() is not None

    def get_candles(self, symbol: str, timeframe: str, count: int = 200) -> Optional[pd.DataFrame]:
        """
        Get candlestick data from MT5

        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            timeframe: Timeframe string (e.g., "H4")
            count: Number of candles to retrieve

        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            # Convert timeframe string to MT5 constant
            tf_value = TIMEFRAMES.get(timeframe)
            if tf_value is None:
                logger.error(f"Invalid timeframe: {timeframe}")
                return None

            # Map to MT5 timeframe constants
            mt5_timeframes = {
                1: mt5.TIMEFRAME_M1,
                5: mt5.TIMEFRAME_M5,
                15: mt5.TIMEFRAME_M15,
                30: mt5.TIMEFRAME_M30,
                60: mt5.TIMEFRAME_H1,
                240: mt5.TIMEFRAME_H4,
                1440: mt5.TIMEFRAME_D1,
                10080: mt5.TIMEFRAME_W1,
                43200: mt5.TIMEFRAME_MN1,
            }

            mt5_tf = mt5_timeframes.get(tf_value)
            if mt5_tf is None:
                logger.error(f"Could not map timeframe: {timeframe}")
                return None

            # Get candles
            rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, count)

            if rates is None or len(rates) == 0:
                logger.error(f"Failed to get candles for {symbol} {timeframe}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')

            return df

        except Exception as e:
            logger.exception(f"Error getting candles: {e}")
            return None

    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        try:
            info = mt5.symbol_info(symbol)
            if info is None:
                return None

            return {
                'symbol': symbol,
                'bid': info.bid,
                'ask': info.ask,
                'last': info.last,
                'spread': info.spread,
                'digits': info.digits,
                'point': info.point,
                'trade_allowed': info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL,
            }

        except Exception as e:
            logger.exception(f"Error getting symbol info: {e}")
            return None

    def get_positions(self) -> List[Dict]:
        """Get open positions"""
        try:
            positions = mt5.positions_get()
            if positions is None:
                return []

            result = []
            for pos in positions:
                result.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'price_current': pos.price_current,
                    'profit': pos.profit,
                    'swap': pos.swap,
                    'comment': pos.comment,
                    'time': datetime.fromtimestamp(pos.time),
                })

            return result

        except Exception as e:
            logger.exception(f"Error getting positions: {e}")
            return []

    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        try:
            account = mt5.account_info()
            if account is None:
                return None

            return {
                'login': account.login,
                'balance': account.balance,
                'equity': account.equity,
                'margin': account.margin,
                'margin_free': account.margin_free,
                'margin_level': account.margin_level if account.margin > 0 else 0,
                'profit': account.profit,
                'currency': account.currency,
                'leverage': account.leverage,
            }

        except Exception as e:
            logger.exception(f"Error getting account info: {e}")
            return None

    def place_order(self, symbol: str, order_type: str, volume: float,
                   sl: float = 0, tp: float = 0, comment: str = "") -> Tuple[bool, str]:
        """
        Place a market order

        Args:
            symbol: Trading symbol
            order_type: 'BUY' or 'SELL'
            volume: Lot size
            sl: Stop loss price (0 = no SL)
            tp: Take profit price (0 = no TP)
            comment: Order comment

        Returns:
            (success, message/error)
        """
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return False, f"Symbol {symbol} not found"

            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    return False, f"Failed to select symbol {symbol}"

            # Determine order type
            if order_type.upper() == 'BUY':
                order_type_mt5 = mt5.ORDER_TYPE_BUY
                price = symbol_info.ask
            elif order_type.upper() == 'SELL':
                order_type_mt5 = mt5.ORDER_TYPE_SELL
                price = symbol_info.bid
            else:
                return False, f"Invalid order type: {order_type}"

            # Prepare request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type_mt5,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 10,
                "magic": 123456,  # Match EA magic number
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Send order
            result = mt5.order_send(request)

            if result is None:
                return False, "Order send failed: No result"

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return False, f"Order failed: {result.comment}"

            logger.trade(f"✓ Order placed - {order_type} {volume} {symbol} @ {price}")
            return True, f"Order #{result.order} executed at {price}"

        except Exception as e:
            logger.exception(f"Error placing order: {e}")
            return False, str(e)

    def close_position(self, ticket: int) -> Tuple[bool, str]:
        """
        Close a position by ticket

        Args:
            ticket: Position ticket number

        Returns:
            (success, message/error)
        """
        try:
            positions = mt5.positions_get(ticket=ticket)
            if positions is None or len(positions) == 0:
                return False, f"Position {ticket} not found"

            position = positions[0]

            # Determine closing order type (opposite of position)
            if position.type == mt5.ORDER_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(position.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(position.symbol).ask

            # Prepare close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": 10,
                "magic": 123456,
                "comment": "Closed by AppleTrader",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Send close order
            result = mt5.order_send(request)

            if result is None:
                return False, "Close order failed: No result"

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return False, f"Close failed: {result.comment}"

            logger.trade(f"✓ Position {ticket} closed at {price}")
            return True, f"Position closed at {price}"

        except Exception as e:
            logger.exception(f"Error closing position: {e}")
            return False, str(e)

    def modify_position(self, ticket: int, sl: float = None, tp: float = None) -> Tuple[bool, str]:
        """
        Modify position SL/TP

        Args:
            ticket: Position ticket
            sl: New stop loss (None = no change)
            tp: New take profit (None = no change)

        Returns:
            (success, message/error)
        """
        try:
            positions = mt5.positions_get(ticket=ticket)
            if positions is None or len(positions) == 0:
                return False, f"Position {ticket} not found"

            position = positions[0]

            # Use existing values if not specified
            new_sl = sl if sl is not None else position.sl
            new_tp = tp if tp is not None else position.tp

            # Prepare modification request
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": ticket,
                "sl": new_sl,
                "tp": new_tp,
            }

            # Send modification
            result = mt5.order_send(request)

            if result is None:
                return False, "Modify failed: No result"

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return False, f"Modify failed: {result.comment}"

            logger.trade(f"✓ Position {ticket} modified - SL: {new_sl}, TP: {new_tp}")
            return True, f"Position modified successfully"

        except Exception as e:
            logger.exception(f"Error modifying position: {e}")
            return False, str(e)

    def read_market_data_file(self) -> Optional[Dict]:
        """
        Read market data from IPC file (sent by EA)

        Returns:
            Market data dictionary or None if file doesn't exist/invalid
        """
        try:
            if not MARKET_DATA_FILE.exists():
                return None

            with open(MARKET_DATA_FILE, 'r') as f:
                data = json.load(f)

            return data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in market data file: {e}")
            return None
        except Exception as e:
            logger.exception(f"Error reading market data file: {e}")
            return None

    def write_command_file(self, command: str, params: Dict) -> bool:
        """
        Write command to IPC file (for EA to read)

        Args:
            command: Command type (e.g., "PLACE_ORDER", "CLOSE_POSITION")
            params: Command parameters

        Returns:
            True if successful
        """
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'command': command,
                'params': params,
            }

            with open(COMMANDS_FILE, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Command written: {command}")
            return True

        except Exception as e:
            logger.exception(f"Error writing command file: {e}")
            return False


# Global connector instance
connector = MT5Connector()
