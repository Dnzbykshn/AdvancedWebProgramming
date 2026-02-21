"""Career Assistant AI Agent — FastAPI Entry Point."""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes.api import router as api_router

app = FastAPI(
    title="Career Assistant AI Agent",
    description="Multi-agent AI system for professional career communication",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Serve static frontend files
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.get("/")
async def serve_frontend():
    """Serve the frontend index.html."""
    return FileResponse(str(frontend_dir / "index.html"))


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("RAILWAY_ENVIRONMENT") is None  # reload only locally
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload)

