"""
构建向量索引
"""

from pathlib import Path
import json

from src.model_config import configure_huggingface_mirror

configure_huggingface_mirror()

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from src.jsonl_tools import read_jsonl



def get_question_text(question):
    """
    获得题干文本
    """
    if isinstance(question, list):
        return "".join(question)
    return question



def get_question_parse_data(question_bank):
    """
    取出question_bank中已经清洗好的数据

    输入: 已经清洗好的jsonl数据
    输出: 题干列表
    """

    questions = []

    for question_line in read_jsonl(question_bank):

        question = question_line["question"]
        
        if isinstance(question, list):
            # 将列表进行转换
            question = "".join(question)
            questions.append(question)

        else:
            questions.append(question)

    return questions


def get_meta_parse_data(question_bank):
    """
    取出meta数据
    """

    metas = []

    for question_line in read_jsonl(question_bank):

        metas.append(
            {
                "type" : question_line["type"],
                "score" : question_line["score"],
                "question" : get_question_text(question_line["question"]),
                "answer" : question_line["answer"],
                "id" : question_line["id"],
                "path" : question_line["path"],
            }
        )
    
    return metas


def main():
    
    # 文件路径
    BASE_DIR = Path(__file__).resolve().parents[1]
    QUESTION_DIR = BASE_DIR / "data" / "processed" / "question_bank.jsonl"
    INDEX_PATH = BASE_DIR / "indexes" / "question.faiss"
    META_PATH = BASE_DIR / "indexes" / "question_meta.json"

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 取出清洗好的数据
    questions = get_question_parse_data(QUESTION_DIR)

    # meta数据
    metas = get_meta_parse_data(QUESTION_DIR)
    
    # 创建词向量嵌入模型
    model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

    # 转向量, 并且归一化处理, 方便后面进行向量点积
    embedding = model.encode(
        questions,
        normalize_embeddings=True
    )

    # 转float32
    embedding = np.array(embedding).astype("float32")

    # 创建索引
    dim = embedding.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embedding)

    # 写入磁盘
    faiss.write_index(index, str(INDEX_PATH))

    # 将Meta数据写入磁盘
    META_PATH.write_text(
        json.dumps(metas, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


    print(f"题目数量: {len(metas)}")
    print(f"索引保存到: {INDEX_PATH}")
    print(f"元数据保存到: {META_PATH}")



if __name__ == "__main__":
    main()
