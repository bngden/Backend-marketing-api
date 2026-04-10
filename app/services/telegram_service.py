import httpx

# Kunci Pas Telegram Anda
TELEGRAM_BOT_TOKEN = "8728100999:AAEJq6WDRuEcAqhPx4wZDfAheLumbnqTGzY"
# Koordinat Grup "MARKET PRODUK AFILIATE"
TELEGRAM_CHAT_ID = "-1003874533814" 

async def post_to_telegram(image_url: str, caption: str) -> bool:
    """Mengirim poster dan copywriting ke Grup Telegram"""
    try:
        print(f"[TELEGRAM] Mengirim Poster ke Grup...")
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "photo": image_url,
            "caption": caption,
            "parse_mode": "HTML" # Biar format tebal/miring terbaca
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, timeout=30.0)
            
            if response.status_code == 200:
                print("[TELEGRAM] BINGO! Berhasil masuk ke Grup!")
                return True
            else:
                print(f" [TELEGRAM] Gagal. Error: {response.text}")
                return False

    except Exception as e:
        print(f"❌ [TELEGRAM] Error Sistem: {str(e)}")
        return False