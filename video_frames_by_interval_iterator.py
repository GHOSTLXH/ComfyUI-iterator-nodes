import os
import logging
import cv2
import numpy as np
from PIL import Image
import base64
import io

# --- 依赖项和日志设置 ---
try:
    import cv2
except ImportError:
    raise ImportError("OpenCV (cv2) is not installed. Please install it by running: pip install opencv-python")

try:
    from PIL import Image
    import numpy as np
except ImportError:
    raise ImportError("Pillow or numpy is not installed. Please ensure your ComfyUI environment is set up correctly.")

logger = logging.getLogger('VideoFramesByIntervalIterator')
# --------------------

CONTENT_ITEM_TYPE = "OAI_CONTENT_ITEM"
MAX_OUTPUT_FRAMES = 10  # 定义节点最多可以输出多少个帧端口

class VideoFramesByIntervalIteratorNode:
    def __init__(self):
        # 迭代器状态管理
        self.index = 0
        self.cached_files = []
        self.cached_folder_path = ""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder_path": ("STRING", {
                    "multiline": False,
                    "default": "C:\\path\\to\\your\\videos_folder"
                }),
                "frame_interval": ("INT", {
                    "default": 30,
                    "min": 1,
                    "step": 1,
                    "display": "number"
                }),
                "max_frames_to_extract": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": MAX_OUTPUT_FRAMES,
                    "step": 1
                }),
                "image_format": (["jpeg", "png", "webp"], {"default": "jpeg"}),
                "quality": ("INT", {"default": 85, "min": 10, "max": 100, "step": 1}),
            }
        }

    RETURN_TYPES = tuple([CONTENT_ITEM_TYPE] * MAX_OUTPUT_FRAMES + ["STRING"])
    RETURN_NAMES = tuple([f"content_item_{i+1}" for i in range(MAX_OUTPUT_FRAMES)] + ["video_filename"])
    
    FUNCTION = "iterate_and_extract"
    CATEGORY = "utilities/loaders/OpenAI"

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        """强制节点重新运行以实现迭代"""
        return float("NaN")

    def get_sorted_video_files(self, folder_path):
        """获取并缓存排序后的视频文件列表"""
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"路径 '{folder_path}' 不是一个有效的文件夹。")

        if folder_path != self.cached_folder_path:
            logger.info(f"[VideoFramesIntervalIterator] 文件夹路径已更改，正在重新扫描: {folder_path}")
            try:
                video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
                all_entries = os.listdir(folder_path)
                files_found = [f for f in all_entries if os.path.splitext(f)[1].lower() in video_extensions]
                files_found.sort()
            except Exception as e:
                raise IOError(f"无法读取文件夹 '{folder_path}': {e}")
            
            self.cached_folder_path = folder_path
            self.cached_files = files_found
            logger.info(f"[VideoFramesIntervalIterator] 找到并排序了 {len(files_found)} 个视频文件。")
            self.index = 0
        return self.cached_files

    def _encode_frame_to_content_item(self, frame, image_format, quality):
        """将单个OpenCV帧编码为CONTENT_ITEM字典"""
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            if image_format.lower() == 'jpeg' and img.mode == 'RGBA':
                img = img.convert('RGB')
            buffer = io.BytesIO()
            save_params = {}
            if image_format.lower() in ['jpeg', 'webp']:
                save_params['quality'] = quality
            img.save(buffer, format=image_format.upper(), **save_params)
            base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            mime_type = f"image/{image_format.lower()}"
            data_url = f"data:{mime_type};base64,{base64_data}"
            content_item = {"input_image": {"image_url": data_url, "detail": "high"}}
            return content_item
        except Exception as e:
            logger.error(f"帧编码失败: {e}")
            return None

    def iterate_and_extract(self, folder_path: str, frame_interval: int, max_frames_to_extract: int, image_format: str, quality: int):
        video_files = self.get_sorted_video_files(folder_path)
        num_videos = len(video_files)

        if num_videos == 0:
            raise FileNotFoundError(f"在文件夹 '{folder_path}' 中没有找到任何视频文件。")

        if self.index >= num_videos:
            self.index = 0
            raise Exception(f"所有 {num_videos} 个视频已处理完毕。工作流已终止。")

        video_filename = video_files[self.index]
        full_video_path = os.path.join(folder_path, video_filename)
        
        logger.info(f"[VideoFramesIntervalIterator] 正在处理视频 {self.index + 1}/{num_videos}: {video_filename}")
        self.index += 1

        cap = cv2.VideoCapture(full_video_path)
        if not cap.isOpened():
            logger.error(f"无法打开视频: {video_filename}")
            return tuple([None] * MAX_OUTPUT_FRAMES + [video_filename])

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        content_items = []
        current_frame_idx = 0

        while current_frame_idx < total_frames and len(content_items) < max_frames_to_extract:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_idx)
            ret, frame = cap.read()
            if ret:
                content_item = self._encode_frame_to_content_item(frame, image_format, quality)
                if content_item:
                    content_items.append(content_item)
                    logger.info(f"  > 已提取第 {len(content_items)} 帧 (位于视频的第 {current_frame_idx} 帧)")
            else:
                logger.warning(f"  > 读取第 {current_frame_idx} 帧失败，提前结束提取。")
                break
            current_frame_idx += frame_interval
        
        cap.release()
        logger.info(f"成功从 '{video_filename}' 提取了 {len(content_items)} 帧。")

        output_list = content_items + [None] * (MAX_OUTPUT_FRAMES - len(content_items))
        output_list.append(os.path.splitext(video_filename)[0])

        return tuple(output_list)

# --------------------------------------------------------------------------------
# ComfyUI 节点注册
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "VideoFramesByIntervalIterator": VideoFramesByIntervalIteratorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoFramesByIntervalIterator": "迭代视频并按间隔提取多帧 (For Chat)"
}