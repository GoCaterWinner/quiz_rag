"""
负责对文本信息进行解析, 确定题目的数据结构
"""


def parse_question(type, score, cleaned_question_texts, cleaned_answer_texts):
    """
    对应题目的数据结构，题目总共有单选题, 多选题, 判断题
    """
 
    # 设计一个字典存储题目的键值对
    question_data = {}


    # 题目类型, 分数, 题干
    question_data["type"] = type
    question_data["score"] = score
    question_data["question"] = cleaned_question_texts
    question_data["answer"] = []

    # 填入答案文本
    for cleaned_answer_text in cleaned_answer_texts:
        question_data["answer"].append(cleaned_answer_text)

    print(question_data)

    return question_data

