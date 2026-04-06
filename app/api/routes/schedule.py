from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.post import ScheduledPost, PostStatus
from app.schemas.post_schema import PostScheduleCreate, PostScheduleUpdate
from app.services.post_service import create_draft_post

router = APIRouter()

# =====================================================================
# 1. CREATE: Simpan Hasil Generate ke Draft
# =====================================================================
@router.post("/")
async def create_schedule(
    post_data: PostScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        new_post = await create_draft_post(db, current_user.id, post_data)
        return {
            "status": "success",
            "message": "✅ Postingan berhasil disimpan sebagai DRAFT!",
            "data": {
                "id": new_post.id,
                "title": new_post.title,
                "scheduled_time": new_post.scheduled_time,
                "platform": new_post.platform
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan draft: {str(e)}")

# =====================================================================
# 2. READ: Ambil Semua Daftar Jadwal & Draft (Untuk Tampilan Card UI)
# =====================================================================
@router.get("/")
async def get_all_schedules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Ambil semua postingan milik user yang sedang login, urutkan dari yang terbaru
        result = await db.execute(
            select(ScheduledPost)
            .filter(ScheduledPost.user_id == current_user.id)
            .order_by(ScheduledPost.scheduled_time.desc())
        )
        posts = result.scalars().all()
        return {"status": "success", "data": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data jadwal: {str(e)}")

# =====================================================================
# 3. UPDATE: Edit Draft (Judul, Caption, Tanggal)
# =====================================================================
@router.put("/{post_id}")
async def update_schedule(
    post_id: int,
    post_data: PostScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(ScheduledPost).filter(ScheduledPost.id == post_id, ScheduledPost.user_id == current_user.id)
    )
    db_post = result.scalar_one_or_none()

    if not db_post:
        raise HTTPException(status_code=404, detail="Draft tidak ditemukan!")
    if db_post.status != PostStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Hanya status DRAFT yang bisa diedit!")

    # Update data opsional
    if post_data.title is not None:
        db_post.title = post_data.title
    if post_data.caption is not None:
        db_post.caption = post_data.caption
    if post_data.scheduled_time is not None:
        db_post.scheduled_time = post_data.scheduled_time.replace(tzinfo=None)

    await db.commit()
    await db.refresh(db_post)

    return {"status": "success", "message": "✅ Draft berhasil diperbarui!", "data": db_post}

# =====================================================================
# 4. DELETE: Buang Draft ke Tempat Sampah
# =====================================================================
@router.delete("/{post_id}")
async def delete_schedule(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(ScheduledPost).filter(ScheduledPost.id == post_id, ScheduledPost.user_id == current_user.id)
    )
    db_post = result.scalar_one_or_none()

    if not db_post:
        raise HTTPException(status_code=404, detail="Draft tidak ditemukan!")

    await db.delete(db_post)
    await db.commit()

    return {"status": "success", "message": "🗑️ Draft berhasil dihapus!"}