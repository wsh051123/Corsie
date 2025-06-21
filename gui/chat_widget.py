"""
聊天组件 - 显示对话历史和处理用户输入
"""

import asyncio
import html
import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QPushButton, QScrollArea, QLabel, QSplitter, QMenu, 
                            QApplication, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction, QClipboard
from pathlib import Path
from .styles import ModernTheme

from gui.widgets.message_bubble import MessageBubble

class ChatWidget(QWidget):
    """聊天组件类"""
    
    message_sent = pyqtSignal(str)
    generation_started = pyqtSignal()
    generation_finished = pyqtSignal()
    session_renamed = pyqtSignal()
    
    def __init__(self, session_manager, ai_client_manager, config_manager):
        super().__init__()
        self.session_manager = session_manager
        self.ai_client_manager = ai_client_manager
        self.config_manager = config_manager
        self.current_session_id = None
        self.is_generating = False
        self.streaming_response = ""
        self.last_scroll_time = 0
        self.current_ai_bubble = None
        self.message_bubbles = []
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(16, 16, 16, 16)
        self.messages_layout.setSpacing(12)
        self.messages_layout.addStretch()
        
        self.scroll_area.setWidget(self.messages_container)
        splitter.addWidget(self.scroll_area)
        
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.user_input = QTextEdit()
        self.user_input.setMaximumHeight(120)
        self.user_input.setMinimumHeight(80)
        self.user_input.setPlaceholderText("在此输入您的消息... (Ctrl+Enter发送)")
        self.user_input.setFont(QFont("Consolas", 10))
        input_layout.addWidget(self.user_input)
        
        button_layout = QHBoxLayout()
        
        self.model_label = QLabel("当前模型：deepseek-chat")
        self.model_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                padding: 8px 12px;
                font-size: 11px;
                color: #666;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        self.model_label.setMinimumHeight(35)
        self.model_label.setMaximumWidth(250)
        self.model_label.setToolTip("当前使用的AI模型")
        
        self.send_button = QPushButton("发送")
        self.send_button.setIcon(self.get_icon("send"))
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setMinimumHeight(35)
        
        self.stop_button = QPushButton("停止")
        self.stop_button.setIcon(self.get_icon("stop"))
        self.stop_button.clicked.connect(self.stop_generation)
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumHeight(35)
        
        self.clear_button = QPushButton("清除")
        self.clear_button.setIcon(self.get_icon("clear"))
        self.clear_button.clicked.connect(self.clear_session)
        self.clear_button.setMinimumHeight(35)
        
        button_layout.addWidget(self.model_label)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.send_button)
        
        input_layout.addLayout(button_layout)
        splitter.addWidget(input_container)
        
        splitter.setSizes([400, 150])
        
        self.apply_modern_styles()
    
    def apply_modern_styles(self):
        """应用现代化样式"""
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {ModernTheme.BACKGROUND_PRIMARY};
                border: none;
                border-radius: {ModernTheme.RADIUS_MEDIUM};
            }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {ModernTheme.TEXT_PLACEHOLDER};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {ModernTheme.TEXT_TERTIARY};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        self.user_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernTheme.BACKGROUND_SECONDARY};
                border: 2px solid {ModernTheme.BORDER_LIGHT};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                color: {ModernTheme.TEXT_PRIMARY};
                selection-background-color: {ModernTheme.PRIMARY_BLUE};
                line-height: 1.4;
            }}
            QTextEdit:focus {{
                border: 2px solid {ModernTheme.FOCUS_RING};
                background-color: {ModernTheme.BACKGROUND_PRIMARY};
            }}
            QTextEdit:disabled {{
                background-color: {ModernTheme.BORDER_LIGHT};
                color: {ModernTheme.TEXT_PLACEHOLDER};
                border: 2px solid {ModernTheme.BORDER_MEDIUM};
            }}
        """)
        
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY_BLUE};
                color: white;
                border: none;
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                padding: 10px 20px;
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
                background-color: {ModernTheme.TEXT_PLACEHOLDER};
                color: white;
            }}
        """)
        
        self.stop_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.WARNING_ORANGE};
                color: white;
                border: none;
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            }}
            QPushButton:hover {{
                background-color: #e6830f;
            }}
            QPushButton:pressed {{
                background-color: #cc7a0d;
            }}
            QPushButton:disabled {{
                background-color: {ModernTheme.TEXT_PLACEHOLDER};
                color: white;
            }}
        """)
        
        self.clear_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.BACKGROUND_SECONDARY};
                color: {ModernTheme.TEXT_PRIMARY};
                border: 1px solid {ModernTheme.BORDER_LIGHT};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.BORDER_LIGHT};
                border: 1px solid {ModernTheme.BORDER_MEDIUM};
            }}
            QPushButton:pressed {{
                background-color: {ModernTheme.BORDER_MEDIUM};
            }}
            QPushButton:disabled {{
                background-color: {ModernTheme.BORDER_LIGHT};
                color: {ModernTheme.TEXT_PLACEHOLDER};
                border: 1px solid {ModernTheme.BORDER_LIGHT};
            }}
        """)
        
        
    def connect_signals(self):
        """连接信号和槽"""
        self.user_input.keyPressEvent = self.on_input_key_press
        
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        clear_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        clear_shortcut.activated.connect(self.clear_display)
        
        copy_all_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        copy_all_shortcut.activated.connect(self.copy_all_content)
        
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self.export_to_markdown)
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        context_menu = QMenu(self)
        
        copy_action = QAction("复制", self)
        copy_action.setIcon(self.get_icon("copy"))
        copy_action.triggered.connect(self.copy_selection)
        copy_action.setEnabled(False)
        context_menu.addAction(copy_action)
        
        copy_all_action = QAction("复制全部", self)
        copy_all_action.triggered.connect(self.copy_all_content)
        context_menu.addAction(copy_all_action)
        
        context_menu.addSeparator()
        
        export_action = QAction("导出为Markdown", self)
        export_action.triggered.connect(self.export_to_markdown)
        context_menu.addAction(export_action)
        
        clear_action = QAction("清除显示", self)
        clear_action.setIcon(self.get_icon("clear"))
        clear_action.triggered.connect(self.clear_display)
        context_menu.addAction(clear_action)
        context_menu.exec(self.scroll_area.mapToGlobal(position))
    
    def copy_selection(self):
        pass
    
    def copy_all_content(self):
        """复制所有内容"""
        if not self.current_session_id:
            return
            
        messages = self.session_manager.get_session_messages(self.current_session_id)
        if not messages:
            return
            
        content = self._format_messages_to_text(messages)
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
    
    def _format_messages_to_text(self, messages) -> str:
        text_lines = []
        
        for message in messages:
            if message.role == "user":
                text_lines.append(f"用户: {message.content}")
            elif message.role == "assistant":
                text_lines.append(f"AI助手: {message.content}")
            elif message.role == "system":
                text_lines.append(f"系统: {message.content}")
            text_lines.append("")
        
        return "\n".join(text_lines)

    def export_to_markdown(self):
        from PyQt6.QtWidgets import QFileDialog
        
        if not self.current_session_id:
            return
        
        session = self.session_manager.get_session(self.current_session_id)
        if not session:
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "导出会话",
            f"{session.title}.md",
            "Markdown files (*.md);;All files (*.*)"
        )
        
        if filename:
            try:
                messages = self.session_manager.get_session_messages(self.current_session_id)
                content = self._format_messages_to_markdown(messages)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# {session.title}\n\n")
                    f.write(f"导出时间: {session.created_at}\n\n")
                    f.write(content)
                
            except Exception as e:
                print(f"Export failed: {e}")
    
    def _format_messages_to_markdown(self, messages) -> str:
        markdown_lines = []
        
        for message in messages:
            if message.role == "user":
                markdown_lines.append("## 👤 用户")
                markdown_lines.append("")
                markdown_lines.append(message.content)
            elif message.role == "assistant":
                markdown_lines.append("## 🤖 AI助手")
                markdown_lines.append("")
                markdown_lines.append(message.content)
            elif message.role == "system":
                markdown_lines.append("## ⚙️ 系统")
                markdown_lines.append("")
                markdown_lines.append(f"`{message.content}`")
            
            markdown_lines.append("")
            markdown_lines.append("---")
            markdown_lines.append("")

        return "\n".join(markdown_lines)

    def clear_display(self):
        self._clear_all_bubbles()
    
    def _clear_all_bubbles(self):
        for bubble in self.message_bubbles:
            bubble.setParent(None)
            bubble.deleteLater()
        
        self.message_bubbles.clear()
        self.current_ai_bubble = None
    
    def get_icon(self, name: str) -> QIcon:
        icon_path = Path(__file__).parent.parent / "icon" / f"{name}.svg"
        if icon_path.exists():
            return QIcon(str(icon_path))
        return QIcon()
    
    def on_input_key_press(self, event):
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.send_message()
        else:
            QTextEdit.keyPressEvent(self.user_input, event)
    
    def load_session(self, session_id: str):
        self.current_session_id = session_id
        self.refresh_chat_display()
        self.update_model_label()
        self.user_input.setFocus()    
        
    def refresh_chat_display(self):
        if not self.current_session_id:
            self._show_welcome_message()
            return
        
        messages = self.session_manager.get_session_messages(self.current_session_id)
        
        self._clear_all_bubbles()
        
        if not messages:
            session = self.session_manager.get_session(self.current_session_id)
            if session:
                self._show_session_welcome(session.title)
            else:
                self._show_error_message("会话加载失败")
            return
        
        for message in messages:
            self._add_message_bubble(message)
        
        self._scroll_to_bottom()
    
    def _show_welcome_message(self):
        self._clear_all_bubbles()
        print("Welcome: Please select or create a session.")
    
    def _show_session_welcome(self, session_title: str):
        print(f"Session '{session_title}' loaded.")
    
    def _show_error_message(self, error_msg: str):
        print(f"Error: {error_msg}")
    
    def _add_message_bubble(self, message):
        is_user = message.role == "user"
        bubble = MessageBubble(message, is_user=is_user)
        
        bubble.copy_requested.connect(self._on_bubble_copy)
        bubble.edit_requested.connect(self._on_bubble_edit)
        bubble.delete_requested.connect(self._on_bubble_delete)
        
        insert_index = self.messages_layout.count() - 1
        self.messages_layout.insertWidget(insert_index, bubble)
        
        self.message_bubbles.append(bubble)
        
        return bubble
    
    def _on_bubble_copy(self, content: str):
        pass
    
    def _on_bubble_edit(self, message_id: str, content: str):
        print("Edit function not implemented yet.")
    
    def _on_bubble_delete(self, message_id: str):
        print("Delete function not implemented yet.")
    
    def _scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        if self.is_generating:
            return
        
        text = self.user_input.toPlainText().strip()
        if not text:
            return
        
        if not self.current_session_id:
            print("No active session selected.")
            return
        
        user_message = self.session_manager.add_user_message(text, self.current_session_id)
        
        self.user_input.clear()
        
        if user_message:
            self._add_message_bubble(user_message)
            self._scroll_to_bottom()
        
        self.message_sent.emit(text)
        
        self.start_ai_response()
    
    def start_ai_response(self):
        if self.is_generating:
            return
        
        session = self.session_manager.get_session(self.current_session_id)
        if not session:
            print("Failed to get session.")
            return
        
        model_parts = session.ai_model.split("/")
        if len(model_parts) >= 2:
            provider = model_parts[0]
            if provider.lower() == "openrouter" and len(model_parts) > 2:
                model = "/".join(model_parts[1:])
            else:
                model = model_parts[1]
        else:
            provider, model = "deepseek", "deepseek-chat"
        
        print(f"[Debug] 解析模型信息: provider={provider}, model={model}")
        
        client = self.ai_client_manager.get_client(provider, model)
        if not client:
            print(f"Failed to get AI client: {provider}")
            return
        
        self.is_generating = True
        self.send_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.user_input.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.generation_started.emit()
        
        context = self.session_manager.get_conversation_context(self.current_session_id)
        self.streaming_response = ""
        
        from core.database import Message
        from datetime import datetime
        
        temp_ai_message = Message(
            id=999999,
            session_id=self.current_session_id,
            role="assistant",
            content="",
            timestamp=datetime.now(),
            metadata={}
        )
        
        self.current_ai_bubble = self._add_message_bubble(temp_ai_message)
        self.current_ai_bubble.set_streaming(True)
        self._scroll_to_bottom()
        
        self.ai_thread = AIResponseThread(client, context)
        self.ai_thread.response_chunk.connect(self.on_ai_response_chunk)
        self.ai_thread.response_finished.connect(self.on_ai_response_finished)
        self.ai_thread.response_error.connect(self.on_ai_response_error)
        self.ai_thread.start()

    def on_ai_response_chunk(self, chunk: str):
        self.streaming_response += chunk
        
        import time
        current_time = time.time()
        if current_time - self.last_scroll_time > 0.1:
            self.last_scroll_time = current_time
            self._update_streaming_bubble()
            self._scroll_to_bottom()
    
    def _update_streaming_bubble(self):
        if self.current_ai_bubble and self.streaming_response:
            self.current_ai_bubble.update_content(self.streaming_response)

    def on_ai_response_finished(self, full_response: str):
        ai_message = self.session_manager.add_assistant_message(full_response, self.current_session_id)
        
        if self.current_ai_bubble:
            self.current_ai_bubble.set_streaming(False)
            self.current_ai_bubble.update_content(full_response)
            if ai_message:
                self.current_ai_bubble.message = ai_message
        
        self.current_ai_bubble = None
        self.is_generating = False
        self.send_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.user_input.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.user_input.setFocus()
        self.generation_finished.emit()
        
        self._check_and_start_renaming()
        
        self._scroll_to_bottom()

    def _check_and_start_renaming(self):
        session = self.session_manager.get_session(self.current_session_id)
        if not session:
            print("[Rename Debug] 自动重命名检查：未找到当前会话。")
            return
            
        print(f"[Rename Debug] 检查会话 '{session.title}'...")
        if session.title != "新对话":
            print(f"[Rename Debug] 标题不是'新对话'，跳过重命名。")
            return
            
        messages = self.session_manager.get_session_messages(self.current_session_id)
        print(f"[Rename Debug] 当前消息数量: {len(messages)}")
        
        if len(messages) == 2:
            print("[Rename Debug] 条件满足，将在2秒后启动标题生成。")
            QTimer.singleShot(2000, self._start_delayed_renaming)
        else:
            print(f"[Rename Debug] 消息数量为 {len(messages)}，不等于2，跳过重命名。")
    
    def _start_delayed_renaming(self):
        print("[Rename Debug] 2秒延迟结束，开始生成标题...")
        session = self.session_manager.get_session(self.current_session_id)
        if not session:
            print("[Rename Debug] 延迟重命名：未找到当前会话。")
            return
            
        model_parts = session.ai_model.split("/")
        if len(model_parts) >= 2:
            provider = model_parts[0]
            if provider.lower() == "openrouter" and len(model_parts) > 2:
                model = "/".join(model_parts[1:])
            else:
                model = model_parts[1]
        else:
            provider, model = "deepseek", "deepseek-chat"
        
        print(f"[Rename Debug] 解析模型信息: provider={provider}, model={model}")
        client = self.ai_client_manager.get_client(provider, model)

        if client:
            self.title_thread = TitleGenerationThread(self.session_manager, client, self.current_session_id)
            self.title_thread.finished_renaming.connect(self.on_title_generated)
            self.title_thread.start()
        else:
            print("[Rename Debug] 无法获取AI客户端，跳过重命名。")

    def on_title_generated(self):
        print("会话标题已自动更新。")
        self.session_renamed.emit()

    def on_ai_response_error(self, error: str):
        if self.current_ai_bubble:
            self.current_ai_bubble.set_streaming(False)
            self.current_ai_bubble.update_content(f"错误: {error}")
        
        print(f"AI Error: {error}")
        
        self.current_ai_bubble = None
        self.is_generating = False
        self.send_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.user_input.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.user_input.setFocus()
        self.generation_finished.emit()
    
    def stop_generation(self):
        if hasattr(self, 'ai_thread') and self.ai_thread.isRunning():
            self.ai_thread.terminate()
            self.ai_thread.wait()
        
        self.is_generating = False
        self.send_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.user_input.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.user_input.setFocus()
        self.generation_finished.emit()

    def clear_session(self):
        if not self.current_session_id:
            print("No active session to clear.")
            return
        
        if self.is_generating:
            self._show_styled_message("无法清除", "AI正在回复中，请等待回复完成后再清除。", "warning")
            return
        
        from PyQt6.QtWidgets import QMessageBox
        
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
            try:
                self.session_manager.clear_session_messages(self.current_session_id)
                
                self._clear_all_bubbles()
                
                session = self.session_manager.get_session(self.current_session_id)
                if session:
                    self._show_session_welcome(session.title)
                
                self.user_input.setFocus()
                
                print("Session cleared.")
                
            except Exception as e:
                print(f"Failed to clear session: {e}")
                self._show_styled_message("清除失败", f"清除会话时发生错误：{str(e)}", "warning")
    
    def refresh_settings(self):
        pass
    
    def update_model_label(self):
        if not self.current_session_id:
            self.model_label.setText("当前模型：未选择")
            return
            
        session = self.session_manager.get_session(self.current_session_id)
        if not session or not session.ai_model:
            self.model_label.setText("当前模型：未设置")
            return
        
        model_parts = session.ai_model.split("/")
        if len(model_parts) >= 2:
            provider = model_parts[0]
            if provider.lower() == "openrouter" and len(model_parts) > 2:
                display_name = "/".join(model_parts[1:])
            else:
                display_name = model_parts[1]
        else:
            display_name = session.ai_model
        
        if ":free" in display_name:
            display_name = display_name.replace(":free", " (Free)")
        
        display_name = self._simplify_model_name(display_name)
        
        self.model_label.setText(f"当前模型：{display_name}")
        self.model_label.setToolTip(f"当前模型: {session.ai_model}")
        
        print(f"[Debug] 更新模型标签显示: {display_name}")
    
    def _simplify_model_name(self, model_name: str) -> str:
        simplifications = {
            "deepseek-r1-0528 (Free)": "R1 (Free)",
            "deepseek-chat-v3-0324 (Free)": "Chat V3 (Free)", 
            "claude-sonnet-4": "Claude 4",
            "claude-3.7-sonnet": "Claude 3.7",
            "gemini-2.5-pro-preview": "Gemini 2.5 Pro",
            "chatgpt-4o-latest": "GPT-4o Latest",
            "grok-3": "Grok 3"
        }
        
        for full_name, simple_name in simplifications.items():
            if full_name in model_name:
                return simple_name
        
        return model_name
    
    def _show_styled_message(self, title: str, text: str, msg_type: str = "information"):
        from PyQt6.QtWidgets import QMessageBox
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

