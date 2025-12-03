"""
AppleTrader Pro - ML Panel
Machine Learning insights, predictions, and model metrics
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QFrame, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from config import settings
from core.data_manager import data_manager
from utils.logger import logger


class MLPanel(QWidget):
    """
    Machine Learning insights panel
    Features:
    - Trade probability gauge
    - Model confidence bar
    - Signal recommendation
    - Top features list
    - Model metrics
    - Training status
    """

    def __init__(self):
        super().__init__()

        self.init_ui()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ml_status)
        self.update_timer.start(settings.app.ui_refresh_interval)

        logger.info("ML panel initialized")

    def init_ui(self):
        """Initialize user interface"""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # ============================================================
        # HEADER
        # ============================================================
        header = QLabel("🤖 MACHINE LEARNING")
        header.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_lg}px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(header)

        # ============================================================
        # ML STATUS
        # ============================================================
        status_section = self.create_ml_status_section()
        layout.addWidget(status_section)

        # ============================================================
        # PREDICTION
        # ============================================================
        prediction_section = self.create_prediction_section()
        layout.addWidget(prediction_section)

        # ============================================================
        # TOP FEATURES
        # ============================================================
        features_section = self.create_features_section()
        layout.addWidget(features_section)

        # ============================================================
        # MODEL METRICS
        # ============================================================
        metrics_section = self.create_metrics_section()
        layout.addWidget(metrics_section)

        layout.addStretch()

    def create_ml_status_section(self) -> QFrame:
        """Create ML status section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border: 1px solid {settings.theme.border_color};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(8)

        # Status label
        self.ml_status_label = QLabel("🔴 ML System: Disabled")
        self.ml_status_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.danger};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(self.ml_status_label)

        # Training data count
        self.training_data_label = QLabel("Training Samples: 0")
        self.training_data_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_sm}px;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(self.training_data_label)

        return frame

    def create_prediction_section(self) -> QFrame:
        """Create prediction section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border: 1px solid {settings.theme.border_color};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        # Title
        title = QLabel("── PREDICTION ──")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.accent};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
                text-align: center;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Signal
        self.signal_label = QLabel("WAIT")
        self.signal_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.warning};
                font-size: {settings.theme.font_size_xxl}px;
                font-weight: 700;
                padding: 16px;
                background-color: {settings.theme.surface_light};
                border-radius: 12px;
                border: 2px solid {settings.theme.warning};
            }}
        """)
        layout.addWidget(self.signal_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Probability
        prob_layout = QVBoxLayout()
        prob_layout.setSpacing(6)

        self.probability_label = QLabel("Probability: 0%")
        self.probability_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        prob_layout.addWidget(self.probability_label)

        self.probability_bar = QProgressBar()
        self.probability_bar.setRange(0, 100)
        self.probability_bar.setValue(0)
        self.probability_bar.setTextVisible(False)
        self.probability_bar.setFixedHeight(10)
        self.probability_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {settings.theme.surface_light};
                border: none;
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background-color: {settings.theme.accent};
                border-radius: 5px;
            }}
        """)
        prob_layout.addWidget(self.probability_bar)

        layout.addLayout(prob_layout)

        # Confidence
        conf_layout = QVBoxLayout()
        conf_layout.setSpacing(6)

        self.confidence_label = QLabel("Confidence: 0%")
        self.confidence_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        conf_layout.addWidget(self.confidence_label)

        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        self.confidence_bar.setValue(0)
        self.confidence_bar.setTextVisible(False)
        self.confidence_bar.setFixedHeight(10)
        self.confidence_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {settings.theme.surface_light};
                border: none;
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background-color: {settings.theme.success};
                border-radius: 5px;
            }}
        """)
        conf_layout.addWidget(self.confidence_bar)

        layout.addLayout(conf_layout)

        return frame

    def create_features_section(self) -> QFrame:
        """Create top features section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border: 1px solid {settings.theme.border_color};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        # Title
        title = QLabel("── TOP CONTRIBUTING FEATURES ──")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.accent};
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title)

        # Features list
        self.features_list = QListWidget()
        self.features_list.setMaximumHeight(200)
        self.features_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: {settings.theme.font_size_sm}px;
                font-family: {settings.theme.font_family_mono};
            }}
            QListWidget::item {{
                padding: 6px;
                border-bottom: 1px solid {settings.theme.border_color};
            }}
            QListWidget::item:selected {{
                background-color: {settings.theme.accent};
                color: {settings.theme.background};
            }}
        """)

        # Add placeholder features
        for i in range(1, 11):
            item = QListWidgetItem(f"{i}. Feature_{i} (0.00%)")
            item.setForeground(Qt.GlobalColor.gray)
            self.features_list.addItem(item)

        layout.addWidget(self.features_list)

        return frame

    def create_metrics_section(self) -> QFrame:
        """Create model metrics section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border: 1px solid {settings.theme.border_color};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(10)

        # Title
        title = QLabel("── MODEL PERFORMANCE ──")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.accent};
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title)

        # Metrics
        metrics = [
            ('Win Rate', '0%'),
            ('Sharpe Ratio', '0.00'),
            ('ROC-AUC', '0.00'),
            ('Avg R:R', '0.00'),
        ]

        self.metric_labels = {}

        for metric_name, default_value in metrics:
            metric_widget = self.create_metric_widget(metric_name, default_value)
            self.metric_labels[metric_name] = metric_widget.findChild(QLabel, "value")
            layout.addWidget(metric_widget)

        return frame

    def create_metric_widget(self, name: str, value: str) -> QWidget:
        """Create metric display widget"""

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        name_label = QLabel(f"{name}:")
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_sm}px;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(name_label)

        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
                font-family: {settings.theme.font_family_mono};
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(value_label)

        layout.addStretch()

        return widget

    def update_ml_status(self):
        """Update ML status and predictions"""

        try:
            ml_data = data_manager.get_ml_status()

            # Update status
            if ml_data.get('enabled'):
                self.ml_status_label.setText("🟢 ML System: Active")
                self.ml_status_label.setStyleSheet(f"""
                    QLabel {{
                        color: {settings.theme.success};
                        font-size: {settings.theme.font_size_md}px;
                        font-weight: 600;
                        background: transparent;
                        border: none;
                    }}
                """)
            else:
                self.ml_status_label.setText("🔴 ML System: Disabled")
                self.ml_status_label.setStyleSheet(f"""
                    QLabel {{
                        color: {settings.theme.danger};
                        font-size: {settings.theme.font_size_md}px;
                        font-weight: 600;
                        background: transparent;
                        border: none;
                    }}
                """)

            # Training data count
            sample_count = ml_data.get('sample_count', 0)
            self.training_data_label.setText(f"Training Samples: {sample_count}")

            # Update prediction
            probability = ml_data.get('probability', 0) * 100
            confidence = ml_data.get('confidence', 0) * 100
            signal = ml_data.get('signal', 'WAIT')

            self.probability_label.setText(f"Probability: {probability:.1f}%")
            self.probability_bar.setValue(int(probability))

            self.confidence_label.setText(f"Confidence: {confidence:.1f}%")
            self.confidence_bar.setValue(int(confidence))

            # Update signal with color
            signal_colors = {
                'ENTER': (settings.theme.success, settings.theme.success),
                'WAIT': (settings.theme.warning, settings.theme.warning),
                'SKIP': (settings.theme.danger, settings.theme.danger),
            }

            text_color, border_color = signal_colors.get(signal, (settings.theme.text_secondary, settings.theme.border_color))

            self.signal_label.setText(signal)
            self.signal_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    font-size: {settings.theme.font_size_xxl}px;
                    font-weight: 700;
                    padding: 16px;
                    background-color: {settings.theme.surface_light};
                    border-radius: 12px;
                    border: 2px solid {border_color};
                }}
            """)

        except Exception as e:
            logger.exception(f"Error updating ML panel: {e}")
