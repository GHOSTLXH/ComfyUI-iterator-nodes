import os
import glob
import torch
import numpy as np
from PIL import Image

# --------------------------------------------------------------------------------
# Class: ImageFileIterator
# 这是一个ComfyUI节点，用于按顺序遍历指定文件夹中的所有图片文件。
# 它会逐个输出图片数据（作为IMAGE张量）和对应的文件名（不含后缀）。
# 处理完最后一个文件后，它会抛出一个异常来终止工作流队列。
#
# 改编自 TextFileIterator
# --------------------------------------------------------------------------------
class ImageFileIterator:
    def __init__(self):
        # 初始化实例变量，这部分迭代逻辑保持不变
        self.index = 0
        self.cached_files = []
        self.cached_folder_path = ""

    @classmethod
    def INPUT_TYPES(cls):
        """
        输入参数不变，仍然是文件夹路径。
        """
        return {
            "required": {
                "folder_path": ("STRING", {
                    "multiline": False,
                    "default": "C:\\path\\to\\your\\image_folder"
                }),
            }
        }

    # --- 修改点 1: 更新返回类型和名称 ---
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "文件名")
    FUNCTION = "iterate_and_load_image"
    CATEGORY = "utilities/loaders"

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        """
        强制节点重新运行以实现迭代，此核心逻辑不变。
        """
        return float("NaN")
        
    def get_sorted_files(self, folder_path):
        """
        获取并缓存排序后的图片文件列表。
        """
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"路径 '{folder_path}' 不是一个有效的文件夹。")

        if folder_path != self.cached_folder_path:
            print(f"[ImageFileIterator] 文件夹路径已更改，正在重新扫描: {folder_path}")
            
            # --- 修改点 2: 搜索多种图片格式 ---
            image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.bmp']
            files_found = []
            for ext in image_extensions:
                # 使用 os.path.join 保证路径正确拼接
                search_pattern = os.path.join(folder_path, f'*{ext}')
                files_found.extend(glob.glob(search_pattern))
            
            # 获取文件名并排序
            image_files = [os.path.basename(f) for f in files_found]
            image_files.sort()
            
            self.cached_folder_path = folder_path
            self.cached_files = image_files
            
            print(f"[ImageFileIterator] 找到并排序了 {len(image_files)} 个图片文件。")
            self.index = 0
            
        return self.cached_files

    # --- 修改点 3: 新增图片加载和转换函数 ---
    def load_image(self, file_path):
        """
        使用Pillow加载图片，并将其转换为ComfyUI所需的Tensor格式。
        返回的Tensor形状为 [1, height, width, 3] (RGB)
        """
        try:
            img = Image.open(file_path)
            # 转换为RGB格式，以统一处理不同模式的图片（如灰度、RGBA等）
            img = img.convert("RGB")
            # 将PIL Image对象转换为Numpy数组，并归一化到 [0, 1]
            img_np = np.array(img).astype(np.float32) / 255.0
            # 将Numpy数组转换为PyTorch Tensor
            img_tensor = torch.from_numpy(img_np)
            # 添加批次维度（batch dimension），ComfyUI期望的格式是 [B, H, W, C]
            img_tensor = img_tensor.unsqueeze(0)
            return img_tensor
        except Exception as e:
            raise IOError(f"加载或转换图片时发生错误: {os.path.basename(file_path)} - {e}")

    def iterate_and_load_image(self, folder_path):
        """
        节点的主执行函数。
        """
        try:
            image_files = self.get_sorted_files(folder_path)
        except Exception as e:
            raise e
            
        num_files = len(image_files)

        if num_files == 0:
            raise FileNotFoundError(f"在文件夹 '{folder_path}' 中没有找到任何支持的图片文件 (.png, .jpg, .jpeg, .webp, .bmp)。")

        # 核心终止逻辑不变
        if self.index >= num_files:
            self.index = 0
            raise Exception(f"所有 {num_files} 个图片已处理完毕。工作流已终止。若要重新开始，请再次点击'Queue Prompt'。")

        filename = image_files[self.index]
        full_path = os.path.join(folder_path, filename)
        
        print(f"[ImageFileIterator] 正在处理: 图片 {self.index + 1}/{num_files} - {filename}")
        
        try:
            # --- 修改点 4: 调用新的图片加载函数 ---
            image_tensor = self.load_image(full_path)
        except Exception as e:
            self.index += 1
            raise e
        
        self.index += 1
        
        filename_no_ext = os.path.splitext(filename)[0]
        
        return (image_tensor, filename_no_ext)


# --------------------------------------------------------------------------------
# ComfyUI 节点注册
# --- 修改点 5: 更新节点映射 ---
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "ImageFileIterator": ImageFileIterator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageFileIterator": "逐个读取图片文件 (Iterator)"
}