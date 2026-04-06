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

async def upload_image_to_cloudinary(image_bytes: bytes, folder_name: str = "marketing_assets") -> str:
    """
    Fungsi ini menerima data mentah gambar (bytes) dari Qwen, 
    mengunggahnya ke Cloudinary, dan mengembalikan Public URL.
    """
    try:
        print(f"☁️ Mengunggah gambar (Bytes) ke Cloudinary (Folder: {folder_name})...")
        
        response = cloudinary.uploader.upload(
            image_bytes,
            folder=folder_name,
            resource_type="image"
        )
        
        secure_url = response.get("secure_url")
        print(f"✅ Sukses Upload Cloudinary! URL: {secure_url}")
        
        return secure_url

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise Exception(f"Gagal mengunggah gambar ke Cloudinary: {str(e)}")


async def upload_base64_to_cloudinary(base64_string: str, folder_name: str = "frontend_uploads") -> str:
    """
    Fungsi BARU: Menerima string base64 dari frontend (Mas Alfin),
    mengunggahnya ke Cloudinary, dan mengembalikan Public URL.
    """
    try:
        print(f"☁️ Mengunggah gambar (Base64) ke Cloudinary (Folder: {folder_name})...")
        
        # Cloudinary uploader sangat pintar, dia bisa langsung membaca string base64
        # asalkan Mas Alfin mengirimnya dengan format "data:image/jpeg;base64,..."
        # atau string base64 murni.
        
        response = cloudinary.uploader.upload(
            base64_string,
            folder=folder_name,
            resource_type="image"
        )
        
        secure_url = response.get("secure_url")
        print(f"✅ Sukses Upload Base64 dari Front-End! URL: {secure_url}")
        
        return secure_url

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise Exception(f"Gagal mengunggah Base64 ke Cloudinary: {str(e)}")