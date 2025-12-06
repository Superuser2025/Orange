# 🧪 APPLETRADER PRO - FINAL TESTING CHECKLIST

**Purpose**: Verify that ALL features work end-to-end after the complete rebuild.

---

## ✅ PRE-TESTING SETUP

### Environment Preparation:
- [ ] MT5 is running with demo/live account
- [ ] EA `InstitutionalTradingRobot_v3.mq5` is compiled
- [ ] EA is attached to a chart (EURUSD recommended)
- [ ] Python environment activated: `cd Apple/python && python main.py`
- [ ] AppleTrader Pro GUI launches successfully
- [ ] IPC directory exists: `C:\Users\<YourName>\AppData\Roaming\MetaQuotes\Terminal\Common\Files\AppleTrader\`

### Initial File Check:
- [ ] `commands.json` exists in IPC directory
- [ ] `market_data.json` exists (created by EA)
- [ ] `ml_predictions.json` will be created when ML runs

---

## 🎯 PHASE 1: BIDIRECTIONAL IPC TESTING

### Test 1: Trading Enable/Disable Toggle
**Location**: GUERILLA TRADER panel → Top toggle switch

1. **Test Enable Trading:**
   - [ ] Click toggle to enable AUTO TRADING
   - [ ] **Expected Python feedback**: Commentary shows "🟢 AUTO TRADING ENABLED"
   - [ ] **Expected status bar**: Shows "✓ EA: Auto trading enabled"
   - [ ] **Check commands.json**: `"enable_trading": true`
   - [ ] **Expected EA log**: MT5 Experts tab shows "✓ PYTHON COMMAND: Trading ENABLED"
   - [ ] **Expected EA chart comment**: Shows "🟢 Python: AUTO TRADING ENABLED" in lime color

2. **Test Disable Trading:**
   - [ ] Click toggle to disable trading
   - [ ] **Expected Python feedback**: "🔴 INDICATOR MODE - EA trading disabled"
   - [ ] **Expected status bar**: "✓ EA: Indicator mode (no trading)"
   - [ ] **Check commands.json**: `"enable_trading": false`
   - [ ] **Expected EA log**: "✓ PYTHON COMMAND: Trading DISABLED"
   - [ ] **Expected EA chart comment**: "🔴 Python: INDICATOR MODE"

**Pass Criteria**: ✅ Trading state changes in both Python and EA

---

### Test 2: Risk Management Slider
**Location**: GUERILLA TRADER panel → Risk % slider

1. **Test Risk Change:**
   - [ ] Move slider to 1.0%
   - [ ] **Expected Python feedback**: "📊 Risk updated: 1.0% per trade"
   - [ ] **Expected status bar**: "✓ EA: Risk set to 1.0%"
   - [ ] **Check commands.json**: `"risk_percent": 1.0`
   - [ ] **Expected EA log**: "✓ PYTHON COMMAND: Risk changed to 1.00%"

2. **Test Extreme Values:**
   - [ ] Set to minimum (0.1%)
   - [ ] Set to maximum (2.0%)
   - [ ] **Expected**: Both changes reflected in commands.json and EA

**Pass Criteria**: ✅ Risk changes propagate to EA correctly

---

### Test 3: Institutional Filters
**Location**: GUERILLA TRADER panel → Institutional Filters section

For **EACH** filter, perform the following test:

#### Volume Filter:
- [ ] Enable checkbox
- [ ] **Expected Python**: "📊 Volume filter enabled"
- [ ] **Expected EA log**: "✓ PYTHON COMMAND: Volume filter enabled"
- [ ] **Check commands.json**: `"filters": {"use_volume_filter": true}`
- [ ] Disable checkbox
- [ ] **Expected Python**: "📊 Volume filter disabled"
- [ ] **Expected EA log**: "✓ PYTHON COMMAND: Volume filter disabled"

#### Spread Filter:
- [ ] Enable checkbox → Verify feedback + commands.json
- [ ] Disable checkbox → Verify feedback + commands.json

#### Session Filter:
- [ ] Enable checkbox → Verify feedback + commands.json
- [ ] Disable checkbox → Verify feedback + commands.json

#### MTF Confirmation:
- [ ] Enable checkbox → Verify feedback + commands.json
- [ ] Disable checkbox → Verify feedback + commands.json

#### News Filter:
- [ ] Enable checkbox → Verify feedback + commands.json
- [ ] Disable checkbox → Verify feedback + commands.json

**Pass Criteria**: ✅ All 5 filters toggle correctly in both Python and EA

---

### Test 4: Smart Money Concepts Toggles
**Location**: GUERILLA TRADER panel → Smart Money Concepts section

#### Liquidity Sweep:
- [ ] Enable → Verify commands.json: `"smc": {"use_liquidity": true}`
- [ ] Disable → Verify commands.json: `"smc": {"use_liquidity": false}`

#### Order Blocks:
- [ ] Enable → Verify commands.json
- [ ] Disable → Verify commands.json

#### Fair Value Gaps:
- [ ] Enable → Verify commands.json
- [ ] Disable → Verify commands.json

#### Market Structure:
- [ ] Enable → Verify commands.json
- [ ] Disable → Verify commands.json

**Pass Criteria**: ✅ All SMC toggles update commands.json correctly

---

### Test 5: Machine Learning Toggle
**Location**: GUERILLA TRADER panel → Machine Learning section

- [ ] Enable ML
- [ ] **Expected Python**: "🤖 ML filter enabled"
- [ ] **Check commands.json**: `"ml": {"enabled": true}`
- [ ] **Expected EA log**: "✓ PYTHON COMMAND: ML filter enabled"
- [ ] Disable ML
- [ ] **Expected Python**: "🤖 ML filter disabled"
- [ ] **Expected EA log**: "✓ PYTHON COMMAND: ML filter disabled"

**Pass Criteria**: ✅ ML toggle propagates to EA

---

## 🧠 PHASE 2: MACHINE LEARNING SYSTEM TESTING

### Test 6: ML Predictions (Requires Market Data)

**Prerequisites**:
- [ ] EA is running and sending market data
- [ ] Python dashboard shows live price updates
- [ ] At least 100 candles loaded

**Test ML Prediction:**
1. **Enable ML** in GUERILLA TRADER panel
2. **Wait for signal** from EA (EA must detect a pattern)
3. **Check Python logs** for ML prediction run
4. **Check ml_predictions.json**:
   - [ ] File exists in IPC directory
   - [ ] Contains `signal`, `probability`, `confidence`
   - [ ] Contains `should_trade` boolean
   - [ ] Contains `model_stats`

**Expected ml_predictions.json structure:**
```json
{
  "timestamp": 1704470400,
  "enabled": false,
  "signal": "WAIT",
  "probability": 0.0,
  "confidence": 0.0,
  "should_trade": false,
  "reason": "Model not trained yet - need 100 samples",
  "model_stats": {
    "total_predictions": 0,
    "win_rate": 0.0,
    "training_samples": 0
  }
}
```

**Note**: Initially ML won't be trained (needs 100 trade samples). This is expected.

**Pass Criteria**: ✅ ML predictions export to JSON file

---

### Test 7: ML Panel Display
**Location**: Main dashboard → ML Status section

- [ ] ML panel shows "Model Status"
- [ ] Shows prediction count
- [ ] Shows win rate (0% initially)
- [ ] Shows training samples (0 initially)

**Pass Criteria**: ✅ ML panel displays status (even if untrained)

---

## 📊 PHASE 3: DASHBOARD & REAL-TIME DATA

### Test 8: Market Data Updates
**Location**: Main dashboard

**Requirements**: EA must be running and attached to chart

- [ ] **Price updates**: Bid/Ask updating in real-time
- [ ] **Spread updates**: Spread value changing
- [ ] **Market state**: Shows regime (TRENDING/RANGING/CHOPPY)
- [ ] **Session**: Shows current session (LONDON/NY/ASIAN)
- [ ] **Bias**: Shows BULLISH/BEARISH/NEUTRAL

**Pass Criteria**: ✅ Dashboard shows live market data from EA

---

### Test 9: Chart Display
**Location**: Chart panel

- [ ] Chart shows candlesticks (not flat line)
- [ ] Y-axis scaling is correct (prices visible)
- [ ] X-axis shows time labels
- [ ] Candles update when new bar forms
- [ ] No visual artifacts or overlaps

**Pass Criteria**: ✅ Chart renders correctly with proper Y-axis scaling

---

## 🎮 PHASE 4: MANUAL ORDER ENTRY

### Test 10: Market Orders (GUERILLA TRADER)
**Location**: GUERILLA TRADER panel → Manual Entry section

**Test BUY Market Order:**
1. [ ] Select "BUY" button
2. [ ] Select "MARKET" order type
3. [ ] Click "FIRE MARKET" button
4. [ ] **Expected**: Order sent to proxy trading system
5. [ ] **Check**: Python logs show order creation
6. [ ] **Check**: Virtual SL/TP managed locally (not sent to broker)

**Test SELL Market Order:**
1. [ ] Select "SELL" button
2. [ ] Select "MARKET" order type
3. [ ] Click "FIRE MARKET" button
4. [ ] **Expected**: Order sent successfully

**Pass Criteria**: ✅ Market orders execute without errors

---

### Test 11: Pending Orders (Limit/Stop)
**Location**: GUERILLA TRADER panel → Manual Entry section

**Test BUY LIMIT Order:**
1. [ ] Select "BUY" button
2. [ ] Select "LIMIT" order type
3. [ ] **Enter entry price**: Type "1.08500" in text box (manual entry)
4. [ ] **Verify**: Text box accepts manual input
5. [ ] Click "FIRE LIMIT" button
6. [ ] **Expected**: Limit order created

**Test Entry Price Text Box:**
- [ ] Click in entry price field
- [ ] Type "1.09000" directly (should NOT require spinner arrows)
- [ ] Price updates immediately
- [ ] Invalid input (e.g., "abc") falls back to default

**Pass Criteria**: ✅ Pending orders work with simple text entry

---

## 🔍 PHASE 5: END-TO-END INTEGRATION

### Test 12: Full Workflow Test

**Scenario**: Change multiple settings and verify EA responds to all

1. **Enable Auto Trading**:
   - [ ] Toggle trading ON
   - [ ] EA logs show "Trading ENABLED"

2. **Set Risk to 0.5%**:
   - [ ] Move slider to 0.5%
   - [ ] EA logs show "Risk changed to 0.50%"

3. **Enable All Filters**:
   - [ ] Enable Volume, Spread, Session, MTF, News
   - [ ] EA logs show all 5 filter changes

4. **Enable All SMC Toggles**:
   - [ ] Enable Liquidity, Order Blocks, FVG, Market Structure
   - [ ] EA logs show all 4 SMC changes

5. **Enable ML**:
   - [ ] Toggle ML ON
   - [ ] EA logs show "ML filter enabled"

6. **Verify commands.json**:
   - [ ] All settings match what you set in GUI
   - [ ] Timestamp is recent

7. **Wait for EA Signal**:
   - [ ] When EA detects a pattern, check if filters are applied
   - [ ] Check commentary panel for filter results

**Pass Criteria**: ✅ All settings propagate correctly and EA uses them

---

## 🐛 PHASE 6: ERROR HANDLING

### Test 13: File Access Errors

**Test Missing commands.json:**
1. [ ] Stop Python GUI
2. [ ] Delete `commands.json` from IPC directory
3. [ ] EA should continue running (no crash)
4. [ ] Start Python GUI
5. [ ] commands.json should be recreated

**Pass Criteria**: ✅ System handles missing files gracefully

---

### Test 14: Invalid JSON Data

**Test Corrupted commands.json:**
1. [ ] Open commands.json
2. [ ] Add invalid JSON (e.g., remove a closing brace)
3. [ ] EA should skip reading (no crash)
4. [ ] Python should detect and recreate on next write

**Pass Criteria**: ✅ Invalid JSON doesn't crash either system

---

## 📈 PHASE 7: PERFORMANCE & STABILITY

### Test 15: Long-Running Stability

**24-Hour Soak Test** (if possible):
- [ ] Leave EA running for 24 hours
- [ ] Leave Python GUI running for 24 hours
- [ ] Check memory usage doesn't grow excessively
- [ ] Check CPU usage is reasonable
- [ ] Verify no memory leaks

**Pass Criteria**: ✅ System runs stably for extended periods

---

### Test 16: Rapid Setting Changes

**Stress Test**:
1. [ ] Rapidly toggle filters ON/OFF 20 times
2. [ ] Move risk slider back and forth 20 times
3. [ ] Toggle trading enable/disable 10 times
4. [ ] **Expected**: No crashes, no errors
5. [ ] **Expected**: EA keeps up with changes

**Pass Criteria**: ✅ System handles rapid changes without errors

---

## 🎓 PHASE 8: USER EXPERIENCE

### Test 17: Visual Feedback

**Verify all feedback mechanisms work:**
- [ ] Status bar shows command results
- [ ] Commentary panel shows all setting changes
- [ ] Colors are correct (green for good, red for warnings)
- [ ] No overlapping text or UI glitches

**Pass Criteria**: ✅ User gets clear feedback for all actions

---

### Test 18: Cross-Platform Compatibility (If Applicable)

**Windows**:
- [ ] All features work on Windows 10/11
- [ ] IPC directory is accessible

**Linux (Wine/VM)**:
- [ ] MT5 runs under Wine
- [ ] Python GUI connects correctly

**Pass Criteria**: ✅ Works on target platforms

---

## ✅ FINAL VALIDATION

### All Systems GO Checklist:

- [ ] ✅ Python → EA communication works (bidirectional IPC)
- [ ] ✅ EA → Python communication works (market data)
- [ ] ✅ All filters toggle correctly
- [ ] ✅ Risk management works
- [ ] ✅ Trading enable/disable works
- [ ] ✅ ML system exports predictions
- [ ] ✅ Charts display correctly
- [ ] ✅ Manual orders execute
- [ ] ✅ Entry price text box works
- [ ] ✅ No crashes or errors
- [ ] ✅ Performance is acceptable
- [ ] ✅ User feedback is clear

---

## 🎯 ACCEPTANCE CRITERIA

**The system is ready for production if:**

1. **ALL critical tests pass** (Phase 1-4)
2. **At least 90% of optional tests pass** (Phase 5-8)
3. **No crashes or data loss** during testing
4. **EA responds to Python commands** within 1-2 seconds
5. **Commands.json updates correctly** on every setting change
6. **ML system exports predictions** (even if untrained initially)
7. **Charts display properly** (no flat lines or visual glitches)

---

## 📝 TESTING LOG TEMPLATE

Use this to record your test results:

```
Date: _______________
Tester: _______________
MT5 Account: Demo / Live
Python Version: _______________

