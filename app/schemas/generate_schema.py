from pydantic import BaseModel, Field

class GenerateCopyRequest(BaseModel):
    product_name: str = Field(..., description="Nama produk, contoh: Sepatu Nike Air Max")
    product_description: str = Field(..., description="Keunggulan produk, contoh: Warna merah, diskon 50%, cocok untuk lari")

class GenerateCopyResponse(BaseModel):
    copywriting: str