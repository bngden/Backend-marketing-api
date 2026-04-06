from google import genai
from app.core.config import settings
import json

# 1. Inisialisasi Client menggunakan SDK versi terbaru
client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def generate_aida_copywriting(user_instruction: str, category: str) -> dict:
    """
    Fungsi ini menjadi "The Master Brain" tanpa butuh nama produk spesifik.
    Menerima instruksi user & kategori, lalu menghasilkan Caption dan Image Prompt sekaligus.
    """
    # 2. Meracik Prompt (Instruksi Sistem)
    system_prompt = f"""
    Kamu adalah seorang Digital Marketer & Sutradara Fotografi Produk Kelas Dunia.
    Tugasmu ada DUA: membuat Caption Instagram (Formula AIDA) dan membuat Prompt Gambar AI.
    
    Info dari user:
    - Kategori Produk: {category}
    - Keinginan User (Tema/Konteks Promosi): {user_instruction}
    
    ATURAN 1 (CAPTION - AIDA):
    - Buat caption Instagram berdaya konversi tinggi untuk produk dengan kategori dan tema di atas.
    - Gunakan bahasa Indonesia yang gaul, asik, dan engaging (target pasar 30-40 tahun).
    - Beri placeholder seperti [Nama Brand/Produk Anda] agar user bisa mengisinya nanti.
    - Gunakan pemformatan spasi yang rapi agar mudah dibaca.
    - Sisipkan emoji relevan dan berikan 5 hashtag viral di bagian paling bawah.
    
    ATURAN 2 (PROMPT GAMBAR AI):
    - Terjemahkan dan kembangkan 'Keinginan User' ke dalam BAHASA INGGRIS yang SANGAT DETAIL.
    - Tambahkan "Magic Words" fotografi komersial. Contoh: "high-end product photography, commercial shot, photorealistic, dramatic studio lighting, sharp focus, realistic shadow and reflections, 8k resolution".
    - Fokus pada mendeskripsikan BACKGROUND, ALAS (podium/meja), EFEK (asap/percikan air), dan PENCAHAYAAN (lighting).
    - INGAT: Jangan mendeskripsikan bentuk produknya, karena produk aslinya akan ditempel oleh sistem.
    
    OUTPUT WAJIB DALAM FORMAT JSON SEPERTI INI (Tanpa awalan/akhiran markdown ```json):
    {{
      "caption": "Teks caption IG AIDA di sini...",
      "image_prompt": "Prompt bahasa inggris yang sangat detail di sini..."
    }}
    """
    
    try:
        # 3. Kirim ke Google Gemini 
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_prompt
        )
        
        # 4. Parsing Output Gemini menjadi Dictionary
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        result_dict = json.loads(clean_text)
        
        print("🧠 Gemini Berhasil Meracik Caption & Prompt Gambar!")
        return result_dict
        
    except Exception as e:
        print(f"⚠️ Error di Gemini AI Service: {e}")
        # Fallback Darurat
        return {
            "caption": f"🌟 Dapatkan koleksi {category} terbaik kami sekarang juga! Tampil memukau dengan tema {user_instruction}. \n\n#Promo #Diskon #Terbaru", 
            "image_prompt": f"High-end product photography of {category}, {user_instruction}, aesthetic background, studio lighting, highly detailed, 8k, realistic shadows."
        }