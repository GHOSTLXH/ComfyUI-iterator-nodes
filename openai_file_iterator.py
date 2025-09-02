import os
import logging

# ComfyUI 核心模块
import folder_paths

# --------------------------------------------------------------------------------
# 兼容性修复：
# 我们不再从其他节点包导入任何东西，以避免因加载顺序或路径问题导致的失败。
# 1. 直接定义（硬编码）节点类型字符串，确保与源节点完全一致。
# 2. 在执行函数中使用“鸭子类型”检查，只验证对象的功能（是否有 .upload_file 方法），
#    而不关心它的具体类名。
# --------------------------------------------------------------------------------

# 从 nodes.py 文件中直接复制的类型定义，确保字符串完全匹配
API_INSTANCE_TYPE = "OPENAI_API_INSTANCE"
CONTENT_ITEM_TYPE = "OAI_CONTENT_ITEM"

# 设置一个独立的logger，避免与其他包冲突
logger = logging.getLogger('FileUploaderIterator')

class OpenAIFileUploaderIteratorNode:
    def __init__(self):
        # 标准迭代器状态管理
        self.index = 0
        self.cached_files = []
        self.cached_folder_path = ""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # 使用硬编码的类型字符串进行端口定义
                "api_instance": (API_INSTANCE_TYPE,),
                "folder_path": ("STRING", {
                    "multiline": False,
                    "default": "C:\\path\\to\\your\\files_folder"
                }),
            },
            "optional": {
                "display_name_prefix": ("STRING", {"default": "", "multiline": False, "placeholder": "可选的前缀"}),
            }
        }

    # 使用硬编码的类型字符串进行端口定义
    RETURN_TYPES = (CONTENT_ITEM_TYPE, "STRING", "STRING",)
    RETURN_NAMES = ("content_item", "filename", "file_id",)
    FUNCTION = "iterate_and_upload"
    CATEGORY = "utilities/loaders/OpenAI"

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        """强制节点重新运行以实现迭代"""
        return float("NaN")

    def get_sorted_files(self, folder_path):
        """获取并缓存排序后的文件列表（不包括子目录）"""
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"路径 '{folder_path}' 不是一个有效的文件夹。")

        if folder_path != self.cached_folder_path:
            logger.info(f"[FileUploaderIterator] 文件夹路径已更改，正在重新扫描: {folder_path}")
            try:
                all_entries = os.listdir(folder_path)
                files_found = [f for f in all_entries if os.path.isfile(os.path.join(folder_path, f))]
                files_found.sort()
            except Exception as e:
                raise IOError(f"无法读取文件夹 '{folder_path}': {e}")
            self.cached_folder_path = folder_path
            self.cached_files = files_found
            logger.info(f"[FileUploaderIterator] 找到并排序了 {len(files_found)} 个文件。")
            self.index = 0
        return self.cached_files

    def iterate_and_upload(self, api_instance, folder_path: str, display_name_prefix: str = ""):
        # 使用“鸭子类型”进行检查
        if not hasattr(api_instance, 'upload_file') or not callable(getattr(api_instance, 'upload_file', None)):
            raise TypeError("传入的 'api_instance' 对象无效。它缺少一个可调用的 'upload_file' 方法。请确保已连接正确的API加载器节点。")

        files = self.get_sorted_files(folder_path)
        num_files = len(files)

        if num_files == 0:
            raise FileNotFoundError(f"在文件夹 '{folder_path}' 中没有找到任何文件。")

        if self.index >= num_files:
            self.index = 0
            raise Exception(f"所有 {num_files} 个文件已处理完毕。工作流已终止。")

        filename = files[self.index]
        full_path = os.path.join(folder_path, filename)
        display_name = f"{display_name_prefix}{filename}" if display_name_prefix else filename
        
        logger.info(f"[FileUploaderIterator] 正在上传: 文件 {self.index + 1}/{num_files} - {filename}")
        
        self.index += 1
        
        try:
            # 调用 api_instance 的方法。我们相信它会返回正确的字典结构。
            result = api_instance.upload_file(full_path, display_name)
            
            # 返回的`result`字典就是 `content_item`，其结构与OpenAIChatNode兼容
            if result and "input_file" in result and result["input_file"] and not result.get("error"):
                file_id = result["input_file"].get("file_id", "ERROR_NO_ID")
                logger.info(f"文件上传完成，file_id: {file_id}")
                
                content_item = result
                filename_no_ext = os.path.splitext(filename)[0]
                
                return (content_item, filename_no_ext, file_id)
            else:
                error_msg = result.get("error", "未知上传错误")
                raise RuntimeError(f"文件上传失败: {error_msg}")

        except Exception as e:
            logger.error(f"[FileUploaderIterator] 文件上传执行错误: {e}")
            self.index -= 1 # 上传失败，将索引退回，以便下次可以重试
            raise

# --------------------------------------------------------------------------------
# ComfyUI 节点注册
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "OpenAIFileUploaderIterator": OpenAIFileUploaderIteratorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenAIFileUploaderIterator": "逐个上传文件到OpenAI (Iterator)"
}