"""FastAPI app for MCP server based on vmware-vra-cli."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from vmware_vra_cli.server.models import HealthResponse, ErrorResponse
from vmware_vra_cli.server.routers import auth, catalog, deployments

import uvicorn
import time

app = FastAPI(title="VMware vRA MCP Server", version="0.1.0")

# Include routers
app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(deployments.router)
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
    return {"message": "Welcome to the VMware vRA MCP Server!"}

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    uptime_seconds = time.time() - uptime_start
    return HealthResponse(
        status="healthy",
        version=app.version,
        uptime=f"{uptime_seconds:.2f} seconds",
    )

# Run the server
def main():
    uvicorn.run("vmware_vra_cli.app:app", host="0.0.0.0", port=8000, reload=True)

