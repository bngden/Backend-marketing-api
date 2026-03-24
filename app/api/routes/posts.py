from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

# --- IMPORT KOKI KITA ---
from app.services.post_service import create_and_schedule_post

router = APIRouter()

@router.post("/schedule")
async def schedule_instagram_post(
    product_name: str = Form(...),
    product_description: str = Form(...),
    category: str = Form(..., description="Pilih: makanan, kosmetik, fashion, elektronik"),
    scheduled_time: str = Form(..., description="Format: YYYY-MM-DD HH:MM:SS"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # 🔐 WAJIB BAWA TIKET LOGIN!
):
    try:
        # 1. Baca file gambar yang diupload user
        image_bytes = await file.read()
        
        # 2. Lempar semua bahan masakan ke Dapur (Service)
        new_post = await create_and_schedule_post(
            db=db,
            user_id=current_user.id,
            product_name=product_name,
            product_description=product_description,
            category=category,
            scheduled_time_str=scheduled_time,
            image_bytes=image_bytes
        )

        # 3. Berikan struk bukti jadwal ke user
        return {
            "status": "success",
            "message": "✅ Postingan berhasil diracik AI dan dijadwalkan!",
            "post_id": new_post.id,
            "scheduled_time": new_post.scheduled_time,
            "preview_image": new_post.image_url
        }

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Gagal menjadwalkan postingan: {str(e)}")