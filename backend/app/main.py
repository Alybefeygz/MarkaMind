# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Create FastAPI instance
app = FastAPI(
    title="MarkaMind API",
    description="Markaniza Ozel Yapay Zeka Destekli Chatbox Sistemi",
    version="1.0.0",
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "MarkaMind API is running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "supabase_configured": bool(settings.supabase_url),
        "openrouter_configured": bool(settings.openrouter_api_key),
        "debug": settings.debug
    }


# Include routers
from app.routers.auth import router as auth_router

app.include_router(auth_router, prefix="/api/v1")

# Additional routers (will be added in next steps)
# app.include_router(brands_router, prefix="/api/v1")
# app.include_router(chatbots_router, prefix="/api/v1")
# app.include_router(widget_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )