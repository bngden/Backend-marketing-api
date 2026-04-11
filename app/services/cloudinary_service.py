import cloudinary
import cloudinary.uploader
from app.core.config import settings
import base64

# --- INISIALISASI KONEKSI KE CLOUDINARY ---
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True # Wajib True agar URL yang dihasilkan pakai HTTPS
)

# 1. TAMBAHKAN PARAMETER resource_type: str = "image"
async def upload_image_to_cloudinary(image_bytes: bytes, folder_name: str = "marketing_assets", resource_type: str = "image") -> str:
    """
    Fungsi ini menerima data mentah (bytes) dari Qwen atau Magic Hour, 
    mengunggahnya ke Cloudinary, dan mengembalikan Public URL.
    """
    try:
        print(f"☁️ Mengunggah data (Bytes) ke Cloudinary (Folder: {folder_name})...")
        
        response = cloudinary.uploader.upload(
            image_bytes,
            folder=folder_name,
            resource_type=resource_type 
        )
        
        secure_url = response.get("secure_url")
        print(f"✅ Sukses Upload Cloudinary! URL: {secure_url}")
        
        return secure_url

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise Exception(f"Gagal mengunggah data bytes ke Cloudinary: {str(e)}")


# 2. TAMBAHKAN PARAMETER resource_type: str = "image" JUGA DI SINI
async def upload_base64_to_cloudinary(base64_string: str, folder_name: str = "frontend_uploads", resource_type: str = "image") -> str:
    """
    Fungsi BARU: Menerima string base64 dari frontend (Mas Alfin),
    mengunggahnya ke Cloudinary, dan mengembalikan Public URL.
    """
    try:
        print(f"☁️ Mengunggah gambar (Base64) ke Cloudinary (Folder: {folder_name})...")
        
        response = cloudinary.uploader.upload(
            base64_string,
            folder=folder_name,
            resource_type=resource_type 
        )
        
        secure_url = response.get("secure_url")
        print(f"✅ Sukses Upload Base64 dari Front-End! URL: {secure_url}")
        
        return secure_url

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise Exception(f"Gagal mengunggah Base64 ke Cloudinary: {str(e)}")