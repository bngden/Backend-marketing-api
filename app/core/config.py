import os
from dotenv import load_dotenv

# Membaca file .env
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Marketing Automation API"
    
    # Mengambil variabel dari .env, jika tidak ada kembalikan string kosong
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    # FAL_API_KEY: str = os.getenv("FAL_API_KEY", "")
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    PHOTOROOM_API_KEY: str = os.getenv("PHOTOROOM_API_KEY", "")
    STABILITY_API_KEY: str = os.getenv("STABILITY_API_KEY", "")
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
    IG_USERNAME: str = os.getenv("IG_USERNAME", "")
    IG_PASSWORD: str = os.getenv("IG_PASSWORD", "")
    IG_USER_ID: str = os.getenv("IG_USER_ID", "")
    META_ACCESS_TOKEN: str = os.getenv("META_ACCESS_TOKEN", "")

    SECRET_KEY: str = "marketing_api_automation"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
# Inisialisasi object settings agar bisa di-import oleh file lain
settings = Settings()