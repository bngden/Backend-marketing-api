from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.post import PostStatus

# 1. Base Schema: Kumpulan data inti yang pasti ada
class PostBase(BaseModel):
    original_image_url: str = Field(..., description="URL gambar asli produk yang diupload user")
    ai_generated_url: Optional[str] = Field(None, description="URL gambar hasil AI Fal.ai/Photoroom")
    caption_text: str = Field(..., description="Teks copywriting AIDA hasil generate Gemini")
    scheduled_at: datetime = Field(..., description="Tanggal dan jam postingan akan di-publish")

# 2. Schema Create: Format JSON yang kita HARAPKAN dari React saat user klik "Simpan Jadwal"
class PostCreate(PostBase):
    pass # Bentuknya sama persis dengan PostBase. Kita tidak minta ID karena ID dibuat otomatis oleh Database.

# 3. Schema Response: Format JSON yang akan kita KEMBALIKAN ke React (misal untuk halaman "Daftar Antrean Posting")
class PostResponse(PostBase):
    id: int
    status: PostStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Konfigurasi ajaib agar Pydantic bisa membaca data langsung dari objek SQLAlchemy (Database)
    class Config:
        from_attributes = True