import sys
import os
import shutil
import subprocess
import logging

# === 版权信息 ===
def show_copyright():
    print("\nPhotoClassifier v1.8.3")
    print("Created by mrliguo")
    print("Licensed under the Apache-2.0 license\n")

# === 依赖检查模块 ===
def check_dependencies():
    """先于所有第三方库导入执行"""
    required = {
        'Pillow': 'PIL',    # 包名: 导入名
        'rawpy': 'rawpy'
    }

    missing = []
    for pkg, imp in required.items():
        try:
            __import__(imp)
        except ImportError:
            missing.append(pkg)

    if missing:
        show_copyright()
        print("缺少依赖库:")
        print("\n".join(f"- {pkg}" for pkg in missing))
        choice = input("是否自动安装？(Y/n): ").lower()
        if choice in ('', 'y'):
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", *missing
                ])
                print("安装成功，请重新运行程序")
                input("按下 [Enter] 键退出...")
                sys.exit(0)
            except Exception as e:
                print(f"安装失败: {str(e)}")
                input("按下 [Enter] 键退出...")
                sys.exit(1)
        else:
            print("必须安装依赖库才能继续")
            input("按下 [Enter] 键退出...")
            sys.exit(1)

# === 导入第三方库 ===
from PIL import Image
from datetime import datetime
import rawpy

# === 跨平台输入处理 ===
try:
    import msvcrt
    def get_key():
        while True:
            ch = msvcrt.getch().decode(errors='ignore').lower()
            if ch in ('\x00', '\xe0'):
                msvcrt.getch()
            else:
                return ch
except ImportError:
    import termios
    import tty
    def get_key():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1).lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

# === 日志配置 ===
class ColorFormatter(logging.Formatter):
    FORMATS = {
        logging.WARNING: "\033[31m[WARNING]\033[0m %(message)s",
        logging.ERROR: "\033[31m[ERROR]\033[0m %(message)s",
        logging.INFO: "[%(levelname)s] %(message)s"
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# 创建并配置日志处理器
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
    """智能判断图片方向"""
    try:
        ext = os.path.splitext(file_path)[1].lower()

        # 处理JPG/JPEG
        if ext in ('.jpg', '.jpeg'):
            with Image.open(file_path) as img:
                # 读取EXIF方向信息
                exif = img.getexif()
                orientation = exif.get(274, 1)

                # 根据方向调整判断
                if orientation in [5, 6, 7, 8]:
                    width, height = img.height, img.width
                else:
                    width, height = img.width, img.height

        # 处理RAW文件
        elif ext in ('.arw', '.dng'):
            with rawpy.imread(file_path) as raw:
                width = raw.sizes.width
                height = raw.sizes.height

        else:
            return None

        # 方向判断逻辑
        if width == height:
            return 'square'
        return 'portrait' if height > width else 'landscape'

    except Exception as e:
        logger.error(f"处理 {os.path.basename(file_path)} 失败: {str(e)}")
        return None

def process_item(path, base_dir=None):
    """处理单个文件或目录"""
    if os.path.isfile(path):
        _process_file(path, base_dir or os.path.dirname(path))
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for f in files:
                file_path = os.path.join(root, f)
                _process_file(file_path, base_dir or root)

def _process_file(file_path, base_dir):
    """实际处理单个文件"""
    global ignored_files, processed_files
    
    # 检查文件类型
    if not file_path.lower().endswith(('.jpg', '.jpeg', '.arw', '.dng')):
        logger.warning(f"不支持的文件类型: {os.path.basename(file_path)}")
        ignored_files += 1
        return

    # 处理文件方向
    try:
        orientation = get_orientation(file_path)
        if not orientation:
            return

        # 创建目标目录
        target_dir = os.path.join(base_dir, {
            'square': "方屏照片",
            'portrait': "竖屏照片",
            'landscape': "横屏照片"
        }[orientation])
        
        os.makedirs(target_dir, exist_ok=True)

        # 移动文件
        target_path = get_unique_path(os.path.join(target_dir, os.path.basename(file_path)))
        shutil.move(file_path, target_path)
        operations.append((file_path, target_path))
        processed_files += 1
        logger.info(f"已移动: {os.path.basename(file_path)} -> {os.path.basename(target_dir)}")

    except Exception as e:
        logger.error(f"处理失败: {os.path.basename(file_path)} - {str(e)}")

def undo_operations():
    """撤销所有操作"""
    if not operations:
        logger.info("没有可撤销的操作")
        return

    # 逆向执行撤销
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
    show_copyright()
    
    if len(sys.argv) < 2:
        print("使用方法：拖放文件/文件夹到程序图标")
        input("按下 [Enter] 键退出...")
        return

    # 重置全局计数器
    global ignored_files, processed_files
    ignored_files = 0
    processed_files = 0

    # 处理文件
    for path in sys.argv[1:]:
        if os.path.exists(path):
            process_item(path)
        else:
            logger.warning(f"路径不存在: {path}")

    # 显示处理结果
    print("\n" + "="*40)
    if processed_files > 0:
        print(f"成功处理 {processed_files} 张图片")
    if ignored_files > 0:
        print(f"忽略 {ignored_files} 个不支持的文件")
    if processed_files == 0 and ignored_files == 0:
        print("没有需要处理的文件")
    print("="*40)

    # 特殊处理：全部文件不支持的情况
    if processed_files == 0 and ignored_files > 0:
        print("\n⚠️ 所有拖入的文件均不支持")
        input("按下 [Enter] 键退出...")
        return

    # 交互操作
    if processed_files > 0:
        print("\n输入 [F] 后按下 [Enter] 键撤销操作\n按下 [Enter] 键退出程序")
        key = input().lower()
        if key == 'f':
            undo_operations()
            print("\n操作已撤销")
            input("按下 [Enter] 键退出...")

if __name__ == "__main__":
    main()
