from pathlib import Path
import json
import os

from src.model_config import configure_huggingface_mirror

configure_huggingface_mirror()

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 模型
MODEL_NAME = "BAAI/bge-small-zh-v1.5"

# 几个文件的地址
BASE_DIR = Path(__file__).resolve().parents[1]
META_DIR = BASE_DIR / "indexes" / "question_meta.json"
INDEX_DIR = BASE_DIR / "indexes" / "question.faiss"


def _set_env(name, value):
    """
    恢复或者设置环境变量
    """
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value


def load_embedding_model_from_cache():
    """
    只从本地缓存加载模型，不触发 Hugging Face 远端检查。
    """

    old_hf_offline = os.environ.get("HF_HUB_OFFLINE")
    old_transformers_offline = os.environ.get("TRANSFORMERS_OFFLINE")

    # 临时将环境变量设置为1
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    try:
        try:
            # 新版本是可支持local_files_only进行离线查询, 如果本地没有, 就报错
            return SentenceTransformer(MODEL_NAME, local_files_only=True)
        except TypeError:
            # 兼容不支持 local_files_only 参数的旧版 sentence_transformers。
            return SentenceTransformer(MODEL_NAME)
    finally:
        # 把环境变量恢复回来
        _set_env("HF_HUB_OFFLINE", old_hf_offline)
        _set_env("TRANSFORMERS_OFFLINE", old_transformers_offline)


def load_embedding_model():
    """
    优先使用本地缓存中的模型，避免每次启动都联网检查。

    如果本地还没有缓存，才回退到默认联网下载逻辑；下载完成后，
    后续启动会走 local_files_only=True 的本地加载路径。
    """

    try:
        return load_embedding_model_from_cache()
    except Exception as cache_error:
        try:
            return SentenceTransformer(MODEL_NAME)
        except Exception as download_error:
            raise RuntimeError(
                f"目前出现了联网异常{MODEL_NAME}"
            ) from download_error


model = load_embedding_model()


# 提取已经存储好的索引信息
index = faiss.read_index(str(INDEX_DIR))

# 读取meta
metas = json.loads(META_DIR.read_text(encoding="utf-8"))


def question_embedding(question, model):
    """
    负责将输入的问题数据, 转换成词向量

    输入: 问题,
    输出: 转换后的词向量
    """

    # 可能会传进来列表, 要先进行转换
    if isinstance(question, list):
        question = "".join(question)

    embedding = model.encode(
        [question],
        normalize_embeddings=True
    )

    return embedding


def search_question(query, top_k=3):

    embedding = question_embedding(query, model)
    embedding = np.array(embedding).astype("float32")


    # 计算评分
    scores, indices = index.search(embedding, top_k)

    results = []

    for score, tip in zip(scores[0], indices[0]):

        if tip == -1:
            continue

        # 确定下标
        meta = metas[tip]   
        results.append(
            {
                "type" : meta["type"],
                "score" : meta["score"],
                "question": meta["question"],
                "answer" : meta["answer"],
                "confidence": float(score),
                "id": meta["id"],
                "path": meta["path"],
            }
        )

    return results
