# 🏗️ AppleTrader Pro - System Architecture

## 📐 Overview

AppleTrader Pro is a complete redesign of the Institutional Trading Robot, separating concerns into:
- **MT5 EA** → Data provider & order executor (lightweight, minimal chart display)
- **Python GUI** → Visualization, control, and ML engine (where the user interacts)
- **IPC Layer** → JSON-based communication between MT5 and Python

This architecture keeps MT5 charts clean while providing a professional Bloomberg Terminal-style interface in Python.

---

## 🎯 Design Principles

1. **Separation of Concerns**
   - MT5 handles market data collection and order execution
   - Python handles visualization, user interaction, and ML
   - Clear interfaces between components

2. **Modularity**
   - Each component is independent and testable
   - Easy to add new features or replace modules
   - Configuration-driven design

3. **Real-Time Performance**
   - 10-second market data updates (as requested)
   - 250ms UI refresh for smooth experience
   - Efficient data buffering and caching

4. **Professional UX**
   - Institutional dark theme
   - Keyboard shortcuts
   - Responsive layout
   - Clear visual hierarchy

---

## 📦 Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLETRADER PRO                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                │
│  │   MT5 EA     │   IPC   │  Python GUI  │                │
│  │              │◄───────►│              │                │
│  │  • Patterns  │         │  • Chart     │                │
│  │  • Filters   │  JSON   │  • Controls  │                │
│  │  • Zones     │  Files  │  • ML        │                │
│  │  • Orders    │         │  • Analytics │                │
│  └──────────────┘         └──────────────┘                │
│         ▲                        ▲                         │
│         │                        │                         │
│         ▼                        ▼                         │
│  ┌──────────────┐         ┌──────────────┐                │
│  │  MT5 Market  │         │    User      │                │
│  │     Data     │         │  Interaction │                │
│  └──────────────┘         └──────────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Python Application Structure

### **Core Layer** (`python/core/`)

Handles fundamental operations:

#### `mt5_connector.py`
- **Purpose**: Bridge between Python and MetaTrader 5
- **Responsibilities**:
  - Initialize MT5 connection
  - Fetch candle data via MT5 Python API
  - Execute orders (buy/sell/close/modify)
  - Read/write IPC files for EA communication
  - Get account and position information

**Key Methods:**
```python
connector.initialize()                    # Connect to MT5
connector.get_candles(symbol, tf, count)  # Fetch OHLC data
connector.place_order(symbol, type, vol)  # Place market order
connector.read_market_data_file()         # Read data from EA
connector.write_command_file(cmd, params) # Send command to EA
```

#### `data_manager.py`
- **Purpose**: Central data buffer and state management
- **Responsibilities**:
  - Buffer candlestick data (circular buffer, max 1000 candles)
  - Store patterns, zones, indicators
  - Manage market state (regime, bias, session)
  - Track filter status and decisions
  - Synchronize MT5 and GUI data

**Data Buffers:**
```python
MarketDataBuffer   # Candle data with efficient updates
PatternBuffer      # Detected patterns with timestamps
ZoneBuffer         # FVGs, Order Blocks, Liquidity zones
```

---

### **GUI Layer** (`python/gui/`)

User interface components:

#### `main_window.py`
- **Purpose**: Main application window and orchestration
- **Responsibilities**:
  - Create menu bar, status bar, panel layout
  - Manage timers (10s market data, 250ms UI refresh)
  - Coordinate panel updates
  - Handle keyboard shortcuts
  - Connection status management

**Timers:**
- `market_data_timer`: Every 10 seconds → fetch data from MT5/EA
- `ui_timer`: Every 250ms → update UI elements smoothly

**Panels** (to be implemented):
- `ChartPanel`: Real-time candlestick chart with overlays
- `DashboardPanel`: Market status, filters, regime, bias
- `ControlsPanel`: All EA settings and toggle buttons
- `CommentaryPanel`: Real-time trading commentary feed
- `MLPanel`: ML predictions, feature importance, metrics
- `OrdersPanel`: Open positions, pending orders, history

---

### **ML Layer** (`python/ml/`)

Machine Learning engine (to be implemented):

#### `ml_engine.py`
- Integrated ML model (XGBoost/RandomForest)
- Feature extraction (40+ market features)
- Real-time predictions
- Model persistence

#### `feature_extractor.py`
- Extract features from market data
- Price action, volume, volatility
- Multi-timeframe features
- Regime-aware feature sets

#### `model_trainer.py`
- Train models on historical data
- Time-series cross-validation
- Walk-forward testing
- Feature importance analysis

#### `prediction_service.py`
- Real-time prediction server
- Probability and confidence scoring
- Signal generation (ENTER/WAIT/SKIP)

---

### **Widgets Layer** (`python/widgets/`)

Custom UI widgets (to be implemented):

#### `advanced_chart.py`
- Professional candlestick chart
- Plotly/Matplotlib integration
- Zoom, pan, crosshair
- Real-time updates

