#===PhotoClassifier has been renamed MeidaClassifier===
#===This version is the last PhotoClassifier release and only supports image processing===
#===You can check the latest distribution on MeidaClassifier.py===
#=== PhotoClassifier已更名为MeidaClassifier ===
#=== 此版本是最后一个PhotoClassifier发行版，仅支持图像处理 ===
#=== 你可以MeidaClassifier.py查看最新分发 ===

import sys
import os
import shutil
import logging
from datetime import datetime


# === 版权信息 ===
def show_copyright():
    print("\nPhotoClassifier v1.8.4")
    print("支持智能图片分类")
    print("Created by mrliguo")
    print("Licensed under the Apache-2.0 license\n")

# === 依赖检查模块 ===
def check_dependencies():
    """强制优先执行的依赖检查"""
    required = {
        'Pillow': 'PIL',
        'rawpy': 'rawpy'
    }
    missing = []
    for pkg, imp in required.items():
        try:
            __import__(imp)
        except ImportError:
            missing.append(pkg)

    if missing:
        print("\nPhotoClassifier 依赖检查")
        print("缺少以下必要依赖库:")
        print("\n".join(f"- {pkg}" for pkg in missing))
        choice = input("是否自动安装？(Y/n): ").lower()
        if choice in ('', 'y'):
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", *missing,
                ])
                print("\n安装成功！请重新运行程序")
                input("按下 [Enter] 键退出...")
                sys.exit(0)
            except Exception as e:
                print(f"\n安装失败: {str(e)}")
                print("请手动执行以下命令安装：")
                print(f"pip install {' '.join(missing)}")
                sys.exit(1)
        else:
            print("\n必须安装依赖库才能继续")
            input("按下 [Enter] 键退出...")
            sys.exit(1)

# === 强制优先执行依赖检查 ===
check_dependencies()
from PIL import Image
import rawpy
import subprocess

# === 文件类型配置 ===
IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', 
             '.webp', '.heic', '.arw', '.dng', '.cr2',
             '.nef', '.raf', '.sr2', '.pef', '.orf')

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
    """获取图片方向信息"""
    try:
        ext = os.path.splitext(file_path)[1].lower()
        width = height = 0

        # 处理图片
        if ext in IMAGE_EXTS:
            # ===== 改进的RAW文件处理逻辑 =====
            if ext == '.dng':
               with rawpy.imread(file_path) as raw:
                    width = raw.sizes.width
                    height = raw.sizes.height
                    # 如果是DNG文件，读取EXIF方向信息
                    try:
                        img = Image.open(file_path)
                        exif = img.getexif()
                        orientation = exif.get(274, 1)
                        # 根据EXIF方向调整
                        if orientation in [5, 6, 7, 8]:
                            width, height = height, width
                    except Exception as e:
                        logger.warning(f"无法读取DNG文件EXIF方向: {str(e)}")

            elif ext in ('.arw', '.cr2', '.nef', '.raf', '.sr2', '.pef', '.orf'):
                # 其他RAW格式：仅使用rawpy处理
                with rawpy.imread(file_path) as raw:
                    width = raw.sizes.width
                    height = raw.sizes.height
                    # 部分RAW文件可能需要交换宽高
                    if raw.sizes.flip in (5, 6, 7, 8):
                        width, height = height, width

            else:
                # 普通图片处理（非RAW格式）
                with Image.open(file_path) as img:
                    exif = img.getexif()
                    orientation = exif.get(274, 1)
                    if orientation in [5, 6, 7, 8]:
                        width, height = img.height, img.width
                    else:
                        width, height = img.width, img.height
            # ===== 改进结束 =====

            return '方屏' if width == height else '竖屏' if height > width else '横屏'

        return None

    except Exception as e:
        logger.error(f"处理失败: {os.path.basename(file_path)} - {str(e)}")
        return None

def process_file(file_path, base_dir):
    """处理单个文件"""
    global ignored_files, processed_files

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in IMAGE_EXTS:
        logger.warning(f"不支持的文件类型: {os.path.basename(file_path)}")
        ignored_files += 1
        return

    orientation = get_orientation(file_path)
    if not orientation:
        return

    # 确定分类模式
    folder_name = f"{orientation}图片"

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

# === 主程序 ===
def main():
    check_dependencies()  # 确保依赖检查最先执行
    show_copyright()

    if len(sys.argv) < 2:
        print("使用方法：拖放文件/文件夹到程序图标")
        input("按下 [Enter] 键退出...")
        return

    # 初始化全局状态
    global ignored_files, processed_files
    ignored_files = 0
    processed_files = 0

    # 处理文件
    for path in sys.argv[1:]:
        if os.path.isfile(path):
            process_file(path, os.path.dirname(path))
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for f in files:
                    file_path = os.path.join(root, f)
                    process_file(file_path, root)
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
            input()
        else:
            pass

if __name__ == "__main__":
    main()
