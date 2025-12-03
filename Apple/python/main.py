#!/usr/bin/env python3
"""
AppleTrader Pro - Main Application Entry Point
Institutional-Grade Trading Platform for MT5

Usage:
    python main.py
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from config import settings
from utils.logger import logger
from gui.main_window import MainWindow


def main():
    """Main application entry point"""

    # Print banner
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     🍎  A P P L E T R A D E R   P R O   v1.0                ║
    ║                                                               ║
    ║           Institutional Trading Platform for MT5              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    logger.info("═" * 60)
    logger.info(f"  {settings.app.app_name} v{settings.app.version}")
    logger.info("  Institutional Trading Platform")
    logger.info("═" * 60)

    # Create Qt application
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName(settings.app.app_name)
    app.setApplicationVersion(settings.app.version)
    app.setOrganizationName("AppleTrader")

    # Note: AA_UseHighDpiPixmaps is deprecated in PyQt6 - high DPI support is enabled by default

    # Set application-wide stylesheet (dark theme)
    app.setStyleSheet(get_application_stylesheet())

    logger.info("✓ Qt Application initialized")

    # Create and show main window
    try:
        main_window = MainWindow()
        main_window.show()

        logger.info("✓ Main window created")
        logger.info("✓ Application ready")
        logger.info("")
        logger.info("→ Connect to MT5 and attach AppleTrader EA to start trading")
        logger.info("")

        # Run application event loop
        sys.exit(app.exec())

    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


def get_application_stylesheet() -> str:
    """
    Get the application-wide stylesheet
    Returns dark institutional theme CSS
    """
    theme = settings.theme

    return f"""
    /* Global styles */
    * {{
        font-family: {theme.font_family_main}, sans-serif;
        font-size: {theme.font_size_md}px;
        color: {theme.text_primary};
    }}

    /* Main window and widgets */
    QMainWindow, QWidget {{
        background-color: {theme.background};
        color: {theme.text_primary};
    }}

    /* Panel backgrounds */
    QFrame {{
        background-color: {theme.surface};
        border: 1px solid {theme.border_color};
        border-radius: 6px;
    }}

    /* Scroll bars */
    QScrollBar:vertical {{
        background: {theme.surface};
        width: 12px;
        margin: 0px;
    }}

    QScrollBar::handle:vertical {{
        background: {theme.surface_light};
        min-height: 20px;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {theme.surface_hover};
    }}

    QScrollBar:horizontal {{
        background: {theme.surface};
        height: 12px;
        margin: 0px;
    }}

    QScrollBar::handle:horizontal {{
        background: {theme.surface_light};
        min-width: 20px;
        border-radius: 6px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: {theme.surface_hover};
    }}

    QScrollBar::add-line, QScrollBar::sub-line {{
        border: none;
        background: none;
    }}

    /* Push buttons */
    QPushButton {{
        background-color: {theme.button_secondary};
        color: {theme.text_primary};
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: bold;
    }}

    QPushButton:hover {{
        background-color: {theme.accent};
    }}

    QPushButton:pressed {{
        background-color: {theme.accent_secondary};
    }}

    QPushButton:disabled {{
        background-color: {theme.button_disabled};
        color: {theme.text_disabled};
    }}

    /* Primary button */
    QPushButton[class="primary"] {{
        background-color: {theme.button_primary};
    }}

    QPushButton[class="primary"]:hover {{
        background-color: {theme.success};
    }}

    /* Danger button */
    QPushButton[class="danger"] {{
        background-color: {theme.button_danger};
    }}

    QPushButton[class="danger"]:hover {{
        background-color: {theme.danger};
    }}

    /* Check boxes */
    QCheckBox {{
        spacing: 8px;
        color: {theme.text_primary};
    }}

    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
        border: 2px solid {theme.border_color_light};
        border-radius: 4px;
        background-color: {theme.surface};
    }}

    QCheckBox::indicator:checked {{
        background-color: {theme.button_primary};
        border-color: {theme.button_primary};
    }}

    QCheckBox::indicator:hover {{
        border-color: {theme.accent};
    }}

    /* Sliders */
    QSlider::groove:horizontal {{
        background: {theme.surface_light};
        height: 6px;
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        background: {theme.accent};
        border: none;
        width: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }}

    QSlider::handle:horizontal:hover {{
        background: {theme.button_primary};
    }}

    /* Labels */
    QLabel {{
        color: {theme.text_primary};
        background: transparent;
        border: none;
    }}

    /* Line edits */
    QLineEdit {{
        background-color: {theme.surface_light};
        color: {theme.text_primary};
        border: 1px solid {theme.border_color};
        border-radius: 4px;
        padding: 8px;
    }}

    QLineEdit:focus {{
        border-color: {theme.accent};
    }}

    /* Combo boxes */
    QComboBox {{
        background-color: {theme.surface_light};
        color: {theme.text_primary};
        border: 1px solid {theme.border_color};
        border-radius: 4px;
        padding: 8px;
    }}

    QComboBox:hover {{
        border-color: {theme.accent};
    }}

    QComboBox::drop-down {{
        border: none;
    }}

    QComboBox::down-arrow {{
        width: 12px;
        height: 12px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {theme.surface_light};
        color: {theme.text_primary};
        selection-background-color: {theme.accent};
        border: 1px solid {theme.border_color};
    }}

    /* Tabs */
    QTabWidget::pane {{
        border: 1px solid {theme.border_color};
        border-radius: 6px;
        background-color: {theme.surface};
    }}

    QTabBar::tab {{
        background-color: {theme.surface};
        color: {theme.text_secondary};
        border: 1px solid {theme.border_color};
        padding: 10px 20px;
        margin-right: 2px;
    }}

    QTabBar::tab:selected {{
        background-color: {theme.surface_light};
        color: {theme.text_primary};
        border-bottom-color: {theme.accent};
    }}

    QTabBar::tab:hover {{
        background-color: {theme.surface_hover};
    }}

    /* Tables */
    QTableWidget {{
        background-color: {theme.surface};
        gridline-color: {theme.border_color};
        border: 1px solid {theme.border_color};
        border-radius: 6px;
    }}

    QTableWidget::item {{
        padding: 8px;
        color: {theme.text_primary};
    }}

    QTableWidget::item:selected {{
        background-color: {theme.accent};
        color: {theme.background};
    }}

    QHeaderView::section {{
        background-color: {theme.surface_light};
        color: {theme.text_primary};
        padding: 10px;
        border: none;
        border-bottom: 2px solid {theme.border_color_light};
        font-weight: bold;
    }}

    /* Tooltips */
    QToolTip {{
        background-color: {theme.surface_light};
        color: {theme.text_primary};
        border: 1px solid {theme.border_color_light};
        border-radius: 4px;
        padding: 6px;
    }}

    /* Status bar */
    QStatusBar {{
        background-color: {theme.surface};
        color: {theme.text_secondary};
        border-top: 1px solid {theme.border_color};
    }}

    /* Menu bar */
    QMenuBar {{
        background-color: {theme.surface};
        color: {theme.text_primary};
        border-bottom: 1px solid {theme.border_color};
    }}

    QMenuBar::item {{
        padding: 8px 15px;
        background: transparent;
    }}

    QMenuBar::item:selected {{
        background-color: {theme.surface_hover};
    }}

    QMenu {{
        background-color: {theme.surface_light};
        color: {theme.text_primary};
        border: 1px solid {theme.border_color};
    }}

    QMenu::item {{
        padding: 8px 30px;
    }}

    QMenu::item:selected {{
        background-color: {theme.accent};
        color: {theme.background};
    }}

    /* Splitter */
    QSplitter::handle {{
        background-color: {theme.border_color};
    }}

    QSplitter::handle:hover {{
        background-color: {theme.accent};
    }}

    /* Progress bar */
    QProgressBar {{
        background-color: {theme.surface_light};
        border: 1px solid {theme.border_color};
        border-radius: 4px;
        text-align: center;
        color: {theme.text_primary};
    }}

    QProgressBar::chunk {{
        background-color: {theme.button_primary};
        border-radius: 3px;
    }}
    """


if __name__ == "__main__":
    main()
