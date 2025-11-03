"""
ShelfLife - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import re

from app.database import init_db
from app.routers import settings, libraries, rules, tasks, candidates, logs
from app.scheduler import start_scheduler

app = FastAPI(title="ShelfLife API", version="3.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    from app.scheduler import stop_scheduler
    stop_scheduler()

# API routes
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(libraries.router, prefix="/api/libraries", tags=["libraries"])
app.include_router(rules.router, prefix="/api/rules", tags=["rules"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["candidates"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])

# Health check
@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "3.0.0"}

# Serve static files in production
static_dir = os.path.join(os.path.dirname(__file__), "static")

def sanitize_path_component(component: str) -> str | None:
    """
    Sanitize a single path component using an allowlist approach.
    Returns None if the component is unsafe.
    """
    if not component:
        return None
    
    # Reject dangerous patterns
    if ".." in component or "\\" in component or "/" in component:
        return None
    
    # Allowlist: only alphanumeric, dots, hyphens, and underscores
    # This allows file extensions but prevents directory traversal
    if not re.match(r'^[a-zA-Z0-9._-]+$', component):
        return None
    
    # Reject components that are just dots (current/parent directory)
    if component == "." or component == "..":
        return None
    
    return component

def sanitize_file_path(user_path: str) -> str | None:
    """
    Sanitize a file path from user input using an allowlist approach.
    Returns None if the path is unsafe, otherwise returns a sanitized path.
    """
    # Early rejection of obviously dangerous patterns
    if ".." in user_path or "\\" in user_path:
        return None
    
    # Reject absolute paths
    if user_path.startswith("/") or user_path.startswith(os.sep):
        return None
    
    # Split into components and validate each one
    path_parts = user_path.split("/")
    sanitized_parts = []
    
    for part in path_parts:
        sanitized = sanitize_path_component(part)
        if sanitized is None:
            # Invalid component - reject entire path
            return None
        sanitized_parts.append(sanitized)
    
    # Reconstruct path from validated components
    return "/".join(sanitized_parts)

if os.path.exists(static_dir):
    # Serve assets
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    # Serve index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            return None
        
        # Sanitize user input using allowlist-based validation
        sanitized_path = sanitize_file_path(full_path)
        if sanitized_path is None:
            # Invalid path - serve index.html for SPA routing instead
            index_path = os.path.join(static_dir, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
            return {"error": "Frontend not found"}
        
        # Check if it's a file request using the sanitized path
        file_path = os.path.join(static_dir, sanitized_path)
        static_dir_abs = os.path.abspath(static_dir)
        file_path_abs = os.path.abspath(file_path)
        
        # Only serve if the path is contained within static_dir
        # Use commonpath to securely verify file_path_abs is within static_dir_abs
        try:
            is_within_static_dir = os.path.commonpath([file_path_abs, static_dir_abs]) == static_dir_abs
        except ValueError:
            # Different drives on Windows cause ValueError; treat as outside static dir
            is_within_static_dir = False

        if is_within_static_dir:
            if os.path.exists(file_path_abs) and os.path.isfile(file_path_abs):
                return FileResponse(file_path_abs)
        
        # Otherwise serve index.html for SPA routing
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "Frontend not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
