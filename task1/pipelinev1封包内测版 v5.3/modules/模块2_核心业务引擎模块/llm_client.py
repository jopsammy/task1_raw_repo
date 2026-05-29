
"""
模块职责：LLM客户端模块
负责多LLM提供商的API调用封装，支持OpenAI兼容的任意提供商
"""

import os
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from abc import ABC, abstractmethod

# 导入运行记录管理器
from modules.模块1_数据锚点与存储模块.run_record_manager import get_run_record_manager


class LLMProvider(ABC):
    """LLM提供商抽象基类"""

    @abstractmethod
    def call(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """
        调用LLM API

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            **kwargs: 其他参数

        Returns:
            包含响应结果的字典
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        健康检查

        Returns:
            健康状态
        """
        pass


class OpenAICompatibleProvider(LLMProvider):
    """通用OpenAI兼容API提供商"""

    def __init__(self, provider_id: str, api_key: str, api_base: str,
                 model: str, timeout: int = 300, max_retries: int = 3):
        """
        初始化OpenAI兼容API提供商

        Args:
            provider_id: 提供商ID
            api_key: API密钥
            api_base: API基础URL
            model: 模型名称
            timeout: 超时时间（秒）
            max_retries: 最大重试次数
        """
        self.provider_id = provider_id
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

    def call(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """
        调用OpenAI兼容API
        """
        try:
            import openai

            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
                timeout=self.timeout
            )

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})

            for attempt in range(self.max_retries):
                try:
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=kwargs.get("temperature", 0.7),
                        max_tokens=kwargs.get("max_tokens", 4096)
                    )

                    return {
                        "success": True,
                        "content": response.choices[0].message.content,
                        "provider": self.provider_id,
                        "model": self.model,
                        "usage": {
                            "input_tokens": response.usage.prompt_tokens,
                            "output_tokens": response.usage.completion_tokens,
                            "total_tokens": response.usage.total_tokens
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                    else:
                        raise
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": self.provider_id,
                "usage": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0
                },
                "timestamp": datetime.now().isoformat()
            }

    def health_check(self) -> bool:
        """
        健康检查 - 简单测试API连通性
        """
        try:
            result = self.call("你是一个助手", "hi", max_tokens=10)
            return result.get("success", False)
        except Exception:
            return False


class LLMClient:
    """
    LLM客户端，统一管理多个LLM提供商
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化LLM客户端

        Args:
            config_path: 配置文件路径，默认从项目根目录加载或环境变量
        """
        if config_path is None:
            config_path = os.environ.get("AC_CONFIG_PATH")
        if config_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '../..'))
            config_path = os.path.join(project_root, "config", "config.json")

        self.config_path = config_path
        self.providers: Dict[str, LLMProvider] = {}
        self.default_provider: Optional[str] = None
        self.run_record_manager = get_run_record_manager()

        self._load_config()
        self._initialize_providers()

    def _load_config(self):
        """
        加载配置文件
        """
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "llm": {
                    "providers": {},
                    "default_provider": "openai"
                }
            }

    def _initialize_providers(self):
        """
        初始化所有提供商
        """
        providers_config = self.config.get("llm", {}).get("providers", {})

        for provider_id, cfg in providers_config.items():
            if cfg.get("api_key"):
                self.providers[provider_id] = OpenAICompatibleProvider(
                    provider_id=provider_id,
                    api_key=cfg["api_key"],
                    api_base=cfg.get("api_base", "https://api.openai.com/v1"),
                    model=cfg.get("model", "gpt-4-turbo"),
                    timeout=cfg.get("timeout", 300),
                    max_retries=cfg.get("max_retries", 3)
                )

        self.default_provider = self.config.get("llm", {}).get("default_provider", "openai")
        if self.default_provider not in self.providers and self.providers:
            self.default_provider = list(self.providers.keys())[0]

    def call_llm(self, system_prompt: str, user_prompt: str,
                  provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        调用LLM

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            provider: 指定提供商，None使用默认
            **kwargs: 其他参数

        Returns:
            响应结果
        """
        if provider is None:
            provider = self.default_provider

        if provider not in self.providers:
            available = list(self.providers.keys())
            result = {
                "success": False,
                "error": f"提供商 {provider} 不可用，可用提供商: {available}",
                "usage": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0
                },
                "timestamp": datetime.now().isoformat()
            }
            return result

        # 记录调用开始时间
        start_time = datetime.now()
        
        # 调用LLM
        result = self.providers[provider].call(system_prompt, user_prompt, **kwargs)
        
        # 记录调用结束时间和响应时间
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        # 添加响应时间到结果
        result["response_time"] = response_time
        result["start_time"] = start_time.isoformat()
        result["end_time"] = end_time.isoformat()
        
        # 记录LLM调用详情（如果有当前运行ID）
        # 注意：这里需要通过参数传递run_id，暂时记录到最新的运行记录中
        latest_run = self.run_record_manager.get_latest_run_record()
        if latest_run and latest_run.get("status") == "running":
            # 确保llm_calls字段存在
            if "llm_calls" not in latest_run:
                latest_run["llm_calls"] = []
            
            # 记录LLM调用详情（不包含敏感信息）
            llm_call_record = {
                "provider": provider,
                "model": self.providers[provider].model,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "response_time": response_time,
                "success": result.get("success", False),
                "usage": result.get("usage", {})
            }
            
            latest_run["llm_calls"].append(llm_call_record)
            latest_run["updated_at"] = datetime.now().isoformat()
            self.run_record_manager.save_run_record(latest_run)
        
        return result

    def call_llm_with_fallback(self, system_prompt: str, user_prompt: str,
                                 providers: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        带降级的LLM调用

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            providers: 提供商列表，按优先级排序
            **kwargs: 其他参数

        Returns:
            响应结果
        """
        if providers is None:
            providers = list(self.providers.keys())

        last_error = None
        for provider in providers:
            result = self.call_llm(system_prompt, user_prompt, provider, **kwargs)
            if result.get("success"):
                return result
            last_error = result

        if last_error:
            return last_error
        return {
            "success": False,
            "error": "所有提供商调用失败",
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_available_providers(self) -> List[str]:
        """
        获取可用的提供商列表

        Returns:
            提供商ID列表
        """
        return list(self.providers.keys())

    def health_check_all(self) -> Dict[str, bool]:
        """
        检查所有提供商的健康状态

        Returns:
            提供商健康状态字典
        """
        results = {}
        for provider_id, provider in self.providers.items():
            results[provider_id] = provider.health_check()
        return results

    def add_provider(self, provider_id: str, provider: LLMProvider):
        """
        动态添加提供商

        Args:
            provider_id: 提供商ID
            provider: 提供商实例
        """
        self.providers[provider_id] = provider

    def set_default_provider(self, provider_id: str):
        """
        设置默认提供商

        Args:
            provider_id: 提供商ID
        """
        if provider_id in self.providers:
            self.default_provider = provider_id


# 全局单例
_llm_client_instance: Optional[LLMClient] = None


def get_llm_client(config_path: Optional[str] = None) -> LLMClient:
    """
    获取LLM客户端单例

    Args:
        config_path: 配置文件路径

    Returns:
        LLMClient实例
    """
    global _llm_client_instance
    if _llm_client_instance is None:
        _llm_client_instance = LLMClient(config_path)
    return _llm_client_instance


def reset_llm_client():
    """重置LLM客户端单例"""
    global _llm_client_instance
    _llm_client_instance = None
