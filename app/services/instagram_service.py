import httpx
import asyncio
from app.core.config import settings

async def post_to_instagram(media_url: str, caption: str, is_video: bool = False) -> bool:
    ig_user_id = getattr(settings, "IG_USER_ID", None)
    access_token = getattr(settings, "META_ACCESS_TOKEN", None)

    if not ig_user_id or not access_token:
        print("⚠️ [INSTAGRAM] IG_USER_ID atau META_ACCESS_TOKEN belum diatur! Posting dibatalkan.")
        return False

    try:
        API_VERSION = "v21.0"
        
        print(f"🚀 [INSTAGRAM] Langkah 1: Membuat Container ({'REELS' if is_video else 'IMAGE'})...")
        container_url = f"https://graph.facebook.com/{API_VERSION}/{ig_user_id}/media"
        
        if is_video:
            container_payload = {
                "media_type": "REELS",          # WAJIB UNTUK VIDEO
                "video_url": media_url,         # Parameter untuk video
                "caption": caption,
                "share_to_feed": "true",        # Munculkan di Feed juga
                "access_token": access_token
            }
        else:
            container_payload = {
                "image_url": media_url,         # Parameter untuk gambar
                "caption": caption,
                "access_token": access_token
            }
        
        async with httpx.AsyncClient() as client:
            # Step 1: Create Container
            container_res = await client.post(container_url, data=container_payload, timeout=60.0)
            
            if container_res.status_code != 200:
                print(f"❌ [INSTAGRAM] Gagal membuat container: {container_res.text}")
                return False
                
            creation_id = container_res.json().get("id")
            print(f"⏳ [INSTAGRAM] Container dibuat (ID: {creation_id}). Menunggu Meta merender...")

            # Jeda Tunggu: Video butuh waktu render lebih lama dari server Meta
            waktu_tunggu = 20 if is_video else 10
            print(f"⏳ Menunggu {waktu_tunggu} detik agar proses di server Meta selesai...")
            await asyncio.sleep(waktu_tunggu) 

            # Step 2: Publish Container
            print("🚀 [INSTAGRAM] Langkah 2: Menerbitkan Container ke Profil...")
            publish_url = f"https://graph.facebook.com/{API_VERSION}/{ig_user_id}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": access_token
            }

            publish_res = await client.post(publish_url, data=publish_payload, timeout=30.0)
            
            if publish_res.status_code == 200:
                print(f"✅ [INSTAGRAM] BINGO! Berhasil posting {'Reels' if is_video else 'Feed'} via Official API!")
                return True
            else:
                print(f"❌ [INSTAGRAM] Gagal menerbitkan: {publish_res.text}")
                return False

    except Exception as e:
        print(f"❌ [INSTAGRAM] Error Sistem: {str(e)}")
        return False