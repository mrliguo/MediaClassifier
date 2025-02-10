# PhotoClassifier
PhotoClassifier is a Python program that automatically distinguishes between horizontal and vertical images.

## Features
- Automatic orientation detection for images
- Drag-and-drop folder/file support
- Automatic directory management
- Auto-installation of dependencies
- Undo functionality by pressing `F` after completion
- Operation statistics and log display in the console

## Supported Formats
Currently supports the following image formats:
- JPG
- ARW 
- DNG

## Dependencies
PhotoClassifier requires these Python libraries:
- `rawpy`
- `Pillow`

The program will automatically detect and install missing dependencies on run. You can also manually install:

```bash
pip install rawpy Pillow
```

## Usage
1. Run the program and drag in targets
2. After processing completes, press `F` to undo the last operation
3. View operation logs directly in the program console

The program will:
- Create `Horizontal` and `Vertical` folders
- Generate backup copies for undo capability
- Display operation statistics and logs in the console

## Notes
- Undo function (`F` key) must be used before closing the program
- Original files remain unchanged in source directory
- Logs include file counts, timestamps, and error messages

# PhotoClassifier

PhotoClassifier 是一个可以自动区分横竖屏图片的 Python 程序。

## 功能
- 智能识别图片方向
- 支持拖拽文件/文件夹操作
- 自动创建分类目录
- 自动安装依赖库
- 完成后按 `F` 键撤销操作
- 操作统计与日志显示在程序运行框中

## 支持的格式
当前支持以下图像格式：
- JPG
- ARW
- DNG

## 依赖库
程序需要以下 Python 库：
- `rawpy`
- `Pillow`

程序运行时将自动检测并安装缺失依赖库，也可手动安装：

```bash
pip install rawpy Pillow
```

## 使用方法
1. 运行程序并拖入目标文件或文件夹
2. 处理完成后，按 `F` 键撤销操作
3. 在程序运行框中查看操作日志

程序将会：
- 创建「横屏照片」和「竖屏照片」分类文件夹
- 生成操作备份以便撤销
- 在运行框中显示操作统计和日志

## 注意事项
- 撤销功能（按 `F` 键）需在关闭程序前使用
- 原始文件始终保留在源目录
- 日志包含文件数量、时间戳和错误信息
