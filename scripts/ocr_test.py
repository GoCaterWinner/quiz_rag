"""
OCR测试脚本

负责提取单张题目的截图，识别文本，清洗文本，并且解析成题目的结构
"""


from pathlib import Path
from src.ocr import get_question_parse      
from scripts import build_question_jsonl


# 测试
if __name__ == "__main__":
  
   # 定位到根目录
    base_dir = Path(__file__).resolve().parents[1]

    image_dir = base_dir/"screenshot"/"data"/"q049.png"
    
    question_data = build_question_jsonl(image_dir)


    
    








