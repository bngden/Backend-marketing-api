from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostScheduleCreate(BaseModel):
    title: str            
    caption: str          
    image_url: str
    video_url: Optional[str] = None        
    platform: str         
    scheduled_time: datetime 

class PostScheduleUpdate(BaseModel):
    title: Optional[str] = None
    caption: Optional[str] = None
    scheduled_time: Optional[datetime] = None