#### `pattern_overlay.py`
- Draw pattern boxes and labels
- Highlight strength indicators
- Multi-timeframe pattern display

#### `zone_overlay.py`
- FVG zones (transparent fills)
- Order Blocks (shaded rectangles)
- Liquidity levels (horizontal lines)

#### `indicator_overlay.py`
- EMA lines
- ATR bands
- RSI, MACD, etc.

---

### **Utils Layer** (`python/utils/`)

Utility modules:

#### `logger.py` ✅ (Created)
- Colored console output
- File logging (daily log files)
- Specialized log types (trade, ML, connection)
- Exception tracking

#### `theme_manager.py`
- Dark institutional theme
- Color scheme management
- Font configuration

#### `notifications.py`
- Desktop notifications
- Sound alerts
- Email/Telegram integration (optional)

---

### **Configuration** (`python/config.py`) ✅

Centralized configuration using dataclasses:

```python
AppConfig        # Window size, update intervals, MT5 connection
ThemeConfig      # Colors, fonts, institutional dark theme
MLConfig         # Model parameters, thresholds, training settings
TradingConfig    # Risk settings, filters, position limits
AlertConfig      # Notification preferences

settings = Settings()  # Global instance
```

All settings are:
- Type-safe (dataclasses)
- Persistent (saved to JSON)
- Runtime-modifiable (GUI can change them)

---

## 📡 Inter-Process Communication (IPC)

### **File-Based IPC**

Why files?
- Simple and reliable
- Language-agnostic
- Easy to debug (human-readable JSON)
- No network dependencies

### **Communication Files**

Located in `shared/ipc/`:

#### 1. `market_data.json` (MT5 → Python)

**Update Frequency**: Every 10 seconds (from EA)

**Contents**:
```json
{
  "timestamp": "2025-01-15T15:32:45",
  "symbol": "EURUSD",
  "timeframe": "H4",
  "price": {
    "bid": 1.08450,
    "ask": 1.08452,
    "spread": 0.00002
  },
  "candles": [/* Last 200 candles */],
  "patterns": {
    "active": {
      "name": "Bullish Engulfing",
      "strength": 5,
      "is_bullish": true
    }
  },
  "zones": {
    "fvgs": [/* FVG data */],
    "order_blocks": [/* OB data */],
    "liquidity": [/* Liquidity levels */]
  },
  "filters": {
    "volume_ok": true,
    "spread_ok": true,
    "mtf_ok": true
  },
  "decision": {
    "action": "ENTER",
    "confluence": 7,
    "required": 7
  },
  "indicators": {
    "ema_200": 1.08200,
    "atr_14": 0.00085
  },
  "positions": [/* Open positions */],
  "account": {
    "balance": 10000.00,
    "equity": 10127.50
  },
  "ml": {
    "enabled": true,
    "sample_count": 150
  }
}
```

#### 2. `commands.json` (Python → MT5)

**Purpose**: Send trading commands to EA

**Examples**:
```json
{
  "timestamp": "2025-01-15T15:33:00",
  "command": "PLACE_ORDER",
  "params": {
    "type": "BUY",
    "symbol": "EURUSD",
    "lots": 0.01,
    "sl_pips": 50,
    "tp1_pips": 100,
    "comment": "ML Approved"
  }
}
```

```json
{
  "command": "CLOSE_POSITION",
  "params": {
    "ticket": 12345
  }
}
```

```json
{
  "command": "UPDATE_SETTINGS",
  "params": {
    "use_ml_filter": true,
    "risk_percent": 0.5
  }
}
```

#### 3. `status.json` (Bidirectional)

**Purpose**: Heartbeat and status synchronization

```json
{
  "python_active": true,
  "ea_active": true,
  "last_python_update": "2025-01-15T15:33:00",
  "last_ea_update": "2025-01-15T15:33:05"
}
```

---

## 🎨 Theme and Visual Design

### **Color Palette** (Institutional Dark Theme)

```
Background:    #0A0E27  (Deep dark blue)
Surface:       #141B2D  (Card background)
Surface Light: #1E293B  (Lighter panels)
Accent:        #00D4FF  (Cyan)
Success:       #10B981  (Green)
Warning:       #F59E0B  (Orange)
Danger:        #EF4444  (Red)
Text Primary:  #F8FAFC  (Almost white)
Text Secondary:#94A3B8  (Gray)
```

### **Typography**

- **Main Font**: Inter (clean, modern sans-serif)
- **Monospace**: JetBrains Mono (for numbers, data)
- **Display**: Poppins (for headers)

### **Sizes**

- XS: 10px
- SM: 11px
- MD: 13px (default)
- LG: 15px
- XL: 18px
- XXL: 24px

---

## 🔄 Data Flow

### **Startup Sequence**

