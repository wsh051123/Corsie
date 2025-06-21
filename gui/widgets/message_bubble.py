"""
消息气泡组件 - 使用QMarkdownWidget库实现
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QMenu, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QAction, QClipboard
import datetime
from ..styles import ModernTheme

try:
    from QMarkdownWidget import QMView, QMLabel
    QMARKDOWN_AVAILABLE = True
except ImportError:
    QMARKDOWN_AVAILABLE = False
    print("警告: QMarkdownWidget 未安装，将使用备选方案")

class MessageBubble(QWidget):
    
    copy_requested = pyqtSignal(str)
    edit_requested = pyqtSignal(str, str)
    delete_requested = pyqtSignal(str)
    
    def __init__(self, message, is_user=True, parent=None):
        super().__init__(parent)
        
        self.message = message
        self.is_user = is_user
        self.is_streaming = False
        
        self.init_ui()
        self.setup_style()
    
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(10)
        
        if self.is_user:
            main_layout.addStretch()
            self.create_user_bubble(main_layout)
        else:
            self.create_ai_bubble(main_layout)
            main_layout.addStretch()
    
    def create_user_bubble(self, layout):
        user_container = QWidget()
        user_layout = QVBoxLayout(user_container)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(2)
        
        bubble_frame = QFrame()
        bubble_frame.setObjectName("userBubble")
        
        bubble_layout = QVBoxLayout(bubble_frame)
        bubble_layout.setContentsMargins(16, 12, 16, 12)
        
        if QMARKDOWN_AVAILABLE:
            content_widget = QMLabel(self.message.content)
        else:
            content_widget = QLabel(self.message.content)
            content_widget.setWordWrap(True)
            content_widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        content_widget.setFont(QFont("Consolas", 10))
        bubble_layout.addWidget(content_widget)
        
        self.content_widget = content_widget
        self.bubble_container = bubble_frame
        
        bubble_frame.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        bubble_frame.customContextMenuRequested.connect(self.show_context_menu)
        
        user_layout.addWidget(bubble_frame)
        
        timestamp_label = QLabel(self._format_timestamp())
        timestamp_label.setStyleSheet(f"""
            color: {ModernTheme.TEXT_TERTIARY}; 
            font-size: 11px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            padding: 4px 8px;
        """)
        timestamp_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        user_layout.addWidget(timestamp_label)
        
        layout.addWidget(user_container)
    
    def create_ai_bubble(self, layout):
        """创建AI消息气泡"""
        
        ai_container = QWidget()
        ai_layout = QVBoxLayout(ai_container)
        ai_layout.setContentsMargins(0, 0, 0, 0)
        ai_layout.setSpacing(2)
        
        bubble_frame = QFrame()
        bubble_frame.setObjectName("aiBubble")
        
        bubble_layout = QVBoxLayout(bubble_frame)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        
        if QMARKDOWN_AVAILABLE:
            content_widget = QMView(self.message.content)
            content_widget.setAutoSize(True, max_width=550)
        else:
            content_widget = QLabel()
            content_widget.setText(self._markdown_to_html(self.message.content))
            content_widget.setWordWrap(True)
            content_widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        content_widget.setFont(QFont("Consolas", 10))
        bubble_layout.addWidget(content_widget)
        
        self.content_widget = content_widget
        self.bubble_container = bubble_frame
        
        bubble_frame.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        bubble_frame.customContextMenuRequested.connect(self.show_context_menu)
        
        ai_layout.addWidget(bubble_frame)
        
        timestamp_label = QLabel(self._format_timestamp())
        timestamp_label.setStyleSheet(f"""
            color: {ModernTheme.TEXT_TERTIARY}; 
            font-size: 11px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            padding: 4px 8px;
        """)
        timestamp_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ai_layout.addWidget(timestamp_label)
        
        layout.addWidget(ai_container)
    
    def _format_timestamp(self) -> str:
        """格式化时间戳"""
        if hasattr(self.message, 'timestamp') and self.message.timestamp:
            if isinstance(self.message.timestamp, datetime.datetime):
                return self.message.timestamp.strftime("%H:%M")
            elif isinstance(self.message.timestamp, (int, float)):
                dt = datetime.datetime.fromtimestamp(self.message.timestamp)
                return dt.strftime("%H:%M")
        return ""
    
    def _markdown_to_html(self, markdown: str) -> str:
        import re
        import html
        
        html_content = html.escape(markdown)
        
        html_content = re.sub(r'```(\w+)?\n(.*?)\n```', 
                             r'<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;"><code>\2</code></pre>', 
                             html_content, flags=re.DOTALL)
        
        html_content = re.sub(r'`([^`]+)`', r'<code style="background: #f5f5f5; padding: 2px 4px;">\1</code>', html_content)
        
        html_content = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', html_content)
        
        html_content = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', html_content)
        
        html_content = html_content.replace('\n', '<br>')
        
        return html_content
    
    def setup_style(self):
        base_style = f"""
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            font-size: 14px;
            line-height: 1.4;
        """

        if self.is_user:
            self.bubble_container.setStyleSheet(f"""
                QFrame#userBubble {{
                    background-color: {ModernTheme.USER_BUBBLE};
                    border: none;
                    border-radius: {ModernTheme.RADIUS_LARGE};
                }}
                QMLabel, QLabel {{
                    background-color: transparent;
                    color: white;
                    {base_style}
                }}
            """)
        else:
            self.bubble_container.setStyleSheet(f"""
                QFrame#aiBubble {{
                    background-color: transparent;
                    border: none;
                }}
            """)

            text_widget_style = f"""
                QMView, QLabel {{
                    background-color: {ModernTheme.AI_BUBBLE};
                    color: {ModernTheme.TEXT_PRIMARY};
                    border: 1px solid {ModernTheme.BORDER_LIGHT};
                    border-radius: {ModernTheme.RADIUS_LARGE};
                    padding: 8px 12px;
                    {base_style}
                }}
            """
            if self.content_widget:
                self.content_widget.setStyleSheet(text_widget_style)
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)
        
        copy_action = QAction("复制", self)
        copy_action.triggered.connect(self.copy_content)
        menu.addAction(copy_action)
        
        if self.is_user:
            select_all_action = QAction("选择全部", self)
            select_all_action.triggered.connect(self.select_all_content)
            menu.addAction(select_all_action)
        else:
            delete_action = QAction("删除", self)
            delete_action.triggered.connect(self.delete_message)
            menu.addAction(delete_action)
        
        menu.exec(self.bubble_container.mapToGlobal(position))
    
    def copy_content(self):
        clipboard = QClipboard()
        clipboard.setText(self.message.content)
        self.copy_requested.emit(self.message.content)
    
    def select_all_content(self):
        if hasattr(self.content_widget, 'selectAll'):
            self.content_widget.selectAll()
    
    def edit_message(self):
        self.edit_requested.emit(str(self.message.id), self.message.content)
    
    def delete_message(self):
        self.delete_requested.emit(str(self.message.id))
    
    def update_content(self, new_content: str):
        self.message.content = new_content
        
        if QMARKDOWN_AVAILABLE:
            if hasattr(self.content_widget, 'setMarkdown'):
                try:
                    self.content_widget.setMarkdown(new_content)
                except Exception as e:
                    print(f"[Debug] QMarkdown更新内容失败: {e}")
                    if hasattr(self.content_widget, 'setText'):
                        self.content_widget.setText(new_content)
        else:
            if hasattr(self.content_widget, 'setText'):
                self.content_widget.setText(new_content)
    
    def set_streaming(self, is_streaming: bool):
        self.is_streaming = is_streaming
        if is_streaming and not self.is_user:
            content = self.message.content + " ▋"
            self.update_content(content) 