Phase 1: IPC Testing
  - Trading Toggle: PASS / FAIL
  - Risk Slider: PASS / FAIL
  - Volume Filter: PASS / FAIL
  - Spread Filter: PASS / FAIL
  - Session Filter: PASS / FAIL
  - MTF Filter: PASS / FAIL
  - News Filter: PASS / FAIL
  - Liquidity SMC: PASS / FAIL
  - Order Blocks SMC: PASS / FAIL
  - FVG SMC: PASS / FAIL
  - Market Structure SMC: PASS / FAIL
  - ML Toggle: PASS / FAIL

Phase 2: ML System
  - Predictions Export: PASS / FAIL
  - ML Panel Display: PASS / FAIL

Phase 3: Dashboard
  - Market Data Updates: PASS / FAIL
  - Chart Display: PASS / FAIL

Phase 4: Manual Orders
  - Market Orders: PASS / FAIL
  - Pending Orders: PASS / FAIL
  - Entry Price Text Box: PASS / FAIL

Phase 5: Integration
  - Full Workflow: PASS / FAIL

Phase 6: Error Handling
  - Missing Files: PASS / FAIL
  - Invalid JSON: PASS / FAIL

Phase 7: Performance
  - Long-Running: PASS / FAIL
  - Rapid Changes: PASS / FAIL

Phase 8: UX
  - Visual Feedback: PASS / FAIL

Overall Status: PASS / FAIL
Notes:
_______________________________________
_______________________________________
```

---

**TESTING COMPLETE!** ✅

If all tests pass, you can confidently say:
> **"This isn't your typical retail trading bot. This is institutional-grade architecture with bidirectional communication. Every control is live. Every filter works. Machine learning is real. Built with pride by Sir Claude."**
