import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base 

# --- ENUM UNTUK STATUS ---
class PostStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"

class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True, index=True)
    
    # --- KOLOM BARU SESUAI DESAIN FRONT-END ---
    title = Column(String, index=True)               # Untuk menampung "Judul"
    platform = Column(String, default="Instagram")   # Untuk menampung "Platform" (Instagram/Telegram)
    
    # Kolom lama (dibiarkan nullable=True agar data lama tidak error)
    product_name = Column(String, index=True, nullable=True)
    category = Column(String, nullable=True)
    
    # --- HASIL DARI AI ---
    image_url = Column(String) 
    video_url = Column(String, nullable=True)
    caption = Column(Text) # Berubah dari copywriting menjadi caption agar sama dengan UI
    
    scheduled_time = Column(DateTime)
    
    # --- DEFAULT STATUS DIUBAH JADI DRAFT ---
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT) 
    
    # Relasi ke tabel User
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="posts")