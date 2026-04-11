import httpx

# Kunci Pas Telegram Anda (Ditanam langsung sesuai instruksi!)
TELEGRAM_BOT_TOKEN = "8728100999:AAEJq6WDRuEcAqhPx4wZDfAheLumbnqTGzY"
TELEGRAM_CHAT_ID = "-1003874533814"

async def post_to_telegram(media_url: str, caption: str, is_video: bool = False) -> bool:
    """Mengirim Poster (Gambar) atau Video ke Grup Telegram"""
    try:
        # 🔀 PERSIMPANGAN LOGIKA (VIDEO vs GAMBAR)
        if is_video:
            print(f"🎬 [TELEGRAM] Mengirim VIDEO ke Grup...")
            # Menggunakan endpoint sendVideo
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "video": media_url, # Telegram meminta nama parameter 'video'
                "caption": caption,
                "parse_mode": "HTML"
            }
        else:
            print(f"🖼️ [TELEGRAM] Mengirim GAMBAR ke Grup...")
            # Menggunakan endpoint sendPhoto
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "photo": media_url, # Telegram meminta nama parameter 'photo'
                "caption": caption,
                "parse_mode": "HTML"
            }

        async with httpx.AsyncClient() as client:
            # Timeout dinaikkan ke 60 detik karena kirim video butuh waktu lebih lama
            response = await client.post(url, data=payload, timeout=60.0)
            
            if response.status_code == 200:
                print(f"✅ [TELEGRAM] BINGO! Berhasil masuk ke Grup!")
                return True
            else:
                print(f"❌ [TELEGRAM] Gagal. Error: {response.text}")
                return False

    except Exception as e:
        print(f"❌ [TELEGRAM] Error Sistem: {str(e)}")
        return False