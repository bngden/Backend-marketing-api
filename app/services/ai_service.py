from google import genai
from app.core.config import settings

# 1. Inisialisasi Client menggunakan SDK versi terbaru
client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def generate_aida_copywriting(product_name: str, product_description: str) -> str:
    # 2. Meracik Prompt (Instruksi Sistem)
    prompt = f"""
    Kamu adalah seorang Copywriter Digital Marketing profesional yang handal.
    Tugasmu adalah membuat caption Instagram untuk produk berikut menggunakan formula AIDA (Attention, Interest, Desire, Action).
    
    Detail Produk:
    - Nama Produk: {product_name}
    - Deskripsi/Kelebihan: {product_description}
    
    Aturan Penulisan:
    1. Gunakan bahasa Indonesia yang gaul, asik, dan engaging (cocok untuk target pasar 30-40 tahun).
    2. Gunakan pemformatan spasi yang rapi agar mudah dibaca.
    3. Sisipkan emoji yang relevan secukupnya.
    4. Berikan 5 hashtag viral di bagian paling bawah.
    """
    
    # 3. Kirim ke Google Gemini menggunakan format SDK baru
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    return response.text