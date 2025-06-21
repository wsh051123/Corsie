"""
现代化主题样式
"""

class ModernTheme:
    
    PRIMARY_BLUE = "#0073c6"
    SECONDARY_BLUE = "#007AFF"
    SUCCESS_GREEN = "#34C759"
    WARNING_ORANGE = "#FF9500"
    ERROR_RED = "#FF3B30"
    
    BACKGROUND_PRIMARY = "#FFFFFF"
    BACKGROUND_SECONDARY = "#F2F2F7"
    BACKGROUND_TERTIARY = "#F9F9F9"
    
    TEXT_PRIMARY = "#000000"
    TEXT_SECONDARY = "#3C3C43"
    TEXT_TERTIARY = "#8E8E93"
    TEXT_PLACEHOLDER = "#C7C7CC"
    
    BORDER_LIGHT = "#E5E5EA"
    BORDER_MEDIUM = "#D1D1D6"
    DIVIDER = "#C6C6C8"
    
    CARD_BACKGROUND = "#FFFFFF"
    CARD_SHADOW = "rgba(0, 0, 0, 0.1)"
    USER_BUBBLE = "#007AFF"
    AI_BUBBLE = "#FFFFFF"
    
    HOVER_OVERLAY = "rgba(0, 0, 0, 0.05)"
    PRESSED_OVERLAY = "rgba(0, 0, 0, 0.1)"
    FOCUS_RING = "#007AFF"
    
    RADIUS_SMALL = "6px"
    RADIUS_MEDIUM = "12px"
    RADIUS_LARGE = "16px"
    RADIUS_EXTRA_LARGE = "24px"
    
    SHADOW_LIGHT = "0 1px 3px rgba(0, 0, 0, 0.1)"
    SHADOW_MEDIUM = "0 4px 12px rgba(0, 0, 0, 0.15)"
    SHADOW_HEAVY = "0 8px 25px rgba(0, 0, 0, 0.2)"
    
    @classmethod
    def get_main_window_style(cls):
        """主窗口样式"""
        return f"""
        QMainWindow {{
            background-color: {cls.BACKGROUND_PRIMARY};
            color: {cls.TEXT_PRIMARY};
        }}
        
        QMenuBar {{
            background-color: {cls.BACKGROUND_PRIMARY};
            border-bottom: 1px solid {cls.BORDER_LIGHT};
            color: {cls.TEXT_PRIMARY};
            font-size: 13px;
            padding: 4px 0px;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 12px;
            border-radius: {cls.RADIUS_SMALL};
            margin: 0px 2px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {cls.HOVER_OVERLAY};
        }}
        
        QMenuBar::item:pressed {{
            background-color: {cls.PRESSED_OVERLAY};
        }}
        
        QMenu {{
            background-color: {cls.BACKGROUND_PRIMARY};
            border: 1px solid {cls.BORDER_LIGHT};
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 8px 16px;
            color: {cls.TEXT_PRIMARY};
        }}
        
        QMenu::item:selected {{
            background-color: {cls.HOVER_OVERLAY};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {cls.BORDER_LIGHT};
            margin: 4px 0px;
        }}
        """
    
    @classmethod
    def get_button_style(cls):
        """按钮样式"""
        return f"""
        QPushButton {{
            background-color: {cls.PRIMARY_BLUE};
            color: white;
            border: none;
            border-radius: {cls.RADIUS_MEDIUM};
            padding: 12px 20px;
            font-size: 14px;
            font-weight: 500;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
        }}
        
        QPushButton:hover {{
            background-color: #0056b3;
        }}
        
        QPushButton:pressed {{
            background-color: #004494;
        }}
        
        QPushButton:disabled {{
            background-color: {cls.TEXT_PLACEHOLDER};
            color: white;
        }}
        
        QPushButton[buttonStyle="secondary"] {{
            background-color: {cls.BACKGROUND_SECONDARY};
            color: {cls.TEXT_PRIMARY};
        }}
        
        QPushButton[buttonStyle="secondary"]:hover {{
            background-color: {cls.BORDER_LIGHT};
        }}
        
        QPushButton[buttonStyle="danger"] {{
            background-color: {cls.ERROR_RED};
        }}
        
        QPushButton[buttonStyle="danger"]:hover {{
            background-color: #d70015;
        }}
        """
    
    @classmethod
    def get_input_style(cls):
        """输入框样式"""
        return f"""
        QTextEdit, QLineEdit {{
            background-color: {cls.BACKGROUND_SECONDARY};
            border: 1px solid {cls.BORDER_LIGHT};
            border-radius: {cls.RADIUS_MEDIUM};
            padding: 12px 16px;
            font-size: 14px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            color: {cls.TEXT_PRIMARY};
            selection-background-color: {cls.PRIMARY_BLUE};
        }}
        
        QTextEdit:focus, QLineEdit:focus {{
            border: 2px solid {cls.FOCUS_RING};
            background-color: {cls.BACKGROUND_PRIMARY};
        }}
        
        QTextEdit::placeholder, QLineEdit::placeholder {{
            color: {cls.TEXT_PLACEHOLDER};
        }}
        
        QScrollBar:vertical {{
            background-color: transparent;
            width: 8px;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {cls.TEXT_PLACEHOLDER};
            border-radius: 4px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {cls.TEXT_TERTIARY};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """
    
    @classmethod
    def get_list_style(cls):
        """列表样式"""
        return f"""
        QListWidget {{
            background-color: {cls.BACKGROUND_PRIMARY};
            border: none;
            border-radius: {cls.RADIUS_MEDIUM};
            padding: 8px;
        }}
        
        QListWidget::item {{
            background-color: transparent;
            border: none;
            border-radius: {cls.RADIUS_SMALL};
            padding: 12px 16px;
            margin: 2px 0px;
            color: {cls.TEXT_PRIMARY};
            font-size: 14px;
        }}
        
        QListWidget::item:hover {{
            background-color: {cls.HOVER_OVERLAY};
        }}
        
        QListWidget::item:selected {{
            background-color: {cls.PRIMARY_BLUE};
            color: white;
        }}
        """
    
    @classmethod
    def get_splitter_style(cls):
        """分割器样式"""
        return f"""
        QSplitter::handle {{
            background-color: {cls.BORDER_LIGHT};
        }}
        
        QSplitter::handle:horizontal {{
            width: 1px;
        }}
        
        QSplitter::handle:vertical {{
            height: 1px;
        }}
        """
    
    @classmethod
    def get_label_style(cls):
        """标签样式"""
        return f"""
        QLabel {{
            color: {cls.TEXT_PRIMARY};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
        }}
        
        QLabel[labelStyle="title"] {{
            font-size: 18px;
            font-weight: 600;
            color: {cls.TEXT_PRIMARY};
        }}
        
        QLabel[labelStyle="subtitle"] {{
            font-size: 14px;
            font-weight: 500;
            color: {cls.TEXT_SECONDARY};
        }}
        
        QLabel[labelStyle="caption"] {{
            font-size: 12px;
            color: {cls.TEXT_TERTIARY};
        }}
        """

    @classmethod
    def get_complete_style(cls):
        """获取完整的应用程序样式"""
        return f"""
        {cls.get_main_window_style()}
        {cls.get_button_style()}
        {cls.get_input_style()}
        {cls.get_list_style()}
        {cls.get_splitter_style()}
        {cls.get_label_style()}
        """
    
    @classmethod
    def get_messagebox_style(cls):
        """通用消息框样式"""
        return f"""
            QMessageBox {{
                background-color: white;
                color: black;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            }}
            QPushButton {{
                background-color: {cls.PRIMARY_BLUE};
                color: white;
                border: none;
                border-radius: {cls.RADIUS_SMALL};
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: #0056b3;
            }}
            QPushButton:pressed {{
                background-color: #004494;
            }}
        """ 