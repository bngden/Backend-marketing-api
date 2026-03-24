from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.schemas.generate_schema import GenerateCopyRequest, GenerateCopyResponse
from app.services.ai_service import generate_aida_copywriting
from app.services.image_service import generate_product_image

router = APIRouter()

@router.post("/copywriting", response_model=GenerateCopyResponse)
async def create_copywriting(request: GenerateCopyRequest):
    result_text = await generate_aida_copywriting(
        product_name=request.product_name,
        product_description=request.product_description
    )
    return GenerateCopyResponse(copywriting=result_text)

# --- ENDPOINT BARU DENGAN KATEGORI ---
@router.post("/image")
async def create_aesthetic_image(
    file: UploadFile = File(...),
    user_prompt: str = Form(""),
    category: str = Form(..., description="Pilih: makanan, kosmetik, fashion, atau elektronik") 
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File yang diunggah harus berupa gambar (JPG/PNG)!")

    image_bytes = await file.read()

    # Panggil fungsi Qwen + Cloudinary kita
    result_url = await generate_product_image(image_bytes, user_prompt, category)

    # Return sebagai JSON agar rapi dan bisa dibaca oleh Frontend / Database nanti
    return {
        "status": "success",
        "category": category,
        "message": "Poster berhasil dibuat dan diunggah ke Cloudinary!",
        "image_url": result_url
    }