from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import webhook, conversations, approvals, settings as settings_api, health, style

app = FastAPI(title="WhatsApp AI Assistant", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router, prefix="/api", tags=["webhook"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(conversations.router, prefix="/api", tags=["conversations"])
app.include_router(approvals.router, prefix="/api", tags=["approvals"])
app.include_router(settings_api.router, prefix="/api", tags=["settings"])
app.include_router(style.router, prefix="/api", tags=["style"])

@app.get("/")
async def root():
    return {"message": "WhatsApp AI Assistant API", "version": "0.1.0"}
