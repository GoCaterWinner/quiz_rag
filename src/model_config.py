"""
模型下载配置。
"""

import os


DEFAULT_HF_ENDPOINT = "https://hf-mirror.com"


def configure_huggingface_mirror():
    """
    设置 Hugging Face 镜像源。

    如果外部已经设置了 HF_ENDPOINT，就尊重外部配置；否则默认使用
    hf-mirror.com，避免 SentenceTransformer 下载模型时直连 huggingface.co。
    """

    os.environ.setdefault("HF_ENDPOINT", DEFAULT_HF_ENDPOINT)
