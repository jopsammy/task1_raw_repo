"""
模块职责：运行记录管理模块
负责Pipeline运行记录的持久化存储、加载、查询
"""

import os
import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class RunRecordManager:
    """
    运行记录管理器，负责Pipeline运行记录的管理
    """
    
    def __init__(self, workspace_dir: str = None):
        """
        初始化运行记录管理器
        
        Args:
            workspace_dir: 工作区目录，默认值为基于项目根目录的路径
        """
        if workspace_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '../..'))
            self.workspace_dir = os.path.join(project_root, "workspace")
        else:
            self.workspace_dir = workspace_dir
            
        self.runs_dir = os.path.join(self.workspace_dir, "runs")
        self._ensure_directories()
    
    def _ensure_directories(self):
        """
        确保必要的目录存在
        """
        if not os.path.exists(self.runs_dir):
            os.makedirs(self.runs_dir, exist_ok=True)
    
    def generate_run_id(self) -> str:
        """
        生成运行记录ID
        
        Returns:
            运行记录ID
        """
        return str(uuid.uuid4())
    
    def _get_date_directory(self, date: Optional[datetime] = None) -> str:
        """
        获取日期目录
        
        Args:
            date: 日期，默认使用当前日期
        
        Returns:
            日期目录路径
        """
        if date is None:
            date = datetime.now()
        date_str = date.strftime("%Y%m%d")
        date_dir = os.path.join(self.runs_dir, date_str)
        if not os.path.exists(date_dir):
            os.makedirs(date_dir, exist_ok=True)
        return date_dir
    
    def save_run_record(self, run_data: Dict[str, Any]) -> str:
        """
        保存运行记录
        
        Args:
            run_data: 运行记录数据
        
        Returns:
            运行记录ID
        """
        # 确保数据完整性
        if "run_id" not in run_data:
            run_data["run_id"] = self.generate_run_id()
        
        if "created_at" not in run_data:
            run_data["created_at"] = datetime.now().isoformat()
        
        if "updated_at" not in run_data:
            run_data["updated_at"] = datetime.now().isoformat()
        else:
            run_data["updated_at"] = datetime.now().isoformat()
        
        # 确定存储目录
        created_date = datetime.fromisoformat(run_data["created_at"])
        date_dir = self._get_date_directory(created_date)
        
        # 保存记录
        run_id = run_data["run_id"]
        file_path = os.path.join(date_dir, f"{run_id}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(run_data, f, ensure_ascii=False, indent=2)
        
        return run_id
    
    def load_run_record(self, run_id: str, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        加载运行记录
        
        Args:
            run_id: 运行记录ID
            date: 日期字符串 (YYYYMMDD)，如果不指定则搜索所有日期目录
        
        Returns:
            运行记录数据，不存在返回None
        """
        if date:
            # 指定日期目录
            date_dir = os.path.join(self.runs_dir, date)
            if os.path.exists(date_dir):
                file_path = os.path.join(date_dir, f"{run_id}.json")
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
        else:
            # 搜索所有日期目录
            for date_dir in os.listdir(self.runs_dir):
                date_path = os.path.join(self.runs_dir, date_dir)
                if os.path.isdir(date_path):
                    file_path = os.path.join(date_path, f"{run_id}.json")
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            return json.load(f)
        
        return None
    
    def list_run_records(self, limit: int = 50, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出运行记录
        
        Args:
            limit: 限制返回数量
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        
        Returns:
            运行记录列表
        """
        records = []
        
        # 获取日期目录列表
        date_dirs = []
        for date_dir in os.listdir(self.runs_dir):
            date_path = os.path.join(self.runs_dir, date_dir)
            if os.path.isdir(date_path):
                # 过滤日期范围
                if start_date and date_dir < start_date:
                    continue
                if end_date and date_dir > end_date:
                    continue
                date_dirs.append(date_dir)
        
        # 按日期降序排序
        date_dirs.sort(reverse=True)
        
        # 收集记录
        for date_dir in date_dirs:
            date_path = os.path.join(self.runs_dir, date_dir)
            for filename in os.listdir(date_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(date_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            record = json.load(f)
                            record["date"] = date_dir
                            records.append(record)
                    except Exception as e:
                        print(f"加载记录 {filename} 失败：{str(e)}")
                    
                    if len(records) >= limit:
                        break
            
            if len(records) >= limit:
                break
        
        # 按创建时间降序排序
        records.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return records
    
    def get_run_records_by_project(self, project_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        按项目ID获取运行记录
        
        Args:
            project_id: 项目ID
            limit: 限制返回数量
        
        Returns:
            运行记录列表
        """
        all_records = self.list_run_records(limit=100)  # 先获取足够多的记录
        project_records = [r for r in all_records if r.get("project_id") == project_id]
        return project_records[:limit]
    
    def delete_run_record(self, run_id: str, date: Optional[str] = None) -> bool:
        """
        删除运行记录
        
        Args:
            run_id: 运行记录ID
            date: 日期字符串 (YYYYMMDD)
        
        Returns:
            是否删除成功
        """
        if date:
            # 指定日期目录
            date_dir = os.path.join(self.runs_dir, date)
            if os.path.exists(date_dir):
                file_path = os.path.join(date_dir, f"{run_id}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True
        else:
            # 搜索所有日期目录
            for date_dir in os.listdir(self.runs_dir):
                date_path = os.path.join(self.runs_dir, date_dir)
                if os.path.isdir(date_path):
                    file_path = os.path.join(date_path, f"{run_id}.json")
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        return True
        
        return False
    
    def get_latest_run_record(self) -> Optional[Dict[str, Any]]:
        """
        获取最新的运行记录
        
        Returns:
            最新的运行记录，不存在返回None
        """
        records = self.list_run_records(limit=1)
        return records[0] if records else None


# 全局单例
_run_record_manager_instance: Optional[RunRecordManager] = None


def get_run_record_manager(workspace_dir: Optional[str] = None) -> RunRecordManager:
    """
    获取运行记录管理器单例
    
    Args:
        workspace_dir: 工作区目录
    
    Returns:
        RunRecordManager实例
    """
    global _run_record_manager_instance
    if _run_record_manager_instance is None:
        _run_record_manager_instance = RunRecordManager(workspace_dir)
    return _run_record_manager_instance


def reset_run_record_manager():
    """重置运行记录管理器单例"""
    global _run_record_manager_instance
    _run_record_manager_instance = None