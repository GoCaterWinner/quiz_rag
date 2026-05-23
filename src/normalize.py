"""
数据清洗流程
"""

import unicodedata


def clean_text(text):
    if not text:
        return ""

    text = text.strip()
    text = unicodedata.normalize("NFKC", text)

    dirty_words = ["A", "B", "C", "D", "收起解析", "展开解析", "起解析", "纠错", "收藏"]

    for word in dirty_words:
        text = text.replace(word, "")

    return text.strip() # 防止去掉的是开头的数据



def clean_data(texts):
    cleaned_texts = []

    if not texts:
        return []

    for text in texts:
        text = clean_text(text)

        if not text:
            continue

        cleaned_texts.append(text)

    return cleaned_texts


