"""
进行得到的初始数据, 对其进行验证环节, 判断数据是否错位等

raw: 存放原始数据
review: 存放待修改的数据
processed: 存放合格的数据
"""


from pathlib import Path
import json

from src.validate import validate_question
from src.jsonl_tools import read_jsonl, write_jsonl

def main():
    """
    进行数据验证
    """

    # 设置文件路径
    base_dir = Path(__file__).resolve().parents[1]
    raw_data = base_dir / "data" / "raw" / "question.jsonl"
    review_data = base_dir / "data" / "review" / "question_review.jsonl"
    processed_data = base_dir / "data" / "processed" / "question_bank.jsonl"

    # 健壮性判断
    review_data.parent.mkdir(parents=True, exist_ok=True)
    processed_data.parent.mkdir(parents=True, exist_ok=True)

    # 清空上一次的结果
    review_data.write_text("", encoding="utf-8")
    processed_data.write_text("", encoding="utf-8")

    # 分区域存储, 没问题的存储到question_bank区域, 有问题的存储到question_review区域
    for raw_line in read_jsonl(raw_data):
        errors = validate_question(raw_line)

        if errors["id"]:
            # 增加字段
            errors["path"] = raw_line["path"]

            write_jsonl(errors, review_data)     
                
        else:
         
            write_jsonl(raw_line, processed_data)


if __name__ == "__main__":
    main()