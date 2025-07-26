import os
import glob

# --------------------------------------------------------------------------------
# Class: TextFileIterator
# 这是一个ComfyUI节点，用于按顺序遍历指定文件夹中的所有.txt文件。
# 它会逐个输出文件内容，直到所有文件都被处理完毕。
# 处理完最后一个文件后，它会抛出一个异常来终止工作流队列。
#
# V3: 新增功能 - 遍历完所有文件后自动报错并终止执行。
# V4: 修改 - “文件名”输出端口不包含文件后缀。
# --------------------------------------------------------------------------------
class TextFileIterator:
    def __init__(self):
        # 初始化实例变量
        self.index = 0
        self.cached_files = []
        self.cached_folder_path = ""

    @classmethod
    def INPUT_TYPES(cls):
        """
        定义节点的输入参数。
        """
        return {
            "required": {
                "folder_path": ("STRING", {
                    "multiline": False,
                    "default": "C:\\path\\to\\your\\folder_A"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "文件名")
    FUNCTION = "iterate_and_read"
    CATEGORY = "utilities/loaders"

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        """
        强制节点在每次队列执行时都重新运行，以实现迭代功能。 通过返回一个独一无二的值（如 float('NaN')），我们告诉ComfyUI这个节点的输出“永远是变化的”。这会强制ComfyUI在每次点击"Queue Prompt"时都重新执行这个节点的 FUNCTION 方法，而不是因为输入没变就使用缓存的结果（懒加载）。
        """
        return float("NaN")
        
    def get_sorted_files(self, folder_path):
        """
        获取并缓存排序后的文件列表，以提高效率。只有当文件夹路径改变时，才重新扫描文件系统。
        """
        if not os.path.isdir(folder_path):
            # 如果路径无效，抛出异常会立即停止执行，这比返回空值更明确
            raise NotADirectoryError(f"路径 '{folder_path}' 不是一个有效的文件夹。")

        # 仅当路径改变时才重新扫描文件系统
        if folder_path != self.cached_folder_path:
            print(f"[TextFileIterator] 文件夹路径已更改，正在重新扫描: {folder_path}")
            search_path = os.path.join(folder_path, '*.txt')
            files = glob.glob(search_path)
            txt_files = [os.path.basename(f) for f in files]
            txt_files.sort()
            
            # 更新缓存
            self.cached_folder_path = folder_path
            self.cached_files = txt_files
            
            print(f"[TextFileIterator] 找到并排序了 {len(txt_files)} 个 .txt 文件。")
            # 当文件夹改变时，重置迭代器索引，从头开始
            self.index = 0
            
        return self.cached_files

    def read_file_with_multiple_encodings(self, file_path):
        """
        尝试使用多种编码格式读取文件内容。
        """
        encodings_to_try = ['utf-8', 'gbk', 'utf-8-sig', 'cp1252', 'latin-1']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"[TextFileIterator] 成功使用 '{encoding}' 编码读取文件。")
                return content
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                raise IOError(f"读取文件时发生意外错误: {e}")
        
        raise UnicodeDecodeError(f"无法使用任何支持的编码格式解码文件 '{os.path.basename(file_path)}'。")

    def iterate_and_read(self, folder_path):
        """
        节点的主执行函数。
        如果所有文件都已处理，则抛出异常终止工作流。
        """
        # 获取文件列表，此函数会处理路径变更和索引重置
        try:
            txt_files = self.get_sorted_files(folder_path)
        except Exception as e:
            # 将 get_sorted_files 中的错误传递给ComfyUI
            raise e
            
        num_files = len(txt_files)

        # 如果文件夹为空，直接终止
        if num_files == 0:
            raise FileNotFoundError(f"在文件夹 '{folder_path}' 中没有找到任何 .txt 文件。")

        # **核心终止逻辑**
        # 检查当前索引是否已经超出文件列表范围
        if self.index >= num_files:
            # 将索引重置为0，以便下次队列可以从头开始
            self.index = 0
            # 抛出异常，终止工作流
            raise Exception(f"所有 {num_files} 个文件已处理完毕。工作流已终止。若要重新开始，请再次点击'Queue Prompt'。")

        # 获取当前文件
        filename = txt_files[self.index]
        full_path = os.path.join(folder_path, filename)
        
        print(f"[TextFileIterator] 正在处理: 文件 {self.index + 1}/{num_files} - {filename}")
        
        try:
            content = self.read_file_with_multiple_encodings(full_path)
        except Exception as e:
            # 如果读取特定文件时出错，也抛出异常终止
            self.index += 1 # 增加索引，以便下次跳过这个坏文件
            raise e
        
        # 为下一次执行准备，将索引加一
        self.index += 1
        
        # --- 修改点 ---
        # 使用 os.path.splitext 来移除文件名中的后缀
        filename_no_ext = os.path.splitext(filename)[0]
        
        return (content, filename_no_ext)


# --------------------------------------------------------------------------------
# ComfyUI 节点注册
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "TextFileIterator": TextFileIterator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextFileIterator": "逐个读取TXT文件 (Iterator)"
}