"""
识别文字模块, 主要起到识别文字的作用
"""

from collections import defaultdict
from paddleocr import PaddleOCR

from src.normalize import clean_data
from src.opencv import get_option_y
from src.tools import get_box_center_y, get_green_center_option_row
from src.parser import parse_question
from src.decorators import timer

ocr = PaddleOCR(use_angle_cls=True, lang="ch")


def combine_text(items):
    """
    将列表进行合并, 先删除元素, 然后进行替换, 坐标只需要替换首尾两个坐标即可

    输入:文本数据, 坐标
    输出: 合并后的文本数据, 合并后的坐标

    item structure:[
                    {
                        "text": text,
                        "coord": (x1, y1, x2, y2),
                        "center_y": center_y,
                    }
                    ]
    """
    if not items:
        return None
    
    # 先按照纵坐标进行排序, 防止因为解析问题, 出现不正确的文本顺序
    items.sort(key = lambda x: x["center_y"])
    
    # 文本, 坐标合并
    text_combined = ""
    new_box = [0, 0, 0, 0]

    for item in items:
        text_combined += item["text"]
        
    new_box[0] = min(item["coord"][0] for item in items)
    new_box[1] = min(item["coord"][1] for item in items)
    new_box[2] = max(item["coord"][2] for item in items)
    new_box[3] = max(item["coord"][3] for item in items)


    return text_combined, new_box

def combine_question_data(result, image_path):
    """
    根据题目的文本数据, 将文本数据的多行进行合并操作
    目标是传入文本数据, 然后填入question字段

    输入: 原图像
    输出: 题干文本列表, 题干坐标列表
    """


    # 列表接收数据, 虽然说题干数据肯定只有一个, 但是为了数据类型的统一, 统一用列表接收
    combined_question_texts, combined_question_coords = [], []

    # 提取坐标信息和文本信息
    boxes = result[0]["rec_boxes"]
    texts = result[0]["rec_texts"]

    # 提取y坐标
    first_option = get_option_y(image_path)

    # 第一个按钮的y坐标, 默认在左上角
    first_option.sort(key = lambda x: x["y"])
    first_option_y = first_option[0]["y"]

    items = []

    for text, box in zip(texts, boxes):

        x1, y1, x2, y2 = box

        # 中心点坐标, 负责比较
        center_y = get_box_center_y(box)

        # 比较条件, 只有在文本的右下角的纵坐标比按钮小的时候，才能进行
        # 为了健壮性起见， 再加入纵坐标下界与第一个按钮进行比较
        if center_y < first_option_y and y2 < first_option_y:
            # 肯定是从第三个文本开始的, 前两个文本必定是type and score, 定位坐标,  起点在i = 2, 终点在坐标为第一个按钮之前
            if text in {"单选题", "多选题", "判断题", "5分"}:
                continue
                
            else:

                # 我们提取核心的索引, 就可以在后面的过程根据索引来对列表进行合并或者删除
                items.append(
                    {
                        "text": text,
                        "coord": (x1, y1, x2, y2),
                        "center_y": center_y,
                    }
                )

        else:
            continue

    
    combined_question_text, combined_question_coord = combine_text(items)

    combined_question_texts.append(combined_question_text)
    combined_question_coords.append(combined_question_coord)


    return combined_question_texts, combined_question_coords


def combine_answer_data(result, image_path, off_set = 30):
    """
    答案数据合并, 思路可以借助题目文本合并的思路, 进行思考

    输入: 图像信息
    输出: 合并后的答案选项, 以及对应新坐标, 判断题这里虽然是A与B, 但是仅仅作为区分, 最终要看正确是否
    """

    # 提取坐标和文本信息, 方便之后进行对比
    texts = result[0]["rec_texts"]
    boxes = result[0]["rec_boxes"]

    # 获得图片的按钮位置
    option_rows = get_option_y(image_path=image_path)

    # 取到可能的y轴坐标, 防止系统出错, 所以要先进行排序操作
    option_rows.sort(key = lambda x: x["y"])


    # 先提取好y坐标
    option_y = []

    # 提取内容, 设计好items字典, 因为其实A, B, C, D四个选项不重要, 重要的是文本, 核心要做的是划区域
    # 既然提到了分组, 那最可能用的东西就是defaultdict
    items = defaultdict(list)
    
    # 取出y坐标, 方便后续进行操作
    for option in option_rows:

        option_y.append(option["y"])

    if len(option_y) < 2:
        return [], []

    # 列表进行配对, 防止出现越界
    option_y_row = list(zip(option_y[:-1], option_y[1:]))
    
    # 映射表
    labels = ["A", "B", "C", "D"]

    # 锁定文本对应选项
    for text, box in zip(texts, boxes):

        x1, y1, x2, y2 = box

        center_y = get_box_center_y(box=box)

        # 锁定文本位置, 这里只能匹配A, B, C三个选项的坐标, D选项需要自行添加
        for i, y in enumerate(option_y_row):
            
            if y[0] - off_set < center_y < y[1]:
                label = labels[i]
                items[label].append(
                    {
                        "text": text,
                        "coord": (x1, y1, x2, y2),
                        "center_y": center_y,
                    }
                )

        # 最后一个选项的文本信息
        if center_y > option_y_row[-1][1]:

            labels = ["A", "B", "C", "D"][:len(option_y)]
            last_label = labels[-1]

            items[last_label].append(
                    {
                        "text": text,
                        "coord": (x1, y1, x2, y2),
                        "center_y": center_y,
                    }
                )


    # 负责接收拼接好的坐标和文本信息
    combined_answer_texts = []
    combined_answer_coords = []

    # 长度其实只有4或者2
    for i in range(len(option_y)):

        label = labels[i]

        if not items[label]:
            combined_answer_texts.append("")
            combined_answer_coords.append(None)
            continue

        # 计算合并之后的坐标与文本
        combined_answer_text, combined_answer_coord = combine_text(items[label])

        combined_answer_texts.append(combined_answer_text)
        combined_answer_coords.append(combined_answer_coord)


    return combined_answer_texts, combined_answer_coords


