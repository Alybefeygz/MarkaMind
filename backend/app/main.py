# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Create FastAPI instance
app = FastAPI(
    title="MarkaMind API",
    description="Markaniza Ozel Yapay Zeka Destekli Chatbox Sistemi",
    version="1.0.0",
    debug=settings.DEBUG,
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
        "supabase_configured": bool(settings.SUPABASE_URL),
        "openrouter_configured": bool(settings.OPENROUTER_API_KEY),
        "debug": settings.DEBUG
    }


# Include routers
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.brands import router as brands_router
from app.routers.stores import router as stores_router
from app.routers.products import router as products_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(brands_router, prefix="/api/v1")
app.include_router(stores_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")

# Additional routers (will be added in next steps)
# app.include_router(chatbots_router, prefix="/api/v1")
# app.include_router(widget_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )