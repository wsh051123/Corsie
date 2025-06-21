

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import base64

class ConfigManager:
    
    
    def __init__(self):
        
        self.config_dir = Path.home() / ".corsie"
        self.config_file = self.config_dir / "config.json"
        self.key_file = self.config_dir / "key.key"
        

        self.config_dir.mkdir(exist_ok=True)
        

        self._init_encryption_key()
        

        self.config = self._load_config()
    
    def _init_encryption_key(self) -> None:
        
        if not self.key_file.exists():

            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        

        with open(self.key_file, 'rb') as f:
            self.cipher_key = f.read()
            self.cipher = Fernet(self.cipher_key)
    def _load_config(self) -> Dict[str, Any]:
        
        default_config = {
            "ai_settings": {
                "default_model": "deepseek/deepseek-chat",
                "max_tokens": 2048,
                "temperature": 0.7,
                "stream_response": True
            },
            "ui_settings": {
                "theme": "light",
                "font_family": "Segoe UI",
                "font_size": 12,
                "window_geometry": {
                    "width": 1200,
                    "height": 800,
                    "x": 100,
                    "y": 100
                },
                "sidebar_width": 300,
                "sidebar_visible": True
            },
            "api_keys": {},
            "shortcuts": {
                "send_message": "Ctrl+Return",
                "new_session": "Ctrl+N",
                "save_session": "Ctrl+S",
                "search": "Ctrl+F",
                "settings": "Ctrl+,",
                "quit": "Ctrl+Q"
            },
            "session_settings": {
                "auto_save": True,
                "max_history": 1000,
                "export_format": "markdown"
            }
        }
        
        if not self.config_file.exists():
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            return self._merge_config(default_config, config)
        except (json.JSONDecodeError, FileNotFoundError):
            return default_config
    
    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        
        for key, value in default.items():
            if key not in loaded:
                loaded[key] = value
            elif isinstance(value, dict) and isinstance(loaded[key], dict):
                loaded[key] = self._merge_config(value, loaded[key])
        return loaded
    
    def _save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        
        keys = key_path.split('.')
        config = self.config
        

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        

        config[keys[-1]] = value
        self._save_config()
    
    def encrypt_text(self, text: str) -> str:
        
        return base64.urlsafe_b64encode(
            self.cipher.encrypt(text.encode())
        ).decode()
    
    def decrypt_text(self, encrypted_text: str) -> str:
        
        try:
            return self.cipher.decrypt(
                base64.urlsafe_b64decode(encrypted_text.encode())
            ).decode()
        except Exception:
            return ""
    
    def set_api_key(self, provider: str, api_key: str) -> None:
        
        if "api_keys" not in self.config:
            self.config["api_keys"] = {}
        
        self.config["api_keys"][provider] = self.encrypt_text(api_key)
        self._save_config()
    
    def get_api_key(self, provider: str) -> Optional[str]:
        
        encrypted_key = self.get(f"api_keys.{provider}")
        if encrypted_key:
            return self.decrypt_text(encrypted_key)
        return None
    
    def remove_api_key(self, provider: str) -> None:
        
        if "api_keys" in self.config and provider in self.config["api_keys"]:
            del self.config["api_keys"][provider]
            self._save_config()
    
    def get_available_providers(self) -> list:
        
        return list(self.config.get("api_keys", {}).keys())
    
    def export_config(self, file_path: str, include_api_keys: bool = False) -> bool:
        
        try:
            export_config = self.config.copy()
            
            if not include_api_keys:
                export_config.pop("api_keys", None)
            else:

                if "api_keys" in export_config:
                    decrypted_keys = {}
                    for provider, encrypted_key in export_config["api_keys"].items():
                        decrypted_keys[provider] = self.decrypt_text(encrypted_key)
                    export_config["api_keys"] = decrypted_keys
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            

            if "api_keys" in imported_config:
                encrypted_keys = {}
                for provider, api_key in imported_config["api_keys"].items():
                    encrypted_keys[provider] = self.encrypt_text(api_key)
                imported_config["api_keys"] = encrypted_keys
            

            self.config = self._merge_config(self.config, imported_config)
            self._save_config()
            return True
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False
    
    def reset_to_defaults(self) -> None:
        
        self.config_file.unlink(missing_ok=True)
        self.config = self._load_config()