def Lock_answer_position(combined_answer_texts, combined_answer_coords, image_path, off_set1 = 10, off_set2 = 10):
    """
    锁定答案的位置

    输入: 合并后的答案文本, 合并后的答案坐标, 原图像
    输出: 对应只有答案的文本以及坐标
    """

    answer_texts = []
    answer_coords = []

    # 取绿色像素的坐标
    green_labels = get_green_center_option_row(image_path=image_path)

    if not green_labels:
        return [], []

    green_labels.sort(key = lambda x: x)

    # 查找答案的文本
    for combined_answer_text, combined_answer_coord in zip(combined_answer_texts, combined_answer_coords):

        if combined_answer_coord is None:
            continue

        x1 ,y1, x2, y2 = combined_answer_coord[0], combined_answer_coord[1], combined_answer_coord[2], combined_answer_coord[3]

        # 遍历绿色坐标, 定位出答案位置
        for green_label in green_labels:
            
            if y1 - off_set1 < green_label < y2 + off_set2:
                answer_texts.append(combined_answer_text)
                answer_coords.append(combined_answer_coord)


    return answer_texts, answer_coords


@timer
def process_image(image_path):
    """
    提取核心文本数据

    输入: 原图像
    输出: 题目类型, 题目分值, 清洗后题干文本列表, 清洗后的答案文本列表
    """

    # 处理图片
    result = ocr.predict(str(image_path))

    # 目前只需要文本信息
    text = result[0]["rec_texts"]
    
    # 题目特性, 题目类型和分数必定在列表第一项和第二项
    question_type = text[0]
    score = text[1]

    # 提取题干文本
    combined_question_texts, _ = combine_question_data(result=result, image_path=image_path)
    combined_answer_texts, combined_answer_coords = combine_answer_data(result=result, image_path=image_path)

    locked_answer = Lock_answer_position(combined_answer_texts, combined_answer_coords, image_path)
    if not locked_answer:
        answer_texts = []
    else:
        answer_texts, _ = locked_answer

    # 数据清洗
    cleaned_question_texts = clean_data(combined_question_texts)
    cleaned_answer_texts = clean_data(answer_texts)

    return question_type, score, cleaned_question_texts, cleaned_answer_texts



@timer
def process_image_without_answer(image_path):
    """
    提取题干文本

    输入: 原图像
    输出: 题目类型, 题目分值, 清洗后题干文本列表
    """

    # 处理图片
    result = ocr.predict(str(image_path))

    # 目前只需要文本信息
    text = result[0]["rec_texts"]
    
    # 题目特性, 题目类型和分数必定在列表第一项和第二项
    question_type = text[0]
    score = text[1]

    # 提取题干文本
    combined_question_texts, _ = combine_question_data(result=result, image_path=image_path)
    
    # 数据清洗
    cleaned_question_texts = clean_data(combined_question_texts)

    return question_type, score, cleaned_question_texts


@timer
def get_question_parse(image_path):
    """
    填写题目的核心的数据结构, 核心就四个字段, 分数, 类型, 题目文本数据, 答案文本数据

    输入: 图像路径
    输出: 题目的数据结构
    """

    type, score, cleaned_question_texts, cleaned_answer_texts = process_image(image_path=image_path)
    question_data = parse_question(type, score, cleaned_question_texts, cleaned_answer_texts)

    return question_data
