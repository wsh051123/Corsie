"""
会话面板 - 管理和显示会话列表
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QListWidget, QListWidgetItem, QLabel, QLineEdit,
                            QMenu, QMessageBox, QInputDialog, QDialog, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
from pathlib import Path
from .styles import ModernTheme

class SessionPanel(QWidget):
    
    session_selected = pyqtSignal(str)
    session_deleted = pyqtSignal(str)
    
    def __init__(self, session_manager):
        super().__init__()
        
        self.session_manager = session_manager
        self.current_session_id = None
        
        self.init_ui()
        self.refresh_sessions()
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        

        
        self.new_session_button = QPushButton(" 新建对话")
        self.new_session_button.setIcon(self.get_icon("add"))
        self.new_session_button.clicked.connect(self.create_new_session)
        self.new_session_button.setFixedHeight(44)
        self.new_session_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY_BLUE};
                color: white;
                border: none;
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                padding: 12px 16px;
                text-align: center;
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
        """)
        layout.addWidget(self.new_session_button)
        
        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self.on_session_clicked)
        self.session_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self.show_context_menu)
        
        self.apply_modern_styles()
        
        layout.addWidget(self.session_list)
    
    def apply_modern_styles(self):
        """应用现代化样式"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.BACKGROUND_SECONDARY};
                border-right: 1px solid {ModernTheme.BORDER_LIGHT};
            }}
        """)
        
        self.session_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {ModernTheme.BACKGROUND_SECONDARY};
                border: none;
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                padding: 8px;
                outline: none;
            }}
            
            QListWidget::item {{
                background-color: transparent;
                border: none;
                border-radius: {ModernTheme.RADIUS_SMALL};
                padding: 12px 16px;
                margin: 2px 0px;
                color: {ModernTheme.TEXT_PRIMARY};
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                min-height: 20px;
            }}
            
            QListWidget::item:hover {{
                background-color: {ModernTheme.HOVER_OVERLAY};
            }}
            
            QListWidget::item:selected {{
                background-color: {ModernTheme.PRIMARY_BLUE};
                color: white;
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
    
    def get_icon(self, name: str) -> QIcon:
        """获取图标"""
        icon_path = Path(__file__).parent.parent / "icon" / f"{name}.svg"
        if icon_path.exists():
            return QIcon(str(icon_path))
        return QIcon()
    
    def refresh_sessions(self):
        """刷新会话列表"""
        self.current_session_id = self.session_manager.current_session_id
        
        self.session_list.clear()
        
        try:
            sessions = self.session_manager.get_all_sessions(limit=100)
            if not sessions:
                item = QListWidgetItem("暂无会话，右键点击此处创建新会话")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                item.setForeground(Qt.GlobalColor.gray)
                self.session_list.addItem(item)
                return
            
            for session in sessions:
                item = QListWidgetItem()
                item.setText(session.title)
                item.setData(Qt.ItemDataRole.UserRole, session.id)
                item.setToolTip(f"创建时间: {session.created_at.strftime('%Y-%m-%d %H:%M')}")
                
                
                self.session_list.addItem(item)
            
        except Exception as e:
            print(f"Error refreshing sessions: {e}")
        
        if self.current_session_id:
            self.select_session(self.current_session_id)
    
    def create_new_session(self):
        sessions = self.session_manager.get_all_sessions(limit=500)
        existing_new_session = next((s for s in sessions if s.title == "新对话"), None)
        
        if existing_new_session:
            self.select_session(existing_new_session.id)
            return

        try:
            session = self.session_manager.create_new_session()
            self.refresh_sessions()
            self.select_session(session.id)
        except Exception as e:
            self._show_styled_message("错误", f"创建会话失败: {str(e)}", "critical")
    
    def on_session_clicked(self, item: QListWidgetItem):
        session_id = item.data(Qt.ItemDataRole.UserRole)
        if session_id:
            self.select_session(session_id)
    
    def select_session(self, session_id: str):
        if not session_id:
            return

        self.current_session_id = session_id

        for i in range(self.session_list.count()):
            item = self.session_list.item(i)
            item_session_id = item.data(Qt.ItemDataRole.UserRole)

            if item_session_id and item_session_id == session_id:
                self.session_list.setCurrentItem(item)
                break
        
        selected_items = self.session_list.findItems(self.session_manager.get_session(session_id).title, Qt.MatchFlag.MatchExactly)
        if selected_items:
            self.session_list.scrollToItem(selected_items[0])

        self.session_selected.emit(session_id)
    
    def show_context_menu(self, position):
        item = self.session_list.itemAt(position)
        menu = QMenu(self)
        
        new_action = menu.addAction(self.get_icon("add"), "新建会话")
        new_action.triggered.connect(self.create_new_session)
        
        if item and item.data(Qt.ItemDataRole.UserRole):
            session_id = item.data(Qt.ItemDataRole.UserRole)
            
            menu.addSeparator()
            
            rename_action = menu.addAction(self.get_icon("edit"), "重命名")
            rename_action.triggered.connect(lambda: self.rename_session(session_id))
            
            export_action = menu.addAction(self.get_icon("copy"), "导出")
            export_action.triggered.connect(lambda: self.export_session(session_id))
            
            menu.addSeparator()
            
            delete_action = menu.addAction(self.get_icon("delete"), "删除")
            delete_action.triggered.connect(lambda: self.delete_session(session_id))
        
        menu.exec(self.session_list.mapToGlobal(position))
    
    def rename_session(self, session_id: str):
        session = self.session_manager.get_session(session_id)
        if not session:
            return
        
        dialog = self._create_rename_dialog(session.title)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_title = dialog.get_text().strip()
            if new_title:
                try:
                    success = self.session_manager.update_session_title(session_id, new_title)
                    if success:
                        self.refresh_sessions()
                    else:
                        self._show_styled_message("警告", "重命名失败", "warning")
                except Exception as e:
                    self._show_styled_message("错误", f"重命名失败: {str(e)}", "critical")
    
    def _create_rename_dialog(self, current_title: str):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
        
        dialog = QDialog(self)
        dialog.setWindowTitle("重命名会话")
        dialog.setFixedSize(450, 200)
        dialog.setObjectName("renameDialog")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        label = QLabel("请输入新的会话名称:")
        label.setObjectName("renameLabel")
        layout.addWidget(label)
        
        line_edit = QLineEdit(current_title)
        line_edit.setObjectName("renameLineEdit")
        line_edit.selectAll()
        layout.addWidget(line_edit)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.setObjectName("renameCancelButton")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        button_layout.addSpacing(12)
        
        ok_button = QPushButton("确定")
        ok_button.setObjectName("renameOkButton")
        ok_button.clicked.connect(dialog.accept)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
        dialog.setStyleSheet(f"""
            QDialog#renameDialog {{
                background-color: {ModernTheme.BACKGROUND_PRIMARY} !important;
                border: none !important;
                border-radius: {ModernTheme.RADIUS_MEDIUM} !important;
            }}
            
            QLabel#renameLabel {{
                color: {ModernTheme.TEXT_PRIMARY} !important;
                font-size: 15px !important;
                font-weight: 500 !important;
                background-color: transparent !important;
                border: none !important;
                padding: 0px !important;
                margin: 0px 0px 8px 0px !important;
            }}
            
            QLineEdit#renameLineEdit {{
                background-color: {ModernTheme.BACKGROUND_SECONDARY} !important;
                border: 2px solid {ModernTheme.BORDER_LIGHT} !important;
                border-radius: {ModernTheme.RADIUS_SMALL} !important;
                padding: 12px 16px !important;
                font-size: 14px !important;
                color: {ModernTheme.TEXT_PRIMARY} !important;
                selection-background-color: {ModernTheme.PRIMARY_BLUE} !important;
                min-height: 20px !important;
            }}
            
            QLineEdit#renameLineEdit:focus {{
                border: 2px solid {ModernTheme.FOCUS_RING} !important;
                background-color: {ModernTheme.BACKGROUND_PRIMARY} !important;
            }}
            
            QPushButton#renameCancelButton {{
                background-color: {ModernTheme.BACKGROUND_SECONDARY} !important;
                color: {ModernTheme.TEXT_PRIMARY} !important;
                border: 1px solid {ModernTheme.BORDER_LIGHT} !important;
                border-radius: {ModernTheme.RADIUS_SMALL} !important;
                padding: 12px 24px !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                min-width: 80px !important;
                min-height: 20px !important;
            }}
            
            QPushButton#renameCancelButton:hover {{
                background-color: {ModernTheme.BORDER_LIGHT} !important;
                border: 1px solid {ModernTheme.BORDER_MEDIUM} !important;
            }}
            
            QPushButton#renameCancelButton:pressed {{
                background-color: {ModernTheme.BORDER_MEDIUM} !important;
            }}
            
            QPushButton#renameOkButton {{
                background-color: {ModernTheme.PRIMARY_BLUE} !important;
                color: white !important;
                border: none !important;
                border-radius: {ModernTheme.RADIUS_SMALL} !important;
                padding: 12px 24px !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                min-width: 80px !important;
                min-height: 20px !important;
            }}
            
            QPushButton#renameOkButton:hover {{
                background-color: #0056b3 !important;
            }}
            
            QPushButton#renameOkButton:pressed {{
                background-color: #004494 !important;
            }}
        """)
        
        dialog.get_text = lambda: line_edit.text()
        
        line_edit.setFocus()
        
        return dialog
    
    def export_session(self, session_id: str):
        """导出会话"""
        
        session = self.session_manager.get_session(session_id)
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
                content = self.session_manager.export_session_to_markdown(session_id)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._show_styled_message("成功", f"会话已导出到: {filename}", "information")
            except Exception as e:
                self._show_styled_message("错误", f"导出失败: {str(e)}", "critical")
    
    def delete_session(self, session_id: str):
        session = self.session_manager.get_session(session_id)
        if not session:
            return
        
        dialog = self._create_delete_dialog(session.title)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                deleted_session_id = session_id
                
                success = self.session_manager.delete_session(deleted_session_id)
                if success:
                    self.session_deleted.emit(deleted_session_id)
                    self.refresh_sessions()
                else:
                    self._show_styled_message("警告", "删除失败", "warning")
            except Exception as e:
                self._show_styled_message("错误", f"删除失败: {str(e)}", "critical")
    
    def _create_delete_dialog(self, session_title: str):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        
        dialog = QDialog(self)
        dialog.setWindowTitle("确认删除")
        dialog.setFixedSize(450, 200)
        dialog.setObjectName("deleteDialog")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        main_label = QLabel(f"确定要删除会话 '{session_title}' 吗？")
        main_label.setObjectName("deleteMainLabel")
        layout.addWidget(main_label)
        
        info_label = QLabel("此操作不可撤销。")
        info_label.setObjectName("deleteInfoLabel")
        layout.addWidget(info_label)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.setObjectName("deleteCancelButton")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        button_layout.addSpacing(12)
        
        delete_button = QPushButton("确定")
        delete_button.setObjectName("deleteConfirmButton")
        delete_button.clicked.connect(dialog.accept)
        delete_button.setDefault(True)
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)
        
        dialog.setStyleSheet(f"""
            QDialog#deleteDialog {{
                background-color: {ModernTheme.BACKGROUND_PRIMARY} !important;
                border: none !important;
                border-radius: {ModernTheme.RADIUS_MEDIUM} !important;
            }}
            
            QLabel#deleteMainLabel {{
                color: {ModernTheme.TEXT_PRIMARY} !important;
                font-size: 15px !important;
                font-weight: 500 !important;
                background-color: transparent !important;
                border: none !important;
                padding: 0px !important;
                margin: 0px 0px 8px 0px !important;
            }}
            
            QLabel#deleteInfoLabel {{
                color: {ModernTheme.TEXT_SECONDARY} !important;
                font-size: 14px !important;
                font-weight: normal !important;
                background-color: transparent !important;
                border: none !important;
                padding: 0px !important;
                margin: 0px 0px 20px 0px !important;
            }}
            
            QPushButton#deleteCancelButton {{
                background-color: {ModernTheme.BACKGROUND_SECONDARY} !important;
                color: {ModernTheme.TEXT_PRIMARY} !important;
                border: 1px solid {ModernTheme.BORDER_LIGHT} !important;
                border-radius: {ModernTheme.RADIUS_SMALL} !important;
                padding: 12px 24px !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                min-width: 80px !important;
                min-height: 20px !important;
            }}
            
            QPushButton#deleteCancelButton:hover {{
                background-color: {ModernTheme.BORDER_LIGHT} !important;
                border: 1px solid {ModernTheme.BORDER_MEDIUM} !important;
            }}
            
            QPushButton#deleteCancelButton:pressed {{
                background-color: {ModernTheme.BORDER_MEDIUM} !important;
            }}
            
            QPushButton#deleteConfirmButton {{
                background-color: {ModernTheme.ERROR_RED} !important;
                color: white !important;
                border: none !important;
                border-radius: {ModernTheme.RADIUS_SMALL} !important;
                padding: 12px 24px !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                min-width: 80px !important;
                min-height: 20px !important;
            }}
            
            QPushButton#deleteConfirmButton:hover {{
                background-color: #d70015 !important;
            }}
            
            QPushButton#deleteConfirmButton:pressed {{
                background-color: #b8000f !important;
            }}
        """)
        
        return dialog
    
    def get_session_count(self) -> int:
        """获取会话数量"""
        try:
            sessions = self.session_manager.get_all_sessions(limit=1000)
            return len(sessions)
        except:
            return 0
    
    def _show_styled_message(self, title: str, text: str, msg_type: str = "information"):
        dialog = self._create_message_dialog(title, text, msg_type)
        dialog.exec()
    
    def _create_message_dialog(self, title: str, text: str, msg_type: str = "information"):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(500, 200)
        dialog.setObjectName("messageDialog")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        main_label = QLabel(text)
        main_label.setObjectName("messageMainLabel")
        main_label.setWordWrap(True)
        layout.addWidget(main_label)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("确定")
        ok_button.setObjectName("messageOkButton")
        ok_button.clicked.connect(dialog.accept)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
        if msg_type == "critical":
            button_color = ModernTheme.ERROR_RED
            button_hover = "#d70015"
            button_pressed = "#b8000f"
        elif msg_type == "warning":
            button_color = "#ff9500"
            button_hover = "#e6850e"
            button_pressed = "#cc7506"
        else:
            button_color = ModernTheme.SUCCESS_GREEN
            button_hover = "#28a745"
            button_pressed = "#1e7e34"
        
        dialog.setStyleSheet(f"""
            QDialog#messageDialog {{
                background-color: {ModernTheme.BACKGROUND_PRIMARY} !important;
                border: none !important;
                border-radius: {ModernTheme.RADIUS_MEDIUM} !important;
            }}
            
            QLabel#messageMainLabel {{
                color: {ModernTheme.TEXT_PRIMARY} !important;
                font-size: 14px !important;
                font-weight: 400 !important;
                background-color: transparent !important;
                border: none !important;
                padding: 0px !important;
                margin: 0px 0px 20px 0px !important;
                line-height: 1.5 !important;
            }}
            
            QPushButton#messageOkButton {{
                background-color: {button_color} !important;
                color: white !important;
                border: none !important;
                border-radius: {ModernTheme.RADIUS_SMALL} !important;
                padding: 12px 32px !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                min-width: 100px !important;
                min-height: 20px !important;
            }}
            
            QPushButton#messageOkButton:hover {{
                background-color: {button_hover} !important;
            }}
            
            QPushButton#messageOkButton:pressed {{
                background-color: {button_pressed} !important;
            }}
        """)
        
        return dialog
