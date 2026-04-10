from pydantic import BaseModel, Field
from typing import Optional

class GenerateStudioRequest(BaseModel):
    image_base64: str  
    category: str      
    prompt_design: str
    media_type: Optional[str] = Field(default="image", description="Pilihan output: 'image' atau 'video'")