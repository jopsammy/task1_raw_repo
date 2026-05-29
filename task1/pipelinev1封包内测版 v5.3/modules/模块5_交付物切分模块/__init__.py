
"""
模块5：交付物切分模块
负责pipeline运行结果的切分、格式化与保存
"""

from .delivery_output_splitter import DeliveryOutputSplitter

_delivery_output_splitter_instance = None


def get_delivery_output_splitter(workspace_dir=None):
    """
    获取交付物切分器全局单例

    Args:
        workspace_dir: 工作区目录，可选

    Returns:
        DeliveryOutputSplitter 实例
    """
    global _delivery_output_splitter_instance
    if _delivery_output_splitter_instance is None:
        _delivery_output_splitter_instance = DeliveryOutputSplitter(workspace_dir)
    return _delivery_output_splitter_instance


__all__ = ['DeliveryOutputSplitter', 'get_delivery_output_splitter']

