import io
import base64
import httpx
from fastapi import HTTPException
from PIL import Image
from rembg import remove
from app.core.config import settings

# --- IMPORT SERVICE CLOUDINARY ---
from app.services.cloudinary_service import upload_image_to_cloudinary

def get_qwen_api_key():
    return settings.DASHSCOPE_API_KEY

async def generate_product_image(image_bytes: bytes, user_prompt: str, category: str) -> str:
    try:
        print("1. Memotong produk dari background asli (Lokal)...")
        raw_img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        raw_img.thumbnail((1024, 1024)) # Jaga ukuran gambar agar proses cepat
        
        temp_io = io.BytesIO()
        raw_img.save(temp_io, format="PNG")
        
        # Eksekusi potong background
        cutout_bytes = remove(temp_io.getvalue())
        product = Image.open(io.BytesIO(cutout_bytes)).convert("RGBA")
        
        # Auto-Crop: Buang sisa transparan di pinggiran gambar
        bbox = product.getbbox()
        if bbox:
            product = product.crop(bbox)
            
        # Convert gambar transparan ke format Base64 URI yang diminta Qwen
        buffered_cutout = io.BytesIO()
        product.save(buffered_cutout, format="PNG")
        base64_img = base64.b64encode(buffered_cutout.getvalue()).decode('utf-8')
        data_uri = f"data:image/png;base64,{base64_img}"

        print(f"2. Memilih Super Prompt untuk Kategori: {category.upper()}...")
        tema_teks = user_prompt if user_prompt else "SPECIAL OFFER"
        
        # --- DYNAMIC PROMPTING (THE MASTER PLAN) ---
        prompts = {
            "makanan": (
                f"A high-end commercial food photography poster for social media. The uploaded image is the main food product. "
                f"Seamlessly integrate it. Place the product on a rustic wooden table or dark aesthetic slate. "
                f"Add dynamic flying elements like subtle water splashes, fresh flying ingredients (leaves, spices), and warm glowing light. "
                f"Vivid, appetizing colors. Include bold, stylish 3D typography reading '{tema_teks}' at the top. "
                f"Dramatic studio lighting with realistic natural shadows. Professional food advertising aesthetic, 8k."
            ),
            "kosmetik": (
                f"Premium cosmetic and skincare social media poster. The uploaded image is the hero product. "
                f"Place the product elegantly on a sleek, modern 3D marble podium or calm water surface. "
                f"Soft, soothing pastel gradient background. Add natural elements like out-of-focus tropical leaves in the foreground and subtle water drops. "
                f"Clean, minimalist typography reading '{tema_teks}' in an elegant sans-serif font. "
                f"Luxurious aesthetic, highly detailed, soft studio lighting reflecting off the product."
            ),
            "fashion": (
                f"Modern streetwear fashion promotional poster for Instagram. The uploaded image is the main subject. "
                f"Enlarge the product to be the center of attention. Background should be a trendy, abstract flat vector design "
                f"with bold geometric shapes, halftone patterns, and dynamic overlapping blocks in contrasting colors. "
                f"Integrate the text '{tema_teks}' in massive, bold, street-style typography behind the product. "
                f"Add realistic drop shadows so the product pops out. High engagement marketing visual, ultra-detailed."
            ),
            "elektronik": (
                f"Futuristic and premium tech electronic product social media poster. The uploaded image is the main gadget. "
                f"Place it floating in a dark, sleek cinematic environment. "
                f"Add neon glowing accents, cybernetic light streaks, and a glossy reflective surface below it. "
                f"High-tech, minimalist, and ultra-modern cyberpunk aesthetic. "
                f"Include sleek typography reading '{tema_teks}' in a futuristic font. Crisp details, 8k resolution."
            )
        }

        # Pilih prompt berdasarkan input user. Default ke 'fashion' jika tidak valid.
        selected_prompt = prompts.get(category.lower(), prompts["fashion"])

        print("3. Meminta AI Qwen Merakit Poster Final (Alibaba Cloud)...")
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
                            {"text": selected_prompt}
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
            folder_name=f"marketing_{category.lower()}"
        )

        print(f"✅ Poster Selesai Dibuat! URL: {cloudinary_url}")
        
        # Kembalikan link Cloudinary-nya
        return cloudinary_url

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Gagal memproses gambar: {str(e)}")