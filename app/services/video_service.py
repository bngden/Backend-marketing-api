import os
import uuid
import httpx
import aiofiles
from magic_hour import AsyncClient
from app.core.config import settings

# Import kurir Cloudinary Anda untuk upload video hasil render nanti
from app.services.cloudinary_service import upload_image_to_cloudinary

async def generate_video_from_image(image_url: str, video_prompt: str) -> str:
    """
    Fungsi Sakti: Mengubah gambar statis menjadi video animasi via Magic Hour API.
    """
    api_key = getattr(settings, "MAGIC_HOUR_API_KEY", None)
    if not api_key:
        raise Exception("API Key Magic Hour belum diatur di .env!")

    # 1. Siapkan nama file lokal sementara (agar tidak bentrok kalau diakses banyak user)
    unique_id = uuid.uuid4().hex
    temp_image = f"temp_input_{unique_id}.jpg"
    temp_video_dir = "./temp_outputs"
    
    # Buat foldernya kalau belum ada
    os.makedirs(temp_video_dir, exist_ok=True)

    try:
        print(f"📥 [VIDEO] 1. Mendownload gambar mentah dari Cloudinary...")
        async with httpx.AsyncClient() as client:
            img_res = await client.get(image_url, timeout=30.0)
            img_res.raise_for_status()
            
            # Simpan file gambar ke server lokal
            async with aiofiles.open(temp_image, mode='wb') as f:
                await f.write(img_res.content)

        print(f"🎬 [VIDEO] 2. Mengirim ke Magic Hour (Prompt: {video_prompt[:40]}...)")
        mh_client = AsyncClient(token=api_key)
        
        # 2. Proses Image-to-Video
        # wait_for_completion=True membuat fungsi ini otomatis polling (menunggu) sampai video jadi
        response = await mh_client.v1.image_to_video.generate(
            assets={"image_file_path": temp_image},
            style={"prompt": video_prompt},
            end_seconds=5.0,     # Durasi 5 detik
            resolution="480p",   # Resolusi 480p (Hemat Kredit: 120 kredit/video)
            wait_for_completion=True,
            download_outputs=True,
            download_directory=temp_video_dir
        )

        # Mendapatkan path file video MP4 yang baru saja didownload dari Magic Hour
        video_file_path = response.downloaded_paths[0]
        
        print(f"📤 [VIDEO] 3. Mengunggah hasil video (MP4) kembali ke Cloudinary...")
        
        # 3. Baca file video dan upload ke Cloudinary
        async with aiofiles.open(video_file_path, mode='rb') as v_file:
            video_bytes = await v_file.read()
            
            # PENTING: resource_type="video" agar Cloudinary tahu ini MP4, bukan JPG
            video_url = await upload_image_to_cloudinary(
                video_bytes, 
                folder_name="marketing_ai_videos",
                resource_type="video" 
            )

        print(f"✅ [VIDEO] Selesai! URL Video: {video_url}")
        return video_url

    except Exception as e:
        print(f"❌ [VIDEO] Error sistem: {str(e)}")
        raise Exception(f"Gagal generate video dari Magic Hour: {str(e)}")
        
    finally:
        # 4. SAPU BERSIH: Hapus file lokal agar SSD server tidak penuh!
        print("🧹 [VIDEO] Membersihkan file sementara...")
        if os.path.exists(temp_image):
            os.remove(temp_image)
            
        if 'video_file_path' in locals() and os.path.exists(video_file_path):
            os.remove(video_file_path)