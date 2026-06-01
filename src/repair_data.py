"""
cascade repair

对于单纯的错误数据, 人工清洗十分复杂, 可能需要多级规则进行级联修复

一级规则: 判断type错误, 如果是type错误进行自动修复(预计可修复70%+的文本错误)
二级规则: 启动视觉LLM进行自动修复错误字段(gpt-5.5, gpt-5.4, gpt-5.4-mini, gemini 3.5-flash)(预计可修复剩下的99%+)
三级规则: 启动文本LLM修复常规语病错误(deepseek v4-flash)(预计可完全修复)
四级规则: 人工审阅
"""
import json
from src.jsonl_tools import write_jsonl, read_jsonl
from pathlib import Path
# 利用默认字典进行错误字体统计, 后期两个用途, 1.作为映射 2. 提供给LLM, 让其判断错误映射概率
from collections import defaultdict
from src.validate_v2 import validate_question
from typing import Callable
from src.vision_llm_client import vision_llm

# 文件地址
BASE_DIR = Path(__file__).resolve().parents[1]
QUESTION_REVIEW_PATH = BASE_DIR / "data" / "review" / "question_review.jsonl"
MAPPINGTABLE_PATH = BASE_DIR / "config" / "type_alias.json"

# LLM修复地址
QUESTION_REVIEW_ON_LLM = BASE_DIR / "data" / "review" / "question_review_on_llm.jsonl"



def load_type_alias(path: Path) -> dict[str, str]:
    """
    读取映射表文件
    """
    return json.loads(path.read_text(encoding="utf-8"))



def write_type_alias(file, path = MAPPINGTABLE_PATH):
    """
    功能: 写入固定路径(并且不删除之前的内容)

    输入: 写入内容, 写入路径
    输出: 转成json送入文件
    """

    with path.open("a", encoding="utf-8") as f:
        file_json = json.dumps(file, ensure_ascii=False)

        f.write(file_json)



def make_type_updater(fixed_type: str):
    """
    做闭包的用途
    """
    def update_data(item: dict) -> dict:
        """
        修复字段
        """

        item["type"] = fixed_type

        return item
    
    return update_data


def update_jsonl_by_id(path: Path, target_id: dict[str, str], updater: Callable[[dict], dict]) -> bool:
    """
    更新原文件内容

    输入: 文件路径, 待修改的id, 修改器启动修改功能
    输出: 根据记录是否被修改输出bool值
    """

    updated = False

    temp_path = path.with_suffix(path.suffix + ".tmp")

    with path.open("r", encoding="utf-8") as p, temp_path.open("w", encoding="utf-8") as tp:

        for line in p:

            if not line.strip():
                continue

            # 转成字典
            item = json.loads(line)
            item_id = item.get("id")

            if item_id in target_id:
                item["type"] = target_id[item_id]
            

            # 更新状态
            updated = True

            tp.write(json.dumps(item, ensure_ascii=False) + "\n")

    temp_path.replace(path)

    return updated


def cascade_repair_on_rule(path_mappingtable: Path = MAPPINGTABLE_PATH, path_question_review: Path = QUESTION_REVIEW_PATH) -> None:
    """
    一级规则, 基于errors的类型, 修复错误, 核心修复type问题(占比最大)

    输出: 数据, 问题类型, 映射表文件
    输出: 经过一级规则修复后的数据
    """ 

    # 映射表, 负责之后传入数据后进行映射
    mapping_dict = {}
    
    expected = ""

    for question_data in read_jsonl(path=path_question_review):

        # 统计错误类型
        errors_data = validate_question(question_data=question_data)


        # 没有错误直接跳过这一个数据修复
        if errors_data["is_valid"] == True:
            continue 
        
        # 存在错误, 核心修复type的错误字段
        else:
            errors = errors_data["errors"]

            for error in errors:

                if error["field"] == "type":

                    if len(error["expected"]) == 1:

                        # id列表进行存储
                        mapping_dict[question_data["id"]] = error["expected"][0]
                        # 全局变量进行记录
                        expected = error["expected"]


    # 进行修改, 遍历到对应ID位置, 进行修改
    updated = update_jsonl_by_id(path_question_review, target_id=mapping_dict, updater=make_type_updater(expected))                   

    return 


def cascade_repair_on_llm(path: Path = QUESTION_REVIEW_PATH) -> None:
    """
    在第一次修复无果后, 调用具有多模态能力的LLM进行图像再次识别, 输出对应格式

    调用GPT-5.5, 进行识别, 输出结果按照固定格式进行修复

    输入: 修复前的文档, 主要提供错误的图片
    输出: LLM执行修复流程
    """

    # 待修复的图片
    image_on_repair_list = []
    # 先清空上次内容
    QUESTION_REVIEW_ON_LLM.write_text("", encoding="utf-8")

    for question_review in read_jsonl(path=path):
        # 获取图片路径
        image_on_repair_list.append(question_review.get("path"))

    # 交给LLM进行执行修复流程
    for image in image_on_repair_list:
        # 拼接图片路径
        image_path = BASE_DIR / image

        # 记录下修复结果
        result = vision_llm(image_path=image_path)

        # 将json转换成字典格式
        result = json.loads(result)

        pid = Path(image).stem

        result["id"] = pid
        result["path"] = image

        write_jsonl(result, path=QUESTION_REVIEW_ON_LLM)

        
    # 再将修好的内容送回
    QUESTION_REVIEW_ON_LLM.replace(path)

    return



def cascade_repair(question_data: dict, errors: dict, path: Path) -> None:
    """
    总框架, 基于一级, 二级规则进行多方面修复数据

    输入: 待修复数据, 错误原因, 映射表文件
    输出: 修复后的数据
    """
    cascade_repair_on_rule()
    cascade_repair_on_llm()


def main():
    path_question_review = BASE_DIR / "data" / "review" / "question_review_test.jsonl"
    cascade_repair_on_rule(path_question_review=path_question_review)