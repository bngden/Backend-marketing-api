from sqlalchemy.ext.asyncio import AsyncSession
from app.models.post import ScheduledPost, PostStatus
from app.schemas.post_schema import PostScheduleCreate
from app.schemas.generate_schema import GenerateStudioRequest
from app.services.ai_service import generate_aida_copywriting
from app.services.image_service import generate_product_image
from app.services.video_service import generate_video_from_image

# =====================================================================
# FUNGSI 1: STUDIO PINTAR (Dipanggil saat klik "Generate" di UI)
# =====================================================================
async def process_studio_generation(request: GenerateStudioRequest) -> dict:
    """
    🧑‍🍳 MANAJER 1: Meracik Caption, Gambar, dan VIDEO (Jika diminta).
    """
    tipe_media = request.media_type.lower() if hasattr(request, 'media_type') and request.media_type else "image"
    print(f"🧑‍🍳 Studio Pintar mulai bekerja untuk kategori: {request.category} (Target: {tipe_media.upper()})...")
    
    # 1. Gemini meracik Caption IG, Prompt Gambar & Prompt Video
    print("🧠 Gemini sedang meracik ide Copywriting & Prompt...")
    ai_brains = await generate_aida_copywriting(request.prompt_design, request.category)
    
    # 2. Qwen menyulap Base64 asli menjadi gambar studio
    print("🎨 Qwen sedang melukis gambar estetik...")
    final_image_url = await generate_product_image(request.image_base64, ai_brains["image_prompt"])

    # 3. Persimpangan Jalan (Apakah User Minta Video?)
    if tipe_media == "video":
        print("🎬 Magic Hour sedang menganimasikan gambar menjadi video...")
        video_prompt = ai_brains.get("video_prompt", "subtle cinematic motion, hyper-realistic")
        final_video_url = await generate_video_from_image(final_image_url, video_prompt)
        
        print("✅ Studio Pintar (Video) selesai!")
        return {
            "format": "video",
            "caption": ai_brains["caption"],
            "image_url": final_image_url,
            "video_url": final_video_url
        }
    else:
        print("✅ Studio Pintar (Gambar) selesai!")
        return {
            "format": "image",
            "caption": ai_brains["caption"],
            "image_url": final_image_url,
            "video_url": None
        }

# =====================================================================
# FUNGSI 2: SIMPAN DRAFT (Dipanggil saat klik "Simpan/Posting" di UI)
# =====================================================================
async def create_draft_post(db: AsyncSession, user_id: int, post_data: PostScheduleCreate) -> ScheduledPost:
    """
    🗂️ MANAJER 2: Menerima hasil final dari Frontend dan menyimpannya ke Kulkas (Database) sbg DRAFT.
    """
    print(f"🗂️ Menyimpan konten '{post_data.title}' ke dalam Draft...")
    
    new_post = ScheduledPost(
        title=post_data.title,
        caption=post_data.caption,
        image_url=post_data.image_url,
        
        # 👇 TAMBAHKAN INI NANTI JIKA DATABASE ANDA SUDAH DI-MIGRASI
        # video_url=post_data.video_url, 
        
        platform=post_data.platform,
        category="Auto-Generated", 
        scheduled_time=post_data.scheduled_time.replace(tzinfo=None), 
        status=PostStatus.DRAFT,   
        user_id=user_id
    )
    
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    print("✅ Draft berhasil diamankan di Database!")
    return new_post