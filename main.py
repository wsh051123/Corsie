import sys
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from gui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from core.config_manager import ConfigManager

def main():
    

    app = QApplication(sys.argv)
    

    app.setApplicationName("Corsie")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Corsie Team")
    

    icon_path = PROJECT_ROOT / "icon" / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    

    config_manager = ConfigManager()
    

    main_window = MainWindow(config_manager)
    main_window.show()
    

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
