from fastapi import APIRouter, HTTPException, Depends
from app.schemas.generate_schema import GenerateStudioRequest
from app.services.post_service import process_studio_generation

# (Opsional) Jika endpoint ini wajib login, uncomment baris di bawah:
from app.api.deps import get_current_user 

router = APIRouter()

@router.post("/studio")
async def create_studio_content(
    request: GenerateStudioRequest,
    current_user = Depends(get_current_user) # Aktifkan jika wajib login
):
    """
    ENDPOINT 1: STUDIO PINTAR (ALL-IN-ONE)
    base64 fin untuk gambarnya 
    (BELUM DISIMPAN KE DATABASE)
    """
    try:
        # Panggil Manajer Studio Pintar kita
        result = await process_studio_generation(request)
        
        # Return sebagai JSON agar Mas Alfin bisa merendernya di layar
        return {
            "status": "success",
            "message": "Poster dan Copywriting berhasil dibuat!",
            "data": result # Akan berisi {"caption": "...", "image_url": "..."}
        }
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Gagal memproses AI Studio: {str(e)}")