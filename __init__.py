# --------------------------------------------------------------------------------
# __init__.py for the custom node package
#
# 这个文件聚合了包内所有自定义节点的映射信息，
# 以便ComfyUI加载器可以一次性找到它们。
# --------------------------------------------------------------------------------

# 导入每个节点文件的映射字典，并使用别名以防名称冲突
from .text_file_iterator import NODE_CLASS_MAPPINGS as text_mappings, NODE_DISPLAY_NAME_MAPPINGS as text_display_mappings
from .image_file_iterator import NODE_CLASS_MAPPINGS as image_mappings, NODE_DISPLAY_NAME_MAPPINGS as image_display_mappings
from .filename_comparator import NODE_CLASS_MAPPINGS as comparator_mappings, NODE_DISPLAY_NAME_MAPPINGS as comparator_display_mappings

# 使用字典解包（**）将所有映射合并到一个字典中
# 这是一种干净且可扩展的方式，未来添加新节点时只需在此处添加即可
NODE_CLASS_MAPPINGS = {
    **text_mappings,
    **image_mappings,
    **comparator_mappings
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **text_display_mappings,
    **image_display_mappings,
    **comparator_display_mappings
}

# `__all__` 定义了当其他模块使用 `from package import *` 时，
# 应该导入哪些名称。ComfyUI会查找并使用这两个聚合后的字典。
__all__ = [
    'NODE_CLASS_MAPPINGS',
    'NODE_DISPLAY_NAME_MAPPINGS'
]

print("✅ 加载自定义节点: Text/Image 迭代器 和 文件名比较器")