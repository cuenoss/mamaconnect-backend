from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.pool import NullPool
from app.database import engine
from sqlmodel import SQLModel
from app.routes import auth, profile, articles, midwife, admin
from app.routes.client import chatbot, dashboard, monitoring, booking, subscription

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend is running"}

app.include_router(chatbot.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(dashboard.router, prefix="/dashboard")
app.include_router(profile.router, prefix="/profile")
app.include_router(articles.router, prefix="/articles")
app.include_router(booking.router,prefix="/booking")
app.include_router(midwife.router, prefix="/midwife")
app.include_router(admin.router, prefix="/admin")
app.include_router(monitoring.router, prefix="/monitoring")
app.include_router(subscription.router, prefix="/subscription")
