from sqlalchemy.ext.asyncio import AsyncSession
from app.models.post import ScheduledPost, PostStatus
from app.schemas.post_schema import PostScheduleCreate
from app.schemas.generate_schema import GenerateStudioRequest
from app.services.ai_service import generate_aida_copywriting
from app.services.image_service import generate_product_image

# =====================================================================
# FUNGSI 1: STUDIO PINTAR (Dipanggil saat klik "Generate" di UI)
# =====================================================================
async def process_studio_generation(request: GenerateStudioRequest) -> dict:
    """
    🧑‍🍳 MANAJER 1: Meracik Caption dan mengedit Gambar, TAPI BELUM DISIMPAN ke DB.
    """
    print(f"🧑‍🍳 Studio Pintar mulai bekerja untuk kategori: {request.category}...")
    
    # 1. Gemini meracik Caption IG & Prompt Gambar Bahasa Inggris
    print("🧠 Gemini sedang meracik ide Copywriting & Prompt...")
    ai_brains = await generate_aida_copywriting(request.prompt_design, request.category)
    
    caption_text = ai_brains["caption"]
    image_prompt = ai_brains["image_prompt"]
    
    # 2. Qwen menyulap Base64 asli menjadi gambar studio pakai Prompt dari Gemini
    print("🎨 Qwen sedang melukis gambar estetik...")
    final_image_url = await generate_product_image(request.image_base64, image_prompt)

    print("✅ Studio Pintar selesai!")
    return {
        "caption": caption_text,
        "image_url": final_image_url
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
        platform=post_data.platform,
        category="Auto-Generated", # Otomatis karena dari AI Studio
        scheduled_time=post_data.scheduled_time.replace(tzinfo=None), # Hilangkan timezone agar aman di DB
        status=PostStatus.DRAFT,   # Sesuai kesepakatan: WAJIB DRAFT!
        user_id=user_id
    )
    
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    print("✅ Draft berhasil diamankan di Database!")
    return new_post