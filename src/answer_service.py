"""
提取前端获得的截图, 然后提取题干信息, 最终返回结果是知识库里面的索引好的答案
"""

from src.ocr import process_image_without_answer
from src.vector_search import search_question

def answer_from_image(image_path):
    """
    根据提取到的截图, 调用process_image, 然后解析出题干信息, 返回最相似的三个答案

    输入: 图片路径
    输出: 返回的知识库中最相似的三个答案
    """

    # 返回questions列表
    _, _, questions = process_image_without_answer(image_path=image_path)

    # 返回搜索结果
    results = search_question(query=questions)


    return {
        "query" : "".join(questions),
        "matches" : results,
        "final_answer" : results[0]["answer"] if results else []
    }