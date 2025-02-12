import sys
import os
import shutil
import subprocess
import logging
from datetime import datetime

# === 依赖检查模块 ===
def check_dependencies():
    """强制优先执行的依赖检查"""
    required = {
        'Pillow': 'PIL',
        'rawpy': 'rawpy',
        'opencv-python': 'cv2',
        'pillow-heif': 'pillow_heif'
    }

    missing = []
    for pkg, imp in required.items():
        try:
            __import__(imp)
        except ImportError:
            missing.append(pkg)

    if missing:
        print("\nMediaClassifier 依赖检查")
        print("缺少以下必要依赖库:")
        print("\n".join(f"- {pkg}" for pkg in missing))
        choice = input("是否自动安装？(Y/n): ").lower()
        if choice in ('', 'y'):
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", *missing,
                    "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
                ])
                print("\n安装成功！请重新运行程序")
                sys.exit(0)
            except Exception as e:
                print(f"\n安装失败: {str(e)}")
                print("请手动执行以下命令安装：")
                print(f"pip install {' '.join(missing)}")
                sys.exit(1)
        else:
            print("\n必须安装依赖库才能继续")
            sys.exit(1)

# === 强制优先执行依赖检查 ===
check_dependencies()

# === 导入第三方库（依赖检查通过后执行）===
from PIL import Image
import rawpy
import cv2
import pillow_heif

# 初始化HEIF支持
pillow_heif.register_heif_opener()

# 初始化HEIF支持
pillow_heif.register_heif_opener()

# === 版权信息 ===
def show_copyright():
    print("\nMediaClassifier v2.1.2")
    print("支持智能媒体分类（照片/视频）")
    print("Created by mrliguo")
    print("Licensed under the Apache-2.0 license\n")

# === 文件类型配置 ===
IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', 
             '.webp', '.heic', '.arw', '.dng', '.cr2',
             '.nef', '.raf', '.sr2', '.pef', '.orf')

VIDEO_EXTS = ('.mp4', '.mov', '.avi', '.mkv', '.flv',
             '.wmv', '.mpeg', '.mpg', '.m4v', '.3gp')

# === 日志配置 ===
class ColorFormatter(logging.Formatter):
    FORMATS = {
        logging.WARNING: "\033[33m[WARNING]\033[0m %(message)s",
        logging.ERROR: "\033[31m[ERROR]\033[0m %(message)s",
        logging.INFO: "\033[36m[INFO]\033[0m %(message)s"
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter())
logger.addHandler(handler)

# === 全局状态 ===
operations = []         # 操作记录
ignored_files = 0       # 不支持文件计数器
processed_files = 0     # 已处理文件计数器
media_types = set()     # 检测到的媒体类型

# === 核心功能 ===
def get_unique_path(target_path):
    """生成唯一文件名"""
    if not os.path.exists(target_path):
        return target_path

    base_dir = os.path.dirname(target_path)
    base_name, ext = os.path.splitext(os.path.basename(target_path))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    new_name = f"{base_name}_{timestamp}{ext}"
    counter = 1
    while os.path.exists(os.path.join(base_dir, new_name)):
        new_name = f"{base_name}_{timestamp}_{counter}{ext}"
        counter += 1

    return os.path.join(base_dir, new_name)

