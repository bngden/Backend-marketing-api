import httpx
import asyncio
from app.core.config import settings

async def post_to_facebook(media_url: str = None, caption: str = "", is_video: bool = False) -> bool:
    """
    Jalur Resmi Meta untuk Facebook Page.
    Membutuhkan FB_PAGE_ID dan FB_PAGE_ACCESS_TOKEN di file .env.
    """
    # Ingat: Untuk FB, kita butuh PAGE ID dan PAGE ACCESS TOKEN (Bukan User Token biasa)
    page_id = getattr(settings, "FB_PAGE_ID", None)
    access_token = getattr(settings, "FB_PAGE_ACCESS_TOKEN", None)

    if not page_id or not access_token:
        print("⚠️ [FACEBOOK] FB_PAGE_ID atau FB_PAGE_ACCESS_TOKEN belum diatur! Posting dibatalkan.")
        return False

    try:
        API_VERSION = "v21.0"
        
        async with httpx.AsyncClient() as client:
            
            # 🔀 PERSIMPANGAN LOGIKA (VIDEO vs GAMBAR vs TEKS)
            
            if media_url and is_video:
                # --- JALUR A: POSTING VIDEO ---
                print("🎬 [FACEBOOK] Mengirim Video ke Page...")
                url = f"https://graph.facebook.com/{API_VERSION}/{page_id}/videos"
                payload = {
                    "file_url": media_url, # FB API menggunakan 'file_url' untuk video
                    "description": caption, # FB API menggunakan 'description' untuk caption video
                    "access_token": access_token
                }
                
                res = await client.post(url, data=payload, timeout=60.0)
                
            elif media_url and not is_video:
                # --- JALUR B: POSTING GAMBAR ---
                print("🖼️ [FACEBOOK] Mengirim Gambar ke Page...")
                url = f"https://graph.facebook.com/{API_VERSION}/{page_id}/photos"
                payload = {
                    "url": media_url, # FB API menggunakan 'url' untuk gambar
                    "message": caption, # FB API menggunakan 'message' untuk caption foto/teks
                    "access_token": access_token
                }
                
                res = await client.post(url, data=payload, timeout=30.0)
                
            else:
                # --- JALUR C: POSTING TEKS SAJA ---
                print("📝 [FACEBOOK] Mengirim Status Teks ke Page...")
                url = f"https://graph.facebook.com/{API_VERSION}/{page_id}/feed"
                payload = {
                    "message": caption,
                    "access_token": access_token
                }
                
                res = await client.post(url, data=payload, timeout=20.0)

            # ==========================================
            # EVALUASI HASIL TEMBAKAN
            # ==========================================
            if res.status_code == 200:
                post_id = res.json().get("id")
                print(f"✅ [FACEBOOK] BINGO! Berhasil posting ke Facebook Page! (ID: {post_id})")
                return True
            else:
                print(f"❌ [FACEBOOK] Gagal posting: {res.text}")
                return False

    except Exception as e:
        print(f"❌ [FACEBOOK] Error Sistem: {str(e)}")
        return False