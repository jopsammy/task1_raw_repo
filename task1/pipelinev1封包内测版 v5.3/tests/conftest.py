"""
pytest配置和fixtures
提供单元测试和E2E测试的通用fixtures
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


@pytest.fixture
def mock_streamlit():
    """
    模拟Streamlit模块
    用于测试依赖Streamlit的UI组件，避免真实渲染
    """
    with patch('streamlit.session_state') as mock_state, \
         patch('streamlit.sidebar') as mock_sidebar, \
         patch('streamlit.main') as mock_main:
        mock_state._data = {}
        mock_state.__getitem__ = lambda self, key: self._data.get(key)
        mock_state.__setitem__ = lambda self, key, value: self._data.update({key: value})
        yield {
            'session_state': mock_state,
            'sidebar': mock_sidebar,
            'main': mock_main
        }


@pytest.fixture
def mock_session_state():
    """模拟Streamlit session_state"""
    class MockSessionState:
        def __init__(self):
            self._data = {}
        
        def __getitem__(self, key):
            return self._data.get(key)
        
        def __setitem__(self, key, value):
            self._data[key] = value
        
        def get(self, key, default=None):
            return self._data.get(key, default)
    
    return MockSessionState()


@pytest.fixture
def sample_requirement_text():
    """示例需求文本"""
    return """
    构建一个用户管理系统，包含以下功能：
    1. 用户注册和登录
    2. 权限管理
    3. 用户信息管理
    """


@pytest.fixture
def sample_requirement_data():
    """
    示例结构化需求数据
    用于测试需求解析和转换功能
    """
    return {
        "project_name": "用户管理系统",
        "version": "1.0.0",
        "functional_requirements": [
            {
                "id": "FR-001",
                "name": "用户注册",
                "description": "支持新用户注册账号",
                "priority": "high"
            },
            {
                "id": "FR-002",
                "name": "用户登录",
                "description": "支持已注册用户登录系统",
                "priority": "high"
            },
            {
                "id": "FR-003",
                "name": "权限管理",
                "description": "管理用户角色和权限",
                "priority": "medium"
            }
        ],
        "non_functional_requirements": [
            {
                "id": "NFR-001",
                "name": "性能要求",
                "description": "响应时间小于200ms",
                "priority": "high"
            }
        ],
        "constraints": [
            "使用Python 3.10+",
            "支持PostgreSQL数据库"
        ]
    }


@pytest.fixture
def sample_architecture_data():
    """
    示例架构方案数据
    用于测试架构生成和方案融合功能
    """
    return {
        "solution_id": "arch-001",
        "solution_name": "微服务架构方案",
        "solution_type": "balanced",
        "modules": [
            {
                "module_id": "模块0_全局调度面板",
                "module_name": "全局调度面板",
                "responsibilities": ["全局状态管理", "进度监控"],
                "dependencies": []
            },
            {
                "module_id": "模块1_用户核心模块",
                "module_name": "用户核心模块",
                "responsibilities": ["用户认证", "权限控制"],
                "dependencies": ["模块0_全局调度面板"]
            },
            {
                "module_id": "模块2_业务逻辑模块",
                "module_name": "业务逻辑模块",
                "responsibilities": ["业务处理", "数据计算"],
                "dependencies": ["模块1_用户核心模块"]
            }
        ],
        "architecture_style": "分层架构",
        "tech_stack": {
            "backend": "Python + FastAPI",
            "frontend": "Streamlit",
            "database": "PostgreSQL",
            "cache": "Redis"
        },
        "quality_attributes": {
            "scalability": "高",
            "maintainability": "高",
            "performance": "中"
        }
    }


@pytest.fixture
def sample_contract_data():
    """
    示例契约数据
    用于测试契约生成和校验功能
    """
    return {
        "contract_version": "1.0.0",
        "data_contracts": {
            "UserSchema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "format": "uuid"},
                    "username": {"type": "string", "minLength": 3, "maxLength": 50},
                    "email": {"type": "string", "format": "email"},
                    "role": {"type": "string", "enum": ["admin", "user", "guest"]}
                },
                "required": ["user_id", "username", "email"]
            },
            "PermissionSchema": {
                "type": "object",
                "properties": {
                    "permission_id": {"type": "string"},
                    "name": {"type": "string"},
                    "resource": {"type": "string"},
                    "action": {"type": "string", "enum": ["read", "write", "delete"]}
                },
                "required": ["permission_id", "name", "resource", "action"]
            }
        },
        "interface_contracts": {
            "IUserService": {
                "methods": {
                    "create_user": {
                        "params": {"username": "string", "email": "string", "password": "string"},
                        "returns": "UserSchema",
                        "raises": ["UserExistsError", "ValidationError"]
                    },
                    "authenticate": {
                        "params": {"username": "string", "password": "string"},
                        "returns": "UserSchema",
                        "raises": ["AuthenticationError"]
                    }
                }
            },
            "IPermissionService": {
                "methods": {
                    "check_permission": {
                        "params": {"user_id": "string", "resource": "string", "action": "string"},
                        "returns": "boolean",
                        "raises": ["PermissionDeniedError"]
                    }
                }
            }
        },
        "config_contracts": {
            "DatabaseConfig": {
                "host": {"type": "string", "default": "localhost"},
                "port": {"type": "integer", "default": 5432},
                "database": {"type": "string", "required": True},
                "username": {"type": "string", "required": True},
                "password": {"type": "string", "required": True, "secret": True}
            }
        }
    }


@pytest.fixture
def sample_pipeline_results():
    """示例Pipeline结果"""
    return {
        "requirement_anchoring": {
            "success": True,
            "structured_requirement": "# 用户管理系统\n\n## 功能需求\n..."
        },
        "requirement_validation": {
            "success": True,
            "validation_result": {"valid": True}
        },
        "architecture_iteration": {
            "success": True,
            "final_solution": {
                "modules": ["模块1", "模块2"],
                "architecture": "微服务架构"
            }
        },
        "contract_generation": {
            "success": True,
            "contracts": {
                "interface": {"API": "..."},
                "data": {"Schema": "..."}
            }
        }
    }


@pytest.fixture
def temp_workspace(tmp_path):
    """
    临时工作空间目录
    用于测试文件读写操作，测试完成后自动清理
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    anchors_dir = workspace / "anchors"
    anchors_dir.mkdir()
    
    outputs_dir = workspace / "outputs"
    outputs_dir.mkdir()
    
    return workspace


@pytest.fixture
def mock_llm_client():
    """
    模拟LLM客户端
    用于测试LLM调用，避免真实API请求
    """
    client = MagicMock()
    client.generate.return_value = "模拟的LLM响应内容"
    client.chat.return_value = {"content": "模拟的对话响应"}
    return client
