"""
将第一轮不合格的数据进行多次识别处理, 从而降低错误率, 方便后续人工进行修改

核心根据准确率和给定循环次数, 进行多轮迭代
"""

from pathlib import Path
from src.ocr import get_question_parse
from src.jsonl_tools import read_jsonl, write_jsonl, jsonl_count
from src.validate_v2 import validate_question
from src.repair_data import cascade_repair_on_rule, cascade_repair_on_llm


# 几个地址
BASE_DIR = Path(__file__).resolve().parents[1]
JSON_TEMPORARY_PATH = BASE_DIR / "data" / "review" / "question_temporary_reviewed.jsonl"
JSON_PATH = BASE_DIR / "data" / "review" / "question_review.jsonl"
JSON_TARGET_PATH = BASE_DIR / "data" / "processed" / "question_bank.jsonl"
IMAGE_DIR = BASE_DIR / "screenshot" / "data"
JSON_TEMPORARY_PATH.parent.mkdir(parents=True, exist_ok=True)
JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
JSON_TARGET_PATH.parent.mkdir(parents=True, exist_ok=True)



def loop_screening(question_review: Path = JSON_PATH, target_count = 20, loop_count: int = 1) -> None:
    """
    对问题数据进行重新筛查, 可以设置循环数目, 以及准确率报告

    输入: 问题数据, 目标最终剩下的错误个数, 循环次数
    输出: 最终的结果
    """ 

    if loop_count == 0:
        cascade_repair_on_llm(path=question_review)

        # validate LLM 修复结果
        JSON_TEMPORARY_PATH.write_text("", encoding="utf-8")

        for question_data in read_jsonl(question_review):
            errors = validate_question(question_data)

            if errors["is_valid"]:
                write_jsonl(question_data, JSON_TARGET_PATH)
            else:
                write_jsonl(question_data, JSON_TEMPORARY_PATH)

        question_review.write_text("", encoding="utf-8")

        for review_data in read_jsonl(JSON_TEMPORARY_PATH):
            write_jsonl(review_data, question_review)

        return
    # 只要在循环次数大于等于1时候, 才能执行这个循环
    if loop_count >= 1:

        # 进行第一级修复
        cascade_repair_on_rule(path_question_review=question_review)

        id_dir = []

        # 记录下当前有问题的图片的序号
        for review_line in read_jsonl(question_review):
            id_dir.append(review_line["id"])

        # 统计总错误数目
        error_count = jsonl_count(question_review)

        # 目前的错误数目
        current_error_count = error_count

        if current_error_count <= target_count:
            return 

        # 只有在达到准确率前才会执行循环
        if current_error_count > target_count:

            JSON_TEMPORARY_PATH.write_text("", encoding="utf-8")

            # OCR识别结果可能每次不同, 对错误结果再次识别
            for id in id_dir:
                question_data = get_question_parse(IMAGE_DIR / f"{id}.png")
                question_data["id"] = id
                question_data["path"] = str((IMAGE_DIR / f"{id}.png").relative_to(BASE_DIR))

                errors = validate_question(question_data=question_data)

                # 待填入效果, 进行字段修复            

                if not errors["is_valid"]:
                    # 内容不可靠, 写入临时区域, 方便下一次递归迁移
                    write_jsonl(question_data, path=JSON_TEMPORARY_PATH)

                if errors["is_valid"]:
                    # 如果内容可靠, 将结果写入目标区域         
                    write_jsonl(question_data, JSON_TARGET_PATH)

                # 计算一次错误数目
                current_error_count = jsonl_count(JSON_TEMPORARY_PATH)

            # 将新数据写入原来的question_review.jsonl
            JSON_PATH.write_text("", encoding="utf-8")

            for review_data in read_jsonl(JSON_TEMPORARY_PATH):
            
                write_jsonl(review_data, question_review)


            loop_screening(question_review, target_count, loop_count = loop_count - 1)



def main():
    loop_screening()

if __name__ == "__main__":
    main()
