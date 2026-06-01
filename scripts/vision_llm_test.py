from src.vision_llm_client import vision_llm
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]
image_path = base_dir / "screenshot" / "data" / "q151.png"

print(vision_llm(image_path=image_path))