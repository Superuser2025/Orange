# 🎯 GUERILLA TRADER - Exact Location Guide

## 📍 **Where to Find It in the GUI**

### **Location: LEFT PANEL (Controls Panel) - Position #3**

When you launch `python main.py` on Windows with MT5, you'll see:

```
┌──────────────────────────────────────────────────────────────┐
│ 🍎 AppleTrader Pro                                           │
│ ─────────────────────────────────────────────────────────────│
│ File  View  Trading  ML  Help                                │
├───────────┬──────────────────────────────┬───────────────────┤
│           │                              │                   │
│  LEFT     │  CENTER                      │  RIGHT            │
│  PANEL    │                              │                   │
│  ⬇️       │                              │                   │
│           │                              │                   │
│ ▼ SCROLL DOWN TO SEE GUERILLA TRADER!    │                   │
│                                           │                   │
└───────────┴──────────────────────────────┴───────────────────┘
```

---

## 📋 **Controls Panel Layout (Top to Bottom)**

### **1. HEADER** (Line 65)
```
⚙️ CONTROLS
```

### **2. TRADING MODE** (Line 81 - Big Toggle)
```
┌─────────────────────────────┐
│     TRADING MODE            │
│ 🔴 INDICATOR MODE           │ ← Big button
└─────────────────────────────┘
```

### **3. UPDATE SPEED** (Line 88)
```
┌─────────────────────────────┐
│ ⚡ Update Speed             │
│ [Fast ▼]                    │
└─────────────────────────────┘
```

### **4. ⚡ GUERILLA TRADER** ← **HERE!** (Line 93)
```
┌─────────────────────────────────────┐
│ ⚡ GUERILLA TRADER    [✓] Proxy Mode│ ← Orange border!
├─────────────────────────────────────┤
│                                     │
│ Symbol: [EURUSD ▼]                  │
│                                     │
│ Lot Size: [0.10]                    │
│                                     │
│ SL Pips: [5 pips]  ← Red bg         │
│                                     │
│ TP Pips: [10 pips] ← Green bg       │
│                                     │
│ ┌──────────┐    ┌──────────┐       │
│ │ 🎯 BUY   │    │ 🎯 SELL  │       │ ← BIG buttons!
│ └──────────┘    └──────────┘       │
│                                     │
│ 💡 Bypasses broker restrictions!    │
└─────────────────────────────────────┘
```
**File:** `Apple/python/gui/controls_panel.py`
**Lines:** 254-536
**Method:** `create_quick_orders_section()`

### **5. RISK MANAGEMENT** (Line 99)
```
💰 Risk Management
[Risk slider]
```

### **6. INSTITUTIONAL FILTERS** (Line 105)
```
🔍 Institutional Filters
[Checkboxes]
```

### **7. SMART MONEY CONCEPTS** (Line 111)
```
💎 Smart Money Concepts
[Checkboxes]
```

### **8. MACHINE LEARNING** (Line 117)
```
🤖 Machine Learning
[Enable ML checkbox]
```

### **9. CHART VISUALS** (Line 123)
```
👁️ Chart Visuals
[Checkboxes]
```

---

## 🎨 **Visual Characteristics**

### **How to Recognize GUERILLA TRADER:**

1. **🟠 Orange/Warning Border**
   - Stands out from other sections
   - Color: `settings.theme.warning`
   - Border: `2px solid`

2. **⚡ Title**
   - Text: "⚡ GUERILLA TRADER"
   - Color: Orange
   - Font: Bold, medium size

3. **✓ Proxy Mode Toggle**
   - Checkbox in header
   - Green when checked (default ON)
   - Text: "Proxy Mode"

4. **🎯 Big Buttons**
   - **BUY**: Green background, 50px height
   - **SELL**: Red background, 50px height
   - Icon: 🎯 (target)

5. **Color-Coded Inputs**
   - **SL Pips**: Red background (danger)
   - **TP Pips**: Green background (success)

6. **💡 Info Message**
   - Bottom text: "💡 Bypasses broker restrictions!"
   - Italic, small font

---

## 📂 **Code Structure**

### **Files Involved:**

1. **`Apple/python/gui/controls_panel.py`**
   - **Line 93:** Section added to layout
   - **Line 254-496:** `create_quick_orders_section()` method
   - **Line 498-516:** `fire_guerilla_buy()` method
   - **Line 518-536:** `fire_guerilla_sell()` method

2. **`Apple/python/gui/main_window.py`**
   - **Line 17:** Import proxy_trader
   - **Line 54-56:** Start GUERILLA TRADER engine
   - **Line 452-454:** Handle guerilla_order signal
   - **Line 469-548:** `handle_guerilla_order()` method
   - **Line 509-531:** Proxy mode execution

3. **`Apple/python/core/proxy_trader.py`**
   - **Complete engine:** 521 lines
   - **Line 123-270:** `place_market_order()` method
   - **Line 272-341:** `place_pending_order()` method
   - **Line 343-354:** `cancel_order()` method
   - **Line 356-369:** `get_statistics()` method
   - **Line 371-387:** `_monitor_loop()` (real-time)

---

## 🖼️ **Detailed Layout Diagram**

