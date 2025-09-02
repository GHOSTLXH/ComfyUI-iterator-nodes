# --- START OF FILE video_object_iterator.py (DEFINITIVE FINAL VERSION) ---

import os
import glob
import torch
import av
import imageio
import numpy as np
from comfy_api.input import VideoInput

# --------------------------------------------------------------------------------
# 1. 创建一个简单的“数据容器”类，作为 VideoInputComponents 的替代品
# --------------------------------------------------------------------------------
class SimpleVideoComponents:
    """一个简单的数据类，用于封装视频组件，以兼容旧版 ComfyUI API。"""
    def __init__(self, images, frame_rate, frame_count):
        self.images = images
        self.frame_rate = frame_rate
        self.frame_count = frame_count

# --------------------------------------------------------------------------------
# 2. 定义我们的具体视频类，让它返回上面创建的简单对象
# --------------------------------------------------------------------------------
class LoadedVideo(VideoInput):
    """
    一个具体的 VideoInput 实现，用于包装从文件中加载的视频数据。
    """
    def __init__(self, images_tensor: torch.Tensor, frame_rate: float, frame_count: int):
        self.images = images_tensor
        self.frame_rate = frame_rate
        self.frame_count = frame_count

    # --- 核心修正点 ---
    def get_components(self):
        """
        实现抽象方法：返回视频的核心组件。
        这次返回我们自己定义的 SimpleVideoComponents 对象，而不是元组。
        """
        return SimpleVideoComponents(
            images=self.images,
            frame_rate=self.frame_rate,
            frame_count=self.frame_count
        )

    def save_to(self, folder: str, file_prefix: str = "ComfyUI", ext: str = "mp4") -> list[str]:
        """
        实现抽象方法：允许在 ComfyUI 中右键保存视频。
        """
        try:
            filepath = os.path.join(folder, f"{file_prefix}_{self.frame_count}frames.{ext}")
            frames_np = (self.images.cpu().numpy() * 255).astype(np.uint8)
            imageio.mimsave(filepath, frames_np, fps=self.frame_rate, quality=8)
            print(f"[VideoObjectIterator] Video saved to: {filepath}")
            return [filepath]
        except Exception as e:
            print(f"Error saving video: {e}")
            return []

# --------------------------------------------------------------------------------
# 3. 迭代器类本身不需要修改
# --------------------------------------------------------------------------------
class VideoObjectIterator:
    def __init__(self):
        self.index = 0
        self.cached_files = []
        self.cached_folder_path = ""

    @classmethod
    def INPUT_TYPES(cls):
        return { "required": { "folder_path": ("STRING", { "multiline": False, "default": "C:\\path\\to\\your\\video_folder" }) } }

    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "filename")
    FUNCTION = "iterate_and_return_object"
    CATEGORY = "utilities/loaders"

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        return float("NaN")
        
    def get_sorted_files(self, folder_path):
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"路径 '{folder_path}' 不是一个有效的文件夹。")
        if folder_path != self.cached_folder_path:
            print(f"[VideoObjectIterator] 文件夹路径已更改，正在重新扫描: {folder_path}")
            video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
            files_found = []
            for ext in video_extensions:
                files_found.extend(glob.glob(os.path.join(folder_path, f'*{ext}')))
            video_files = sorted([os.path.basename(f) for f in files_found])
            self.cached_folder_path = folder_path
            self.cached_files = video_files
            print(f"[VideoObjectIterator] 找到并排序了 {len(video_files)} 个视频文件。")
            self.index = 0
        return self.cached_files

    def load_video_from_path(self, video_path):
        try:
            with av.open(video_path) as container:
                frames = [torch.from_numpy(frame.to_ndarray(format='rgb24')) for frame in container.decode(video=0)]
                if not frames:
                    raise ValueError(f"无法从视频 '{video_path}' 解码任何帧。")
                frames_tensor = torch.stack(frames).to(torch.float32) / 255.0
                fps = float(container.streams.video[0].average_rate)
                print(f"[VideoObjectIterator] 视频加载成功: {len(frames)} 帧, {fps:.2f} FPS")
                return frames_tensor, fps, len(frames)
        except Exception as e:
            raise IOError(f"加载或解码视频 '{video_path}' 时出错: {e}") from e

    def iterate_and_return_object(self, folder_path):
        video_files = self.get_sorted_files(folder_path)
        if not video_files:
            raise FileNotFoundError(f"在文件夹 '{folder_path}' 中没有找到任何支持的视频文件。")
        if self.index >= len(video_files):
            print(f"所有 {len(video_files)} 个视频已处理完毕。工作流已停止。")
            return (None, None)
        filename = video_files[self.index]
        full_path = os.path.join(folder_path, filename)
        print(f"[VideoObjectIterator] 正在处理: 视频 {self.index + 1}/{len(video_files)} - {filename}")
        try:
            frames_tensor, fps, frame_count = self.load_video_from_path(full_path)
            video_object = LoadedVideo(images_tensor=frames_tensor, frame_rate=fps, frame_count=frame_count)
        except Exception as e:
            raise e
        self.index += 1
        filename_no_ext = os.path.splitext(filename)[0]
        print(f"[VideoObjectIterator] 成功创建并提供 VIDEO 对象: {filename}")
        return (video_object, filename_no_ext)

# --------------------------------------------------------------------------------
# ComfyUI 节点注册
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = { "VideoObjectIterator": VideoObjectIterator }
NODE_DISPLAY_NAME_MAPPINGS = { "VideoObjectIterator": "逐个读取视频对象 (Iterator)" }