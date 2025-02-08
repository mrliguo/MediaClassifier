import sys
import os
from PIL import Image, ExifTags
import shutil
import logging
import rawpy

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_image_orientation(image_path):
    try:
        # 获取文件名用于日志显示
        filename = os.path.basename(image_path)
        
        # 对于JPG文件
        if image_path.lower().endswith(('.jpg', '.jpeg')):
            with Image.open(image_path) as img:
                # 获取原始尺寸
                orig_width, orig_height = img.size
                logger.info(f"正在处理 {filename} - 原始尺寸 - 宽: {orig_width}, 高: {orig_height}")
                
                # 获取EXIF数据
                try:
                    exif = img._getexif()
                    if exif:
                        orientation = exif.get(274, 1)  # 274 是方向标签的ID
                        logger.info(f"EXIF方向值: {orientation}")
                        
                        # 检查是否需要交换宽高
                        width, height = orig_width, orig_height
                        if orientation in [5, 6, 7, 8]:
                            width, height = height, width
                            logger.info(f"根据EXIF调整后 - 宽: {width}, 高: {height}")
                    else:
                        width, height = orig_width, orig_height
                        logger.info("未找到EXIF数据")
                except Exception as e:
                    width, height = orig_width, orig_height
                    logger.info(f"读取EXIF时出错: {str(e)}")
                
        # 对于RAW文件（ARW和DNG）
        elif image_path.lower().endswith(('.arw', '.dng')):
            with rawpy.imread(image_path) as raw:
                # 获取原始图像尺寸
                width = raw.sizes.width
                height = raw.sizes.height
                logger.info(f"RAW文件({os.path.splitext(image_path)[1]}) - 宽: {width}, 高: {height}")
        else:
            return None
        
        # 判断方向
        ratio = width / height
        logger.info(f"宽高比: {ratio}")
        
        # 如果宽高比接近1（正方形），默认为横屏
        if 0.95 <= ratio <= 1.05:
            logger.info("接近正方形的图片，默认作为横屏")
            return 'landscape'
        
        is_portrait = height > width
        logger.info(f"判定为: {'竖屏' if is_portrait else '横屏'}")
        return 'portrait' if is_portrait else 'landscape'
                
    except Exception as e:
        logger.error(f"处理文件 {image_path} 时出错: {str(e)}")
        return None

def process_directory(directory):
    logger.info(f"\n处理文件夹: {directory}")
    
    # 先扫描一遍文件夹，判断是否有横/竖屏照片
    has_landscape = False
    has_portrait = False
    image_orientations = {}  # 存储每个文件的方向
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # 跳过文件夹和非图片文件
        if os.path.isdir(file_path):
            continue
        if not filename.lower().endswith(('.jpg', '.jpeg', '.arw', '.dng')):
            continue
            
        orientation = get_image_orientation(file_path)
        if orientation:
            image_orientations[file_path] = orientation
            if orientation == 'landscape':
                has_landscape = True
            else:
                has_portrait = True
    
    # 只在需要时创建文件夹
    landscape_dir = os.path.join(directory, "横屏照片") if has_landscape else None
    portrait_dir = os.path.join(directory, "竖屏照片") if has_portrait else None
    
    if landscape_dir:
        os.makedirs(landscape_dir, exist_ok=True)
    if portrait_dir:
        os.makedirs(portrait_dir, exist_ok=True)
    
    # 移动文件
    for file_path, orientation in image_orientations.items():
        if orientation == 'landscape' and landscape_dir:
            target_dir = landscape_dir
        elif orientation == 'portrait' and portrait_dir:
            target_dir = portrait_dir
        else:
            continue
            
        filename = os.path.basename(file_path)
        target_path = os.path.join(target_dir, filename)
        
        try:
            shutil.move(file_path, target_path)
            logger.info(f"已将 {filename} 移动到: {target_dir}")
        except Exception as e:
            logger.error(f"移动文件时出错: {str(e)}")

def process_recursive(path):
    """递归处理文件夹"""
    if os.path.isfile(path):
        directory = os.path.dirname(path)
        if not directory:
            directory = os.getcwd()
        process_directory(directory)
    elif os.path.isdir(path):
        # 先处理当前文件夹中的文件
        process_directory(path)
        
        # 再递归处理子文件夹
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path) and item not in ["横屏照片", "竖屏照片"]:
                process_recursive(item_path)

def main(paths):
    for path in paths:
        process_recursive(path)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1:])
        input("处理完成，按Enter键退出...")
    else:
        print("请将文件或文件夹拖放到此脚本上。")
        input("按Enter键退出...")