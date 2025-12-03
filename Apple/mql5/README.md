# AppleTrader Pro - MQL5 Expert Advisor

## Overview

The AppleTrader EA is the MetaTrader 5 component of the AppleTrader Pro system. It provides:

- **20 Institutional Filters** - Professional-grade entry validation
- **Pattern Recognition** - Double tops, H&S, triangles, wedges, channels
- **Supply/Demand Zones** - Institutional level detection
- **Risk Management** - Position sizing, daily limits, drawdown protection
- **JSON IPC** - Real-time communication with Python GUI
- **Machine Learning Integration** - Receives ML signals from Python

## Installation

### Step 1: Copy Files to MT5

1. Open MetaTrader 5
2. Open the Data Folder: `File` → `Open Data Folder`
3. Navigate to `MQL5/`
4. Copy the following files:

```
AppleTrader/
├── mql5/
│   ├── Experts/
│   │   └── AppleTrader.mq5          → Copy to MQL5/Experts/
│   └── Include/
│       └── AppleTrader/
│           ├── JSONExporter.mqh     → Copy to MQL5/Include/AppleTrader/
│           ├── JSONReader.mqh
│           ├── Filters.mqh
│           ├── Patterns.mqh
│           ├── Zones.mqh
│           └── RiskManager.mqh
```

### Step 2: Compile the EA

1. In MT5, press `F4` to open MetaEditor
2. In the Navigator, find `Experts/AppleTrader.mq5`
3. Double-click to open
4. Press `F7` to compile (or click `Compile` button)
5. Check for errors in the Toolbox (should compile successfully)

### Step 3: Attach to Chart

1. In MT5, open a chart (e.g., EURUSD M15)
2. In the Navigator panel, find `Expert Advisors`
3. Drag `AppleTrader` onto your chart
4. Configure settings in the popup window (or use defaults)
5. Enable **AutoTrading** button in MT5 toolbar (if you want auto trading)

### Step 4: Configure Python Connection

The EA exports data to and reads commands from these JSON files:
- **Export**: `<MT5 Data Folder>/Common/Files/AppleTrader/market_data.json`
- **Commands**: `<MT5 Data Folder>/Common/Files/AppleTrader/commands.json`

The Python GUI automatically connects to these files.

## EA Settings

### Trading Mode

- **EnableAutoTrading** - `false` = Indicator Mode (no trades), `true` = Auto Trading
- **RequireConfirmation** - Require manual approval before each trade

### Update Settings

- **DataExportInterval** - How often to export data to Python (default: 10000ms = 10 seconds)
- **ExportFilePath** - JSON export path (default: `AppleTrader/market_data.json`)
- **CommandFilePath** - Command reader path (default: `AppleTrader/commands.json`)

### Risk Management

- **RiskPercentage** - Risk per trade (default: 0.5%)
- **MaxDailyLoss** - Max daily loss limit (default: 2.0%)
- **MaxDailyProfit** - Max daily profit target (default: 5.0%)
- **MaxDailyTrades** - Max trades per day (default: 5)
- **MaxOpenPositions** - Max simultaneous positions (default: 1)

### 20 Institutional Filters

Each filter can be enabled/disabled independently:

1. **Filter_Trend** - 200 EMA trend filter
2. **Filter_HTF_Alignment** - Higher timeframe alignment
3. **Filter_MarketStructure** - Higher highs/lower lows
4. **Filter_Supply_Demand** - Supply/demand zones
5. **Filter_Session** - Trading session filter
6. **Filter_Spread** - Maximum spread limit
7. **Filter_Volatility** - ATR-based volatility
8. **Filter_News** - High-impact news avoidance
9. **Filter_Volume** - Minimum volume requirement
10. **Filter_OrderFlow** - Buying/selling pressure
11. **Filter_Momentum** - RSI momentum
12. **Filter_Confluence** - Multi-timeframe agreement
13. **Filter_FairValueGap** - FVG/imbalance detection
14. **Filter_LiquiditySweep** - Stop hunts
15. **Filter_ChochBOS** - Change of character/break of structure
16. **Filter_Divergence** - RSI vs price divergence
17. **Filter_SmartMoney** - Order blocks, mitigation zones
18. **Filter_TimeOfDay** - Optimal trading hours
19. **Filter_Correlation** - Currency correlation
20. **Filter_ML_Signal** - Machine learning signals from Python

### Machine Learning

- **EnableML** - Enable ML integration (default: true)
- **MinMLConfidence** - Minimum confidence threshold (default: 0.65)
- **MinMLProbability** - Minimum probability threshold (default: 0.60)

### Pattern Recognition

- **EnablePatterns** - Enable pattern detection (default: true)
- **Pattern_DoubleTop** - Double top/bottom patterns
- **Pattern_HeadShoulders** - Head & shoulders patterns
- **Pattern_Triangle** - Triangle patterns
- **Pattern_Wedge** - Wedge patterns
- **Pattern_Channel** - Channel patterns

### Supply/Demand Zones

- **ZoneLookback** - Bars to analyze (default: 100)
- **ZoneStrength** - Minimum zone strength (default: 2.0)
- **SupplyZoneColor** - Display color for supply zones
- **DemandZoneColor** - Display color for demand zones

