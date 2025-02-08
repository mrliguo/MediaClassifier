# PhotoClassifier
PhotoClassifier is a Python program that automatically distinguishes between horizontal and vertical images.

## Features
Automatically distinguishes the orientation of images.

Supports dragging and dropping folders or files for processing.

Automatically creates directories to store classified images when processing folders.

## Supported Formats
Currently supports the following image formats:
- JPG
- ARW
- DNG

## Dependencies
Before using PhotoClassifier, make sure you have installed the following Python libraries:
- `rawpy`
- `Pillow`

## Usage
1. Install the required libraries:

   ```bash
   pip install rawpy Pillow
   ```
2. Run the program and drag in folders or files.

The program will automatically classify images and create corresponding folders in the specified directory.

# PhotoClassifier

PhotoClassifier 是一个自动区分横竖屏图片的 Python 程序。

## 功能

- 自动区分图片的横竖屏方向。
- 支持拖入文件夹或文件进行处理。
- 在处理文件夹时，自动创建目录以存放分类后的图片。

## 支持的格式

目前支持以下图片格式：
- JPG
- ARW
- DNG

## 依赖库

在使用 PhotoClassifier 之前，请确保已安装以下 Python 库：
- `rawpy`
- `Pillow`

## 使用方法

1. 安装依赖库：
   ```bash
   pip install rawpy Pillow
   ```
2. 运行程序并拖入文件夹或文件。

程序会自动分类图片并在指定目录中创建相应的文件夹。

