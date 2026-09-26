"""数据目录与设置（base url / model id / api key）读写。"""
import json
import os
from pathlib import Path

from pydantic import BaseModel

# 项目根目录（backend/../）
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 数据目录：默认 <项目根>/data，可用环境变量覆盖
DATA_DIR = Path(os.environ.get("CRYPTO_AGENT_DATA_DIR", BASE_DIR / "data"))
SESSIONS_DIR = DATA_DIR / "sessions"
SETTINGS_FILE = DATA_DIR / "settings.json"


class Settings(BaseModel):
    base_url: str = ""          # OpenAI 兼容 API 地址，例如 https://api.deepseek.com/v1
    model_id: str = ""          # 模型 id，例如 deepseek-chat
    api_key: str = ""           # 模型 API Key
    cryptopanic_key: str = ""   # CryptoPanic 免费 API Key（可选，用于新闻工具）


def ensure_dirs() -> None:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def load_settings() -> Settings:
    ensure_dirs()
    if SETTINGS_FILE.exists():
        try:
            return Settings(**json.loads(SETTINGS_FILE.read_text(encoding="utf-8")))
        except Exception:
            return Settings()
    return Settings()


def save_settings(s: Settings) -> Settings:
    ensure_dirs()
    SETTINGS_FILE.write_text(
        json.dumps(s.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return s
