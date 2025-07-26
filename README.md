# ComfyUI-iterator-nodes
这是几个通过遍历特定文件夹来向后续节点逐个输送文件夹中图像文件和对应prompt的ComfyUI节点 

These are ComfyUI nodes that iterate through a specified folder, passing the image files and their corresponding prompts one by one to the next nodes.

通过开启ComfyUI队列执行模式中的执行（变更时）模式来实现按特定顺序将文件夹中的图像\txt文件中的内容（常为prompt）一起传输给下一个节点，直到该文件夹内所有图像\txt文件均被传输后自动报错停止。此时将队列执行模式改回默认模式即可。

By enabling the 'Execute (on change)' mode in ComfyUI's queue execution settings, the system sequentially transfers images from a folder along with their corresponding text file contents (typically prompts) to the next node in a specified order. Once all image/text files in the folder have been processed, it automatically stops and throws an error. At this point, simply switch the queue execution mode back to the default setting.

其中ImageFileIterator节点和TextFileIterator节点分别为按顺序逐个传输特定文件夹内的图像和txt文件的节点，而FilenameComparator节点则在同时使用图像和txt传输节点时使用，其作用是检验两个节点同时传输的文件名是否一致，若不一致会报错停止队列执行以防造成更大的错误。

The ImageFileIterator node and TextFileIterator node are designed to sequentially transmit image files and text (.txt) files from a specified folder, one by one. When both image and text transmission nodes are used simultaneously, the FilenameComparator node comes into play—it checks whether the filenames being transmitted by both nodes match. If they don't, it triggers an error and halts queue execution to prevent further issues.





