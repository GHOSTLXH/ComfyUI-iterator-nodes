# ComfyUI-iterator-nodes
这是几个通过遍历特定文件夹来向后续节点逐个输送文件夹中图像、提示词（prompt）、视频文件（拆成图片组）、整个视频文件与逐个将视频文件通过API（openAI格式）上传给对应的大模型的ComfyUI节点。 

This is a set of ComfyUI nodes that traverse specific folders to sequentially deliver images, prompts, video files (split into image sequences), entire video files, and individually upload video files via an API (OpenAI format) to corresponding LLM for subsequent nodes.

注意1：这些逐个输送文件的节点均需要在ComfyUI开启 运行（更改时） 这一队列执行模式下才能全自动运行！若以普通运行模式运行的话就是点一次运行一次。

Note 1: These nodes that sequentially deliver files all require ComfyUI to be set to the **"Run (on change)"** queue execution mode for fully automatic operation! If running in the standard run mode, they will execute only once per manual run click.

注意2：逐个将视频文件通过API（openAI格式）上传给对应的大模型的ComfyUI节点（openai_file_iterator）后续需要搭配诸如spawner1145的aichat节点（https://github.com/spawner1145/comfyui-aichat ，在此感谢他制作的开源节点）等llm对话节点进行使用，且由于当前不同模型API提供商的“兼容”OpenAI格式的API对文件的上传与上传后的应答等方面的要求均不相同，因此可能会出现各种各样的问题，强烈建议在上传文件前仔细查看API提供商的API文档并根据其格式对节点程序文件本身做对应的修改（如果你实在要用这个API提供商的API的话...）

Note 2: The ComfyUI node (openai_file_iterator) that sequentially uploads video files via an API (OpenAI format) to corresponding large models needs to be used in conjunction with LLM dialogue nodes such as spawner1145's aichat node (https://github.com/spawner1145/comfyui-aichat—special and thanks to him for creating this open-source node). Additionally, since different API providers currently have varying requirements for file uploads and responses under their "compatible" OpenAI-style APIs, various issues may arise. It is strongly recommended to carefully review the API provider’s documentation and modify the node program file accordingly based on their specific format (if you have to use that particular API provider...).

节点功能：（nodes function）

（1）逐个读取图片文件（image_file_iterator node）

![image_file_iterator node](picture/wechat_2025-09-02_212449_354.png)

这个节点用于逐个从特定文件夹中（文件夹绝对路径在file_path中输入或通过其他字符串节点导入到file_path）按命名顺序逐个读取并输出图像文件。在该文件夹内所有图片均被输出后节点将会主动报错停止队列来提示任务已经完成。

This node is used to sequentially read and output image files from a specific folder (the absolute folder path is input in `file_path` or imported via other string nodes into `file_path`) in alphabetical order. After all images in the folder have been output, the node will actively throw an error to stop the queue, indicating that the task has been completed.

（2）逐个读取txt文件（text_file_iterator node）

![text_file_iterator node](picture/wechat_2025-09-02_212457_441.png)

这个节点用于逐个从特定文件夹中（文件夹绝对路径在file_path中输入或通过其他字符串节点导入到file_path）按命名顺序逐个读取并输出txt文件的内容（一般与逐个读取图片文件节点（image_file_iterator node）配合使用以同时输出图像和与图像文件同名的txt文件内的prompt内容）。在该文件夹内所有txt文件的内容均被输出后节点将会主动报错停止队列来提示任务已经完成。

This node is used to sequentially read and output the contents of txt files from a specific folder (the absolute folder path is input in `file_path` or imported via other string nodes into `file_path`) in alphabetical order. It is typically used in conjunction with the image file iterator node to simultaneously output images and the prompt content from txt files sharing the same filename as the image files. After the contents of all txt files in the folder have been output, the node will actively throw an error to stop the queue, indicating that the task has been completed.

（3）比较文件名（filename_comparator node）

![filename_comparator node](picture/wechat_2025-09-02_212508_041.png)

这个节点用于比较两个输出节点的输出文件名（filename）是否一致，并会在两个节点同时输出的文件名不一致时报错及时终止进程以避免造成更大的错误。此节点的filename输出可以接到诸如保存文件节点的文件名等地方。（你也不希望忙活了半天发现白忙活了对吧）

This node is used to compare whether the output filenames (`filename`) from two output nodes are consistent. It will throw an error and immediately terminate the process if the filenames output by the two nodes do not match, thereby preventing further errors. The `filename` output of this node can be connected to components such as the filename input of a save file node (You wouldn’t want to put in a lot of effort only to realize it was all in vain, right?).

（4）逐个读取视频文件（video_file_iterator node）

![video_file_iterator node](picture/wechat_2025-09-02_212515_145.png)

这个节点用于逐个从特定文件夹中（文件夹绝对路径在file_path中输入或通过其他字符串节点导入到file_path）按命名顺序逐个读取视频文件并将拆帧成一系列图片组。在该文件夹内所有视频文件均被输出后节点将会主动报错停止队列来提示任务已经完成。

This node is designed to sequentially read video files from a specified folder (the absolute path is provided via the `file_path` input, either directly or through other string nodes) in alphabetical order, and split each video into a series of image frames. After all video files in the folder have been processed and output, the node will actively throw an error to stop the queue, indicating that the task has been completed.











































