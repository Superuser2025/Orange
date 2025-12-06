"""
AppleTrader Pro - Machine Learning Trading System
Real XGBoost-based trade prediction with 40+ engineered features
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import pickle
import json
from pathlib import Path

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠ XGBoost not installed - ML system will use mock mode")

from config import settings, ML_DATA_DIR
from utils.logger import logger


class MLTradingSystem:
    """
    Professional machine learning system for trade filtering and prediction

    Features:
    - 40+ engineered features from market data
    - XGBoost classification model
    - Real-time prediction with probability and confidence
    - Auto-retraining every N trades
    - Performance tracking and validation
    """

    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.is_trained = False

        # Model files
        self.model_file = ML_DATA_DIR / "trading_model.pkl"
        self.scaler_file = ML_DATA_DIR / "feature_scaler.pkl"
        self.performance_file = ML_DATA_DIR / "ml_performance.json"

        # Training data
        self.training_data = []
        self.trades_since_retrain = 0

        # Performance metrics
        self.total_predictions = 0
        self.correct_predictions = 0
        self.win_rate = 0.0
        self.sharpe_ratio = 0.0

        # Load existing model if available
        self.load_model()

        logger.info("✓ ML Trading System initialized")

    def extract_features(self, market_data: Dict) -> Optional[np.ndarray]:
        """
        Extract 40+ features from current market state

        Args:
            market_data: Dictionary with OHLC, indicators, patterns, etc.

        Returns:
            Feature vector as numpy array, or None if data insufficient
        """
        try:
            features = []

            # === PRICE ACTION FEATURES (10) ===
            close = market_data.get('close', [])
            high = market_data.get('high', [])
            low = market_data.get('low', [])
            open_price = market_data.get('open', [])

            if len(close) < 50:
                return None  # Need at least 50 candles

            # 1-5: Returns and volatility
            features.append(self._pct_change(close, 1))   # 1-bar return
            features.append(self._pct_change(close, 5))   # 5-bar return
            features.append(self._pct_change(close, 20))  # 20-bar return
            features.append(self._volatility(close, 20))  # 20-bar volatility
            features.append(self._volatility(close, 50))  # 50-bar volatility

            # 6-10: Range and momentum
            features.append(self._atr_normalized(high, low, close, 14))
            features.append(self._rsi(close, 14))
            features.append(self._price_position(close, 20))  # % position in 20-bar range
            features.append(self._trend_strength(close, 20))
            features.append(self._momentum(close, 10))

            # === MARKET STRUCTURE FEATURES (8) ===
            structure = market_data.get('market_structure', {})

            # 11-14: Trend and bias
            features.append(1.0 if structure.get('trend') == 'BULLISH' else (-1.0 if structure.get('trend') == 'BEARISH' else 0.0))
            features.append(1.0 if structure.get('bias') == 'BULLISH' else (-1.0 if structure.get('bias') == 'BEARISH' else 0.0))
            features.append(structure.get('last_swing_high', close[-1]) / close[-1] - 1.0)
            features.append(structure.get('last_swing_low', close[-1]) / close[-1] - 1.0)

            # 15-18: Break of structure signals
            features.append(1.0 if structure.get('bos_detected') else 0.0)
            features.append(1.0 if structure.get('choch_detected') else 0.0)
            features.append(float(structure.get('swing_count', 0)) / 100.0)  # Normalized
            features.append(float(structure.get('structure_breaks', 0)) / 10.0)

            # === SMART MONEY CONCEPTS (8) ===
            patterns = market_data.get('patterns', {})

            # 19-22: Order blocks and FVG
            features.append(1.0 if patterns.get('bullish_ob_active') else 0.0)
            features.append(1.0 if patterns.get('bearish_ob_active') else 0.0)
            features.append(1.0 if patterns.get('bullish_fvg_active') else 0.0)
            features.append(1.0 if patterns.get('bearish_fvg_active') else 0.0)

            # 23-26: Liquidity and sweeps
            features.append(1.0 if patterns.get('liquidity_sweep_detected') else 0.0)
            features.append(float(patterns.get('liquidity_score', 0)) / 100.0)
            features.append(1.0 if patterns.get('retail_trap_detected') else 0.0)
            features.append(float(patterns.get('ob_test_count', 0)) / 3.0)  # Max 3 tests

            # === VOLUME AND SENTIMENT (6) ===
            volume = market_data.get('volume', [])

            # 27-30: Volume analysis
            features.append(self._volume_ratio(volume, 20) if len(volume) >= 20 else 1.0)
            features.append(self._volume_trend(volume, 10) if len(volume) >= 10 else 0.0)
            features.append(1.0 if market_data.get('volume_spike') else 0.0)
            features.append(float(market_data.get('spread', 2.0)) / 10.0)  # Normalized spread

            # 31-32: Session and regime
            features.append(self._session_encoding(market_data.get('session', 'LONDON')))
            features.append(1.0 if market_data.get('regime') == 'TRENDING' else (-1.0 if market_data.get('regime') == 'RANGING' else 0.0))

            # === MULTI-TIMEFRAME (4) ===
            mtf = market_data.get('higher_timeframe', {})

            # 33-36: Higher TF alignment
            features.append(1.0 if mtf.get('trend') == 'BULLISH' else (-1.0 if mtf.get('trend') == 'BEARISH' else 0.0))
            features.append(1.0 if mtf.get('above_ema') else 0.0)
            features.append(mtf.get('ema_distance', 0.0) / 100.0)  # % distance to EMA
            features.append(1.0 if mtf.get('alignment') else 0.0)  # Trend alignment

            # === CONFLUENCE AND FILTERS (4) ===
            # 37-40: Overall signal quality
            features.append(float(market_data.get('confluence_score', 0)) / 100.0)
            features.append(1.0 if market_data.get('all_filters_passed') else 0.0)
            features.append(float(market_data.get('active_filters_count', 0)) / 6.0)  # Max 6 filters
            features.append(float(market_data.get('pattern_age', 0)) / 5.0)  # Bars since pattern

            # Convert to numpy array
            feature_array = np.array(features, dtype=np.float32)

            # Store feature names on first extraction
            if not self.feature_names:
                self.feature_names = [f"feature_{i+1}" for i in range(len(features))]

            return feature_array.reshape(1, -1)

        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return None

    def predict(self, market_data: Dict) -> Dict:
        """
        Generate trading prediction with probability and confidence

        Args:
            market_data: Current market state

        Returns:
            {
                'signal': 'BUY'/'SELL'/'WAIT',
                'probability': 0.0-1.0,
                'confidence': 0.0-1.0,
                'should_trade': bool
            }
        """
        if not self.is_trained or not XGBOOST_AVAILABLE:
            # Return neutral prediction in mock mode
            return {
                'signal': 'WAIT',
                'probability': 0.5,
                'confidence': 0.0,
                'should_trade': False,
                'reason': 'Model not trained' if not self.is_trained else 'XGBoost not available'
            }

        # Extract features
        features = self.extract_features(market_data)
        if features is None:
            return {
                'signal': 'WAIT',
                'probability': 0.0,
                'confidence': 0.0,
                'should_trade': False,
                'reason': 'Insufficient data for features'
            }

        try:
            # Get prediction probabilities
            probabilities = self.model.predict_proba(features)[0]

            # Class 0 = LOSE, Class 1 = WIN
            win_probability = probabilities[1]

            # Determine signal
            if win_probability >= settings.ml.min_probability:
                signal = 'BUY' if market_data.get('signal_type') == 'BUY' else 'SELL'
            else:
                signal = 'WAIT'

            # Calculate confidence (how sure the model is)
            confidence = abs(win_probability - 0.5) * 2  # 0.0 to 1.0 scale

            # Should trade if both thresholds met
            should_trade = (
                win_probability >= settings.ml.min_probability and
                confidence >= settings.ml.min_confidence
            )

            self.total_predictions += 1

            return {
                'signal': signal,
                'probability': float(win_probability),
                'confidence': float(confidence),
                'should_trade': should_trade,
                'reason': 'ML approved' if should_trade else 'Below ML thresholds'
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                'signal': 'WAIT',
                'probability': 0.0,
                'confidence': 0.0,
                'should_trade': False,
                'reason': f'Prediction error: {str(e)}'
            }

    def add_training_sample(self, features: np.ndarray, outcome: bool):
        """
        Add trade outcome to training data

        Args:
            features: Feature vector used for prediction
            outcome: True if trade was profitable, False otherwise
        """
        self.training_data.append({
            'features': features,
            'outcome': 1 if outcome else 0,
            'timestamp': datetime.now()
        })

        self.trades_since_retrain += 1

        # Auto-retrain if threshold reached
        if self.trades_since_retrain >= settings.ml.retrain_every_n_trades:
            logger.info(f"Auto-retraining ML model after {self.trades_since_retrain} trades")
            self.train_model()

    def train_model(self) -> bool:
        """
        Train XGBoost model on collected data

        Returns:
            True if training successful
        """
        if not XGBOOST_AVAILABLE:
            logger.warning("XGBoost not available - cannot train model")
            return False

        if len(self.training_data) < settings.ml.min_samples_for_training:
            logger.warning(f"Insufficient training data: {len(self.training_data)} samples (need {settings.ml.min_samples_for_training})")
            return False

        try:
            # Prepare training data
            X = np.vstack([sample['features'] for sample in self.training_data])
            y = np.array([sample['outcome'] for sample in self.training_data])

            logger.info(f"Training ML model on {len(y)} samples...")

            # Create and train model
            self.model = XGBClassifier(
                n_estimators=settings.ml.xgb_n_estimators,
                max_depth=settings.ml.xgb_max_depth,
                learning_rate=settings.ml.xgb_learning_rate,
                subsample=settings.ml.xgb_subsample,
                colsample_bytree=settings.ml.xgb_colsample_bytree,
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            )

            self.model.fit(X, y)

            # Calculate training accuracy
            train_accuracy = self.model.score(X, y)

            self.is_trained = True
            self.trades_since_retrain = 0

            # Save model
            self.save_model()

            logger.info(f"✓ ML model trained successfully! Accuracy: {train_accuracy:.2%}")

            return True

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False

    def save_model(self):
        """Save trained model and scaler to disk"""
        try:
            if self.model is not None:
                with open(self.model_file, 'wb') as f:
                    pickle.dump(self.model, f)
                logger.info(f"✓ Model saved: {self.model_file}")

            # Save performance metrics
            metrics = {
                'total_predictions': self.total_predictions,
                'correct_predictions': self.correct_predictions,
                'win_rate': self.win_rate,
                'sharpe_ratio': self.sharpe_ratio,
                'last_trained': datetime.now().isoformat()
            }

            with open(self.performance_file, 'w') as f:
                json.dump(metrics, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save model: {e}")

    def load_model(self):
        """Load trained model from disk"""
        try:
            if self.model_file.exists() and XGBOOST_AVAILABLE:
                with open(self.model_file, 'rb') as f:
                    self.model = pickle.load(f)
                self.is_trained = True
                logger.info("✓ ML model loaded from disk")

                # Load performance metrics
                if self.performance_file.exists():
                    with open(self.performance_file, 'r') as f:
                        metrics = json.load(f)
                        self.total_predictions = metrics.get('total_predictions', 0)
                        self.correct_predictions = metrics.get('correct_predictions', 0)
                        self.win_rate = metrics.get('win_rate', 0.0)
                        self.sharpe_ratio = metrics.get('sharpe_ratio', 0.0)

        except Exception as e:
            logger.warning(f"Could not load model: {e}")
            self.is_trained = False

    # ========== HELPER METHODS FOR FEATURE ENGINEERING ==========

    def _pct_change(self, data: List, period: int) -> float:
        """Calculate percentage change"""
        if len(data) < period + 1:
            return 0.0
        return (data[-1] / data[-period-1] - 1.0) * 100.0

    def _volatility(self, data: List, period: int) -> float:
        """Calculate volatility (std dev of returns)"""
        if len(data) < period + 1:
            return 0.0
        returns = [data[i]/data[i-1] - 1.0 for i in range(-period, 0)]
        return np.std(returns) * 100.0

    def _atr_normalized(self, high: List, low: List, close: List, period: int) -> float:
        """Average True Range normalized by price"""
        if len(high) < period + 1:
            return 0.0
        tr = [max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
              for i in range(-period, 0)]
        return (np.mean(tr) / close[-1]) * 100.0

    def _rsi(self, data: List, period: int) -> float:
        """Relative Strength Index"""
        if len(data) < period + 1:
            return 50.0
        changes = [data[i] - data[i-1] for i in range(-period, 0)]
        gains = [c if c > 0 else 0 for c in changes]
        losses = [-c if c < 0 else 0 for c in changes]
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def _price_position(self, data: List, period: int) -> float:
        """Where price is in the N-bar range (0-100%)"""
        if len(data) < period:
            return 50.0
        period_data = data[-period:]
        high_val = max(period_data)
        low_val = min(period_data)
        if high_val == low_val:
            return 50.0
        return ((data[-1] - low_val) / (high_val - low_val)) * 100.0

    def _trend_strength(self, data: List, period: int) -> float:
        """Linear regression slope as trend strength"""
        if len(data) < period:
            return 0.0
        period_data = data[-period:]
        x = np.arange(period)
        slope = np.polyfit(x, period_data, 1)[0]
        return (slope / period_data[0]) * 100.0  # Normalized by price

    def _momentum(self, data: List, period: int) -> float:
        """Price momentum"""
        if len(data) < period + 1:
            return 0.0
        return ((data[-1] / data[-period-1]) - 1.0) * 100.0

    def _volume_ratio(self, volume: List, period: int) -> float:
        """Current volume vs average volume"""
        if len(volume) < period + 1:
            return 1.0
        avg_vol = np.mean(volume[-period-1:-1])
        if avg_vol == 0:
            return 1.0
        return volume[-1] / avg_vol

    def _volume_trend(self, volume: List, period: int) -> float:
        """Volume trend direction"""
        if len(volume) < period:
            return 0.0
        x = np.arange(period)
        slope = np.polyfit(x, volume[-period:], 1)[0]
        return 1.0 if slope > 0 else -1.0

    def _session_encoding(self, session: str) -> float:
        """Encode trading session"""
        session_map = {
            'ASIAN': 0.0,
            'LONDON': 0.5,
            'NY': 1.0,
            'OVERLAP': 0.75
        }
        return session_map.get(session, 0.5)

    def get_status(self) -> Dict:
        """Get current ML system status"""
        return {
            'enabled': self.is_trained and XGBOOST_AVAILABLE,
            'model_trained': self.is_trained,
            'total_predictions': self.total_predictions,
            'win_rate': self.win_rate,
            'sharpe_ratio': self.sharpe_ratio,
            'training_samples': len(self.training_data),
            'trades_since_retrain': self.trades_since_retrain
        }


# Global ML system instance
ml_system = MLTradingSystem()
