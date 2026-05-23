"""
将提取到的数据做成json
"""

from pathlib import Path
from src.ocr import get_question_parse
import json


def main():

    # 文件路径
    base_dir = Path(__file__).resolve().parents[1]   

    # 图片位置
    image_dir = base_dir / "screenshot" / "data"
    
    # 输出路径
    output = base_dir / "data" / "raw" / "question.jsonl"
   
    # 对题目进行解析，获取题目到答案的数据结构
    images = sorted(image_dir.glob("q*.png"))

    if not images:
        raise ValueError(f"找不到对应的图片, 文件路径是:{image_dir}")

    # 打开输出路径jsonl文件, 负责写入
    with output.open("w", encoding="utf-8") as f:
        for image in images:
            question_data = get_question_parse(image_path=image)

            # 增加字段, 负责起到编号作用
            question_data["id"] = str(image.stem)
            question_data["path"] = str(image.relative_to(base_dir))

            # 转成json进行存储
            json_line = json.dumps(question_data, ensure_ascii=False)
            f.write(json_line + "\n")
            
            
if __name__ == "__main__":
    main()