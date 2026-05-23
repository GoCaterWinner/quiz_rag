"""
人工筛选过程, 防止题目出现错位等问题, 筛选下来的低质量数据, 进行人工筛查
"""

valid_types = {"单选题", "多选题", "判断题"}

# 答案验证集合, 筛选出有问题的答案, 可以进行人工筛选
def validate_question(question_data):
    """
    核心防止题目字段的错位问题

    输入: question_data的数据结构
    输出: 错误字典, 核心是看有没有错误, 如果没有错误, 最后判断一次id是否存在, 不存在就返回空列表, 表示没有错误即可
    """

    # 该数据结构用来存储错误类型
    errors = {
        "id" : "",
        "type_error" : "",
        "score_error" : "",
        "question_error" : [],
        "answer_error" : [],
    }
    
    if question_data["type"] not in valid_types:
        errors["type_error"] = "题目类型错误, 极可能出现错位现象"
        
    if question_data["score"] != "5分":
        errors["score_error"] = "分数错误, 只有5分的好吗!"

    if not question_data["question"]:
        errors["question_error"].append("题目出现空集合错误")

    if not question_data["answer"]:
        errors["answer_error"].append("答案出现空集合错误")

    if question_data["type"] in {"单选题", "判断题"} and len(question_data["answer"]) != 1:
        errors["answer_error"].append("单选题出现答案数目问题")

    if question_data["type"] == "多选题" and len(question_data["answer"]) == 1:
        errors["answer_error"].append("多选题出现答案数目问题")


    # 判断所有容器是否是空集, 如果是, 那么就不要给id赋值
    if all(not error for error in errors.values()):
        pass

    else:
        errors["id"] = str(question_data["id"])

    return errors

    