```
1. Python app starts
   └─► Initialize logger
   └─► Load configuration
   └─► Create main window
   └─► Initialize MT5 connector
   └─► Connect to MT5
   └─► Start timers

2. EA attached to chart
   └─► Initialize EA
   └─► Detect patterns/zones
   └─► Write market_data.json
   └─► Update every 10 seconds

3. Data synchronization
   └─► Python reads market_data.json (every 10s)
   └─► Update data_manager buffers
   └─► Refresh GUI panels (every 250ms)
   └─► Emit data_updated signal
```

### **Trading Flow**

```
1. User clicks "PLACE BUY" in Python GUI
   └─► Show confirmation dialog
   └─► Write commands.json
   └─► Display "Order pending..." status

2. EA reads commands.json
   └─► Validate order parameters
   └─► Check filters and risk limits
   └─► Execute order via MT5 API
   └─► Write result to market_data.json

3. Python receives result
   └─► Update orders panel
   └─► Show notification
   └─► Log trade action
```

---

## 🧪 Testing Strategy

### **Unit Tests**

- Test each module independently
- Mock MT5 API for testing without live connection
- Validate data transformations

### **Integration Tests**

- Test IPC file read/write
- Test data flow between components
- Verify signal propagation

### **End-to-End Tests**

- Full workflow testing
- User interaction simulation
- Performance benchmarks

---

## 📈 Performance Considerations

### **Optimizations**

1. **Data Buffering**
   - Circular buffers for candles (max 1000)
   - Only update changed data
   - Lazy evaluation where possible

2. **UI Updates**
   - Separate timers for data (10s) and UI (250ms)
   - Only redraw changed elements
   - Use Qt signals for efficient updates

3. **File I/O**
   - Atomic writes to prevent corruption
   - Check file modification time before reading
   - Cache parsed JSON

### **Memory Management**

- Fixed-size buffers to prevent growth
- Regular cleanup of old data
- Efficient pandas DataFrames

---

## 🔐 Security Considerations

1. **Order Validation**
   - Confirmation dialogs for all trades
   - Position size limits enforced
   - Daily/weekly loss limits respected

2. **Connection Safety**
   - Connection monitoring and auto-reconnect
   - Graceful degradation on disconnect
   - Emergency stop functionality

3. **Data Integrity**
   - JSON schema validation
   - Error handling for corrupted files
   - Logging of all operations

---

## 🚀 Future Enhancements

### **Phase 1: Core Functionality** (Current)
- ✅ Basic architecture
- ✅ MT5 connector
- ✅ Data management
- ✅ Main window skeleton
- ⏳ GUI panels implementation
- ⏳ EA development

### **Phase 2: ML Integration**
- ML engine integration
- Feature visualization
- Model training UI
- Performance analytics

### **Phase 3: Advanced Features**
- Backtesting integration
- Strategy optimization
- Portfolio management
- Risk analytics dashboard

### **Phase 4: Cloud Features**
- Cloud data storage
- Multi-account support
- Mobile companion app
- Trade copy service

---

## 📚 Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| GUI Framework | PyQt6 | Professional desktop UI |
| Charting | Plotly/Matplotlib | Advanced chart visualization |
| MT5 Integration | MetaTrader5 Python | Direct MT5 API access |
| Data Processing | pandas, numpy | Efficient data handling |
| Machine Learning | XGBoost, scikit-learn | Trade filtering and prediction |
| IPC | JSON files | MT5 ↔ Python communication |
| Logging | Custom logger | Professional logging system |
| Configuration | Python dataclasses | Type-safe configuration |

---

## 🎓 Key Architectural Decisions

### **Why Python GUI instead of MT5 chart?**

✅ **Advantages**:
- Modern UI frameworks (PyQt6)
- Rich charting libraries (Plotly)
- Full ML ecosystem (scikit-learn, XGBoost)
- Professional desktop app capabilities
- Clean MT5 charts (minimal distractions)
- Easier to maintain and extend

❌ **Disadvantages**:
- Requires Python installation
- IPC overhead (minimal with 10s updates)
- Additional complexity

**Decision**: Benefits far outweigh costs for professional trading

### **Why file-based IPC instead of sockets?**

✅ **Advantages**:
- Simplicity (no network layer)
- Reliability (no connection drops)
- Debuggability (human-readable JSON)
- Language-agnostic (MQL5 ↔ Python)
- No firewall issues

❌ **Disadvantages**:
- Slightly slower than sockets (negligible at 10s interval)
- Disk I/O overhead (minimal with modern SSDs)

**Decision**: Simplicity and reliability prioritized

### **Why 10-second updates?**

✅ **Rationale**:
- User requested specifically
- Sufficient for H4/D1 trading
- Reduces CPU/disk usage
- Allows MT5 EA to do heavy lifting
- Python GUI remains responsive

**Note**: Can be configured for faster updates if needed (config.py)

---

**Built with institutional-grade standards for professional traders** 🍎
