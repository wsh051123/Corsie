"""
会话管理器 - 处理会话逻辑和消息管理
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from .database import DatabaseManager, Session, Message

class SessionManager:
    """会话管理器类"""
    
    def __init__(self, db_manager: DatabaseManager):
        """初始化会话管理器"""
        self.db = db_manager
        self.current_session_id: Optional[str] = None
        self._session_cache: Dict[str, Session] = {}
    
    def create_new_session(self, title: Optional[str] = "新对话", 
                          ai_model: str = "deepseek/deepseek-chat",
                          system_prompt: str = "") -> Session:
        """创建新会话"""
        session = self.db.create_session(title, ai_model, system_prompt)
        self._session_cache[session.id] = session
        self.current_session_id = session.id
        
        return session
    
    def get_current_session(self) -> Optional[Session]:
        """获取当前活动会话"""
        if not self.current_session_id:
            return None
        
        return self.get_session(self.current_session_id)
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取指定会话"""
        if session_id in self._session_cache:
            return self._session_cache[session_id]
        
        session = self.db.get_session(session_id)
        if session:
            self._session_cache[session_id] = session
        
        return session
    
    def switch_to_session(self, session_id: str) -> bool:
        """切换到指定会话"""
        session = self.get_session(session_id)
        if session:
            self.current_session_id = session_id
            return True
        return False
    
    def get_all_sessions(self, limit: int = 100, offset: int = 0) -> List[Session]:
        """获取所有会话列表"""
        return self.db.get_all_sessions(limit, offset)
    
    def update_session_title(self, session_id: str, new_title: str) -> bool:
        """更新会话标题"""
        success = self.db.update_session(session_id, title=new_title)
        if success and session_id in self._session_cache:
            self._session_cache[session_id].title = new_title
        return success
    
    def update_session_model(self, session_id: str, ai_model: str) -> bool:
        """更新会话AI模型"""
        success = self.db.update_session(session_id, ai_model=ai_model)
        if success and session_id in self._session_cache:
            self._session_cache[session_id].ai_model = ai_model
        return success
    
    def update_session_system_prompt(self, session_id: str, system_prompt: str) -> bool:
        """更新会话系统提示"""
        success = self.db.update_session(session_id, system_prompt=system_prompt)
        if success and session_id in self._session_cache:
            self._session_cache[session_id].system_prompt = system_prompt
        return success
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        success = self.db.delete_session(session_id)
        if success:
            self._session_cache.pop(session_id, None)
            
            if self.current_session_id == session_id:
                self.current_session_id = None
        
        return success
    
    def add_user_message(self, content: str, session_id: Optional[str] = None) -> Optional[Message]:
        """添加用户消息"""
        if session_id is None:
            session_id = self.current_session_id
        
        if not session_id:
            return None
        
        return self.db.add_message(session_id, "user", content)
    
    def add_assistant_message(self, content: str, session_id: Optional[str] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> Optional[Message]:
        """添加AI助手消息"""
        if session_id is None:
            session_id = self.current_session_id
        
        if not session_id:
            return None
        
        return self.db.add_message(session_id, "assistant", content, metadata)
    
    def add_system_message(self, content: str, session_id: Optional[str] = None) -> Optional[Message]:
        """添加系统消息"""
        if session_id is None:
            session_id = self.current_session_id
        
        if not session_id:
            return None
        
        return self.db.add_message(session_id, "system", content)
    
    def get_session_messages(self, session_id: Optional[str] = None, 
                           limit: int = 100, offset: int = 0) -> List[Message]:
        """获取会话消息"""
        if session_id is None:
            session_id = self.current_session_id
        
        if not session_id:
            return []
        
        return self.db.get_messages(session_id, limit, offset)
    
    def get_conversation_context(self, session_id: Optional[str] = None,
                               max_messages: int = 20) -> List[Dict[str, str]]:
        """获取对话上下文"""
        if session_id is None:
            session_id = self.current_session_id
        
        if not session_id:
            return []
        
        session = self.get_session(session_id)
        if not session:
            return []
        
        context = []
        
        if session.system_prompt:
            context.append({
                "role": "system",
                "content": session.system_prompt
            })
        
        messages = self.get_session_messages(session_id, limit=max_messages)
        
        for message in messages:
            if message.role in ["user", "assistant"]:
                context.append({
                    "role": message.role,
                    "content": message.content
                })
        
        return context
    
    def delete_message(self, message_id: str) -> bool:
        """删除指定消息"""
        return self.db.delete_message(message_id)
    
    async def auto_generate_session_title(self, session_id: str, client: Any) -> Optional[str]:
        print(f"[Rename Debug] 开始为会话 {session_id} 生成标题...")
        
        if not client:
            print("[Rename Debug] 客户端为空，无法生成标题")
            return None
        
        messages = self.get_session_messages(session_id, limit=10)
        print(f"[Rename Debug] 获取到 {len(messages)} 条消息")
        
        user_messages = [msg for msg in messages if msg.role == "user"]
        
        if not user_messages:
            print("[Rename Debug] 没有找到用户消息，无法生成标题")
            return None

        user_message = user_messages[0].content
        
        print(f"[Rename Debug] 用户消息: {user_message[:50]}...")
        
        prompt = f"""请根据用户的提问，为这个对话生成一个不超过10个字的简洁标题。请只返回标题，不要包含任何其他多余的内容或标点符号。

用户提问: {user_message}"""

        try:
            print("[Rename Debug] 开始调用AI生成标题...")
            
            response = await client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=50
            )

            print(f"[Rename Debug] AI响应: {response}")

            if response and not response.error and response.content:
                raw_title = response.content
                print(f"[Rename Debug] AI原始返回标题: '{raw_title}'")

                new_title = raw_title.strip().replace('"', '').replace("'", "").replace("标题：", "").replace("标题:", "")
                new_title = new_title.strip()
                
                print(f"[Rename Debug] 清理后的标题: '{new_title}'")

                if new_title:
                    print(f"[Rename Debug] 正在用新标题更新会话 {session_id}...")
                    success = self.update_session_title(session_id, new_title)
                    if success:
                        print(f"[Rename Debug] 标题更新成功: '{new_title}'")
                        return new_title
                    else:
                        print("[Rename Debug] 标题更新失败")
                        return None
                else:
                    print("[Rename Debug] 清理后的标题为空")
                    return None
            else:
                print(f"[Rename Debug] AI响应无效: error={getattr(response, 'error', 'unknown')}, content={getattr(response, 'content', 'none')}")
                return None

        except Exception as e:
            print(f"[Rename Debug] 自动生成标题失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def clear_session_messages(self, session_id: str) -> bool:
        """清除指定会话的所有消息"""
        try:
            messages = self.get_session_messages(session_id, limit=10000)
            
            deleted_count = 0
            for message in messages:
                if self.db.delete_message(message.id):
                    deleted_count += 1
            
            return deleted_count > 0
        except Exception:
            return False
    
    def export_session_to_markdown(self, session_id: str) -> str:
        """导出会话为Markdown"""
        return self.db.export_session_to_markdown(session_id)
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """获取会话摘要信息"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        messages = self.get_session_messages(session_id, limit=10000)
        
        user_messages = [m for m in messages if m.role == "user"]
        assistant_messages = [m for m in messages if m.role == "assistant"]
        
        total_chars = sum(len(m.content) for m in messages)
        
        return {
            "session_id": session_id,
            "title": session.title,
            "ai_model": session.ai_model,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "total_characters": total_chars,
            "has_system_prompt": bool(session.system_prompt)
        }
    
    def cleanup_empty_sessions(self) -> int:
        sessions = self.get_all_sessions(limit=1000)
        deleted_count = 0
        
        for session in sessions:
            messages = self.get_session_messages(session.id, limit=1)
            if not messages:
                if self.delete_session(session.id):
                    deleted_count += 1
        
        return deleted_count
    
    def get_stats(self) -> Dict[str, Any]:
        return self.db.get_session_stats()
