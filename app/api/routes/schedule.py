from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Import file-file buatan kita sebelumnya
from app.db.database import get_db
from app.models.post import ScheduledPost
from app.schemas.post_schema import PostCreate, PostResponse

# Inisialisasi Router khusus untuk fitur Scheduling
router = APIRouter()

# 1. Endpoint CREATE: Menerima data JSON dan menyimpannya ke Neon Database
# response_model=PostResponse akan otomatis menyaring data yang dikembalikan ke user
@router.post("/", response_model=PostResponse, status_code=201)
async def create_scheduled_post(post_data: PostCreate, db: AsyncSession = Depends(get_db)):
    # Pindahkan data dari Pydantic (post_data) ke SQLAlchemy Model (ScheduledPost)
    new_post = ScheduledPost(
        original_image_url=post_data.original_image_url,
        ai_generated_url=post_data.ai_generated_url,
        caption_text=post_data.caption_text,
        scheduled_at=post_data.scheduled_at
    )
    
    # Proses simpan ke database (Async)
    db.add(new_post)
    await db.commit()           # Simpan permanen
    await db.refresh(new_post)  # Ambil ulang datanya untuk mendapatkan ID otomatis
    
    return new_post

# 2. Endpoint READ: Mengambil semua daftar jadwal postingan
@router.get("/", response_model=list[PostResponse])
async def get_all_scheduled_posts(db: AsyncSession = Depends(get_db)):
    # Lakukan query SELECT * FROM scheduled_posts
    result = await db.execute(select(ScheduledPost))
    posts = result.scalars().all()
    
    return posts