class AIResponseThread(QThread):
    
    response_chunk = pyqtSignal(str)
    response_finished = pyqtSignal(str)
    response_error = pyqtSignal(str)
    
    def __init__(self, client, messages):
        super().__init__()
        self.client = client
        self.messages = messages
        self.full_response = ""
    
    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            loop.run_until_complete(self._get_response())
            
        except Exception as e:
            self.response_error.emit(str(e))
        finally:
            try:
                loop.close()
            except:
                pass
    
    async def _get_response(self):
        try:
            async for chunk in self.client.chat_completion_stream(
                messages=self.messages,
                temperature=0.7,
                max_tokens=2048
            ):
                if chunk and not chunk.startswith("错误:"):
                    self.full_response += chunk
                    self.response_chunk.emit(chunk)
                elif chunk.startswith("错误:"):
                    self.response_error.emit(chunk)
                    return
            
            self.response_finished.emit(self.full_response)
            
        except Exception as e:
            self.response_error.emit(str(e))

class TitleGenerationThread(QThread):
    finished_renaming = pyqtSignal()

    def __init__(self, session_manager, ai_client, session_id):
        super().__init__()
        self.session_manager = session_manager
        self.ai_client = ai_client
        self.session_id = session_id

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(self._generate_and_save_title())
            finally:
                try:
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    
                    if pending:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                        
                except Exception as cleanup_error:
                    print(f"[Rename Debug] 清理事件循环时出错: {cleanup_error}")
                finally:
                    loop.close()
                    
        except Exception as e:
            print(f"[Rename Debug] 标题生成线程错误: {e}")
        finally:
            self.finished_renaming.emit()

    async def _generate_and_save_title(self):
        try:
            result = await self.session_manager.auto_generate_session_title(self.session_id, self.ai_client)
            if result:
                print(f"[Rename Debug] 标题生成成功: {result}")
            else:
                print("[Rename Debug] 标题生成失败或返回空结果")
        except Exception as e:
            print(f"[Rename Debug] 生成标题时出错: {e}")
            raise
