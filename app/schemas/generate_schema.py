from pydantic import BaseModel

class GenerateStudioRequest(BaseModel):
    image_base64: str  
    category: str      
    prompt_design: str