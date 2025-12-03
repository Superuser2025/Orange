"""
AppleTrader Pro - Configuration Module
Centralized configuration for the entire application
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum
import json
import os


def get_mt5_common_path():
    """
    Automatically detect MT5 Common folder path
    Returns Path to MT5 Terminal/Common/Files directory
    """
    # MT5 Common folder is typically at:
    # C:\Users\<Username>\AppData\Roaming\MetaQuotes\Terminal\Common\Files

    appdata = os.environ.get('APPDATA')  # Get Windows AppData path
    if appdata:
        mt5_common = Path(appdata) / "MetaQuotes" / "Terminal" / "Common" / "Files"
        if mt5_common.exists():
            return mt5_common

    # Fallback: Try to find it in user's home directory
    home = Path.home()
    mt5_common = home / "AppData" / "Roaming" / "MetaQuotes" / "Terminal" / "Common" / "Files"
    if mt5_common.exists():
        return mt5_common

    # If not found, return None (will use local directory as fallback)
    print("⚠ Warning: MT5 Common folder not found, using local directory")
    return None


# Base paths
BASE_DIR = Path(__file__).parent.parent
SHARED_DIR = BASE_DIR / "shared"
DATA_DIR = SHARED_DIR / "data"
ML_DATA_DIR = DATA_DIR / "ml_data"

# Try to use MT5 Common folder for IPC, fallback to local directory
MT5_COMMON_PATH = get_mt5_common_path()
if MT5_COMMON_PATH:
    IPC_DIR = MT5_COMMON_PATH / "AppleTrader"
    print(f"✓ Using MT5 Common folder: {IPC_DIR}")
else:
    IPC_DIR = SHARED_DIR / "ipc"
    print(f"✓ Using local IPC folder: {IPC_DIR}")

# Ensure directories exist
IPC_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
ML_DATA_DIR.mkdir(parents=True, exist_ok=True)

# IPC File paths (these files are in MT5 Common/Files/AppleTrader/)
MARKET_DATA_FILE = IPC_DIR / "market_data.json"
COMMANDS_FILE = IPC_DIR / "commands.json"
STATUS_FILE = IPC_DIR / "status.json"

print(f"📁 Market data file: {MARKET_DATA_FILE}")

# Data persistence
SETTINGS_FILE = DATA_DIR / "settings.json"
TRADE_JOURNAL_FILE = DATA_DIR / "trade_journal.json"


# ============================================================
# UPDATE SPEED PRESETS
# ============================================================
class UpdateSpeed(Enum):
    """
    Configurable update speed presets
    User can choose based on their trading style and system performance
    """
    REALTIME = "realtime"       # Ultra-fast updates (100ms) - For scalpers, high-end systems
    FAST = "fast"               # Fast updates (1 second) - For active day traders
    NORMAL = "normal"           # Normal updates (10 seconds) - For swing/position traders
    SLOW = "slow"               # Slow updates (30 seconds) - For conservative systems
    CUSTOM = "custom"           # Custom intervals set by user


# Update speed configurations (in milliseconds)
UPDATE_SPEED_CONFIGS = {
    UpdateSpeed.REALTIME: {
        'market_data': 100,      # 100ms - Real-time tick data
        'chart_refresh': 100,    # 100ms - Ultra smooth chart
        'ui_refresh': 50,        # 50ms - Instant UI response
        'description': 'Real-time (100ms) - For scalpers on high-performance systems'
    },
    UpdateSpeed.FAST: {
        'market_data': 1000,     # 1 second
        'chart_refresh': 500,    # 500ms
        'ui_refresh': 100,       # 100ms
        'description': 'Fast (1s) - For day traders and active trading'
    },
    UpdateSpeed.NORMAL: {
        'market_data': 10000,    # 10 seconds (original request)
        'chart_refresh': 1000,   # 1 second
        'ui_refresh': 250,       # 250ms
        'description': 'Normal (10s) - For swing/position traders (Recommended)'
    },
    UpdateSpeed.SLOW: {
        'market_data': 30000,    # 30 seconds
        'chart_refresh': 5000,   # 5 seconds
        'ui_refresh': 500,       # 500ms
        'description': 'Slow (30s) - For conservative systems or low bandwidth'
    },
}


@dataclass
class AppConfig:
    """Main application configuration"""

    # Application metadata
    app_name: str = "AppleTrader Pro"
    version: str = "1.0.0"
    window_title: str = "AppleTrader Pro - Institutional Trading Platform"

    # Window settings
    window_width: int = 1920
    window_height: int = 1080
    window_min_width: int = 1280
    window_min_height: int = 720

    # Update speed preset (user can change in GUI)
    update_speed_preset: UpdateSpeed = UpdateSpeed.NORMAL

    # Update frequencies (milliseconds) - Set by update_speed_preset
    market_data_update_interval: int = 10000  # 10 seconds (NORMAL preset)
    chart_refresh_interval: int = 1000        # 1 second
    ui_refresh_interval: int = 250            # 250ms for smooth UI

    # MT5 Connection
    mt5_timeout: int = 30                     # Connection timeout (seconds)
    max_reconnect_attempts: int = 5
    reconnect_delay: int = 5                  # Seconds between reconnect attempts

    def set_update_speed(self, speed: UpdateSpeed):
        """
        Apply update speed preset

        Args:
            speed: UpdateSpeed enum value
        """
        if speed == UpdateSpeed.CUSTOM:
            # Don't change intervals for custom
            return

        config = UPDATE_SPEED_CONFIGS.get(speed)
        if config:
            self.update_speed_preset = speed
            self.market_data_update_interval = config['market_data']
            self.chart_refresh_interval = config['chart_refresh']
            self.ui_refresh_interval = config['ui_refresh']
            print(f"✓ Update speed changed to: {config['description']}")

    def get_update_speed_description(self) -> str:
        """Get description of current update speed"""
        if self.update_speed_preset == UpdateSpeed.CUSTOM:
            return f"Custom ({self.market_data_update_interval}ms)"

        config = UPDATE_SPEED_CONFIGS.get(self.update_speed_preset)
        return config['description'] if config else "Unknown"

    # Chart settings
    default_symbol: str = "EURUSD"
    default_timeframe: str = "H4"
    chart_candles_visible: int = 200          # Number of candles to display
    chart_max_candles: int = 1000             # Maximum candles to keep in memory

    # File paths
    base_dir: Path = field(default_factory=lambda: BASE_DIR)
    ipc_dir: Path = field(default_factory=lambda: IPC_DIR)
    data_dir: Path = field(default_factory=lambda: DATA_DIR)
    ml_data_dir: Path = field(default_factory=lambda: ML_DATA_DIR)

    # Theme and colors
    theme: str = "dark"
    enable_animations: bool = True
    enable_sound_alerts: bool = True


@dataclass
class ThemeConfig:
    """UI Theme Configuration - Institutional Dark Theme"""

    # Base colors
    background: str = "#0A0E27"              # Deep dark blue
    surface: str = "#141B2D"                 # Card background
    surface_light: str = "#1E293B"           # Lighter surface
    surface_hover: str = "#2D3748"           # Hover state

    # Accent colors
    accent: str = "#00D4FF"                  # Cyan accent
    accent_secondary: str = "#7C3AED"        # Purple
    accent_tertiary: str = "#F59E0B"         # Orange/Gold

    # Status colors
    success: str = "#10B981"                 # Green
    warning: str = "#F59E0B"                 # Orange
    danger: str = "#EF4444"                  # Red
    info: str = "#3B82F6"                    # Blue

    # Text colors
    text_primary: str = "#F8FAFC"            # Almost white
    text_secondary: str = "#94A3B8"          # Gray
    text_disabled: str = "#475569"           # Dark gray

    # Chart colors
    chart_background: str = "#0A0E27"
    chart_grid: str = "#1E293B"
    chart_crosshair: str = "#64748B"

    # Candlestick colors
    bullish: str = "#10B981"                 # Green
    bearish: str = "#EF4444"                 # Red

    # Pattern colors
    pattern_box_bullish: str = "rgba(16, 185, 129, 0.1)"
    pattern_box_bearish: str = "rgba(239, 68, 68, 0.1)"
    pattern_label_bullish: str = "#10B981"
    pattern_label_bearish: str = "#EF4444"

    # Zone colors
    fvg_bullish: str = "rgba(16, 185, 129, 0.15)"
    fvg_bearish: str = "rgba(239, 68, 68, 0.15)"
    order_block_bullish: str = "rgba(0, 100, 0, 0.2)"
    order_block_bearish: str = "rgba(220, 38, 38, 0.2)"
    liquidity_support: str = "#3B82F6"
    liquidity_resistance: str = "#EF4444"

    # Indicator colors
    ema_200: str = "#F59E0B"
    atr_bands: str = "#6366F1"
    volume_bar: str = "#64748B"

    # UI Element colors
    button_primary: str = "#10B981"
    button_secondary: str = "#3B82F6"
    button_danger: str = "#EF4444"
    button_disabled: str = "#475569"

    border_color: str = "#1E293B"
    border_color_light: str = "#334155"

    # Fonts
    font_family_main: str = "Inter"
    font_family_mono: str = "JetBrains Mono"
    font_family_display: str = "Poppins"

    font_size_xs: int = 10
    font_size_sm: int = 11
    font_size_md: int = 13
    font_size_lg: int = 15
    font_size_xl: int = 18
    font_size_xxl: int = 24


@dataclass
class MLConfig:
    """Machine Learning Configuration"""

    # Model settings
    model_type: str = "xgboost"              # 'xgboost', 'random_forest', 'gradient_boosting'
    feature_count: int = 40                   # Number of features to extract

    # Training settings
    retrain_every_n_trades: int = 100
    min_samples_for_training: int = 50
    test_size: float = 0.2
    cv_splits: int = 5

    # Prediction thresholds
    min_probability: float = 0.60             # Minimum probability to enter (60%)
    min_confidence: float = 0.50              # Minimum confidence (50%)

    # Model persistence
    model_file: str = "trading_model.pkl"
    scaler_file: str = "feature_scaler.pkl"
    feature_importance_file: str = "feature_importance.csv"

    # Data export
    auto_export_enabled: bool = True
    export_interval_minutes: int = 30

    # Model parameters (XGBoost)
    xgb_n_estimators: int = 200
    xgb_max_depth: int = 7
    xgb_learning_rate: float = 0.05
    xgb_subsample: float = 0.8
    xgb_colsample_bytree: float = 0.8

    # Random Forest parameters
    rf_n_estimators: int = 200
    rf_max_depth: int = 15
    rf_min_samples_split: int = 20
    rf_min_samples_leaf: int = 10


@dataclass
class TradingConfig:
    """Trading Configuration"""

    # Default risk settings
    default_risk_percent: float = 0.5        # 0.5% per trade
    min_risk_percent: float = 0.1
    max_risk_percent: float = 2.0

    # Position limits
    max_lot_per_trade: float = 0.05
    max_lots_per_symbol: float = 0.10
    max_open_trades: int = 999

    # Loss limits
    daily_loss_limit_percent: float = 2.0
    weekly_loss_limit_percent: float = 5.0

    # Default take profit levels (R:R)
    default_tp1_rr: float = 2.0
    default_tp2_rr: float = 3.0
    default_tp3_rr: float = 5.0

    # Partial take profit percentages
    tp1_close_percent: float = 50.0
    tp2_close_percent: float = 30.0
    tp3_close_percent: float = 20.0

    # Stop loss
    default_sl_atr_multiplier: float = 2.0

    # Order confirmation
    require_confirmation: bool = True         # Ask before placing orders

    # Filters (default states)
    use_volume_filter: bool = True
    use_spread_filter: bool = True
    use_mtf_confirmation: bool = True
    use_session_filter: bool = True
    use_news_filter: bool = True
    use_ml_filter: bool = False               # ML disabled by default


@dataclass
class AlertConfig:
    """Alert and Notification Configuration"""

    # Desktop notifications
    enable_desktop_notifications: bool = True

    # Sound alerts
    enable_sound_alerts: bool = True
    sound_volume: float = 0.7                 # 0.0 to 1.0

    # Alert triggers
    alert_on_pattern: bool = True
    alert_on_trade_entry: bool = True
    alert_on_trade_exit: bool = True
    alert_on_ml_signal: bool = True
    alert_on_critical_only: bool = False      # Only critical priority

    # Email alerts (optional)
    enable_email_alerts: bool = False
    email_smtp_server: str = ""
    email_smtp_port: int = 587
    email_from: str = ""
    email_to: str = ""
    email_username: str = ""
    email_password: str = ""

    # Mobile push (optional - Telegram)
    enable_telegram: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""


class Settings:
    """Global settings manager"""

    def __init__(self):
        self.app = AppConfig()
        self.theme = ThemeConfig()
        self.ml = MLConfig()
        self.trading = TradingConfig()
        self.alerts = AlertConfig()

        # Load saved settings
        self.load()

    def load(self):
        """Load settings from file"""
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    data = json.load(f)

                # Update configs from saved data
                for key, value in data.get('trading', {}).items():
                    if hasattr(self.trading, key):
                        setattr(self.trading, key, value)

                for key, value in data.get('ml', {}).items():
                    if hasattr(self.ml, key):
                        setattr(self.ml, key, value)

                for key, value in data.get('alerts', {}).items():
                    if hasattr(self.alerts, key):
                        setattr(self.alerts, key, value)

                print("✓ Settings loaded from file")
            except Exception as e:
                print(f"Warning: Could not load settings: {e}")

    def save(self):
        """Save settings to file"""
        try:
            data = {
                'trading': {
                    'default_risk_percent': self.trading.default_risk_percent,
                    'require_confirmation': self.trading.require_confirmation,
                    'use_volume_filter': self.trading.use_volume_filter,
                    'use_spread_filter': self.trading.use_spread_filter,
                    'use_mtf_confirmation': self.trading.use_mtf_confirmation,
                    'use_session_filter': self.trading.use_session_filter,
                    'use_news_filter': self.trading.use_news_filter,
                    'use_ml_filter': self.trading.use_ml_filter,
                },
                'ml': {
                    'min_probability': self.ml.min_probability,
                    'min_confidence': self.ml.min_confidence,
                    'auto_export_enabled': self.ml.auto_export_enabled,
                },
                'alerts': {
                    'enable_desktop_notifications': self.alerts.enable_desktop_notifications,
                    'enable_sound_alerts': self.alerts.enable_sound_alerts,
                    'sound_volume': self.alerts.sound_volume,
                    'alert_on_pattern': self.alerts.alert_on_pattern,
                    'alert_on_trade_entry': self.alerts.alert_on_trade_entry,
                    'alert_on_trade_exit': self.alerts.alert_on_trade_exit,
                    'alert_on_ml_signal': self.alerts.alert_on_ml_signal,
                }
            }

            with open(SETTINGS_FILE, 'w') as f:
                json.dump(data, f, indent=2)

            print("✓ Settings saved to file")
        except Exception as e:
            print(f"Warning: Could not save settings: {e}")


# Global settings instance
settings = Settings()


# Timeframe mapping (MT5 constants)
TIMEFRAMES = {
    'M1': 1,
    'M5': 5,
    'M15': 15,
    'M30': 30,
    'H1': 60,
    'H4': 240,
    'D1': 1440,
    'W1': 10080,
    'MN1': 43200,
}

# Reverse mapping
TIMEFRAME_NAMES = {v: k for k, v in TIMEFRAMES.items()}


# Chart display settings
CHART_CONFIG = {
    'show_grid': True,
    'show_crosshair': True,
    'show_volume': True,
    'show_ema_200': True,
    'show_atr_bands': False,
    'show_patterns': True,
    'show_zones': True,
    'show_liquidity': True,
}


# Priority levels (matching EA)
PRIORITY_CRITICAL = 1
PRIORITY_IMPORTANT = 2
PRIORITY_INFO = 3
