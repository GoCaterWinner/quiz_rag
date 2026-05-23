"""
工具栏
"""
from PIL import Image
import json
from pathlib import Path

def get_box_center_y(box):
    """
    box对应四个元素,分别是左上角的x, y坐标和右下角的x, y坐标
    """
    return (box[1] + box[3]) / 2


def is_green_region(count):
    """
    判断是不是绿色像素点
    """

    if count > 20:
        return True
    
    return False


def dectect_color(r, g, b):
    """目前只判断绿色和白色, 以后别的颜色再说"""

    if 150 < g < 220  and 80 < r < 100 and 140 < b < 180:
        return "green"
    
    elif r > 235 and g > 235 and b > 235:
        return "white"
    

def get_green_center_option_row(image_path, threshold = 0) -> list:
    """
    设置两层状态扫描机, 分为出绿色区域状态和进入绿色区域状态

    输入: 图像路径
    输出: 一个列表, 里面放着所有绿色像素点的中点坐标, 之后负责与所有的按钮像素纵坐标进行比较.
    """

    option_rows = []
        
    image = Image.open(str(image_path)).convert("RGB")

    last_rigion_count = 0

    for y in range(image.height):

        # 设置两层状态机
        current_rigion_count = 0

        for x in range(image.width):

            # 扫描逻辑, 从上到下, 到做到右, 碰到碰到进入绿色区域就append, 出绿色区域append第二次, 误差后期可以进行阈值调整
            r, g, b = image.getpixel((x, y))

            if dectect_color(r, g, b) == "green":
                current_rigion_count += 1

        if is_green_region(current_rigion_count) and not is_green_region(last_rigion_count): # 进区域
        
            option_rows.append(y - threshold)

        elif not is_green_region(current_rigion_count) and is_green_region(last_rigion_count): # 出区域
        
            option_rows.append(y + threshold)

        last_rigion_count = current_rigion_count

    # 我们只需要一个绿色按钮的纵坐标的中点坐标即可

    option_green_center_rows = []

    option_rows = list(zip(option_rows[0::2], option_rows[1::2]))

    for option_row in option_rows:

        green_center_y = ( option_row[0] + option_row[1] ) / 2
        option_green_center_rows.append(green_center_y)
                                
    return option_green_center_rows


ScreenDir = Path("../screenshot/data")

# 支持的图片格式
image_dir = [".jpg", ".jpeg", ".png"]


