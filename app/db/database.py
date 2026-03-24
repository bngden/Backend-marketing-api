import ssl # Tambahkan ini di bagian atas file
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# --- TAMBAHKAN BAGIAN INI ---
# Membuat konteks SSL yang mengabaikan verifikasi ketat (standar untuk Neon/Supabase di tahap dev)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
# -----------------------------

# Ubah pembuatan engine dengan menyisipkan connect_args
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=True,
    connect_args={"ssl": ssl_context} # Berikan pengaturan SSL ke asyncpg
)
# 2. Membuat Session Factory (Pabrik pembuat sesi koneksi per request user)
AsyncSessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 3. Base class untuk semua Model/Tabel kita nantinya
Base = declarative_base()

# 4. Dependency Injection (Sangat penting di FastAPI)
# Fungsi ini akan otomatis membuka dan menutup koneksi database setiap kali ada request
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session