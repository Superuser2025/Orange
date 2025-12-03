"""
AppleTrader Pro - Orders Panel
Position management and order history
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from config import settings
from core.data_manager import data_manager
from utils.logger import logger


class OrdersPanel(QWidget):
    """
    Orders and positions management panel
    Features:
    - Active positions table
    - Order history
    - One-click close buttons
    - P/L tracking
    - Position modification
    """

    # Signals
    close_position_requested = pyqtSignal(int)  # ticket
    modify_position_requested = pyqtSignal(int, float, float)  # ticket, sl, tp

    def __init__(self):
        super().__init__()

        self.init_ui()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_positions)
        self.update_timer.start(settings.app.ui_refresh_interval)

        logger.info("Orders panel initialized")

    def init_ui(self):
        """Initialize user interface"""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ============================================================
        # HEADER
        # ============================================================
        header_layout = QHBoxLayout()

        header = QLabel("📋 ORDERS & POSITIONS")
        header.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_lg}px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        header_layout.addWidget(header)

        header_layout.addStretch()

        # Close all button
        close_all_btn = QPushButton("🚫 Close All")
        close_all_btn.clicked.connect(self.close_all_positions)
        close_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {settings.theme.danger};
                color: {settings.theme.background};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {settings.theme.danger};
            }}
        """)
        header_layout.addWidget(close_all_btn)

        layout.addLayout(header_layout)

        # ============================================================
        # TOTAL P/L SUMMARY
        # ============================================================
        summary_frame = self.create_pnl_summary()
        layout.addWidget(summary_frame)

        # ============================================================
        # TABS: Active Positions | History
        # ============================================================
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {settings.theme.border_color};
                border-radius: 8px;
                background-color: {settings.theme.surface};
            }}
            QTabBar::tab {{
                background-color: {settings.theme.surface};
                color: {settings.theme.text_secondary};
                border: none;
                padding: 10px 20px;
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.accent};
                border-bottom: 2px solid {settings.theme.accent};
            }}
            QTabBar::tab:hover {{
                background-color: {settings.theme.surface_hover};
            }}
        """)

        # Active positions tab
        self.positions_table = self.create_positions_table()
        tabs.addTab(self.positions_table, "Active Positions")

        # History tab
        self.history_table = self.create_history_table()
        tabs.addTab(self.history_table, "History")

        layout.addWidget(tabs)

    def create_pnl_summary(self) -> QFrame:
        """Create P/L summary section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border: 1px solid {settings.theme.border_color};
                border-radius: 8px;
                padding: 12px 16px;
            }}
        """)

        layout = QHBoxLayout(frame)
        layout.setSpacing(20)

        # Total P/L
        self.total_pnl_label = QLabel("Total P/L: $0.00")
        self.total_pnl_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 700;
                font-family: {settings.theme.font_family_mono};
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(self.total_pnl_label)

        layout.addStretch()

        # Open positions count
        self.positions_count_label = QLabel("Positions: 0")
        self.positions_count_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(self.positions_count_label)

        return frame

    def create_positions_table(self) -> QTableWidget:
        """Create active positions table"""

        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            'Ticket', 'Type', 'Size', 'Entry', 'Current', 'P/L', 'Action'
        ])

        # Table styling
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {settings.theme.surface};
                gridline-color: {settings.theme.border_color};
                border: none;
                border-radius: 8px;
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_sm}px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {settings.theme.border_color};
            }}
            QTableWidget::item:selected {{
                background-color: {settings.theme.accent};
                color: {settings.theme.background};
            }}
            QHeaderView::section {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_secondary};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {settings.theme.border_color_light};
                font-weight: 600;
                font-size: {settings.theme.font_size_sm}px;
            }}
        """)

        # Column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Ticket
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Entry
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Current
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # P/L
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Action

        # No vertical header
        table.verticalHeader().setVisible(False)

        # Alternating row colors
        table.setAlternatingRowColors(True)

        return table

    def create_history_table(self) -> QTableWidget:
        """Create order history table"""

        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            'Ticket', 'Type', 'Size', 'Entry', 'Exit', 'P/L', 'Time'
        ])

        # Same styling as positions table
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {settings.theme.surface};
                gridline-color: {settings.theme.border_color};
                border: none;
                border-radius: 8px;
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_sm}px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {settings.theme.border_color};
            }}
            QTableWidget::item:selected {{
                background-color: {settings.theme.accent};
                color: {settings.theme.background};
            }}
            QHeaderView::section {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_secondary};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {settings.theme.border_color_light};
                font-weight: 600;
                font-size: {settings.theme.font_size_sm}px;
            }}
        """)

        # Column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # No vertical header
        table.verticalHeader().setVisible(False)

        # Alternating row colors
        table.setAlternatingRowColors(True)

        return table

    def update_positions(self):
        """Update positions table with latest data"""

        try:
            # Get positions from data manager
            positions = data_manager.get_positions()

            # Update count and total P/L
            self.positions_count_label.setText(f"Positions: {len(positions)}")

            total_pnl = sum(pos.get('profit', 0) for pos in positions)
            pnl_color = settings.theme.success if total_pnl >= 0 else settings.theme.danger

            self.total_pnl_label.setText(f"Total P/L: ${total_pnl:+.2f}")
            self.total_pnl_label.setStyleSheet(f"""
                QLabel {{
                    color: {pnl_color};
                    font-size: {settings.theme.font_size_md}px;
                    font-weight: 700;
                    font-family: {settings.theme.font_family_mono};
                    background: transparent;
                    border: none;
                }}
            """)

            # Clear and repopulate table
            self.positions_table.setRowCount(0)

            for row, pos in enumerate(positions):
                self.positions_table.insertRow(row)

                # Ticket
                ticket_item = QTableWidgetItem(str(pos.get('ticket', '')))
                ticket_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.positions_table.setItem(row, 0, ticket_item)

                # Type (BUY/SELL)
                order_type = pos.get('type', 'UNKNOWN')
                type_item = QTableWidgetItem(order_type)
                type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if order_type == 'BUY':
                    type_item.setForeground(QColor(settings.theme.success))
                elif order_type == 'SELL':
                    type_item.setForeground(QColor(settings.theme.danger))

                self.positions_table.setItem(row, 1, type_item)

                # Size
                size_item = QTableWidgetItem(f"{pos.get('volume', 0):.2f}")
                size_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.positions_table.setItem(row, 2, size_item)

                # Entry price
                entry_item = QTableWidgetItem(f"{pos.get('price_open', 0):.5f}")
                entry_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.positions_table.setItem(row, 3, entry_item)

                # Current price
                current_item = QTableWidgetItem(f"{pos.get('price_current', 0):.5f}")
                current_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.positions_table.setItem(row, 4, current_item)

                # P/L
                profit = pos.get('profit', 0)
                pnl_item = QTableWidgetItem(f"${profit:+.2f}")
                pnl_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                if profit >= 0:
                    pnl_item.setForeground(QColor(settings.theme.success))
                else:
                    pnl_item.setForeground(QColor(settings.theme.danger))

                self.positions_table.setItem(row, 5, pnl_item)

                # Close button
                close_btn = QPushButton("✕ Close")
                close_btn.setProperty('ticket', pos.get('ticket'))
                close_btn.clicked.connect(lambda checked, t=pos.get('ticket'): self.close_position(t))
                close_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {settings.theme.danger};
                        color: {settings.theme.background};
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-size: {settings.theme.font_size_xs}px;
                        font-weight: 600;
                    }}
                    QPushButton:hover {{
                        background-color: {settings.theme.danger};
                    }}
                """)
                self.positions_table.setCellWidget(row, 6, close_btn)

        except Exception as e:
            logger.exception(f"Error updating positions table: {e}")

    def close_position(self, ticket: int):
        """Request position close"""

        logger.info(f"Close position requested: {ticket}")
        self.close_position_requested.emit(ticket)

    def close_all_positions(self):
        """Request closing all positions"""

        positions = data_manager.get_positions()
        if not positions:
            logger.info("No positions to close")
            return

        logger.warning(f"Close all positions requested ({len(positions)} positions)")

        # Emit close signal for each position
        for pos in positions:
            self.close_position_requested.emit(pos.get('ticket'))
