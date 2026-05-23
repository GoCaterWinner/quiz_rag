"""
后端
"""

# FastAPI用来创建实例, UploadFile用来上传文件的类型, File用来FastAPI, 这个文件来自文件上传表单
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
# shutil用于文件操作
import shutil
from src.ocr import get_question_parse
from src.answer_service import answer_from_image


# 创建FastAPI实例对象
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保文件路径存在
BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
FRONTEND_DIR = BASE_DIR / "frontend"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def root():
    """
    进入后端
    """
    return {
        "message" : "quiz rag backend is running",
    }



@app.get("/api/healthy")
def healthy_check():
    return {
        "status" : "ok",
    }



@app.post("/api/ocr")
def parse_image(file: UploadFile = File(...)):
    """
    上传图片, 保存到 data/uploads, 并返回 OCR 解析结果
    """

    save_path = UPLOAD_DIR / file.filename

    with save_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    question_data = get_question_parse(save_path)

    return {
        "image_name": file.filename,
        "image_saved_path": str(save_path),
        "image_type": file.content_type,
        "question_data": question_data,
    }



@app.post("/api/answer")
def answer_service(file: UploadFile = File(...)):
    """
    上传图片, 获取答案
    """

    save_path = UPLOAD_DIR / file.filename

    with save_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    answers = answer_from_image(save_path)

    return {
        "image_name": file.filename,
        "image_saved_path": str(save_path),
        "image_type": file.content_type,
        "answer_data": answers,
    }


app.mount("/ui", StaticFiles(directory=FRONTEND_DIR, html=True), name="ui")