### Trading Sessions (GMT)

- **Trade_Asian** - Trade Asian session (default: false)
- **Trade_London** - Trade London session (default: true)
- **Trade_NewYork** - Trade New York session (default: true)
- **AsianStart/End** - Asian session hours
- **LondonStart/End** - London session hours
- **NewYorkStart/End** - New York session hours

## Architecture

### Components

1. **AppleTrader.mq5** - Main EA logic
   - Coordinates all subsystems
   - Exports market data every 10 seconds
   - Reads commands from Python
   - Executes trading logic

2. **JSONExporter.mqh** - Data export system
   - Exports market data, filter states, positions to JSON
   - Python GUI reads this file for display

3. **JSONReader.mqh** - Command reader
   - Reads trading commands from Python GUI
   - Executes orders, closes positions, updates settings

4. **Filters.mqh** - All 20 institutional filters
   - Each filter returns pass/fail
   - Calculates confluence score (percentage passing)
   - Determines market bias and regime

5. **Patterns.mqh** - Pattern recognition
   - Detects chart patterns in real-time
   - Returns active pattern name

6. **Zones.mqh** - Supply/demand zones
   - Detects and tracks zones
   - Draws rectangles on chart
   - Calculates zone strength

7. **RiskManager.mqh** - Risk management
   - Position sizing based on risk %
   - Daily loss/profit limits
   - Trade count limits
   - Drawdown protection

### Data Flow

```
MT5 EA (Every 10 seconds)
    ↓
Export market_data.json
    ├─ Market info (bid, ask, spread)
    ├─ Context (bias, regime, session)
    ├─ Filter states (all 20 filters)
    ├─ Pattern detection
    ├─ Trading status (positions, P/L)
    ├─ ML data (if available)
    └─ Risk metrics
    ↓
Python GUI reads and displays

Python GUI (User action)
    ↓
Write commands.json
    ├─ PLACE_ORDER
    ├─ CLOSE_POSITION
    ├─ CLOSE_ALL
    ├─ UPDATE_SETTINGS
    └─ UPDATE_ML
    ↓
MT5 EA reads and executes
```

## Trading Logic

### Signal Generation

The EA generates trading signals when:

1. **Minimum Confluence** - At least 70% of active filters pass
2. **Market Bias** - Clear bullish or bearish bias established
3. **All Active Filters Pass** - Every enabled filter must pass
4. **Risk Limits OK** - Within daily loss/profit/trade limits

### Entry Rules

**BUY Signal:**
- Market bias = BULLISH
- Price near demand zone (optional)
- All filters passing
- Confluence ≥ 70%
- SL: Below nearest demand zone
- TP: 2:1 Risk:Reward (or better)

**SELL Signal:**
- Market bias = BEARISH
- Price near supply zone (optional)
- All filters passing
- Confluence ≥ 70%
- SL: Above nearest supply zone
- TP: 2:1 Risk:Reward (or better)

### Exit Rules

- **Take Profit** - Hit TP level (2:1 R:R minimum)
- **Stop Loss** - Hit SL level
- **Manual Close** - From Python GUI
- **Daily Limit** - Max loss/profit/trades reached

## Monitoring

### In MT5

- **Chart Display** - Zones drawn as colored rectangles
- **Experts Tab** - Logs all EA activity
- **Journal Tab** - System messages

### In Python GUI

- **Dashboard Panel** - Real-time filter states
- **Chart Panel** - TradingView-style charts
- **Orders Panel** - Open positions and P/L
- **Commentary Panel** - Trade commentary feed
- **ML Panel** - Machine learning predictions

## Troubleshooting

### EA Not Compiling

- Ensure all `.mqh` files are in `MQL5/Include/AppleTrader/`
- Check for MQL5 syntax errors in MetaEditor
- Update to latest MT5 build

### No Data Export

- Check `Experts` tab for file write errors
- Ensure `Allow DLL imports` is enabled in EA settings
- Verify `<MT5 Data>/Common/Files/AppleTrader/` directory exists

### Python Not Receiving Data

- Check file path: `<MT5 Data>/Common/Files/AppleTrader/market_data.json`
- Verify JSON file is being updated (check timestamp)
- Ensure Python GUI is configured with correct path

### Filters Not Working

- Check filter is enabled in EA settings
- View filter states in Python GUI Dashboard
- Check `Experts` tab for filter-specific errors

## Performance Tips

1. **Start in Indicator Mode** - Test with `EnableAutoTrading = false` first
2. **Use Higher Timeframes** - M15+ recommended for institutional trading
3. **Enable Key Filters Only** - Start with 10-12 most important filters
4. **Monitor Confluence** - Aim for 70-85% confluence for best results
5. **Respect Daily Limits** - Let risk management protect your account

## Support

For issues or questions:
1. Check MT5 `Experts` tab for error messages
2. Review Python GUI `Commentary` panel for warnings
3. Verify all files are correctly installed
4. Check MT5 AutoTrading is enabled (if trading)

## Version History

**v1.00** - Initial Release
- 20 institutional filters
- Pattern recognition (5 types)
- Supply/demand zones
- JSON IPC with Python GUI
- ML integration
- Professional risk management
