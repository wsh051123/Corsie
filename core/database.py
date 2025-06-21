"""
数据库管理器 - 处理SQLite数据库操作和数据持久化
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Session:
    """会话数据类"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    ai_model: str = "deepseek/deepseek-chat"
    system_prompt: str = ""

@dataclass 
class Message:
    """消息数据类"""
    id: str
    session_id: str
    role: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

class DatabaseManager:
    """数据库管理器类，负责处理数据持久化"""
    
    def __init__(self, db_path: Optional[str] = None):
        """初始化数据库管理器"""
        if db_path is None:
            db_path = Path.home() / ".corsie" / "corsie.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        self._init_database()
    
    def _init_database(self) -> None:
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ai_model TEXT DEFAULT 'deepseek/deepseek-chat',
                    system_prompt TEXT DEFAULT ''
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session_id 
                ON messages(session_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
                ON messages(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_updated_at 
                ON sessions(updated_at)
            """)
            
            conn.commit()
    
    def create_session(self, title: str, ai_model: str = "deepseek/deepseek-chat", 
                      system_prompt: str = "") -> Session:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sessions (id, title, created_at, updated_at, ai_model, system_prompt)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, title, now, now, ai_model, system_prompt))
            conn.commit()
        
        return Session(
            id=session_id,
            title=title,
            created_at=now,
            updated_at=now,
            ai_model=ai_model,
            system_prompt=system_prompt
        )
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取指定会话"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM sessions WHERE id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                return Session(
                    id=row['id'],
                    title=row['title'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    ai_model=row['ai_model'],
                    system_prompt=row['system_prompt']
                )
        return None
    
    def get_all_sessions(self, limit: int = 100, offset: int = 0) -> List[Session]:
        """获取所有会话，按更新时间倒序"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM sessions 
                ORDER BY updated_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append(Session(
                    id=row['id'],
                    title=row['title'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    ai_model=row['ai_model'],
                    system_prompt=row['system_prompt']
                ))
            
            return sessions
    
    def update_session(self, session_id: str, title: Optional[str] = None,
                      ai_model: Optional[str] = None, 
                      system_prompt: Optional[str] = None) -> bool:
        """更新会话信息"""
        fields = []
        values = []
        
        if title is not None:
            fields.append("title = ?")
            values.append(title)
        
        if ai_model is not None:
            fields.append("ai_model = ?")
            values.append(ai_model)
        
        if system_prompt is not None:
            fields.append("system_prompt = ?")
            values.append(system_prompt)
        
        if not fields:
            return False
        
        fields.append("updated_at = ?")
        values.append(datetime.now())
        values.append(session_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"""
                UPDATE sessions SET {', '.join(fields)}
                WHERE id = ?
            """, values)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话及其所有消息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def add_message(self, session_id: str, role: str, content: str,
                   metadata: Optional[Dict[str, Any]] = None) -> Message:
        """添加消息到会话"""
        message_id = str(uuid.uuid4())
        now = datetime.now()
        metadata_json = json.dumps(metadata or {})
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO messages (id, session_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, session_id, role, content, now, metadata_json))
            
            conn.execute("""
                UPDATE sessions SET updated_at = ? WHERE id = ?
            """, (now, session_id))
            
            conn.commit()
        
        return Message(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            timestamp=now,
            metadata=metadata
        )
    
    def get_messages(self, session_id: str, limit: int = 100, 
                    offset: int = 0) -> List[Message]:
        """获取会话中的消息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM messages 
                WHERE session_id = ? 
                ORDER BY timestamp ASC 
                LIMIT ? OFFSET ?
            """, (session_id, limit, offset))
            
            messages = []
            for row in cursor.fetchall():
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                messages.append(Message(
                    id=row['id'],
                    session_id=row['session_id'],
                    role=row['role'],
                    content=row['content'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    metadata=metadata
                ))
            
            return messages
    
    def delete_message(self, message_id: str) -> bool:
        """删除指定消息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_session_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            session_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM messages")
            message_count = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT created_at FROM sessions 
                ORDER BY created_at ASC 
                LIMIT 1
            """)
            first_session = cursor.fetchone()
            
            return {
                "total_sessions": session_count,
                "total_messages": message_count,
                "first_session_date": first_session[0] if first_session else None,
                "db_size": self.db_path.stat().st_size if self.db_path.exists() else 0
            }
    
    def export_session_to_markdown(self, session_id: str) -> str:
        """将会话导出为Markdown格式"""
        session = self.get_session(session_id)
        if not session:
            return ""
        
        messages = self.get_messages(session_id, limit=10000)
        
        markdown_content = f"# {session.title}\n\n"
        markdown_content += f"**创建时间**: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        markdown_content += f"**AI模型**: {session.ai_model}\n"
        
        if session.system_prompt:
            markdown_content += f"**系统提示**: {session.system_prompt}\n"
        
        markdown_content += "\n---\n\n"
        
        for message in messages:
            role_name = {"user": "用户", "assistant": "AI助手", "system": "系统"}
            markdown_content += f"## {role_name.get(message.role, message.role)}\n\n"
            markdown_content += f"{message.content}\n\n"
            markdown_content += f"*{message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            markdown_content += "---\n\n"
        
        return markdown_content
    
    def cleanup_old_data(self, days: int = 90) -> Tuple[int, int]:
        """清理指定天数前的旧数据"""
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM messages 
                WHERE timestamp < ?
            """, (cutoff_date,))
            deleted_messages = cursor.rowcount
            
            cursor = conn.execute("""
                DELETE FROM sessions 
                WHERE id NOT IN (SELECT DISTINCT session_id FROM messages)
            """, (cutoff_date,))
            deleted_sessions = cursor.rowcount
            
            conn.commit()
        
        return deleted_sessions, deleted_messages
