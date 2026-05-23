# 方便处理文件路径的库
from pathlib import Path
"""
该脚本的作用是, 找到你某个文件夹的图片, 按照修改时间排序, 然后批量重命名, 方便后面OCR进行循环读取
"""

# 如果你的截图放在 screenshot/data，脚本文件放在 scripts 里，那么这个路径就是 ../screenshot/data
BASE_DIR = Path(__file__).resolve().parents[1]
ScreenDir = BASE_DIR / "screenshot" / "data"

# 支持的图片格式
image_dir = [".jpg", ".jpeg", ".png"]



def main():
    # 先判断这个文件夹是否存在，不存在就退出
    if not ScreenDir.exists():
        print(f"文件{ScreenDir}不存在")
        return 
   
    # 拿文件名
    image = [ p for p in ScreenDir.iterdir() if p.is_file() and p.suffix.lower() in image_dir ]

    # 按修改时间排序，通常就是截图顺序
    image_sorted = sorted(image, key= lambda p: p.stat().st_mtime)
   
    # 第一步：先改成临时名，避免 q001.png 已存在时互相覆盖
    # 先建立一个空列表
    temp_images = []
    for i, old_name in enumerate(image_sorted, start=1):
        temp_new_name = ScreenDir/f"_temp_{i:04d}{old_name.suffix.lower()}"
        old_name.rename(temp_new_name)
        temp_images.append(temp_new_name)


    # 第二步：改成最终名 q001.png, q002.png...
    for i, temp_name in enumerate(temp_images, start=1):
        new_name = ScreenDir/f"q{i:03d}{temp_name.suffix.lower()}"
        temp_name.rename(new_name)


if __name__ == "__main__":
    main()



