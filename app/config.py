import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE_DIR / ".env")


def build_database_uri() -> str:
    direct_uri = os.getenv("DATABASE_URL")
    if direct_uri:
        return direct_uri

    mysql_host = os.getenv("MYSQL_HOST")
    mysql_database = os.getenv("MYSQL_DATABASE")
    if mysql_host and mysql_database:
        mysql_port = os.getenv("MYSQL_PORT", "3306")
        mysql_user = os.getenv("MYSQL_USER", "root")
        mysql_password = os.getenv("MYSQL_PASSWORD", "")
        return (
            f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/"
            f"{mysql_database}?charset=utf8mb4"
        )

    sqlite_path = (INSTANCE_DIR / "ai_learning_agent.db").as_posix()
    return f"sqlite:///{sqlite_path}"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    JSON_AS_ASCII = False
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = str(BASE_DIR / "logs")
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")
    GENERATED_FOLDER = str(BASE_DIR / "uploads" / "generated")
    REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    AI_PROVIDER = os.getenv("AI_PROVIDER", "mock")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    AI_REQUEST_TIMEOUT = int(os.getenv("AI_REQUEST_TIMEOUT", "30"))
    AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true"
    PROFILE_DIMENSIONS = [
        "knowledge_base",
        "cognitive_style",
        "learning_goal",
        "weak_points",
        "learning_pace",
        "interest_direction",
        "common_errors",
    ]
    PROFILE_DIMENSION_LABELS = {
        "knowledge_base": "知识基础",
        "cognitive_style": "认知风格",
        "learning_goal": "学习目标",
        "weak_points": "知识短板",
        "learning_pace": "学习节奏",
        "interest_direction": "兴趣方向",
        "common_errors": "易错点",
    }
    EBBINGHAUS_FACTORS = {
        0: 1.0,
        1: 0.92,
        3: 0.78,
        7: 0.55,
        14: 0.38,
        21: 0.26,
    }
    RESOURCE_TYPES = [
        "course_document",
        "mind_map",
        "quiz_bank",
        "video_script",
        "code_example",
        "ppt_outline",
    ]

