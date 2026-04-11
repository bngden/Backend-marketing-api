from pydantic import BaseModel
from typing import Optional, Union, List
from datetime import datetime
from app.models.post import PostStatus

class PostScheduleCreate(BaseModel):
    title: str            
    caption: str          
    image_url: str
    video_url: Optional[str] = None        
    platform: Union[str, List[str]]         
    scheduled_time: datetime 

class PostScheduleUpdate(BaseModel):
    title: Optional[str] = None
    caption: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    status: Optional[PostStatus] = None
    platform: Optional[Union[str, List[str]]] = None