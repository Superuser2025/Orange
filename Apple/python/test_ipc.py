"""
Quick test script to verify IPC communication with MT5 EA
Reads market_data.json from MT5 Common folder
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent))

from config import MARKET_DATA_FILE, IPC_DIR

def test_ipc_connection():
    """Test reading market data from MT5 EA"""

    print("=" * 60)
    print("AppleTrader IPC Connection Test")
    print("=" * 60)

    print(f"\n📂 IPC Directory: {IPC_DIR}")
    print(f"📄 Market Data File: {MARKET_DATA_FILE}")

    # Check if directory exists
    if not IPC_DIR.exists():
        print(f"\n❌ ERROR: IPC directory not found!")
        print(f"   Expected: {IPC_DIR}")
        return False

    print(f"\n✓ IPC directory exists")

    # Check if market_data.json exists
    if not MARKET_DATA_FILE.exists():
        print(f"\n⚠ WARNING: market_data.json not found!")
        print(f"   Expected: {MARKET_DATA_FILE}")
        print(f"\n💡 Make sure:")
        print(f"   1. MT5 is running")
        print(f"   2. AppleTrader EA is attached to a chart")
        print(f"   3. At least 10 seconds have passed (export interval)")
        return False

    print(f"✓ market_data.json found")

    # Try to read and parse the file
    try:
        with open(MARKET_DATA_FILE, 'r') as f:
            data = json.load(f)

        print(f"\n✓ Successfully read market data JSON")
        print(f"\n📊 Market Data Summary:")
        print(f"   Symbol: {data.get('symbol', 'N/A')}")
        print(f"   Bid: {data.get('bid', 'N/A')}")
        print(f"   Ask: {data.get('ask', 'N/A')}")
        print(f"   Spread: {data.get('spread', 'N/A')} pips")
        print(f"   Timeframe: {data.get('timeframe', 'N/A')}")
        print(f"   Timestamp: {data.get('timestamp', 'N/A')}")

        print(f"\n📈 Trading Context:")
        print(f"   Bias: {data.get('bias', 'N/A')}")
        print(f"   Regime: {data.get('regime', 'N/A')}")
        print(f"   Session: {data.get('session', 'N/A')}")
        print(f"   Pattern: {data.get('pattern', 'N/A')}")

        print(f"\n🎯 Filter Status:")
        print(f"   Passed Filters: {data.get('passed_filters', 'N/A')}")
        print(f"   Confluence Score: {data.get('confluence', 'N/A')}%")

        print(f"\n💰 Account Info:")
        print(f"   Balance: ${data.get('account_balance', 'N/A')}")
        print(f"   Equity: ${data.get('account_equity', 'N/A')}")
        print(f"   Open Positions: {data.get('positions', 'N/A')}")
        print(f"   Total P/L: ${data.get('total_pnl', 'N/A')}")

        print(f"\n🤖 ML Status:")
        print(f"   Enabled: {data.get('ml_enabled', False)}")
        print(f"   Signal: {data.get('ml_signal', 'N/A')}")
        print(f"   Probability: {data.get('ml_probability', 'N/A')}")
        print(f"   Confidence: {data.get('ml_confidence', 'N/A')}")

        print("\n" + "=" * 60)
        print("✅ IPC CONNECTION TEST PASSED!")
        print("=" * 60)
        print("\n💡 Next Step: Run the full GUI with:")
        print("   python main.py")

        return True

    except json.JSONDecodeError as e:
        print(f"\n❌ ERROR: Invalid JSON format")
        print(f"   {e}")
        return False

    except Exception as e:
        print(f"\n❌ ERROR: Failed to read market data")
        print(f"   {e}")
        return False


if __name__ == "__main__":
    success = test_ipc_connection()
    sys.exit(0 if success else 1)
