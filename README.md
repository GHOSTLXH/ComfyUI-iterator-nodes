# ComfyUI-iterator-nodes
这是几个通过遍历特定文件夹来向后续节点逐个输送文件夹中图像、提示词（prompt）、视频文件（拆成图片组）、整个视频文件与逐个将视频文件通过API（openAI格式）上传给对应的大模型的ComfyUI节点。 

This is a set of ComfyUI nodes that traverse specific folders to sequentially deliver images, prompts, video files (split into image sequences), entire video files, and individually upload video files via an API (OpenAI format) to corresponding LLM for subsequent nodes.

注意：逐个将视频文件通过API（openAI格式）上传给对应的大模型的ComfyUI节点（openai_file_iterator）后续需要搭配诸如spawner1145的aichat节点（https://github.com/spawner1145/comfyui-aichat ，在此感谢他制作的开源节点）等llm对话节点进行使用，且由于当前不同模型API提供商的“兼容”OpenAI格式的API对文件的上传与上传后的应答等方面的要求均不相同，因此可能会出现各种各样的问题，强烈建议在上传文件前仔细查看API提供商的API文档并根据其格式对节点程序文件本身做对应的修改（如果你实在要用这个API提供商的API的话...）

Note: The ComfyUI node (openai_file_iterator) that sequentially uploads video files via an API (OpenAI format) to corresponding large models needs to be used in conjunction with LLM dialogue nodes such as spawner1145's aichat node (https://github.com/spawner1145/comfyui-aichat—special and thanks to him for creating this open-source node). Additionally, since different API providers currently have varying requirements for file uploads and responses under their "compatible" OpenAI-style APIs, various issues may arise. It is strongly recommended to carefully review the API provider’s documentation and modify the node program file accordingly based on their specific format (if you have to use that particular API provider...).


















