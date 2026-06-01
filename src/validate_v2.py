"""
人工筛选过程, 防止题目出现错位等问题, 筛选下来的低质量数据, 进行人工筛查
"""

from pathlib import Path
import json
from src.jsonl_tools import read_jsonl, write_jsonl


valid_types = {"单选题", "多选题", "判断题"}

# 答案验证集合, 筛选出有问题的答案, 可以进行人工筛选
def validate_question(question_data):
    """
    核心防止题目字段的错位问题

    输入: question_data的数据结构
    输出: 错误字典, 核心是看有没有错误, 如果没有错误, 最后判断一次id是否存在, 不存在就返回空列表, 表示没有错误即可

    "errors"核心存入:
            {
                "field" : "",
                "code" : "",
                "message" : "",
                "expected" : [],
                "repairable" : bool,
            }
    """
    # 该数据结构用来存储错误类型, 方便后续进行LLM作为prompt
    errors = []

    errors_data = {
        "id" : question_data["id"],
        "path" : question_data["path"],
        "errors" : errors,
        "is_valid" : True
    }

    # type字段问题   
    if question_data["type"] not in valid_types:

        errors_data["is_valid"] = False

        if "题" in question_data["type"]:

            type_error = {
                "field": "type",
                "code": "incomplete_type",
                "message": "题目类型的字段信息不完整, 需进行补全",
                "value": question_data["type"],
                "expected": ["判断题", "单选题", "多选题"],
                "repairable": True,
            }

            errors.append(type_error)

            if question_data["question"] and question_data["answer"] and question_data["score"] == "5分":
                if len(question_data["answer"]) > 1:
                    errors[0]["expected"] = ["多选题"]

                if len(question_data["answer"]) == 1:
                    if question_data["answer"] in [["正确"], ["错误"]]:
                        errors[0]["expected"] = ["判断题"]

                    else:
                        errors[0]["expected"] = ["单选题"]

        else:
            
            type_error = {
                "field": "type",
                "code": "invalid_type",
                "message": "题目类型字段错误, 无法通过规则自动判断",
                "value": question_data["type"],
                "expected": ["判断题", "单选题", "多选题"],
                "repairable": False,
            }

            errors.append(type_error)

    
    # score字段问题
    if question_data["score"] != "5分":

        errors_data["is_valid"] = False

        score_error = {
            "field": "score",
            "code": "invalid_score",
            "message": "分数字段错误, 当前只接受5分题目",
            "value": question_data["score"],
            "expected": ["5分"],
            "repairable": False,
        }

        errors.append(score_error)

    # question错误
    if not question_data["question"]:

        errors_data["is_valid"] = False

        question_error = {
                "field" : "question",
                "code" : "question_gap",
                "message" : "题目内容缺失, 你要做的是根据我给你的图片, 重新提取题目信息, 输出是字符串的格式",
                "value": question_data["question"],
                "expected" : ["题目内容存在"],
                "repairable" : True,
            }

        errors.append(question_error)

    # answer错误
    if not question_data["answer"]:

        errors_data["is_valid"] = False

        answer_error = {
                    "field" : "answer",
                    "code" : "answer_gap",
                    "message" : "答案内容缺失, 你要做的是根据我给你的图片, 重新提取答案信息, 答案存在于每个“绿色按钮”右边,输出是字符串的格式,如果是多选题,请在每一题之间用/进行分隔",
                    "value" : question_data["answer"],
                    "expected" : ["答案内容存在"],
                    "repairable" : True,
                }
        errors.append(answer_error)

    # 判断答案数量
    if question_data["answer"]:

        if question_data["type"] in {"单选题", "判断题"} and len(question_data["answer"]) != 1:

            errors_data["is_valid"] = False

            answer_error = {
                    "field" : "answer",
                    "code" : "answer_number_error",
                    "message" : "答案数目错误",
                    "value" : question_data["answer"],
                    "expected" : ["答案数量只有一个"],
                    "repairable" : True,
                }
            errors.append(answer_error)


        if question_data["type"] == "多选题" and len(question_data["answer"]) == 1:

            errors_data["is_valid"] = False

            answer_error = {
                    "field" : "answer",
                    "code" : "answer_number_error",
                    "message" : "答案数目错误",
                    "value" : question_data["answer"],
                    "expected" : ["答案数量有多个"],
                    "repairable" : True,
                }
            errors.append(answer_error)


    # 只有存在错误, 再填入这些信息
    if errors:
        errors_data["is_valid"] = False
    
    return errors_data
