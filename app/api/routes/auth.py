from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_current_user
# UBAH BARIS INI: Ambil get_db dari folder db
from app.db.database import get_db 
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.models.user import User
from app.schemas.auth_schema import UserCreate, UserLogin, Token, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Cek apakah email sudah terdaftar (Cara Async)
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar!")
    
    # 2. Hash password-nya
    hashed_pwd = get_password_hash(user_data.password)
    
    # 3. Simpan user baru ke database (Cara Async)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd,
        first_name=user_data.first_name,
    last_name=user_data.last_name,
    business=user_data.business,
    domicile=user_data.domicile
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
async def login_user(
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends() # <--- INI KUNCI UTAMANYA
):
    # Form dari Swagger secara default menggunakan kolom "username"
    # Jadi kita anggap user mengetikkan EMAIL mereka di kolom "username" pada Swagger
    result = await db.execute(select(User).filter(User.email == form_data.username))
    user = result.scalars().first()
    
    # Cek user & kecocokan password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email atau Password salah!")
    
    # Buat JWT Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user