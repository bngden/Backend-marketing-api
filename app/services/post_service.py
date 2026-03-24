from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


from app.models.post import ScheduledPost, PostStatus
from app.services.ai_service import generate_aida_copywriting
from app.services.image_service import generate_product_image

async def create_and_schedule_post(
    db: AsyncSession,
    user_id: int,
    product_name: str,
    product_description: str,
    category: str,
    scheduled_time_str: str,
    image_bytes: bytes
) -> ScheduledPost:
    """
    🧑‍🍳 KOKI DAPUR: Menerima pesanan, menyuruh AI memasak, lalu menyimpan ke kulkas (Database).
    """
    print(f"🧑‍🍳 Koki mulai meracik konten AI untuk produk: {product_name}...")
    
    # 1. Konversi format waktu ke zona waktu kita (WIB / Asia/Jakarta)
    target_time = datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M:%S")

    # 2. PROSES AI BEKERJA (Copywriting + Image Generator)
    print("🧠 Gemini sedang menulis Caption AIDA...")
    copywriting_result = await generate_aida_copywriting(product_name, product_description)
    
    print("🎨 Qwen sedang membuat Poster Estetik...")
    image_url_result = await generate_product_image(image_bytes, user_prompt=f"Promo {product_name}", category=category)

    # 3. SIMPAN MASAKAN KE KULKAS (Database Neon)
    new_post = ScheduledPost(
        product_name=product_name,
        category=category,
        image_url=image_url_result,
        copywriting=copywriting_result,
        scheduled_time=target_time,
        status=PostStatus.SCHEDULED,
        user_id=user_id
    )
    
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    print("✅ Konten siap! Sudah dijadwalkan di Database.")
    return new_post