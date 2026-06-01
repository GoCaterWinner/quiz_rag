"""
调用视觉LLM, 在第二级修复中, 进行修复内容, 从而进行二次数据恢复
"""

from pathlib import Path
import base64
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

# 引入环境变量
load_dotenv()

# prompt地址
BASE_DIR = Path(__file__).resolve().parents[1]
PROMPT_PATH = BASE_DIR / "config" / "check_prompt"


# 实例化模型
CLIENT = OpenAI(
    api_key= os.environ.get("VISION_LLM_API_KEY"),
    base_url=os.environ.get("VISION_LLM_BASE_URL")
)


def image_to_base64(image_path: Path) -> str:
    """
    将图片类型进行转换

    输入: 图片路径
    输出: data URL格式
    """

    # 读取二进制内容
    image_bytes = image_path.read_bytes()

    # 转换
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    # 获得image_type
    image_suffix = image_path.suffix.lower()

    # 如果是在jpg或者jpeg的格式, 修改成jpeg的, 其余的全部设定成png的
    if image_suffix in {".jpg", ".jpeg"}:
        image_type = "jpeg"
    elif image_suffix == ".png":
        image_type = "png"
    else:
        raise ValueError(f"不支持的图片格式类型{image_suffix}")


    return f"data:image/{image_type};base64,{encoded}"



def vision_llm(image_path: Path, prompt_path: Path = PROMPT_PATH) -> str:
    """
    调用视觉LLM, 重新提取图片语言信息

    输入: 对应图片的路径, 提示词路径
    输出: 对应提取后提示词
    """

    # 读取提示词内容
    prompt = prompt_path.read_text(encoding="utf-8")

    # 图片格式转换
    image_url = image_to_base64(image_path=image_path)

    response = CLIENT.chat.completions.create(
        model= os.environ.get("VISION_LLM_MODEL"),
        messages=[
            {"role":"system", "content":"你是一个题目内容的提取者，你根据题目内容进行提取"},
            {"role":"user", "content":[
                {
                    "type" : "text", "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {"url": image_url},
                },
            ]
            },

        ],
        stream=False,
    )

    return response.choices[0].message.content
