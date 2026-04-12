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
        target_platforms = []

        # LOGIKA DETEKSI PLATFORM YANG SANGAT FLEKSIBEL
        if isinstance(post_data.platform, list):
            # Jika Frontend mengirim Array: ["Instagram", "Facebook"]
            target_platforms = post_data.platform
        else:
            # Jika Frontend mengirim String text biasa
            plat_str = post_data.platform.strip().lower()
            if plat_str in ["all", "semua", "semua platform", "All" , "ALL"]:
                target_platforms = ["Instagram", "Facebook", "Telegram"]
            elif "," in plat_str:
                target_platforms = [p.strip() for p in plat_str.split(",")]
            else:
                target_platforms = [post_data.platform]

        saved_posts = []

        # Looping Kloning Data ke Database sesuai jumlah platform yang dipilih
        for plat in target_platforms:
            clean_plat_name = plat.capitalize()
            post_data.platform = clean_plat_name 
            
            # Panggil service untuk menyimpan ke database
            new_post = await create_draft_post(db, current_user.id, post_data)
            
            # 👇 INI DIA YANG KETINGGALAN! 👇
            saved_posts.append({
                "id": new_post.id,
                "title": new_post.title,
                "platform": new_post.platform,
                "scheduled_time": new_post.scheduled_time,
                "image_url": new_post.image_url,  # <-- SUDAH KEMBALI!
                "video_url": new_post.video_url   # <-- SUDAH KEMBALI!
            })

        return {
            "status": "success",
            "message": f"✅ {len(saved_posts)} Postingan berhasil dipecah & disimpan sebagai DRAFT!",
            "data": saved_posts
        }
    except Exception as e:
        import traceback
        print(traceback.format_exc())
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
# 3. UPDATE: Edit Draft & Aktifkan Jadwal (Trigger Robot)
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
        raise HTTPException(status_code=404, detail="Data tidak ditemukan!")
        
    # Perbaikan Logika: Boleh mengedit asalkan belum PUBLISHED (biar kalau ada typo sebelum tayang bisa diedit)
    if db_post.status == PostStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Postingan yang sudah tayang tidak bisa diedit!")

    # Update data opsional
    if post_data.title is not None:
        db_post.title = post_data.title
    if post_data.caption is not None:
        db_post.caption = post_data.caption
    if post_data.scheduled_time is not None:
        db_post.scheduled_time = post_data.scheduled_time.replace(tzinfo=None)
        
    # --- TAMBAHAN BARU UNTUK MENDUKUNG VIDEO & STATUS ROBOT ---
    if hasattr(post_data, 'image_url') and post_data.image_url is not None:
        db_post.image_url = post_data.image_url
    if hasattr(post_data, 'video_url') and post_data.video_url is not None:
        db_post.video_url = post_data.video_url
        
    # KUNCI UTAMA: Mengubah DRAFT menjadi SCHEDULED agar dieksekusi robot
    if hasattr(post_data, 'status') and post_data.status is not None:
        db_post.status = post_data.status

    await db.commit()
    await db.refresh(db_post)

    return {"status": "success", "message": "✅ Jadwal berhasil diperbarui!", "data": db_post}

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

    return {"status": "success", "message": "🗑️ Data berhasil dihapus!"}
