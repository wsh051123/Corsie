"""
AI客户端抽象层 - 统一不同AI服务提供商的接口
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator, Callable
from dataclasses import dataclass
from openai import OpenAI, AsyncOpenAI
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

@dataclass
class AIResponse:
    """AI响应数据类"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    error: Optional[str] = None

@dataclass
class AIModelInfo:
    """AI模型信息"""
    provider: str
    model_id: str
    name: str
    max_tokens: int
    supports_streaming: bool = True
    cost_per_token: Optional[float] = None

class AIClientBase(ABC):
    """AI客户端基类"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """创建HTTP会话，配置重试策略"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    @abstractmethod
    async def chat_completion(self, messages: List[Dict[str, str]], 
                            temperature: float = 0.7,
                            max_tokens: int = 2048,
                            stream: bool = False) -> AIResponse:
        pass
    
    @abstractmethod
    async def chat_completion_stream(self, messages: List[Dict[str, str]],
                                   temperature: float = 0.7,
                                   max_tokens: int = 2048) -> AsyncGenerator[str, None]:
        pass
    
    @abstractmethod
    def get_model_info(self) -> AIModelInfo:
        pass

class DeepSeekClient(AIClientBase):
    """DeepSeek客户端"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        super().__init__(api_key, model)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    async def chat_completion(self, messages: List[Dict[str, str]], 
                            temperature: float = 0.7,
                            max_tokens: int = 2048,
                            stream: bool = False) -> AIResponse:
        try:
            if stream:
                full_content = ""
                async for chunk in self.chat_completion_stream(messages, temperature, max_tokens):
                    full_content += chunk
                
                return AIResponse(
                    content=full_content,
                    model=self.model,
                    finish_reason="stop"
                )
            else:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return AIResponse(
                    content=response.choices[0].message.content,
                    model=response.model,
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    },
                    finish_reason=response.choices[0].finish_reason
                )
        
        except Exception as e:
            return AIResponse(
                content="",
                model=self.model,
                error=str(e)
            )
    
    async def chat_completion_stream(self, messages: List[Dict[str, str]],
                                   temperature: float = 0.7,
                                   max_tokens: int = 2048) -> AsyncGenerator[str, None]:
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            yield f"错误: {str(e)}"
    
    def get_model_info(self) -> AIModelInfo:
        """获取DeepSeek模型信息"""
        return AIModelInfo(
            provider="DeepSeek",
            model_id=self.model,
            name=self.model,
            max_tokens=32768,
            supports_streaming=True,
            cost_per_token=0.0014
        )

class OpenRouterClient(AIClientBase):
    """OpenRouter客户端"""
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        super().__init__(api_key, model)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
    
    async def chat_completion(self, messages: List[Dict[str, str]], 
                            temperature: float = 0.7,
                            max_tokens: int = 2048,
                            stream: bool = False) -> AIResponse:
        try:
            if stream:
                full_content = ""
                async for chunk in self.chat_completion_stream(messages, temperature, max_tokens):
                    full_content += chunk
                
                return AIResponse(
                    content=full_content,
                    model=self.model,
                    finish_reason="stop"
                )
            else:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_headers={
                        "X-Title": "Corsie"
                    }
                )
                
                return AIResponse(
                    content=response.choices[0].message.content,
                    model=response.model,
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    },
                    finish_reason=response.choices[0].finish_reason
                )
        
        except Exception as e:
            return AIResponse(
                content="",
                model=self.model,
                error=str(e)
            )
    
    async def chat_completion_stream(self, messages: List[Dict[str, str]],
                                   temperature: float = 0.7,
                                   max_tokens: int = 2048) -> AsyncGenerator[str, None]:
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                extra_headers={
                    "X-Title": "Corsie"
                }
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            yield f"错误: {str(e)}"
    
    def get_model_info(self) -> AIModelInfo:
        """获取OpenRouter模型信息"""
        return AIModelInfo(
            provider="OpenRouter",
            model_id=self.model,
            name=self.model,
            max_tokens=4096,
            supports_streaming=True,
            cost_per_token=0.001
        )

class AIClientManager:
    """AI客户端管理器"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self._clients: Dict[str, AIClientBase] = {}
    
    def get_client(self, provider: str, model: str) -> Optional[AIClientBase]:
        """获取AI客户端实例"""
        client_key = f"{provider}:{model}"
        
        if client_key in self._clients:
            return self._clients[client_key]
        
        api_key = self.config_manager.get_api_key(provider.lower())
        if not api_key:
            return None
        
        try:
            if provider.lower() == "deepseek":
                client = DeepSeekClient(api_key, model)
            elif provider.lower() == "openrouter":
                client = OpenRouterClient(api_key, model)
            else:
                return None
            
            self._clients[client_key] = client
            return client
        
        except Exception as e:
            print(f"创建AI客户端失败: {e}")
            return None
    
    def get_available_models(self) -> List[AIModelInfo]:
        """获取可用模型列表"""
        models = []
        
        if self.config_manager.get_api_key("deepseek"):
            deepseek_models = [
                ("deepseek-chat", "DeepSeek Chat", 32768, 0.0014),
                ("deepseek-reasoner", "DeepSeek Reasoner", 32768, 0.0055),
            ]
            for model_id, name, max_tokens, cost in deepseek_models:
                models.append(AIModelInfo(
                    provider="DeepSeek",
                    model_id=model_id,
                    name=name,
                    max_tokens=max_tokens,
                    supports_streaming=True,
                    cost_per_token=cost
                ))
        
        if self.config_manager.get_api_key("openrouter"):
            openrouter_models = [
                ("deepseek/deepseek-r1-0528:free", "DeepSeek R1 (Free)", 32768, 0.0),
                ("deepseek/deepseek-chat-v3-0324:free", "DeepSeek Chat V3 (Free)", 32768, 0.0),
                ("anthropic/claude-sonnet-4", "Claude Sonnet 4", 200000, 0.003),
                ("anthropic/claude-3.7-sonnet", "Claude 3.7 Sonnet", 200000, 0.003),
                ("google/gemini-2.5-pro-preview", "Gemini 2.5 Pro Preview", 2097152, 0.00125),
                ("openai/chatgpt-4o-latest", "ChatGPT-4o Latest", 128000, 0.0025),
                ("x-ai/grok-3", "Grok 3", 131072, 0.002),
            ]
            for model_id, name, max_tokens, cost in openrouter_models:
                models.append(AIModelInfo(
                    provider="OpenRouter",
                    model_id=model_id,
                    name=name,
                    max_tokens=max_tokens,
                    supports_streaming=True,
                    cost_per_token=cost
                ))
        
        return models
    
    def clear_cache(self):
        self._clients.clear()
