"""
Mock MetaTrader5 module for Linux development/testing
This allows the GUI to run on Linux for development purposes
For actual trading, you need Windows with MT5 installed
"""

# MT5 constants
TIMEFRAME_M1 = 1
TIMEFRAME_M5 = 5
TIMEFRAME_M15 = 15
TIMEFRAME_M30 = 30
TIMEFRAME_H1 = 60
TIMEFRAME_H4 = 240
TIMEFRAME_D1 = 1440
TIMEFRAME_W1 = 10080
TIMEFRAME_MN1 = 43200

ORDER_TYPE_BUY = 0
ORDER_TYPE_SELL = 1
ORDER_TYPE_BUY_LIMIT = 2
ORDER_TYPE_SELL_LIMIT = 3
ORDER_TYPE_BUY_STOP = 4
ORDER_TYPE_SELL_STOP = 5

TRADE_ACTION_DEAL = 1
TRADE_ACTION_SLTP = 5

TRADE_RETCODE_DONE = 10009

ORDER_TIME_GTC = 0
ORDER_FILLING_IOC = 1

SYMBOL_TRADE_MODE_FULL = 4


class MockTick:
    """Mock tick data"""
    def __init__(self):
        self.bid = 1.0850
        self.ask = 1.0852
        self.last = 1.0851


class MockSymbolInfo:
    """Mock symbol info"""
    def __init__(self):
        self.bid = 1.0850
        self.ask = 1.0852
        self.last = 1.0851
        self.spread = 2
        self.digits = 5
        self.point = 0.00001
        self.trade_mode = SYMBOL_TRADE_MODE_FULL
        self.visible = True


class MockAccount:
    """Mock account info"""
    def __init__(self):
        self.login = 12345678
        self.balance = 10000.0
        self.equity = 10000.0
        self.margin = 0.0
        self.margin_free = 10000.0
        self.margin_level = 0.0
        self.profit = 0.0
        self.currency = "USD"
        self.leverage = 100
        self.server = "MockBroker-Demo"


class MockResult:
    """Mock order result"""
    def __init__(self, success=True):
        self.retcode = TRADE_RETCODE_DONE if success else 10013
        self.comment = "Done" if success else "Invalid request"
        self.order = 123456


def initialize():
    """Mock MT5 initialize"""
    print("🔧 Mock MT5: Initialized (Linux development mode)")
    return True


def shutdown():
    """Mock MT5 shutdown"""
    print("🔧 Mock MT5: Shutdown")


def last_error():
    """Mock last error"""
    return (0, "Success")


def account_info():
    """Mock account info"""
    return MockAccount()


def terminal_info():
    """Mock terminal info"""
    class TerminalInfo:
        connected = True
    return TerminalInfo()


def symbol_info(symbol):
    """Mock symbol info"""
    return MockSymbolInfo()


def symbol_info_tick(symbol):
    """Mock tick data"""
    return MockTick()


def symbol_select(symbol, enable):
    """Mock symbol select"""
    return True


def copy_rates_from_pos(symbol, timeframe, start_pos, count):
    """Mock historical data"""
    import numpy as np
    import time

    # Generate mock candles
    current_time = int(time.time())
    times = [current_time - (i * 3600) for i in range(count)][::-1]

    rates = np.array([
        (t, 1.08 + (i % 50) * 0.0001, 1.08 + (i % 50) * 0.0001 + 0.001,
         1.08 + (i % 50) * 0.0001 - 0.001, 1.08 + (i % 50) * 0.0001 + 0.0005,
         1000, 0, 0)
        for i, t in enumerate(times)
    ], dtype=[('time', 'i8'), ('open', 'f8'), ('high', 'f8'),
              ('low', 'f8'), ('close', 'f8'), ('tick_volume', 'i8'),
              ('spread', 'i4'), ('real_volume', 'i8')])

    return rates


def positions_get(ticket=None):
    """Mock positions"""
    return []  # No open positions in mock mode


def order_send(request):
    """Mock order send"""
    print(f"🔧 Mock MT5: Order sent - {request}")
    return MockResult(success=True)


print("⚠️  MetaTrader5 Mock Module Loaded (Linux Development Mode)")
print("   For actual trading, use Windows with MT5 installed")
