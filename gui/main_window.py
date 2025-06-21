"""
主窗口 - Corsie AI对话软件的主界面
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QMenuBar, QMenu, QStatusBar,
                            QMessageBox, QFileDialog, QApplication, QDialog)
from PyQt6.QtCore import Qt, QTimer, QSettings, pyqtSignal
from PyQt6.QtGui import QIcon, QKeySequence, QAction, QFont

from gui.chat_widget import ChatWidget
from gui.session_panel import SessionPanel  
from gui.settings_dialog import SettingsDialog
from gui.styles import ModernTheme
from core.config_manager import ConfigManager
from core.database import DatabaseManager
from core.session_manager import SessionManager
from core.ai_client import AIClientManager

class MainWindow(QMainWindow):
    """主窗口类"""
    
    session_changed = pyqtSignal(str)
    message_sent = pyqtSignal(str)
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        
        self.config_manager = config_manager
        self.db_manager = DatabaseManager()
        self.session_manager = SessionManager(self.db_manager)
        self.ai_client_manager = AIClientManager(self.config_manager)
        
        self.settings = QSettings("Corsie", "AI Chat")
        self.init_ui()
        self.create_menus()
        self.setup_shortcuts()
        self.connect_signals()
        
        self.load_window_settings()
        self.apply_modern_theme()
        
        self.init_first_session()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Corsie")
        self.setMinimumSize(800, 600)
        
        icon_path = Path(__file__).parent.parent / "icon" / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)
        
        self.session_panel = SessionPanel(self.session_manager)
        self.session_panel.setMaximumWidth(400)
        self.session_panel.setMinimumWidth(200)
        
        self.chat_widget = ChatWidget(
            self.session_manager, 
            self.ai_client_manager,
            self.config_manager
        )
        
        self.splitter.addWidget(self.session_panel)
        self.splitter.addWidget(self.chat_widget)
        
        sidebar_width = self.config_manager.get("ui_settings.sidebar_width", 300)
        new_sidebar_width = int(sidebar_width * 2 / 3)
        self.splitter.setSizes([new_sidebar_width, 800])
        
        sidebar_visible = self.config_manager.get("ui_settings.sidebar_visible", True)
        self.session_panel.setVisible(sidebar_visible)
    
    def create_menus(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("文件(&F)")
        
        new_action = QAction("新建会话(&N)", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.setIcon(self.get_icon("add"))
        new_action.triggered.connect(self.new_session)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("导出会话(&E)", self)
        export_action.triggered.connect(self.export_current_session)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()

        self.stop_action = QAction("停止生成(&S)", self)
        self.stop_action.setIcon(self.get_icon("stop"))
        self.stop_action.setShortcut(QKeySequence("Esc"))
        self.stop_action.triggered.connect(self.stop_generation)
        self.stop_action.setEnabled(False)
        file_menu.addAction(self.stop_action)
        
        clear_action = QAction("清除当前会话(&C)", self)
        clear_action.setIcon(self.get_icon("clear"))
        clear_action.triggered.connect(self.clear_current_session)
        file_menu.addAction(clear_action)

        file_menu.addSeparator()

        settings_action = QAction("设置(&P)", self)        
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.setIcon(self.get_icon("setting"))
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)

        view_menu = menubar.addMenu("查看(&V)")
        
        toggle_sidebar_action = QAction("切换侧边栏(&S)", self)
        toggle_sidebar_action.setShortcut(QKeySequence("Ctrl+B"))
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)
        
        fullscreen_action = QAction("全屏(&F)", self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        self.model_menu = menubar.addMenu("模型选择(&M)")
        self.create_model_menu()
        
        help_menu = menubar.addMenu("帮助(&H)")
        
        user_docs_action = QAction("用户文档(&D)", self)
        user_docs_action.triggered.connect(self.show_user_docs)
        help_menu.addAction(user_docs_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("关于Corsie(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_shortcuts(self):
        """设置快捷键"""
        shortcuts = self.config_manager.get("shortcuts", {})
        
        pass
    
    def connect_signals(self):
        """连接信号和槽"""
        self.session_panel.session_selected.connect(self.on_session_selected)
        self.session_panel.session_deleted.connect(self.on_session_deleted)
        
        self.chat_widget.message_sent.connect(self.on_message_sent)
        self.chat_widget.generation_started.connect(self.on_generation_started)
        self.chat_widget.generation_finished.connect(self.on_generation_finished)
        self.chat_widget.session_renamed.connect(self.session_panel.refresh_sessions)
    
    def get_icon(self, name: str) -> QIcon:
        """获取图标"""
        icon_path = Path(__file__).parent.parent / "icon" / f"{name}.svg"
        if icon_path.exists():
            return QIcon(str(icon_path))
        return QIcon()
    
    def apply_modern_theme(self):
        font_family = self.config_manager.get("ui_settings.font_family", "-apple-system")
        font_size = self.config_manager.get("ui_settings.font_size", 13)
        
        font = QFont(font_family, font_size)
        font.setStyleHint(QFont.StyleHint.System)
        self.setFont(font)
        QApplication.instance().setFont(font)
        
        self.setStyleSheet(ModernTheme.get_complete_style())
    
    def apply_theme(self):
        self.apply_modern_theme()
    
    def load_window_settings(self):
        geometry = self.config_manager.get("ui_settings.window_geometry", {})
        
        if geometry:
            self.resize(geometry.get("width", 1200), geometry.get("height", 800))
            self.move(geometry.get("x", 100), geometry.get("y", 100))
    
    def save_window_settings(self):
        geometry = self.geometry()
        self.config_manager.set("ui_settings.window_geometry", {
            "width": geometry.width(),
            "height": geometry.height(),
            "x": geometry.x(),
            "y": geometry.y()
        })
        
        if self.splitter.sizes():
            self.config_manager.set("ui_settings.sidebar_width", self.splitter.sizes()[0])
        
        self.config_manager.set("ui_settings.sidebar_visible", self.session_panel.isVisible())
    
    def init_first_session(self):
        sessions = self.session_manager.get_all_sessions(limit=1)
        if sessions:
            latest_session = sessions[0]
            self.session_panel.refresh_sessions()
            self.session_panel.select_session(latest_session.id)
        else:
            session = self.session_manager.create_new_session("欢迎使用Corsie")
            self.session_panel.refresh_sessions()
            self.session_panel.select_session(session.id)
    
    def new_session(self):
        """新建会话"""
        session = self.session_manager.create_new_session()
        self.session_panel.refresh_sessions()
        self.session_panel.select_session(session.id)
    
    def on_session_selected(self, session_id: str):
        self.session_manager.switch_to_session(session_id)
        self.chat_widget.load_session(session_id)
        self.session_changed.emit(session_id)
        self.update_model_menu_selection()
    
    def on_session_deleted(self, session_id: str):
        if self.session_manager.current_session_id is None:
            sessions = self.session_manager.get_all_sessions(limit=1)
            if sessions:
                self.session_panel.select_session(sessions[0].id)
            else:
                self.new_session()
    
    def on_message_sent(self, message: str):
        self.message_sent.emit(message)
    
    def on_generation_started(self):
        self.stop_action.setEnabled(True)
    
    def on_generation_finished(self):
        self.stop_action.setEnabled(False)
    
    def stop_generation(self):
        self.chat_widget.stop_generation()
    
    def clear_current_session(self):
        """清除当前会话"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("确认清除")
        msg_box.setText("确定要清除当前会话的所有消息吗？")
        msg_box.setInformativeText("此操作不可撤销。")
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        yes_button = msg_box.addButton("确定", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("取消", QMessageBox.ButtonRole.NoRole)
        
        msg_box.setStyleSheet(ModernTheme.get_messagebox_style())
        
        msg_box.exec()
        reply = msg_box.clickedButton()
        
        if reply == yes_button:
            self.chat_widget.clear_session()
    
    def toggle_sidebar(self):
        visible = not self.session_panel.isVisible()
        self.session_panel.setVisible(visible)
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            self.apply_theme()
            self.chat_widget.refresh_settings()
    
    def export_current_session(self):
        current_session = self.session_manager.get_current_session()
        if not current_session:
            self._show_styled_message("警告", "没有可导出的会话。", "warning")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出会话",
            f"{current_session.title}.md",
            "Markdown files (*.md);;All files (*.*)"
        )
        
        if file_path:
            try:
                content = self.session_manager.export_session_to_markdown(current_session.id)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._show_styled_message("成功", f"会话已导出到: {file_path}", "information")
            except Exception as e:
                self._show_styled_message("错误", f"导出失败: {str(e)}", "critical")
    
    def show_user_docs(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
        
        docs_dialog = QDialog(self)
        docs_dialog.setWindowTitle("用户文档")
        docs_dialog.resize(800, 600)
        
        layout = QVBoxLayout(docs_dialog)
        
        docs_text = QTextEdit()
        docs_text.setReadOnly(True)
        docs_text.setHtml("""
        <h1>Corsie AI 用户文档</h1>
        
        <h2>网络要求</h2>
        <p>部分OpenRouter模型需要特殊的网络环境才能正常使用：</p>
        
        <h3>🌐 需要VPN的模型</h3>
        <ul>
            <li><strong>OpenAI系列模型</strong>（如 ChatGPT-4o等）
                <ul>
                    <li>需要VPN连接</li>
                    <li><span style="color: red; font-weight: bold;">特别注意：必须在香港以外的区域使用</span></li>
                    <li>推荐使用美国、欧洲等地区的VPN节点</li>
                </ul>
            </li>
            <li><strong>Grok系列模型</strong>（如 Grok-3等）
                <ul>
                    <li>需要VPN连接</li>
                    <li>推荐使用美国地区的VPN节点</li>
                </ul>
            </li>
        </ul>
        
        <h3>✅ 无需VPN的模型</h3>
        <ul>
            <li><strong>DeepSeek系列模型</strong>（直接访问或OpenRouter代理）</li>
            <li><strong>Claude系列模型</strong>（通过OpenRouter）</li>
            <li><strong>Gemini系列模型</strong>（通过OpenRouter）</li>
        </ul>
        
        <h2>使用建议</h2>
        <ul>
            <li>如果您在中国大陆使用，建议优先选择DeepSeek或Claude模型</li>
            <li>如需使用OpenAI模型，请确保VPN连接稳定且节点位于香港以外地区</li>
            <li>网络不稳定时可能出现连接超时，请稍后重试</li>
        </ul>
        
        <h2>API密钥配置</h2>
        <p>在菜单栏 <strong>文件 → 设置</strong> 中配置您的API密钥：</p>
        <ul>
            <li><strong>DeepSeek API密钥</strong>：用于DeepSeek模型</li>
            <li><strong>OpenRouter API密钥</strong>：用于所有OpenRouter代理的模型</li>
        </ul>
        
        <h2>常用快捷键</h2>
        <ul>
            <li><strong>Ctrl+N</strong>：新建对话</li>
            <li><strong>Ctrl+Enter</strong>：发送消息</li>
            <li><strong>Esc</strong>：停止生成</li>
            <li><strong>Ctrl+,</strong>：打开设置</li>
            <li><strong>Ctrl+B</strong>：切换侧边栏</li>
        </ul>
        """)
        
        layout.addWidget(docs_text)
        
        button_layout = QHBoxLayout()
        close_button = QPushButton("关闭")
        close_button.clicked.connect(docs_dialog.accept)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY_BLUE};
                color: white;
                border: none;
                border-radius: {ModernTheme.RADIUS_SMALL};
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color:
            }}
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        docs_dialog.setStyleSheet(f"""
            QDialog {{
                background-color: white;
                color: black;
            }}
            QTextEdit {{
                background-color: white;
                border: 1px solid {ModernTheme.BORDER_LIGHT};
                border-radius: {ModernTheme.RADIUS_SMALL};
                padding: 16px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                font-size: 14px;
                line-height: 1.5;
            }}
        """)
        
        docs_dialog.exec()
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于Corsie",
            "<h3>Corsie AI对话助手</h3>"
            "<p>版本: 1.0.0</p>"
            "<p>一个现代化的AI对话应用程序，支持多种AI模型。</p>"
            "<p>基于PyQt6和QMarkdownWidget构建。</p>"
            "<p>Copyright © 2025 wsh. All rights reserved.</p>"
        )
    
    def create_model_menu(self):
        """创建模型选择菜单"""
        self.model_menu.clear()
        self.model_actions = {}
        
        available_models = self.ai_client_manager.get_available_models()
        
        if not available_models:
            no_models_action = QAction("无可用模型", self)
            no_models_action.setEnabled(False)
            self.model_menu.addAction(no_models_action)
            return
        
        current_model = self.get_current_session_model()
        
        models_by_provider = {}
        for model in available_models:
            provider = model.provider
            if provider not in models_by_provider:
                models_by_provider[provider] = []
            models_by_provider[provider].append(model)
        
        for provider, models in models_by_provider.items():
            provider_menu = self.model_menu.addMenu(f"{provider}")
            
            for model in models:
                model_key = f"{provider.lower()}/{model.model_id}"
                action = QAction(f"{model.name}", self)
                action.setCheckable(True)
                action.setChecked(current_model == model_key)
                action.triggered.connect(lambda checked, m=model_key: self.on_model_selected(m))
                
                tooltip = f"模型: {model.model_id}\n"
                tooltip += f"最大令牌: {model.max_tokens}\n"
                tooltip += f"支持流式: {'是' if model.supports_streaming else '否'}"
                if model.cost_per_token:
                    tooltip += f"\n每令牌成本: ${model.cost_per_token:.6f}"
                action.setToolTip(tooltip)
                
                provider_menu.addAction(action)
                self.model_actions[model_key] = action
        
        self.model_menu.addSeparator()
        refresh_action = QAction("刷新模型列表", self)
        refresh_action.setIcon(self.get_icon("refresh"))
        refresh_action.triggered.connect(self.refresh_model_menu)
        self.model_menu.addAction(refresh_action)
    
    def get_current_session_model(self) -> str:
        current_session = self.session_manager.get_current_session()
        if current_session and current_session.ai_model:
            return current_session.ai_model
        return self.config_manager.get("ai_settings.default_model", "deepseek/deepseek-chat")
    
    def on_model_selected(self, model_key: str):
        for key, action in self.model_actions.items():
            action.setChecked(key == model_key)
        
        current_session = self.session_manager.get_current_session()
        if current_session:
            success = self.session_manager.update_session_model(current_session.id, model_key)
            if success:
                self.ai_client_manager.clear_cache()
                self.chat_widget.update_model_label()
                print(f"已切换到模型: {model_key}")
            else:
                print(f"切换模型失败: {model_key}")
                old_model = self.get_current_session_model()
                if old_model in self.model_actions:
                    self.model_actions[old_model].setChecked(True)
                if model_key in self.model_actions:
                    self.model_actions[model_key].setChecked(False)
        else:
            self.config_manager.set("ai_settings.default_model", model_key)
            print(f"已设置默认模型: {model_key}")
    
    def refresh_model_menu(self):
        self.create_model_menu()
    
    def update_model_menu_selection(self):
        if not hasattr(self, 'model_actions'):
            return
            
        current_model = self.get_current_session_model()
        
        for key, action in self.model_actions.items():
            action.setChecked(key == current_model)
    
    def _show_styled_message(self, title: str, text: str, msg_type: str = "information"):
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
    
    def closeEvent(self, event):
        self.save_window_settings()
        
        self.chat_widget.stop_generation()
        
        event.accept()
