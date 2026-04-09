from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.future import select

# Import koneksi database dan model
from app.db.database import engine, Base, AsyncSessionLocal
from app.models.post import ScheduledPost, PostStatus

# Import services (Kurir Pengantar)
from app.services.instagram_service import post_to_instagram
from app.services.telegram_service import post_to_telegram # Import kurir baru

# Import routes (Pintu Gerbang API)
from app.api.routes import auth, generate, schedule # Posts sudah dibuang

# Inisialisasi Robot Penjadwal (Scheduler)
scheduler = AsyncIOScheduler()

# =====================================================================
# 🤖 ROBOT KURIR OTOMATIS: Mengecek Database setiap 1 menit
# =====================================================================
@scheduler.scheduled_job('interval', minutes=1)
async def check_and_publish_scheduled_posts():
    # Ambil waktu Jakarta (WIB)
    now_wib = datetime.now(ZoneInfo("Asia/Jakarta")).replace(tzinfo=None)
    print(f"[{now_wib.strftime('%H:%M:%S')}] 🤖 Robot sedang mengecek antrean Draft...")
    
    async with AsyncSessionLocal() as db:
        # Cari postingan yang statusnya DRAFT (atau SCHEDULED) dan waktunya sudah tiba/lewat
        result = await db.execute(
            select(ScheduledPost).filter(
                ScheduledPost.status.in_([PostStatus.DRAFT, PostStatus.SCHEDULED]),
                ScheduledPost.scheduled_time <= now_wib
            )
        )
        posts_to_publish = result.scalars().all()

        for p in posts_to_publish:
            print(f"🚀 Memproses [{p.platform}] ID: {p.id} - Judul: {p.title}...")
            
            is_success = False
            
            # LOGIKA PEMILIHAN KURIR BERDASARKAN PLATFORM
            if p.platform.lower() == "instagram":
                is_success = await post_to_instagram(image_url=p.image_url, caption=p.caption)
            elif p.platform.lower() == "telegram":
                is_success = await post_to_telegram(image_url=p.image_url, caption=p.caption)
            else:
                print(f"⚠️ Platform '{p.platform}' tidak dikenal!")
                continue

            # Update status hasil pengiriman di database
            if is_success:
                p.status = PostStatus.PUBLISHED
                print(f"✅ Postingan {p.id} Sukses Terbit!")
            else:
                p.status = PostStatus.FAILED
                print(f"❌ Postingan {p.id} Gagal Terbit!")
            
            db.add(p)
            await db.commit()

# =====================================================================
# ⚡ LIFESPAN MANAGER (Startup & Shutdown)
# =====================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    # 1. Sinkronisasi Tabel Database Neon (Pastikan kolom baru title & platform sudah ada)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database Neon Sinkron!")
    
    # 2. Jalankan Robot Scheduler
    if not scheduler.running:
        scheduler.start()
    print("⏰ Robot APScheduler Aktif (Cek tiap 1 menit)!")
    
    yield # --- SERVER BERJALAN ---
    
    # --- SHUTDOWN ---
    scheduler.shutdown()
    print("🛑 Robot APScheduler dimatikan dengan aman.")


# =====================================================================
# 🚀 INISIALISASI FASTAPI
# =====================================================================
app = FastAPI(
    title="AiGoncy - Marketing Automation API",
    description="Backend cerdas untuk AI Studio Pintar & Auto-Posting Instagram/Telegram",
    version="2.0.0",
    lifespan=lifespan
)

# MIDDLEWARE CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5173/ai",
        "https://marketing-ai-gency.vercel.app/ai",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://marketing-ai-gency.vercel.app", 
        "https://marketing-ai-gency.vercel.app/" 
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REGISTRASI ROUTES (Pintu Masuk API)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(generate.router, prefix="/api/v1/generate", tags=["AI Studio Pintar"])
app.include_router(schedule.router, prefix="/api/v1/schedule", tags=["Schedule & Draft Management"])

@app.get("/", tags=["Root"])
async def root():
    return {
        "status": "online", 
        "app_name": "AiGoncy API",
        "current_time_wib": datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")
    }
