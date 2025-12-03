"""
AppleTrader Pro - Commentary Panel
Real-time trading commentary feed with auto-scrolling
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat

from datetime import datetime
from collections import deque

from config import settings, PRIORITY_CRITICAL, PRIORITY_IMPORTANT, PRIORITY_INFO
from utils.logger import logger
from analysis.trading_commentary import commentary_generator


class CommentaryPanel(QWidget):
    """
    Real-time trading commentary feed
    Features:
    - Auto-scrolling commentary
    - Color-coded priority levels
    - Timestamps
    - Search/filter functionality
    - Export capability
    """

    def __init__(self):
        super().__init__()

        # Commentary buffer
        self.commentary_buffer = deque(maxlen=1000)

        self.init_ui()

        # Setup auto-update timer for live commentary
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_live_commentary)
        self.update_timer.start(10000)  # Update every 10 seconds

        # Generate initial commentary
        self.update_live_commentary()

        logger.info("Commentary panel initialized with live updates")

    def init_ui(self):
        """Initialize user interface"""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ============================================================
        # HEADER
        # ============================================================
        header_layout = QHBoxLayout()

        header = QLabel("💬 TRADING COMMENTARY")
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

        # Clear button
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_commentary)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {settings.theme.text_secondary};
                border: 1px solid {settings.theme.border_color};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: {settings.theme.font_size_sm}px;
            }}
            QPushButton:hover {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                border-color: {settings.theme.accent};
            }}
        """)
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # ============================================================
        # SEARCH/FILTER BAR
        # ============================================================
        search_layout = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search commentary...")
        self.search_box.textChanged.connect(self.filter_commentary)
        self.search_box.setStyleSheet(f"""
            QLineEdit {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                border: 1px solid {settings.theme.border_color};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: {settings.theme.font_size_sm}px;
            }}
            QLineEdit:focus {{
                border-color: {settings.theme.accent};
            }}
        """)
        search_layout.addWidget(self.search_box)

        layout.addLayout(search_layout)

        # ============================================================
        # COMMENTARY TEXT AREA (HTML SUPPORTED)
        # ============================================================
        self.commentary_text = QTextEdit()
        self.commentary_text.setReadOnly(True)
        self.commentary_text.setAcceptRichText(True)  # Enable HTML
        self.commentary_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {settings.theme.surface};
                color: {settings.theme.text_primary};
                border: 1px solid {settings.theme.border_color};
                border-radius: 8px;
                padding: 12px;
                font-family: {settings.theme.font_family_mono};
                font-size: {settings.theme.font_size_sm}px;
                line-height: 1.6;
            }}
        """)
        layout.addWidget(self.commentary_text)

    def add_comment(self, message: str, priority: int = PRIORITY_INFO):
        """
        Add commentary message

        Args:
            message: Commentary text
            priority: Priority level (CRITICAL, IMPORTANT, INFO)
        """

        # Add to buffer
        timestamp = datetime.now()
        self.commentary_buffer.append({
            'timestamp': timestamp,
            'message': message,
            'priority': priority
        })

        # Get color based on priority
        if priority == PRIORITY_CRITICAL:
            color = settings.theme.danger
            prefix = "🔴"
        elif priority == PRIORITY_IMPORTANT:
            color = settings.theme.warning
            prefix = "🟡"
        else:
            color = settings.theme.text_primary
            prefix = "🔵"

        # Format timestamp
        time_str = timestamp.strftime("%H:%M:%S")

        # Create formatted text
        cursor = self.commentary_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Timestamp format
        timestamp_format = QTextCharFormat()
        timestamp_format.setForeground(QColor(settings.theme.text_secondary))
        timestamp_format.setFont(QFont(settings.theme.font_family_mono, settings.theme.font_size_xs))

        # Message format
        message_format = QTextCharFormat()
        message_format.setForeground(QColor(color))
        message_format.setFont(QFont(settings.theme.font_family_mono, settings.theme.font_size_sm))

        # Insert timestamp
        cursor.insertText(f"[{time_str}] ", timestamp_format)

        # Insert prefix and message
        cursor.insertText(f"{prefix} {message}\n", message_format)

        # Auto-scroll to bottom
        self.commentary_text.setTextCursor(cursor)
        self.commentary_text.ensureCursorVisible()

        # Log to file
        logger.info(f"[COMMENTARY] {message}")

    def clear_commentary(self):
        """Clear all commentary"""

        self.commentary_text.clear()
        self.commentary_buffer.clear()

        self.add_comment("Commentary cleared", PRIORITY_INFO)
        logger.info("Commentary cleared by user")

    def filter_commentary(self, search_text: str):
        """Filter commentary by search text"""

        if not search_text:
            # Show all commentary
            self.refresh_commentary()
            return

        # Clear and show filtered
        self.commentary_text.clear()

        search_lower = search_text.lower()

        for entry in self.commentary_buffer:
            if search_lower in entry['message'].lower():
                # Get color based on priority
                if entry['priority'] == PRIORITY_CRITICAL:
                    color = settings.theme.danger
                    prefix = "🔴"
                elif entry['priority'] == PRIORITY_IMPORTANT:
                    color = settings.theme.warning
                    prefix = "🟡"
                else:
                    color = settings.theme.text_primary
                    prefix = "🔵"

                time_str = entry['timestamp'].strftime("%H:%M:%S")

                cursor = self.commentary_text.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)

                timestamp_format = QTextCharFormat()
                timestamp_format.setForeground(QColor(settings.theme.text_secondary))

                message_format = QTextCharFormat()
                message_format.setForeground(QColor(color))

                cursor.insertText(f"[{time_str}] ", timestamp_format)
                cursor.insertText(f"{prefix} {entry['message']}\n", message_format)

    def refresh_commentary(self):
        """Refresh all commentary (used after filter clear)"""

        self.commentary_text.clear()

        for entry in self.commentary_buffer:
            # Get color based on priority
            if entry['priority'] == PRIORITY_CRITICAL:
                color = settings.theme.danger
                prefix = "🔴"
            elif entry['priority'] == PRIORITY_IMPORTANT:
                color = settings.theme.warning
                prefix = "🟡"
            else:
                color = settings.theme.text_primary
                prefix = "🔵"

            time_str = entry['timestamp'].strftime("%H:%M:%S")

            cursor = self.commentary_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)

            timestamp_format = QTextCharFormat()
            timestamp_format.setForeground(QColor(settings.theme.text_secondary))

            message_format = QTextCharFormat()
            message_format.setForeground(QColor(color))

            cursor.insertText(f"[{time_str}] ", timestamp_format)
            cursor.insertText(f"{prefix} {entry['message']}\n", message_format)

    def export_commentary(self, filename: str):
        """Export commentary to file"""

        try:
            with open(filename, 'w') as f:
                f.write("AppleTrader Pro - Commentary Export\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")

                for entry in self.commentary_buffer:
                    time_str = entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                    priority_str = {
                        PRIORITY_CRITICAL: "CRITICAL",
                        PRIORITY_IMPORTANT: "IMPORTANT",
                        PRIORITY_INFO: "INFO"
                    }.get(entry['priority'], "UNKNOWN")

                    f.write(f"[{time_str}] [{priority_str}] {entry['message']}\n")

            logger.info(f"Commentary exported to: {filename}")
            self.add_comment(f"Commentary exported to {filename}", PRIORITY_INFO)

        except Exception as e:
            logger.exception(f"Error exporting commentary: {e}")
            self.add_comment(f"Export failed: {e}", PRIORITY_CRITICAL)

    def update_live_commentary(self):
        """Update with live institutional trading commentary"""
        try:
            # Generate fresh commentary
            commentary_data = commentary_generator.generate_commentary()

            # Format as HTML
            html_content = commentary_generator.format_commentary_html(commentary_data)

            # Display in text widget
            self.commentary_text.setHtml(html_content)

            # Auto-scroll to top to show current analysis
            cursor = self.commentary_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.commentary_text.setTextCursor(cursor)

            logger.debug("Live commentary updated")

        except Exception as e:
            logger.exception(f"Error updating live commentary: {e}")
            self.commentary_text.setHtml(f"""
            <div style="color: #EF4444; font-family: monospace; padding: 20px;">
                ⚠️ Commentary Update Error: {str(e)}
                <br><br>
                Retrying in 10 seconds...
            </div>
            """)
