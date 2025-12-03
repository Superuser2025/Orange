# 🍎 AppleTrader Pro - Institutional Trading Platform

**A Citadel-Grade Trading Dashboard for MT5**

## 📋 Overview

AppleTrader Pro is a complete architectural redesign of the Institutional Trading Robot, moving all visual elements and controls to a professional Python-based GUI while keeping the MT5 chart clean and minimal.

## 🎯 Key Features

### **Python GUI Application**
- **Real-time charting** with advanced overlays (patterns, zones, indicators)
- **Institutional dark theme** optimized for extended trading sessions
- **ML integration** with visual insights and explainability
- **Complete EA control** - all settings accessible via GUI
- **Order management** - place, modify, close orders from Python
- **Advanced analytics** - equity curve, drawdown, performance metrics
- **Smart alerts** - desktop notifications, sound, optional email/mobile

### **MT5 Expert Advisor**
- **Lightweight data provider** - sends market data to Python every 10 seconds
- **Order executor** - receives commands from Python
- **All original EA logic preserved** - patterns, filters, risk management
- **Clean chart** - minimal on-chart display, all visuals in Python app

### **Machine Learning**
- **Integrated ML engine** in Python GUI
- **Feature engineering** with 40+ market features
- **XGBoost classifier** for trade filtering
- **Live predictions** with probability and confidence
- **Visual feature importance** and model metrics

## 🚀 Quick Start

### **Prerequisites**
```bash
# Python 3.9+
pip install PyQt6 plotly pandas numpy xgboost scikit-learn MetaTrader5 pytz
```

### **Installation**
1. **Copy EA to MT5:**
   - Copy `mql5/AppleTrader_EA.mq5` and related `.mqh` files to your MT5 `MQL5/Experts/` folder
   - Compile in MetaEditor

2. **Run Python App:**
   ```bash
   cd python
   python main.py
   ```

3. **Attach EA to Chart:**
   - Open any chart in MT5
   - Attach `AppleTrader_EA`
   - The Python app will automatically connect

## 📁 Project Structure

```
Apple/
├── python/                     # Python GUI Application
│   ├── main.py                # Application entry point
│   ├── config.py              # Configuration
│   ├── core/                  # Core functionality
│   ├── ml/                    # Machine Learning
│   ├── gui/                   # GUI components
│   ├── widgets/               # Custom widgets
│   └── utils/                 # Utilities
│
├── mql5/                      # MetaTrader 5 EA
│   ├── AppleTrader_EA.mq5    # Main EA file
│   └── *.mqh                  # Helper modules
│
└── shared/                    # Shared resources
    ├── ipc/                   # Inter-process communication
    └── data/                  # Data storage
```

## 🔧 Architecture

### **Communication Flow**
```
MT5 EA → market_data.json → Python App
Python App → commands.json → MT5 EA
```

**Update Frequency:** 10 seconds (configurable)

### **Data Exchange**
- **MT5 → Python:** Price data, patterns, zones, filters, positions, account info
- **Python → MT5:** Trade commands, setting changes, control signals

## 🎨 GUI Layout

```
┌─────────────────────────────────────────────────────────┐
│  AppleTrader Pro  |  Symbol  |  Status  |  ML          │
├──────────┬─────────────────────────────────┬────────────┤
│ CONTROLS │      ADVANCED CHART             │ MARKET     │
│          │                                 │ STATUS     │
│ Filters  │  Real-time candlestick chart    │            │
│ Settings │  + Pattern overlays             │ Regime     │
│ ML       │  + Order blocks                 │ Bias       │
│ Risk     │  + FVG zones                    │ Session    │
│          │  + Liquidity levels             │ Filters    │
├──────────┼─────────────────────────────────┼────────────┤
│ ML       │      COMMENTARY                 │ ORDERS     │
│ INSIGHTS │                                 │            │
└──────────┴─────────────────────────────────┴────────────┘
```

## 📊 Features Preserved from Original EA

✅ All 20 institutional filters
✅ Smart Money Concepts (OB, FVG, Liquidity Sweeps)
✅ Multi-timeframe pattern recognition
✅ Regime detection (Trending/Ranging/Choppy)
✅ Session filtering (London/NY/Asian)
✅ Risk management with partial TPs
✅ ML-based trade filtering
✅ Pattern performance tracking
✅ Adaptive parameters
✅ Re-entry logic
✅ Pyramiding support

## 🆕 New Features in AppleTrader Pro

🚀 **Professional GUI** - Bloomberg Terminal-style interface
🚀 **Advanced charting** - Multi-indicator overlays
🚀 **ML visualization** - Feature importance, model metrics
🚀 **Performance analytics** - Equity curve, drawdown charts
🚀 **Order management** - Full control from Python
🚀 **Alert system** - Desktop notifications, sounds
🚀 **Trade journal** - Annotated trade history
🚀 **Backtesting** - Visual strategy tester connection

## ⚙️ Configuration

Edit `python/config.py` for:
- GUI theme colors
- Update frequency
- Chart settings
- ML parameters
- Alert preferences

## 📈 Machine Learning

### **Training**
```bash
cd python/ml
python model_trainer.py
```

### **Features**
- 40+ engineered market features
- Price action, volume, volatility, MTF
- Regime-aware feature sets

### **Model**
- XGBoost classifier
- Time-series cross-validation
- Walk-forward testing
- Auto-retraining every 100 trades

## 🔒 Safety Features

- **Confirmation dialogs** for all trades
- **Position size limits** enforced
- **Daily/weekly loss limits** respected
- **Connection monitoring** - auto-pause on disconnect
- **Emergency stop** button (Ctrl+Q)

## 📝 License

Proprietary - Institutional Grade Trading System

## 🤝 Support

For issues, questions, or feature requests, please check the documentation or contact support.

---

**Built with ❤️ for professional traders**

*Clean charts. Clear decisions. Confident trading.*
