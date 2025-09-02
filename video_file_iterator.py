import os
import glob
import torch
import numpy as np
import cv2  # 导入OpenCV库

# --------------------------------------------------------------------------------
# Class: VideoFileIterator
# 这是一个ComfyUI节点，用于按顺序遍历指定文件夹中的所有视频文件。
# 它会一次性加载一个视频的所有帧，并将其作为IMAGE张量批次输出。
# 同时，它也会输出对应的文件名（不含后缀）。
# 处理完最后一个文件后，它会抛出一个异常来终止工作流队列。
#
# 改编自 ImageFileIterator
# --------------------------------------------------------------------------------
class VideoFileIterator:
    def __init__(self):
        # 初始化实例变量，迭代逻辑与图片/文本迭代器保持一致
        self.index = 0
        self.cached_files = []
        self.cached_folder_path = ""

    @classmethod
    def INPUT_TYPES(cls):
        """
        输入参数仍然是文件夹路径。
        """
        return {
            "required": {
                "folder_path": ("STRING", {
                    "multiline": False,
                    "default": "C:\\path\\to\\your\\video_folder"
                }),
            }
        }

    # --- 修改点 1: 更新返回类型和名称 ---
    # 返回的是一个图像批次（视频的所有帧）
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("frames", "文件名")
    FUNCTION = "iterate_and_load_video"
    CATEGORY = "utilities/loaders"

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        """
        强制节点重新运行以实现迭代，此核心逻辑不变。
        """
        return float("NaN")
        
    def get_sorted_files(self, folder_path):
        """
        获取并缓存排序后的视频文件列表。
        """
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"路径 '{folder_path}' 不是一个有效的文件夹。")

        if folder_path != self.cached_folder_path:
            print(f"[VideoFileIterator] 文件夹路径已更改，正在重新扫描: {folder_path}")
            
            # --- 修改点 2: 搜索多种视频格式 ---
            video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
            files_found = []
            for ext in video_extensions:
                search_pattern = os.path.join(folder_path, f'*{ext}')
                files_found.extend(glob.glob(search_pattern))
            
            video_files = [os.path.basename(f) for f in files_found]
            video_files.sort()
            
            self.cached_folder_path = folder_path
            self.cached_files = video_files
            
            print(f"[VideoFileIterator] 找到并排序了 {len(video_files)} 个视频文件。")
            self.index = 0
            
        return self.cached_files

    # --- 修改点 3: 新增视频加载和转换函数 ---
    def load_video_frames(self, file_path):
        """
        使用OpenCV加载视频，并将其所有帧转换为ComfyUI所需的Tensor格式。
        返回的Tensor形状为 [frame_count, height, width, 3] (RGB)
        """
        try:
            # 使用OpenCV打开视频文件
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                raise IOError(f"无法打开视频文件: {os.path.basename(file_path)}")

            frames = []
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break # 视频读取完毕或发生错误
                
                # OpenCV默认读取为BGR格式，需要转换为RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # 将Numpy数组转换为Tensor，并归一化到 [0, 1]
                frame_tensor = torch.from_numpy(frame_rgb.astype(np.float32) / 255.0)
                frames.append(frame_tensor)
            
            cap.release()

            if not frames:
                raise ValueError(f"视频文件 '{os.path.basename(file_path)}' 为空或无法解码。")

            # 将帧列表堆叠成一个批次张量
            return torch.stack(frames)
            
        except Exception as e:
            # 确保即使出错也释放资源
            if 'cap' in locals() and cap.isOpened():
                cap.release()
            raise IOError(f"加载或转换视频时发生错误: {os.path.basename(file_path)} - {e}")

    def iterate_and_load_video(self, folder_path):
        """
        节点的主执行函数。
        """
        try:
            video_files = self.get_sorted_files(folder_path)
        except Exception as e:
            raise e
            
        num_files = len(video_files)

        if num_files == 0:
            raise FileNotFoundError(f"在文件夹 '{folder_path}' 中没有找到任何支持的视频文件 (.mp4, .mov, .avi, etc.)。")

        # 核心终止逻辑不变
        if self.index >= num_files:
            self.index = 0
            raise Exception(f"所有 {num_files} 个视频已处理完毕。工作流已终止。若要重新开始，请再次点击'Queue Prompt'。")

        filename = video_files[self.index]
        full_path = os.path.join(folder_path, filename)
        
        print(f"[VideoFileIterator] 正在处理: 视频 {self.index + 1}/{num_files} - {filename}")
        
        try:
            # --- 修改点 4: 调用新的视频加载函数 ---
            video_frames_tensor = self.load_video_frames(full_path)
        except Exception as e:
            self.index += 1
            raise e
        
        self.index += 1
        
        filename_no_ext = os.path.splitext(filename)[0]
        
        return (video_frames_tensor, filename_no_ext)


# --------------------------------------------------------------------------------
# ComfyUI 节点注册
# --- 修改点 5: 更新节点映射 ---
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "VideoFileIterator": VideoFileIterator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoFileIterator": "逐个读取视频文件 (Iterator)"
}