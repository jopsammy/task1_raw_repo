"""
模块职责：数据锚点与存储模块
负责需求锚点管理、架构锚点管理、契约锚点管理、全链路可追溯机制、数据JSON存储与读取
"""

import os
import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class DataAnchorManager:
    """
    数据锚点管理器，提供需求锚点、架构锚点、契约锚点的管理，以及全链路可追溯机制
    """
    
    def __init__(self, workspace_dir: str = None):
        """
        初始化数据锚点管理器
        
        Args:
            workspace_dir: 工作区目录，默认值为基于项目根目录的路径
        """
        if workspace_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '../..'))
            self.workspace_dir = os.path.join(project_root, "workspace")
        else:
            self.workspace_dir = workspace_dir
            
        self.requirements_dir = os.path.join(self.workspace_dir, "requirements")
        self.anchors_dir = os.path.join(self.workspace_dir, "anchors")
        self.backups_dir = os.path.join(self.workspace_dir, "backups")
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """
        确保必要的目录存在
        """
        for directory in [self.requirements_dir, self.anchors_dir, self.backups_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
    
    def create_anchor(self, content: str) -> str:
        """
        生成内容锚点ID（MD5哈希）
        
        Args:
            content: 内容文本
            
        Returns:
            MD5哈希值作为锚点ID
        """
        md5_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        return md5_hash
    
    def generate_uuid(self) -> str:
        """
        生成UUID唯一标识
        
        Returns:
            UUID字符串
        """
        return str(uuid.uuid4())
    
    def create_requirement_project(self, project_name: str) -> str:
        """
        创建新的需求项目
        
        Args:
            project_name: 项目名称
            
        Returns:
            项目唯一ID（project_id）
            
        Raises:
            IOError: 目录创建失败或文件写入失败时抛出
        """
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        random_str = f"{int(now.timestamp() % 1000000):06d}"
        project_id = f"{date_str}_{random_str}"
        
        project_data = {
            "project_id": project_id,
            "project_name": project_name,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "requirements": [],
            "metadata": {}
        }
        
        self._save_requirement_project(project_id, project_data)
        return project_id
    
    def load_requirement_project(self, project_id: str) -> Dict:
        """
        加载指定ID的需求项目
        
        Args:
            project_id: 项目唯一ID
            
        Returns:
            项目数据字典
            
        Raises:
            FileNotFoundError: 项目不存在时抛出
            ValueError: 项目数据不符合Schema时抛出
        """
        file_path = os.path.join(self.requirements_dir, f"{project_id}.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"需求项目 {project_id} 不存在")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        self._validate_project_schema(project_data)
        return project_data
    
    def save_requirement_project(self, project_id: str, project_data: Dict) -> bool:
        """
        保存需求项目数据
        
        Args:
            project_id: 项目唯一ID
            project_data: 项目数据字典
            
        Returns:
            保存成功返回True，失败返回False
            
        Raises:
            ValueError: 数据不符合Schema时抛出
        """
        try:
            self._validate_project_schema(project_data)
            project_data["updated_at"] = datetime.now().isoformat()
            self._save_requirement_project(project_id, project_data)
            self._create_backup(project_id, project_data)
            return True
        except Exception as e:
            print(f"保存项目失败：{str(e)}")
            return False
    
    def _save_requirement_project(self, project_id: str, project_data: Dict):
        """
        内部方法：保存需求项目数据
        """
        file_path = os.path.join(self.requirements_dir, f"{project_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
    
    def add_requirement_item(self, project_id: str, requirement_item: Dict) -> str:
        """
        向项目中添加需求条目
        
        Args:
            project_id: 项目唯一ID
            requirement_item: 需求条目数据
            
        Returns:
            需求条目ID（req_id）
        """
        project_data = self.load_requirement_project(project_id)
        
        if "req_id" not in requirement_item:
            requirement_item["req_id"] = self.generate_uuid()
        
        if "anchor_id" not in requirement_item and "content" in requirement_item:
            requirement_item["anchor_id"] = self.create_anchor(requirement_item["content"])
        
        if "created_at" not in requirement_item:
            requirement_item["created_at"] = datetime.now().isoformat()
        
        project_data["requirements"].append(requirement_item)
        self.save_requirement_project(project_id, project_data)
        
        return requirement_item["req_id"]
    
    def update_requirement_item(self, project_id: str, req_id: str, updates: Dict) -> bool:
        """
        更新需求条目
        
        Args:
            project_id: 项目唯一ID
            req_id: 需求条目ID
            updates: 更新字段
            
        Returns:
            更新成功返回True，失败返回False
        """
        project_data = self.load_requirement_project(project_id)
        
        for item in project_data["requirements"]:
            if item["req_id"] == req_id:
                item.update(updates)
                
                if "content" in updates:
                    item["anchor_id"] = self.create_anchor(updates["content"])
                
                self.save_requirement_project(project_id, project_data)
                return True
        
        return False
    
    def get_requirement_item(self, project_id: str, req_id: str) -> Optional[Dict]:
        """
        获取指定需求条目
        
        Args:
            project_id: 项目唯一ID
            req_id: 需求条目ID
            
        Returns:
            需求条目数据，不存在返回None
        """
        project_data = self.load_requirement_project(project_id)
        
        for item in project_data["requirements"]:
            if item["req_id"] == req_id:
                return item
        
        return None
    
    def list_requirement_projects(self) -> List[Dict]:
        """
        列出所有需求项目
        
        Returns:
            项目列表，每个元素包含项目ID、名称和更新时间
        """
        projects = []
        
        if not os.path.exists(self.requirements_dir):
            return projects
        
        for filename in os.listdir(self.requirements_dir):
            if filename.endswith(".json") and not filename.startswith("."):
                project_id = filename[:-5]
                try:
                    project_data = self.load_requirement_project(project_id)
                    projects.append({
                        "project_id": project_id,
                        "project_name": project_data["project_name"],
                        "created_at": project_data["created_at"],
                        "updated_at": project_data["updated_at"]
                    })
                except Exception as e:
                    print(f"加载项目 {project_id} 失败：{str(e)}")
        
        projects.sort(key=lambda x: x["updated_at"], reverse=True)
        return projects
    
    def create_requirement_anchor(self, project_id: str, req_id: str, content: str) -> Dict:
        """
        创建需求锚点
        
        Args:
            project_id: 项目ID
            req_id: 需求条目ID
            content: 需求内容
            
        Returns:
            锚点数据
        """
        anchor_id = self.create_anchor(content)
        timestamp = datetime.now().isoformat()
        
        anchor_data = {
            "anchor_id": anchor_id,
            "anchor_type": "requirement",
            "project_id": project_id,
            "req_id": req_id,
            "content": content,
            "frozen": False,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        self._save_anchor(anchor_id, anchor_data)
        return anchor_data
    
    def freeze_requirement_anchor(self, anchor_id: str) -> bool:
        """
        冻结需求锚点
        
        Args:
            anchor_id: 锚点ID
            
        Returns:
            成功返回True，失败返回False
        """
        try:
            anchor_data = self._load_anchor(anchor_id)
            anchor_data["frozen"] = True
            anchor_data["updated_at"] = datetime.now().isoformat()
            self._save_anchor(anchor_id, anchor_data)
            return True
        except Exception as e:
            print(f"冻结锚点失败：{str(e)}")
            return False
    
    def create_architecture_anchor(self, project_id: str, architecture_data: Dict) -> Dict:
        """
        创建架构锚点
        
        Args:
            project_id: 项目ID
            architecture_data: 架构数据
            
        Returns:
            锚点数据
        """
        content = json.dumps(architecture_data, ensure_ascii=False, sort_keys=True)
        anchor_id = self.create_anchor(content)
        timestamp = datetime.now().isoformat()
        
        anchor_data = {
            "anchor_id": anchor_id,
            "anchor_type": "architecture",
            "project_id": project_id,
            "content": architecture_data,
            "frozen": False,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        self._save_anchor(anchor_id, anchor_data)
        return anchor_data
    
    def create_contract_anchor(self, project_id: str, contract_type: str, contract_data: Dict) -> Dict:
        """
        创建契约锚点
        
        Args:
            project_id: 项目ID
            contract_type: 契约类型（如 'interface', 'data'）
            contract_data: 契约数据
            
        Returns:
            锚点数据
        """
        content = json.dumps(contract_data, ensure_ascii=False, sort_keys=True)
        anchor_id = self.create_anchor(content)
        timestamp = datetime.now().isoformat()
        
        anchor_data = {
            "anchor_id": anchor_id,
            "anchor_type": f"contract_{contract_type}",
            "project_id": project_id,
            "contract_type": contract_type,
            "content": contract_data,
            "frozen": False,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        self._save_anchor(anchor_id, anchor_data)
        return anchor_data
    
    def get_anchor(self, anchor_id: str) -> Optional[Dict]:
        """
        获取锚点数据
        
        Args:
            anchor_id: 锚点ID
            
        Returns:
            锚点数据，不存在返回None
        """
        try:
            return self._load_anchor(anchor_id)
        except Exception:
            return None
    
    def list_anchors(self, project_id: str = None, anchor_type: str = None) -> List[Dict]:
        """
        列出锚点
        
        Args:
            project_id: 可选，项目ID过滤
            anchor_type: 可选，锚点类型过滤
            
        Returns:
            锚点列表
        """
        anchors = []
        
        if not os.path.exists(self.anchors_dir):
            return anchors
        
        for filename in os.listdir(self.anchors_dir):
            if filename.endswith(".json") and not filename.startswith("."):
                anchor_id = filename[:-5]
                try:
                    anchor_data = self._load_anchor(anchor_id)
                    
                    if project_id and anchor_data.get("project_id") != project_id:
                        continue
                    if anchor_type and anchor_data.get("anchor_type") != anchor_type:
                        continue
                    
                    anchors.append(anchor_data)
                except Exception as e:
                    print(f"加载锚点 {anchor_id} 失败：{str(e)}")
        
        anchors.sort(key=lambda x: x["created_at"], reverse=True)
        return anchors
    
    def add_traceability_link(self, from_id: str, to_id: str, link_type: str) -> bool:
        """
        添加可追溯链接
        
        Args:
            from_id: 源锚点/需求ID
            to_id: 目标锚点/需求ID
            link_type: 链接类型（如 'implements', 'depends_on', 'derived_from'）
            
        Returns:
            成功返回True，失败返回False
        """
        trace_file = os.path.join(self.workspace_dir, "traceability.json")
        
        trace_data = {
            "from_id": from_id,
            "to_id": to_id,
            "link_type": link_type,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            if os.path.exists(trace_file):
                with open(trace_file, 'r', encoding='utf-8') as f:
                    traces = json.load(f)
            else:
                traces = []
            
            traces.append(trace_data)
            
            with open(trace_file, 'w', encoding='utf-8') as f:
                json.dump(traces, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"添加追溯链接失败：{str(e)}")
            return False
    
    def get_traceability_chain(self, start_id: str) -> List[Dict]:
        """
        获取追溯链
        
        Args:
            start_id: 起始ID
            
        Returns:
            追溯链列表
        """
        trace_file = os.path.join(self.workspace_dir, "traceability.json")
        
        if not os.path.exists(trace_file):
            return []
        
        with open(trace_file, 'r', encoding='utf-8') as f:
            traces = json.load(f)
        
        chain = []
        visited = set()
        queue = [start_id]
        
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)
            
            for trace in traces:
                if trace["from_id"] == current_id:
                    chain.append(trace)
                    if trace["to_id"] not in visited:
                        queue.append(trace["to_id"])
                elif trace["to_id"] == current_id:
                    chain.append(trace)
                    if trace["from_id"] not in visited:
                        queue.append(trace["from_id"])
        
        return chain
    
    def _load_anchor(self, anchor_id: str) -> Dict:
        """
        内部方法：加载锚点数据
        """
        file_path = os.path.join(self.anchors_dir, f"{anchor_id}.json")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_anchor(self, anchor_id: str, anchor_data: Dict):
        """
        内部方法：保存锚点数据
        """
        file_path = os.path.join(self.anchors_dir, f"{anchor_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(anchor_data, f, ensure_ascii=False, indent=2)
    
    def _create_backup(self, project_id: str, project_data: Dict):
        """
        内部方法：创建项目备份
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{project_id}_{timestamp}.json"
            backup_path = os.path.join(self.backups_dir, backup_file)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"创建备份失败：{str(e)}")
    
    def _validate_project_schema(self, project_data: Dict):
        """
        验证项目数据是否符合Schema
        
        Args:
            project_data: 项目数据字典
            
        Raises:
            ValueError: 数据不符合Schema时抛出
        """
        required_fields = ["project_id", "project_name", "created_at", "requirements"]
        for field in required_fields:
            if field not in project_data:
                raise ValueError(f"项目数据缺少必填字段：{field}")
        
        if not isinstance(project_data["requirements"], list):
            raise ValueError("requirements必须是列表类型")
