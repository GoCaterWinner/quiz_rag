"""
OpenCV模块, 负责解析按钮的坐标
"""

import cv2
import numpy as np

def get_option_y(image_path):
    """
    找到所有按钮的y坐标, 如果要返回第一个按钮的y坐标, 进行排序即可, 最后的结果应该是返回一个列表

    输入: 图片路径
    输出: 所有按钮的纵坐标上界
    """

    # 读取图片
    image = cv2.imread(str(image_path))

    # 我们这次只要左边的数据, opencv的格式先y轴再x轴
    left_image = image[:, :260]

    # 转换成灰度图
    left_image_gray = cv2.cvtColor(left_image, cv2.COLOR_BGR2GRAY)

    # np转掩码
    mask = np.where(left_image_gray < 245, 255, 0).astype("uint8")

    candidate_option_y = []

    # 找连通区域
    label_num, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)

    # 遍历连通区域，我们通过stats里面的长度和宽度的比率来确定正方形区域和圆形区域, 如果规则不够，可以添加新区域
    for x, y, w, h, area in stats:

        ratio = w / h
        
        if 0.8 < ratio < 1.2 and 40 < w < 100 and 40 < h < 100 and y > 100:

            # 最好加入条件多一点, 方便后续进行观察
            candidate_option_y.append({
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "area": area
            })

    if not candidate_option_y:
        candidate_option_y.append(
            {
                "x": 0,
                "y": 10000,
                "w": 1,
                "h": 1,
                "area": 0,           
            }
        )

    return candidate_option_y