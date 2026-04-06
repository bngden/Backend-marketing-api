import httpx
import asyncio
from app.core.config import settings

async def post_to_instagram(image_url: str, caption: str) -> bool:
    """
    Jalur Resmi Meta untuk Akun Bisnis/Kreator (Developer Mode).
    Membutuhkan IG_USER_ID dan META_ACCESS_TOKEN di file .env.
    """
    # Mengambil token dari sistem environment
    ig_user_id = getattr(settings, "IG_USER_ID", None)
    access_token = getattr(settings, "META_ACCESS_TOKEN", None)

    if not ig_user_id or not access_token:
        print("⚠️ [INSTAGRAM] IG_USER_ID atau META_ACCESS_TOKEN belum diatur! Posting IG dibatalkan.")
        return False

    try:
        # Kita gunakan API versi v21.0 (Versi stabil terbaru Meta)
        API_VERSION = "v21.0"
        
        print("🚀 [INSTAGRAM] Langkah 1: Membuat Container Media di Server Meta...")
        container_url = f"https://graph.facebook.com/{API_VERSION}/{ig_user_id}/media"
        container_payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": access_token
        }
        
        async with httpx.AsyncClient() as client:
            container_res = await client.post(container_url, data=container_payload, timeout=30.0)
            
            if container_res.status_code != 200:
                print(f"❌ [INSTAGRAM] Gagal membuat container: {container_res.text}")
                return False
                
            creation_id = container_res.json().get("id")
            print(f"⏳ [INSTAGRAM] Container dibuat (ID: {creation_id}). Menunggu Meta merender...")

            # Jeda 10 detik. Meta kadang butuh waktu agak lama untuk download gambar dari Cloudinary
            await asyncio.sleep(10) 

            print("🚀 [INSTAGRAM] Langkah 2: Menerbitkan Container ke Feed...")
            publish_url = f"https://graph.facebook.com/{API_VERSION}/{ig_user_id}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": access_token
            }

            publish_res = await client.post(publish_url, data=publish_payload, timeout=30.0)
            
            if publish_res.status_code == 200:
                print("✅ [INSTAGRAM] BINGO! Berhasil posting ke Feed via Official API!")
                return True
            else:
                print(f"❌ [INSTAGRAM] Gagal menerbitkan: {publish_res.text}")
                return False

    except Exception as e:
        print(f"❌ [INSTAGRAM] Error Sistem: {str(e)}")
        return False