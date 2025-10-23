"""FastAPI app for REST API server based on vmware-vra-cli."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from vmware_vra_cli.rest_server.models import HealthResponse, ErrorResponse
from vmware_vra_cli.rest_server.routers import auth, catalog, deployments, reports, workflows, analytics, projects, vm_templates
from vmware_vra_cli.rest_server.database import init_db

import uvicorn
import time

app = FastAPI(title="VMware vRA REST API Server", version="0.1.0")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        # Don't fail the app startup if DB is not available

# Include routers
app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(deployments.router)
app.include_router(reports.router)
app.include_router(workflows.router)
app.include_router(analytics.router)
app.include_router(projects.router)
app.include_router(vm_templates.router)
uptime_start = time.time()

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom error handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": exc.errors(),
            "timestamp": int(time.time()),
        },
    )

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the VMware vRA REST API Server!"}

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    uptime_seconds = time.time() - uptime_start
    vra_status = "unknown"
    
    # Try to check VRA connection
    try:
        from vmware_vra_cli.auth import TokenManager
        from vmware_vra_cli.config import get_config
        
        config = get_config()
        if config and config.get('api_url'):
            try:
                # Check if we have tokens stored
                access_token = TokenManager.get_access_token()
                if access_token:
                    vra_status = "connected"
                else:
                    refresh_token = TokenManager.get_refresh_token()
                    if refresh_token:
                        vra_status = "refresh_token_available"
                    else:
                        vra_status = "not_authenticated"
            except Exception as e:
                vra_status = f"error: {str(e)[:50]}"
        else:
            vra_status = "not_configured"
    except Exception as e:
        vra_status = f"check_failed: {str(e)[:50]}"
    
    return HealthResponse(
        status="healthy",
        version=app.version,
        uptime=f"{uptime_seconds:.2f} seconds",
        vra_connection=vra_status,
    )

# Run the server
def main():
    uvicorn.run("vmware_vra_cli.app:app", host="0.0.0.0", port=8000, reload=True)

