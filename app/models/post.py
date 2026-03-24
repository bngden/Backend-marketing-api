import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base 

# --- INI DIA YANG DICARI OLEH ERROR TADI ---
class PostStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"

class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    category = Column(String)
    
    # Hasil dari AI:
    image_url = Column(String) 
    copywriting = Column(Text) 
    
    scheduled_time = Column(DateTime)
    
    # --- UBAH KOLOM INI MENJADI ENUM ---
    status = Column(Enum(PostStatus), default=PostStatus.SCHEDULED) 
    
    # Relasi ke tabel User
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="posts")