```
AppleTrader Pro Window (1920x1080)
├── Menu Bar (top)
│   ├── File
│   ├── View
│   ├── Trading
│   ├── ML
│   └── Help
│
├── Main Content (3-panel layout)
│   │
│   ├── LEFT PANEL (400px wide, SCROLL!)
│   │   │
│   │   ├── [1] ⚙️ CONTROLS (header)
│   │   │
│   │   ├── [2] TRADING MODE
│   │   │   └── 🔴 INDICATOR MODE (toggle button)
│   │   │
│   │   ├── [3] ⚡ UPDATE SPEED
│   │   │   └── [Dropdown: Fast/Medium/Slow]
│   │   │
│   │   ├── [4] ⚡ GUERILLA TRADER ◀━━━━━━━━ HERE!
│   │   │   ├── Header: "⚡ GUERILLA TRADER" | [✓] Proxy Mode
│   │   │   ├── Symbol: [EURUSD ▼]
│   │   │   ├── Lot Size: [0.10]
│   │   │   ├── SL Pips: [5 pips] (red)
│   │   │   ├── TP Pips: [10 pips] (green)
│   │   │   ├── [🎯 BUY]  [🎯 SELL]
│   │   │   └── 💡 Bypasses broker restrictions!
│   │   │
│   │   ├── [5] 💰 RISK MANAGEMENT
│   │   ├── [6] 🔍 INSTITUTIONAL FILTERS
│   │   ├── [7] 💎 SMART MONEY CONCEPTS
│   │   ├── [8] 🤖 MACHINE LEARNING
│   │   └── [9] 👁️ CHART VISUALS
│   │
│   ├── CENTER PANEL (expandable)
│   │   ├── Chart (matplotlib)
│   │   ├── Commentary Panel
│   │   └── ML Panel
│   │
│   └── RIGHT PANEL (420px wide)
│       ├── Dashboard Panel
│       ├── Market Drivers
│       └── Orders Panel
│
└── Status Bar (bottom)
    ├── 🟢 Connected
    ├── 📊 Data: 15:34:12
    └── 🤖 ML: Off
```

---

## 🚀 **How to Launch on Windows**

### **Requirements:**
1. ✅ Windows OS
2. ✅ MetaTrader 5 installed
3. ✅ Python 3.9+
4. ✅ All dependencies installed

### **Steps:**

1. **Open Command Prompt / PowerShell**

2. **Navigate to directory:**
   ```cmd
   cd C:\path\to\Orange\Apple\python
   ```

3. **Install requirements:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Launch the app:**
   ```cmd
   python main.py
   ```

5. **Look for GUERILLA TRADER:**
   - Left panel
   - Scroll down past "Trading Mode" and "Update Speed"
   - Look for **orange border** section
   - Title: **⚡ GUERILLA TRADER**

---

## 🎯 **Quick Visual Test**

When you see this, you've found it:

```
┌───────────────────────────────────────────┐
│ ⚡ GUERILLA TRADER          [✓] Proxy Mode│ ◀─ Orange header
├───────────────────────────────────────────┤
│ Symbol: EURUSD                            │
│ Lot Size: 0.10                            │
│ SL Pips: 5 pips                           │ ◀─ Red background
│ TP Pips: 10 pips                          │ ◀─ Green background
│                                           │
│ [ 🎯 BUY ]         [ 🎯 SELL ]           │ ◀─ BIG buttons!
│                                           │
│ 💡 Bypasses broker restrictions!          │
└───────────────────────────────────────────┘
```

**If you see this → YOU FOUND IT!** ✅

---

## 🐛 **Troubleshooting**

### **"I don't see it!"**

1. **Check if scrolling is needed:**
   - The left panel is scrollable
   - Scroll DOWN past Trading Mode and Update Speed
   - GUERILLA TRADER is section #4

2. **Check window size:**
   - Minimum: 1400x900
   - Recommended: 1920x1080
   - Left panel might be collapsed on small screens

3. **Check for errors:**
   - Open terminal/console
   - Look for error messages
   - Check `Apple/python/logs/` folder

4. **Verify code is present:**
   ```bash
   grep "GUERILLA TRADER" Apple/python/gui/controls_panel.py
   ```
   Should return: Line 255 and Line 273

5. **Check imports:**
   - Make sure `core/proxy_trader.py` exists
   - Verify no import errors on startup

---

## 📸 **Expected Appearance**

### **Colors:**
- **Border:** Orange (#F97316)
- **Title:** Orange
- **Proxy checkbox:** Green when checked
- **SL input:** Red background (#EF4444)
- **TP input:** Green background (#10B981)
- **BUY button:** Green (#10B981)
- **SELL button:** Red (#EF4444)

### **Size:**
- **Section width:** ~368px (400px panel - 32px padding)
- **Button height:** 50px each
- **Total section height:** ~350px

---

## ✅ **Confirmation Checklist**

When you run the app, verify:

- [ ] App launches without errors
- [ ] MT5 connection status shown (🟢 or ⚫)
- [ ] Left panel visible with "⚙️ CONTROLS" header
- [ ] Can scroll in left panel
- [ ] **⚡ GUERILLA TRADER** section visible after scrolling
- [ ] Orange border around section
- [ ] All inputs visible (Symbol, Lot, SL, TP)
- [ ] **🎯 BUY** and **🎯 SELL** buttons visible
- [ ] Buttons are clickable

---

## 🎉 **Success!**

If you can see all of the above, **GUERILLA TRADER is ready to use!**

Try clicking **🎯 BUY** to see the confirmation dialog and test the system.

Happy trading! 🚀
