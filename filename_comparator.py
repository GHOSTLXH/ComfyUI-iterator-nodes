# --------------------------------------------------------------------------------
# Class: FilenameComparator
# 这是一个ComfyUI节点，用作一个“门控”或“断言”节点。
# 它接收两个文件名（字符串）作为输入。
# - 如果两个文件名完全相同，它会允许工作流继续，并向下游传递该文件名。
# - 如果两个文件名不匹配，它会抛出一个错误，并立即终止当前的工作流队列。
#
# 这对于确保成对处理的数据（如图片和其对应的提示词文件）是同步的非常有用。
# --------------------------------------------------------------------------------
class FilenameComparator:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """
        定义节点的输入参数。
        'forceInput': True 强制这些输入只能通过连接获取，不能在UI中手动输入，
                      这更符合其作为流程控制节点的用途。
        """
        return {
            "required": {
                "filename_a": ("STRING", {"forceInput": True}),
                "filename_b": ("STRING", {"forceInput": True}),
            }
        }

    # 它成功时会传出一个文件名，所以返回类型是 STRING
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename",)
    FUNCTION = "compare_filenames"
    CATEGORY = "utilities/logic"  # 放在逻辑类别下更合适

    def compare_filenames(self, filename_a, filename_b):
        """
        节点的主执行函数。
        比较两个输入的文件名。
        """
        print(f"[FilenameComparator] 正在比较: A='{filename_a}' vs B='{filename_b}'")
        
        # 核心逻辑：检查两个文件名是否相等
        if filename_a != filename_b:
            # 如果不匹配，构造一个清晰的错误信息并抛出异常
            error_message = f"文件名不匹配！'{filename_a}' 与 '{filename_b}' 不同。工作流已终止。"
            print(f"[FilenameComparator] 错误: {error_message}")
            raise ValueError(error_message)
        
        # 如果文件名匹配，打印成功信息并将其传递下去
        print(f"[FilenameComparator] 文件名匹配。工作流继续。")
        
        # 返回一个元组，即使只有一个返回值
        return (filename_a,)

# --------------------------------------------------------------------------------
# ComfyUI 节点注册
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "FilenameComparator": FilenameComparator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FilenameComparator": "比较文件名 (Comparator)"
}