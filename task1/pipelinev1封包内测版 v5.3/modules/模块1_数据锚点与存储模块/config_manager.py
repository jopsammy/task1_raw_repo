
"""
模块职责：配置管理模块
负责配置文件的加载、保存、验证
"""

import os
import json
from typing import Dict, Any, Optional, List


class ConfigManager:
    """
    配置管理器
    负责加载和保存配置文件
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径，None则使用默认路径或环境变量
        """
        if config_path is None:
            config_path = os.environ.get("AC_CONFIG_PATH")
        if config_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '../..'))
            config_path = os.path.join(project_root, "config", "config.json")
        
        self.config_path = config_path
        self.config_template_path = os.path.join(
            os.path.dirname(config_path), 
            "config_template.json"
        )
        self.config: Dict[str, Any] = {}
        
        self._load_config()

    def _load_config(self):
        """
        加载配置文件
        如果文件不存在，从模板创建
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                self._load_from_template()
        else:
            self._load_from_template()

    def _load_from_template(self):
        """
        从模板加载配置
        """
        if os.path.exists(self.config_template_path):
            try:
                with open(self.config_template_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.save_config()
            except Exception as e:
                print(f"加载配置模板失败: {e}")
                self._init_default_config()
        else:
            self._init_default_config()

    def _init_default_config(self):
        """
        初始化默认配置
        """
        self.config = {
            "project": {
                "name": "需求结构化分析工具",
                "version": "1.0.0",
                "description": "基于AC范式的需求结构化分析工具"
            },
            "llm": {
                "providers": {
                    "openai": {
                        "api_key": "",
                        "api_base": "https://api.openai.com/v1",
                        "model": "gpt-4",
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "timeout": 300
                    },
                    "deepseek": {
                        "api_key": "",
                        "api_base": "https://api.deepseek.com/v1",
                        "model": "deepseek-chat",
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "timeout": 300
                    },
                    "doubao": {
                        "api_key": "",
                        "api_base": "https://ark.cn-beijing.volces.com/api/v3",
                        "model": "ep-20250301123456-abcd",
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "timeout": 300
                    }
                },
                "default_provider": "openai"
            },
            "workspace": {
                "root_dir": "workspace",
                "data_dir": "workspace/data",
                "backup_dir": "workspace/backups",
                "export_dir": "workspace/exports"
            },
            "storage": {
                "auto_backup": True,
                "max_backup_count": 50,
                "content_fingerprint_algorithm": "md5"
            },
            "ui": {
                "theme": "light",
                "page_title": "需求结构化分析工具",
                "page_icon": "📊"
            }
        }
        self.save_config()

    def save_config(self):
        """
        保存配置到文件
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """
        获取完整配置

        Returns:
            配置字典
        """
        return self.config.copy()

    def get_llm_providers(self) -> Dict[str, Any]:
        """
        获取LLM提供商配置

        Returns:
            LLM提供商配置字典
        """
        return self.config.get("llm", {}).get("providers", {}).copy()

    def get_llm_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定LLM提供商配置

        Args:
            provider_id: 提供商ID

        Returns:
            提供商配置，不存在返回None
        """
        return self.get_llm_providers().get(provider_id)

    def set_llm_provider(self, provider_id: str, config: Dict[str, Any]):
        """
        设置LLM提供商配置

        Args:
            provider_id: 提供商ID
            config: 配置字典
        """
        if "llm" not in self.config:
            self.config["llm"] = {}
        if "providers" not in self.config["llm"]:
            self.config["llm"]["providers"] = {}
        self.config["llm"]["providers"][provider_id] = config

    def get_default_provider(self) -> str:
        """
        获取默认LLM提供商

        Returns:
            默认提供商ID
        """
        return self.config.get("llm", {}).get("default_provider", "openai")

    def set_default_provider(self, provider_id: str):
        """
        设置默认LLM提供商

        Args:
            provider_id: 提供商ID
        """
        if "llm" not in self.config:
            self.config["llm"] = {}
        self.config["llm"]["default_provider"] = provider_id

    def update_config(self, updates: Dict[str, Any]):
        """
        批量更新配置

        Args:
            updates: 更新字典
        """
        def deep_update(target, source):
            for key, value in source.items():
                if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                    deep_update(target[key], value)
                else:
                    target[key] = value
        
        deep_update(self.config, updates)

    def get_provider_slots(self) -> List[str]:
        """
        获取前3个provider槽位

        Returns:
            provider_id列表，不足3个时用slot_1/slot_2/slot_3补齐
        """
        providers = self.get_llm_providers()
        provider_ids = list(providers.keys())
        
        while len(provider_ids) < 3:
            slot_id = f"slot_{len(provider_ids) + 1}"
            provider_ids.append(slot_id)
        
        return provider_ids[:3]

    def validate_api_base(self, api_base: str) -> bool:
        """
        验证api_base格式

        Args:
            api_base: API基础URL

        Returns:
            验证是否通过
        """
        if not api_base:
            return False
        return api_base.startswith("http://") or api_base.startswith("https://")

    def validate_model(self, model: str) -> bool:
        """
        验证model非空

        Args:
            model: 模型名称

        Returns:
            验证是否通过
        """
        return bool(model and model.strip())

    def update_provider_fields(self, provider_id: str, api_base: Optional[str] = None, 
                               api_key: Optional[str] = None, model: Optional[str] = None) -> bool:
        """
        更新provider的指定字段（仅更新api_base/api_key/model）

        Args:
            provider_id: 提供商ID
            api_base: API基础URL（None表示不更新）
            api_key: API密钥（None表示不更新，空字符串表示保持原值）
            model: 模型名称（None表示不更新）

        Returns:
            更新是否成功
        """
        providers = self.get_llm_providers()
        
        if provider_id not in providers:
            providers[provider_id] = {
                "api_key": "",
                "api_base": "",
                "model": "",
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout": 300
            }
        
        provider = providers[provider_id]
        
        if api_base is not None:
            if not self.validate_api_base(api_base):
                return False
            provider["api_base"] = api_base
        
        if api_key is not None:
            if api_key:
                provider["api_key"] = api_key
        
        if model is not None:
            if not self.validate_model(model):
                return False
            provider["model"] = model
        
        self.set_llm_provider(provider_id, provider)
        return True


_config_manager_instance: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """
    获取配置管理器单例

    Args:
        config_path: 配置文件路径

    Returns:
        ConfigManager实例
    """
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager(config_path)
    return _config_manager_instance


def reset_config_manager():
    """重置配置管理器单例"""
    global _config_manager_instance
    _config_manager_instance = None
