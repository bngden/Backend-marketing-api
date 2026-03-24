from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String) # Ingat, password HARUS di-hash, tidak boleh plain text!

    # Relasi: 1 User bisa punya banyak Postingan
    posts = relationship("ScheduledPost", back_populates="owner")