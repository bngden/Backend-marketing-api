import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.services.cloudinary_service import upload_image_to_cloudinary

def get_qwen_api_key():
    return settings.DASHSCOPE_API_KEY

async def generate_product_image(base64_string: str, ai_image_prompt: str) -> str:
    """
    Bekerja murni Image-to-Image tanpa potong manual. 
    Objek menyatu sempurna dengan pencahayaan dan bayangan asli.
    """
    try:
        print("1. Menyiapkan Gambar Mentah (Tanpa Potong Manual!)...")
        
        # Qwen membutuhkan format Data URI. Kita pastikan formatnya benar.
        data_uri = base64_string
        if not base64_string.startswith("data:image"):
            # Jika Front-End mengirim base64 murni tanpa header, kita tambahkan
            data_uri = f"data:image/jpeg;base64,{base64_string}"

        print("2. Meminta AI Qwen Melakukan 'Magic Blend' (Image-to-Image)...")
        api_key = get_qwen_api_key()
        if not api_key:
            raise Exception("API Key DashScope (Qwen) belum di-set di .env!")

        # Payload konfigurasi Qwen
        payload = {
            "model": "qwen-image-2.0-pro",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": data_uri},
                            {"text": ai_image_prompt} # Menggunakan instruksi cerdas dari Gemini
                        ]
                    }
                ]
            },
            "parameters": {
                "n": 1,
                "size": "1024*1024",
                "watermark": False
            }
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=120.0)

            if response.status_code != 200:
                print(f"Error Qwen: {response.status_code} - {response.text}")
                raise Exception(f"Gagal generate dari Qwen AI: {response.status_code}")

            # Ambil URL sementara dari Alibaba
            resp_data = response.json()
            image_url_qwen = resp_data["output"]["choices"][0]["message"]["content"][0]["image"]

        print("4. Mengunduh Hasil Final dari Server Alibaba...")
        # Download gambar jadinya
        async with httpx.AsyncClient() as client:
            img_response = await client.get(image_url_qwen, timeout=60.0)
            final_image_bytes = img_response.content

        print("5. Meneruskan Gambar ke Cloudinary...")
        # Upload ke Cloudinary dan dapatkan link publik permanen
        cloudinary_url = await upload_image_to_cloudinary(
            final_image_bytes, 
            folder_name="marketing_ai_results"
        )

        print(f"✅ Poster Kelas Studio Selesai Dibuat! URL: {cloudinary_url}")
        return cloudinary_url

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Gagal memproses gambar: {str(e)}")