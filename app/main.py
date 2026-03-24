from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.future import select # WAJIB IMPORT INI UNTUK QUERY DB DI SCHEDULER

# Import koneksi database dan model
from app.db.database import engine, Base, AsyncSessionLocal
from app.models import post # Mendaftarkan tabel
from app.models.post import ScheduledPost, PostStatus

# Import services & routes
from app.services.instagram_service import post_to_instagram
from app.api.routes import schedule, generate, auth, posts

# Inisialisasi Mesin Waktu (Scheduler)
scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=1)
async def check_and_publish_scheduled_posts():
    # Ambil waktu Jakarta, lalu copot label zonanya (replace tzinfo=None) agar DB tidak bingung!
    now_wib = datetime.now(ZoneInfo("Asia/Jakarta")).replace(tzinfo=None)
    print(f"[{now_wib.strftime('%H:%M:%S')}] 🤖 Mengecek jadwal postingan IG...")
    
    # Buka koneksi database di latar belakang
    async with AsyncSessionLocal() as db:
        # Cari postingan yang waktunya sudah tiba, dan statusnya masih SCHEDULED
        result = await db.execute(
            select(ScheduledPost).filter(
                ScheduledPost.status == PostStatus.SCHEDULED,
                ScheduledPost.scheduled_time <= now_wib
            )
        )
        posts_to_publish = result.scalars().all()

        for p in posts_to_publish:
            print(f"🚀 Memproses Postingan ID: {p.id} ({p.product_name})...")
            
            # PANGGIL KURIR INSTAGRAM!
            is_success = await post_to_instagram(image_url=p.image_url, caption=p.copywriting)

            # Update status di database
            if is_success:
                p.status = PostStatus.PUBLISHED
            else:
                p.status = PostStatus.FAILED
            
            db.add(p)
            await db.commit()

# --- LIFESPAN MANAGER (Gaya Modern FastAPI) ---
# Menggabungkan pembuatan tabel DB dan nyala/matinya Scheduler di satu tempat
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. STARTUP: Sinkronisasi Tabel Database Neon
    async with engine.begin() as conn:
        #drop dlu yak
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Semua tabel berhasil disinkronkan ke Database Neon!")
    
    # 2. STARTUP: Nyalakan Robot Scheduler
    scheduler.start()
    print("⏰ Robot APScheduler berhasil dijalankan!")
    
    yield # --- APLIKASI FASTAPI BERJALAN DI SINI ---
    
    # 3. SHUTDOWN: Matikan Robot saat server Uvicorn dimatikan (CTRL+C)
    scheduler.shutdown()
    print("🛑 Robot APScheduler dimatikan dengan aman.")


# --- INISIALISASI APLIKASI FASTAPI ---
app = FastAPI(
    title="Marketing Automation API",
    description="Backend cerdas untuk AI Poster & Copywriting",
    version="1.0.0",
    lifespan=lifespan # Pasang mesin lifespan yang sudah kita buat di atas
)

# --- MIDDLEWARE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTRASI ROUTES ---
# Mendaftarkan semua endpoint dengan rapi, tidak ada yang dobel!
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(generate.router, prefix="/api/v1/generate", tags=["AI Generation"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["Instagram Auto-Poster"])
app.include_router(schedule.router, prefix="/api/v1/schedule", tags=["Legacy Scheduling"])

# --- ROOT ENDPOINT ---
@app.get("/", tags=["Root"])
async def root():
    return {"status": "online", "message": "FastAPI Server is running smoothly!"}