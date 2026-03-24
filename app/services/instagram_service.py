# import httpx

# # URL Webhook Sakti dari Make.com Anda
# MAKE_WEBHOOK_URL = "https://hook.eu1.make.com/mr2xjzb8m2hqd2sesqt03nrc1opwy9tr"

# async def post_to_instagram(image_url: str, caption: str) -> bool:
#     """
#     Kurir VIP: Mengirimkan pesanan langsung ke Make.com via Webhook.
#     Make.com yang akan mengurus upload ke Instagram Official API.
#     """
#     try:
#         print(f"🚀 1. Memanggil Make.com via Webhook...")
        
#         # Ini kotak paket yang akan dikirim ke Make.com
#         payload = {
#             "image_url": image_url,
#             "caption": caption
#         }

#         # Mengirim POST request ke Make.com secara asinkron
#         async with httpx.AsyncClient() as client:
#             response = await client.post(MAKE_WEBHOOK_URL, json=payload, timeout=30.0)
            
#             # Kalau Make.com membalas dengan status 200 (OK)
#             if response.status_code in [200, 201]:
#                 print("✅ BINGO! Make.com berhasil menerima data dan sedang memposting ke IG!")
#                 return True
#             else:
#                 print(f"⚠️ Make.com menolak data. Status: {response.status_code}")
#                 return False

#     except Exception as e:
#         print(f"❌ Gagal mengirim ke Webhook Make.com: {str(e)}")
#         return False

# ini adalah rekayasa untuk mengirim ke telegram ya

import httpx

# Kunci Pas Telegram Anda
TELEGRAM_BOT_TOKEN = "8728100999:AAEJq6WDRuEcAqhPx4wZDfAheLumbnqTGzY"

# Koordinat Grup "MARKET PRODUK AFILIATE"
TELEGRAM_CHAT_ID = "-1003874533814" 

async def post_to_instagram(image_url: str, caption: str) -> bool:
    """
    Sssst... Namanya masih post_to_instagram, 
    tapi aslinya kurir ini sekarang ngirim ke Telegram! 🤫🚀
    """
    try:
        print(f"🚀 1. Mengirim Poster dan Copywriting AI ke Telegram...")
        
        # Endpoint resmi Telegram untuk mengirim foto
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        
        # Paket data untuk Telegram
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "photo": image_url,
            "caption": caption,
            "parse_mode": "HTML" # Biar format tebal/miring dari Gemini terbaca
        }

        # Tembak langsung!
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, timeout=30.0)
            
            if response.status_code == 200:
                print("✅ BINGO! Berhasil masuk ke Grup Telegram!")
                return True
            else:
                print(f"⚠️ Telegram menolak. Error: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Gagal mengirim ke Telegram: {str(e)}")
        return False