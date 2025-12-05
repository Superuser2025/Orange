"""
AppleTrader Pro - Command Manager
Handles bidirectional communication between Python app and MT5 EA
Sends commands from Python → EA via commands.json
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from threading import Lock

from config import COMMANDS_FILE
from utils.logger import logger


class CommandManager:
    """
    Manages command queue for Python → EA communication

    Commands are written to commands.json and read by the EA
    Each command has a unique ID and timestamp for tracking
    """

    def __init__(self):
        self.lock = Lock()
        self.command_id = 0

        # Initialize commands file with empty structure
        self._init_commands_file()

        logger.info("✓ Command Manager initialized")

    def _init_commands_file(self):
        """Initialize commands.json with proper structure"""
        try:
            initial_structure = {
                "timestamp": int(time.time()),
                "commands": [],
                "settings": {
                    "enable_trading": True,
                    "risk_percent": 0.5,
                    "filters": {
                        "use_volume_filter": True,
                        "use_spread_filter": True,
                        "use_mtf_confirmation": True,
                        "use_session_filter": True,
                        "use_news_filter": False,
                        "use_correlation_filter": False
                    },
                    "smc": {
                        "use_liquidity": True,
                        "use_order_blocks": True,
                        "use_fvg": True,
                        "use_market_structure": True
                    },
                    "ml": {
                        "enabled": False,
                        "min_probability": 0.60,
                        "min_confidence": 0.50
                    }
                }
            }

            with self.lock:
                with open(COMMANDS_FILE, 'w') as f:
                    json.dump(initial_structure, f, indent=2)

            logger.info(f"✓ Commands file initialized: {COMMANDS_FILE}")

        except Exception as e:
            logger.error(f"Failed to initialize commands file: {e}")

    def send_command(self, command_type: str, params: Dict[str, Any]) -> bool:
        """
        Send a command to the EA

        Args:
            command_type: Type of command (e.g., "set_filter", "set_risk", "enable_trading")
            params: Command parameters

        Returns:
            True if command sent successfully
        """
        try:
            with self.lock:
                # Read current commands
                if COMMANDS_FILE.exists():
                    with open(COMMANDS_FILE, 'r') as f:
                        data = json.load(f)
                else:
                    self._init_commands_file()
                    with open(COMMANDS_FILE, 'r') as f:
                        data = json.load(f)

                # Create command
                self.command_id += 1
                command = {
                    "id": self.command_id,
                    "type": command_type,
                    "params": params,
                    "timestamp": int(time.time()),
                    "executed": False
                }

                # Add to command queue
                data["commands"].append(command)
                data["timestamp"] = int(time.time())

                # Write back
                with open(COMMANDS_FILE, 'w') as f:
                    json.dump(data, f, indent=2)

                logger.info(f"✓ Command sent: {command_type} - ID: {self.command_id}")
                return True

        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return False

    def update_setting(self, setting_path: str, value: Any) -> bool:
        """
        Update a persistent setting in commands.json

        Args:
            setting_path: Dot-notation path (e.g., "filters.use_volume_filter")
            value: New value

        Returns:
            True if successful
        """
        try:
            with self.lock:
                # Read current data
                if COMMANDS_FILE.exists():
                    with open(COMMANDS_FILE, 'r') as f:
                        data = json.load(f)
                else:
                    self._init_commands_file()
                    with open(COMMANDS_FILE, 'r') as f:
                        data = json.load(f)

                # Navigate to setting using dot notation
                parts = setting_path.split('.')
                target = data["settings"]

                for part in parts[:-1]:
                    if part not in target:
                        target[part] = {}
                    target = target[part]

                # Set value
                target[parts[-1]] = value
                data["timestamp"] = int(time.time())

                # Write back
                with open(COMMANDS_FILE, 'w') as f:
                    json.dump(data, f, indent=2)

                logger.info(f"✓ Setting updated: {setting_path} = {value}")
                return True

        except Exception as e:
            logger.error(f"Failed to update setting {setting_path}: {e}")
            return False

    def set_trading_enabled(self, enabled: bool) -> bool:
        """Enable or disable EA trading"""
        return self.update_setting("enable_trading", enabled)

    def set_risk_percent(self, risk: float) -> bool:
        """Set risk percentage (0.1 to 2.0)"""
        risk = max(0.1, min(2.0, risk))  # Clamp to valid range
        return self.update_setting("risk_percent", risk)

    def set_filter(self, filter_name: str, enabled: bool) -> bool:
        """
        Enable/disable a specific filter

        Args:
            filter_name: Filter name (e.g., "use_volume_filter")
            enabled: True to enable, False to disable
        """
        return self.update_setting(f"filters.{filter_name}", enabled)

    def set_smc_feature(self, feature_name: str, enabled: bool) -> bool:
        """
        Enable/disable SMC feature

        Args:
            feature_name: Feature name (e.g., "use_liquidity")
            enabled: True to enable, False to disable
        """
        return self.update_setting(f"smc.{feature_name}", enabled)

    def set_ml_enabled(self, enabled: bool) -> bool:
        """Enable or disable ML filter"""
        return self.update_setting("ml.enabled", enabled)

    def set_ml_thresholds(self, min_probability: float, min_confidence: float) -> bool:
        """Set ML prediction thresholds"""
        success = True
        success &= self.update_setting("ml.min_probability", min_probability)
        success &= self.update_setting("ml.min_confidence", min_confidence)
        return success

    def clear_executed_commands(self) -> bool:
        """Remove executed commands from queue to prevent file bloat"""
        try:
            with self.lock:
                if not COMMANDS_FILE.exists():
                    return True

                with open(COMMANDS_FILE, 'r') as f:
                    data = json.load(f)

                # Keep only unexecuted commands
                data["commands"] = [cmd for cmd in data["commands"] if not cmd.get("executed", False)]
                data["timestamp"] = int(time.time())

                with open(COMMANDS_FILE, 'w') as f:
                    json.dump(data, f, indent=2)

                return True

        except Exception as e:
            logger.error(f"Failed to clear executed commands: {e}")
            return False

    def get_current_settings(self) -> Optional[Dict]:
        """Get current settings from commands file"""
        try:
            if not COMMANDS_FILE.exists():
                return None

            with self.lock:
                with open(COMMANDS_FILE, 'r') as f:
                    data = json.load(f)
                return data.get("settings", {})

        except Exception as e:
            logger.error(f"Failed to read settings: {e}")
            return None


# Global singleton instance
command_manager = CommandManager()
