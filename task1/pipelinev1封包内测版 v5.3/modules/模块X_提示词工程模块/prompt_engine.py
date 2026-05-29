"""
提示词工程模块 - 核心类文件
负责提示词模板的管理、加载、缓存、渲染和调试
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound


class PromptEngine:
    """
    提示词引擎核心类
    提供提示词模板管理、渲染、缓存、热更新等功能
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        初始化提示词引擎
        
        :param template_dir: 提示词模板目录，若为None则使用当前文件所在目录下的prompts文件夹
        """
        if template_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(current_dir, "prompts")
        
        self.template_dir = template_dir
        self._ensure_template_dir()
        
        # 初始化Jinja2环境
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False
        )
        
        # 模板缓存
        self._template_cache: Dict[str, Template] = {}
        self._template_mtime: Dict[str, float] = {}
        
        # 提示词元数据缓存
        self._template_meta_cache: Dict[str, Dict[str, Any]] = {}
        
        # 预加载所有模板
        self._load_all_templates()
    
    def _ensure_template_dir(self):
        """确保模板目录存在"""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir, exist_ok=True)
    
    def _load_all_templates(self):
        """预加载所有模板文件"""
        if not os.path.exists(self.template_dir):
            return
        
        for filename in os.listdir(self.template_dir):
            if filename.endswith(".jinja"):
                template_id = filename[:-6]  # 去掉.jinja后缀
                try:
                    self._load_template(template_id)
                except Exception as e:
                    print(f"[WARNING] 加载模板 {template_id} 失败: {e}")
    
    def _load_template(self, template_id: str) -> Template:
        """
        加载指定模板，支持热更新
        
        :param template_id: 模板ID（不含.jinja后缀）
        :return: Jinja2模板对象
        """
        filename = f"{template_id}.jinja"
        filepath = os.path.join(self.template_dir, filename)
        
        if not os.path.exists(filepath):
            raise TemplateNotFound(f"模板文件不存在: {filepath}")
        
        # 检查文件是否更新
        mtime = os.path.getmtime(filepath)
        if template_id in self._template_cache and self._template_mtime.get(template_id) == mtime:
            return self._template_cache[template_id]
        
        # 加载或重新加载模板
        template = self.jinja_env.get_template(filename)
        self._template_cache[template_id] = template
        self._template_mtime[template_id] = mtime
        
        # 尝试加载元数据
        self._load_template_meta(template_id, filepath)
        
        return template
    
    def _load_template_meta(self, template_id: str, filepath: str):
        """
        加载模板元数据（从模板文件的注释中提取）
        
        :param template_id: 模板ID
        :param filepath: 模板文件路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的元数据提取：从开头的注释中提取
            meta = {
                "template_id": template_id,
                "name": template_id,
                "category": "custom",
                "version": "v1.0.0",
                "created_at": datetime.now().isoformat(),
                "variables": []
            }
            
            # 尝试从模板内容中推断变量
            variables = set()
            for token in self.jinja_env.lex(content):
                if token.type == 'name' and not token.value.startswith('_'):
                    variables.add(token.value)
            
            meta["variables"] = [{"name": var, "type": "any", "required": True} for var in variables]
            self._template_meta_cache[template_id] = meta
            
        except Exception:
            pass
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """
        获取指定模板的完整信息
        
        :param template_id: 模板ID
        :return: 模板信息字典
        """
        template = self._load_template(template_id)
        meta = self._template_meta_cache.get(template_id, {})
        
        return {
            "template_id": template_id,
            "name": meta.get("name", template_id),
            "category": meta.get("category", "custom"),
            "version": meta.get("version", "v1.0.0"),
            "meta": meta,
            "template": template
        }
    
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出所有可用模板
        
        :param category: 分类过滤，None表示返回所有
        :return: 模板信息列表
        """
        templates = []
        for template_id in self._template_cache.keys():
            meta = self._template_meta_cache.get(template_id, {})
            if category is None or meta.get("category") == category:
                templates.append({
                    "template_id": template_id,
                    "name": meta.get("name", template_id),
                    "category": meta.get("category", "custom"),
                    "version": meta.get("version", "v1.0.0")
                })
        return templates
    
    def validate_variables(self, template_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证模板变量是否完整
        
        :param template_id: 模板ID
        :param context: 变量上下文
        :return: 验证结果，包含missing_vars、extra_vars
        """
        meta = self._template_meta_cache.get(template_id, {})
        required_vars = {var["name"] for var in meta.get("variables", []) if var.get("required", True)}
        provided_vars = set(context.keys())
        
        missing_vars = required_vars - provided_vars
        extra_vars = provided_vars - required_vars
        
        return {
            "valid": len(missing_vars) == 0,
            "missing_vars": list(missing_vars),
            "extra_vars": list(extra_vars)
        }
    
    def generate_prompt(self, template_id: str, context: Dict[str, Any], 
                        system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        生成完整的提示词对象
        
        :param template_id: 模板ID
        :param context: 变量上下文
        :param system_prompt: 可选的系统提示词，覆盖模板中的
        :return: 提示词对象，包含system_prompt、user_prompt、raw_template等
        """
        template = self._load_template(template_id)
        
        # 渲染用户提示词
        user_prompt = template.render(**context)
        
        # 如果模板有元数据，尝试获取系统提示词
        meta = self._template_meta_cache.get(template_id, {})
        if system_prompt is None:
            system_prompt = meta.get("system_prompt", "")
        
        # 计算内容指纹
        content_hash = hashlib.md5((system_prompt + user_prompt).encode('utf-8')).hexdigest()
        
        return {
            "template_id": template_id,
            "generated_at": datetime.now().isoformat(),
            "content_hash": content_hash,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "context": context
        }
    
    def preview_prompt(self, template_id: str, context: Dict[str, Any]) -> str:
        """
        预览渲染后的提示词（用于调试）
        
        :param template_id: 模板ID
        :param context: 变量上下文
        :return: 格式化的提示词预览文本
        """
        prompt_obj = self.generate_prompt(template_id, context)
        
        preview = []
        preview.append("=" * 80)
        preview.append(f"【提示词预览】模板: {template_id}")
        preview.append("=" * 80)
        preview.append("\n[系统提示词]\n")
        preview.append(prompt_obj["system_prompt"] or "(无)")
        preview.append("\n" + "=" * 80)
        preview.append("\n[用户提示词]\n")
        preview.append(prompt_obj["user_prompt"])
        preview.append("\n" + "=" * 80)
        preview.append(f"\n[元数据] 生成时间: {prompt_obj['generated_at']}, 内容指纹: {prompt_obj['content_hash']}")
        
        return "\n".join(preview)
    
    def render_raw(self, template_id: str, context: Dict[str, Any]) -> str:
        """
        仅渲染用户提示词部分（原始文本）
        
        :param template_id: 模板ID
        :param context: 变量上下文
        :return: 渲染后的文本
        """
        template = self._load_template(template_id)
        return template.render(**context)
    
    def add_template_from_string(self, template_id: str, template_content: str, 
                                  meta: Optional[Dict[str, Any]] = None):
        """
        从字符串添加新模板
        
        :param template_id: 模板ID
        :param template_content: 模板内容
        :param meta: 可选的元数据
        """
        filepath = os.path.join(self.template_dir, f"{template_id}.jinja")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        if meta:
            self._template_meta_cache[template_id] = meta
        
        self._load_template(template_id)
    
    def get_template_content(self, template_id: str) -> str:
        """
        获取模板原始内容
        
        :param template_id: 模板ID
        :return: 模板内容字符串
        """
        filepath = os.path.join(self.template_dir, f"{template_id}.jinja")
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def clear_cache(self):
        """清空模板缓存"""
        self._template_cache.clear()
        self._template_mtime.clear()
        self._template_meta_cache.clear()
        self._load_all_templates()


# 全局单例
_prompt_engine_instance: Optional[PromptEngine] = None


def get_prompt_engine() -> PromptEngine:
    """
    获取提示词引擎单例
    
    :return: PromptEngine实例
    """
    global _prompt_engine_instance
    if _prompt_engine_instance is None:
        _prompt_engine_instance = PromptEngine()
    return _prompt_engine_instance


def reset_prompt_engine():
    """重置提示词引擎单例"""
    global _prompt_engine_instance
    _prompt_engine_instance = None
