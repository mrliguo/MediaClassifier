# MediaClassifier

`MediaClassifier` is a Python program that automatically classifies photos and videos based on their orientation (landscape, portrait, or square).

## Features
- Smart detection of photo and video orientation
- Drag-and-drop file/folder support
- Automatic directory creation
- Auto-installation of dependencies
- Undo operation by pressing `F` after completion
- Operation statistics and logs displayed in the console
- Support for mixed media types (photos + videos)
- Undo functionality to restore files to their original locations

## Supported Formats
### Photo Formats
- JPG/JPEG
- PNG
- BMP
- TIFF
- WEBP
- HEIC
- RAW Formats: ARW, DNG, CR2, NEF, RAF, SR2, PEF, ORF

### Video Formats
- MP4
- MOV
- AVI
- MKV
- FLV
- WMV
- MPEG/MPG
- M4V
- 3GP

## Dependencies
The program requires the following Python libraries:
- `Pillow` (image processing)
- `rawpy` (RAW file support)
- `opencv-python` (video processing)
- `pillow-heif` (HEIC file support)

The program will automatically detect and install missing dependencies. You can also manually install them:

```bash
pip install Pillow rawpy opencv-python pillow-heif
```

## Usage
1. Run the program and drag in files or folders.
2. The program will classify media into:
   - `Landscape`
   - `Portrait`
   - `Square`
3. Press `F` after processing to undo operations.
4. View logs directly in the console.

### Classification Modes
- **Single Media Type** (photos or videos only):
  - Creates folders like `Landscape Photos` or `Portrait Videos`.
- **Mixed Media Types** (photos + videos):
  - The program will ask whether to separate classifications:
    - `Yes`: Creates separate folders for photos and videos.
    - `No`: Creates unified folders like `Landscape Media`.

## Notes
- The undo function (`F` key) must be used before closing the program.
- Original files remain in the source directory; the program moves files for classification.
- Logs include file counts, timestamps, and error messages.
- Conflicting filenames are automatically resolved with timestamps.
- Empty directories are cleaned up after undo.

## Example
### Input Directory
```
/Photos
    image1.jpg
    video1.mp4
```

### Output Directory (Separate Classification)
```
/Photos
    /Landscape Photos
        image1.jpg
    /Landscape Videos
        video1.mp4
```

---

# MediaClassifier

`MediaClassifier` 是一个基于 Python 的媒体分类工具，可自动按方向（横屏、竖屏、方屏）分类照片和视频。

## 功能
- 智能识别照片和视频方向
- 支持拖拽文件/文件夹操作
- 自动创建分类目录
- 自动安装依赖库
- 按 `F` 键撤销操作
- 控制台显示操作统计和日志
- 支持混合媒体类型（照片+视频）
- 提供撤销功能以恢复文件到原始位置

## 支持的格式
### 照片格式
- JPG/JPEG
- PNG
- BMP
- TIFF
- WEBP
- HEIC
- RAW 格式: ARW, DNG, CR2, NEF, RAF, SR2, PEF, ORF

### 视频格式
- MP4
- MOV
- AVI
- MKV
- FLV
- WMV
- MPEG/MPG
- M4V
- 3GP

## 依赖库
程序需要以下 Python 库：
- `Pillow`（图像处理）
- `rawpy`（RAW 文件支持）
- `opencv-python`（视频处理）
- `pillow-heif`（HEIC 文件支持）

程序会自动检测并安装缺失依赖库，也可手动安装：

```bash
pip install Pillow rawpy opencv-python pillow-heif
```

## 使用方法
1. 运行程序并拖入文件或文件夹。
2. 程序会按方向分类媒体：
   - `横屏`
   - `竖屏`
   - `方屏`
3. 处理完成后按 `F` 键撤销操作。
4. 在控制台中查看操作日志。

### 分类模式
- **单一媒体类型**（仅照片或视频）：
  - 创建 `横屏照片`、`竖屏视频` 等目录。
- **混合媒体类型**（照片+视频）：
  - 程序会询问是否分开分类：
    - `是`：分别为照片和视频创建目录。
    - `否`：统一创建 `横屏媒体` 等目录。

## 注意事项
- 撤销功能（`F` 键）需在关闭程序前使用。
- 原始文件保留在源目录，程序通过移动文件进行分类。
- 日志包含文件数量、时间戳和错误信息。
- 文件名冲突时自动添加时间戳。
- 撤销操作后会清理空目录。

## 示例
### 输入目录结构
```
/Photos
    image1.jpg
    video1.mp4
```

### 输出目录结构（分开分类）
```
/Photos
    /横屏照片
        image1.jpg
    /横屏视频
        video1.mp4
```
