"""
设置对话框 - 配置应用程序设置
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QWidget, QLabel, QLineEdit, QPushButton, QGroupBox, 
                            QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    """设置对话框类"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        layout = QVBoxLayout(self)

        api_settings_group = QGroupBox("API 设置")
        api_settings_layout = QVBoxLayout(api_settings_group)
        
        deepseek_group = QGroupBox("DeepSeek API")
        deepseek_layout = QFormLayout(deepseek_group)
        
        self.deepseek_api_key = QLineEdit()
        self.deepseek_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.deepseek_api_key.setPlaceholderText("输入您的DeepSeek API密钥")
        deepseek_layout.addRow("API密钥:", self.deepseek_api_key)
        
        api_settings_layout.addWidget(deepseek_group)
        
        openrouter_group = QGroupBox("OpenRouter API")
        openrouter_layout = QFormLayout(openrouter_group)
        
        self.openrouter_api_key = QLineEdit()
        self.openrouter_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openrouter_api_key.setPlaceholderText("输入您的OpenRouter API密钥")
        openrouter_layout.addRow("API密钥:", self.openrouter_api_key)
        
        api_settings_layout.addWidget(openrouter_group)
        
        layout.addWidget(api_settings_group)
        
        layout.addStretch()
        
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept_settings)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self.apply_settings)
        
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
    
    def _show_styled_message(self, title: str, text: str, msg_type: str = "information"):
        from .styles.modern_theme import ModernTheme
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        
        if msg_type == "critical":
            msg_box.setIcon(QMessageBox.Icon.Critical)
        elif msg_type == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
        elif msg_type == "information":
            msg_box.setIcon(QMessageBox.Icon.Information)
        
        msg_box.setStyleSheet(ModernTheme.get_messagebox_style())
        msg_box.exec()
    
    def load_settings(self):
        deepseek_key = self.config_manager.get_api_key("deepseek")
        if deepseek_key:
            self.deepseek_api_key.setText(deepseek_key)
        
        openrouter_key = self.config_manager.get_api_key("openrouter")
        if openrouter_key:
            self.openrouter_api_key.setText(openrouter_key)
    
    def apply_settings(self):
        try:
            deepseek_key = self.deepseek_api_key.text().strip()
            if deepseek_key:
                self.config_manager.set_api_key("deepseek", deepseek_key)
            
            openrouter_key = self.openrouter_api_key.text().strip()
            if openrouter_key:
                self.config_manager.set_api_key("openrouter", openrouter_key)
            
            self._show_styled_message("成功", "设置已保存", "information")
            
        except Exception as e:
            self._show_styled_message("错误", f"保存设置失败: {str(e)}", "critical")
    
    def accept_settings(self):
        self.apply_settings()
        self.accept()