def get_orientation(file_path):
    """获取媒体方向信息"""
    try:
        ext = os.path.splitext(file_path)[1].lower()
        width, height = 0, 0

        # 处理图片
        if ext in IMAGE_EXTS:
            media_types.add("photo")
            # RAW格式处理
            if ext in ('.arw', '.dng', '.cr2', '.nef', '.raf', '.sr2', '.pef', '.orf'):
                with rawpy.imread(file_path) as raw:
                    width = raw.sizes.width
                    height = raw.sizes.height
            # 普通图片处理
            else:
                with Image.open(file_path) as img:
                    exif = img.getexif()
                    orientation = exif.get(274, 1)
                    if orientation in [5, 6, 7, 8]:
                        width, height = img.height, img.width
                    else:
                        width, height = img.width, img.height

        # 处理视频
        elif ext in VIDEO_EXTS:
            media_types.add("video")
            cap = cv2.VideoCapture(file_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()

        else:
            return None

        # 判断方向
        if width == height:
            return '方屏'
        return '竖屏' if height > width else '横屏'

    except Exception as e:
        logger.error(f"处理失败: {os.path.basename(file_path)} - {str(e)}")
        return None

def process_file(file_path, base_dir, separate_mode):
    """处理单个文件"""
    global ignored_files, processed_files

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in IMAGE_EXTS + VIDEO_EXTS:
        logger.warning(f"不支持的文件类型: {os.path.basename(file_path)}")
        ignored_files += 1
        return

    orientation = get_orientation(file_path)
    if not orientation:
        return

    # 确定分类模式
    media_type = "图片" if ext in IMAGE_EXTS else "视频"
    folder_name = f"{orientation}{media_type}" if separate_mode else f"{orientation}媒体"

    # 创建目标目录
    target_dir = os.path.join(base_dir, folder_name)
    os.makedirs(target_dir, exist_ok=True)

    # 移动文件
    target_path = get_unique_path(os.path.join(target_dir, os.path.basename(file_path)))
    try:
        shutil.move(file_path, target_path)
        operations.append((file_path, target_path))
        processed_files += 1
        logger.info(f"已移动: {os.path.basename(file_path)} -> {folder_name}")
    except Exception as e:
        logger.error(f"移动失败: {str(e)}")

def undo_operations():
    """撤销所有操作"""
    if not operations:
        logger.info("没有可撤销的操作")
        return

    restored = 0
    for src, dest in reversed(operations):
        try:
            if os.path.exists(dest):
                os.makedirs(os.path.dirname(src), exist_ok=True)
                shutil.move(dest, src)
                restored += 1
                logger.info(f"已撤销: {os.path.basename(dest)}")
        except Exception as e:
            logger.error(f"撤销失败: {str(e)}")

    # 清理空目录
    processed_dirs = set(os.path.dirname(dest) for _, dest in operations)
    for d in processed_dirs:
        try:
            if os.path.exists(d) and not os.listdir(d):
                os.rmdir(d)
                logger.info(f"清理空目录: {d}")
        except Exception as e:
            logger.error(f"清理目录失败: {str(e)}")

    operations.clear()
    logger.info(f"成功撤销 {restored} 个文件")

def main():
    check_dependencies()
    show_copyright()

# === 主程序 ===
def main():
    check_dependencies()  # 确保依赖检查最先执行
    show_copyright()

    if len(sys.argv) < 2:
        print("使用方法：拖放文件/文件夹到程序图标")
        input("按下 [Enter] 键退出...")
        return

    # 初始化全局状态
    global media_types, ignored_files, processed_files
    media_types.clear()
    ignored_files = 0
    processed_files = 0

    # 预扫描媒体类型
    for path in sys.argv[1:]:
        if os.path.isfile(path):
            ext = os.path.splitext(path)[1].lower()
            if ext in IMAGE_EXTS:
                media_types.add("photo")
            elif ext in VIDEO_EXTS:
                media_types.add("video")
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in IMAGE_EXTS:
                        media_types.add("photo")
                    elif ext in VIDEO_EXTS:
                        media_types.add("video")

    # 确定分类模式
    separate_mode = True
    if len(media_types) > 1:
        print("\n检测到混合媒体类型（照片+视频）")
        choice = input("是否分开分类？(Y/n): ").lower()
        separate_mode = choice in ('', 'y')

    # 处理文件
    for path in sys.argv[1:]:
        if os.path.isfile(path):
            process_file(path, os.path.dirname(path), separate_mode)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for f in files:
                    file_path = os.path.join(root, f)
                    process_file(file_path, root, separate_mode)
        else:
            logger.warning(f"路径不存在: {path}")

    # 显示结果
    print("\n" + "="*40)
    print(f"成功处理 {processed_files} 个文件")
    print(f"忽略 {ignored_files} 个不支持的文件")
    print("="*40)

    # 撤销功能
    if processed_files > 0:
        print("\n输入 [F] 后按下 [Enter] 键撤销操作\n按下 [Enter] 键退出程序")
        choice = input().lower()
        if choice == 'f':
            undo_operations()
            print("\n操作已撤销，按 [Enter] 键退出...")
            input()  # 关键修改：等待用户确认
        else:
            pass

if __name__ == "__main__":
    main()