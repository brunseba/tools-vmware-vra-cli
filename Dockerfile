# syntax=docker/dockerfile:1.4
# VMware vRA CLI MCP Server Docker Image
# 
# This Dockerfile creates a containerized version of the VMware vRA CLI
# as a Model Context Protocol (MCP) server, providing REST API access
# to VMware vRealize Automation functionality.
# 
# Build: docker build -t vmware-vra-cli:latest .
# Run:   docker run -p 8000:8000 vmware-vra-cli:latest

FROM python:3.10-slim AS base

# =============================================================================
# METADATA AND LABELS
# =============================================================================

# OCI Image Format Specification labels
LABEL org.opencontainers.image.title="VMware vRA CLI MCP Server"
LABEL org.opencontainers.image.description="VMware vRealize Automation CLI as a Model Context Protocol server providing REST API access to vRA functionality (airgap-compatible)"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.created="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
LABEL org.opencontainers.image.authors="Sebastien Brun <sebastien.brun@example.com>"
LABEL org.opencontainers.image.url="https://github.com/brunseba/tools-vmware-vra-cli"
LABEL org.opencontainers.image.documentation="https://brunseba.github.io/tools-vmware-vra-cli"
LABEL org.opencontainers.image.source="https://github.com/brunseba/tools-vmware-vra-cli"
LABEL org.opencontainers.image.vendor="Sebastien Brun"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.ref.name="vmware-vra-cli"

# Docker-specific labels
LABEL maintainer="Sebastien Brun <sebastien.brun@example.com>"
LABEL description="Fast, secure, and feature-rich MCP server for VMware vRealize Automation"

# Application-specific labels
LABEL com.vmware.vra.version="8.x"
LABEL com.vmware.vra.component="mcp-server"
LABEL com.vmware.vra.framework="fastapi"
LABEL com.vmware.vra.python.version="3.10"
LABEL com.vmware.vra.build.system="uv"

# Usage and documentation labels
LABEL usage="docker run -p 8000:8000 -e VRA_URL=https://vra.example.com vmware-vra-cli:latest"
LABEL help="Visit https://brunseba.github.io/tools-vmware-vra-cli for comprehensive documentation"

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================

# Python environment optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH" \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Application environment defaults
ENV UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8000 \
    UVICORN_LOG_LEVEL=info \
    UVICORN_ACCESS_LOG=true \
    UVICORN_WORKERS=1

# Security and operational settings
ENV USER_UID=1001 \
    USER_GID=1001 \
    APP_USER=appuser \
    APP_HOME=/app

# =============================================================================
# SYSTEM DEPENDENCIES AND SECURITY UPDATES
# =============================================================================

# Update system packages and install required dependencies
# hadolint ignore=DL3008,DL3009
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools for native extensions
    build-essential \
    # HTTP client for health checks and API calls
    curl \
    # Clean up package cache to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install uv package manager for fast Python dependency management
# hadolint ignore=DL3013
RUN pip install --no-cache-dir uv==0.8.0

# =============================================================================
# APPLICATION SETUP
# =============================================================================

# Create application directory with proper ownership
WORKDIR ${APP_HOME}

# Copy dependency specifications first for better Docker layer caching
# This allows dependency installation to be cached when source code changes
COPY --chown=${USER_UID}:${USER_GID} pyproject.toml uv.lock ./

# Copy source code (required for uv_build backend during dependency resolution)
COPY --chown=${USER_UID}:${USER_GID} src/ ./src/
COPY --chown=${USER_UID}:${USER_GID} README.md LICENSE ./

# Install Python dependencies using uv for faster installation
# --no-dev excludes development dependencies for smaller production image
# --locked ensures exact versions from uv.lock are used
RUN uv sync --no-dev --locked && \
    # Create logs directory for application logging
    mkdir -p logs output && \
    # Verify installation by checking if the package can be imported
    uv run python -c "import vmware_vra_cli.app; print('Installation verified successfully')"

# =============================================================================
# SECURITY: NON-ROOT USER SETUP
# =============================================================================

# Create a non-root user for security best practices
# Using specific UID/GID for consistency across environments
RUN groupadd --gid ${USER_GID} ${APP_USER} && \
    useradd --uid ${USER_UID} --gid ${USER_GID} --create-home --shell /bin/bash ${APP_USER} && \
    # Set proper ownership of application files
    chown -R ${APP_USER}:${APP_USER} ${APP_HOME}

# Switch to non-root user for security
USER ${APP_USER}

# =============================================================================
# RUNTIME CONFIGURATION
# =============================================================================

# Expose the application port
# Port 8000 is the default for the FastAPI/Uvicorn server
EXPOSE 8000

# Create mount points for persistent data
# These can be used with Docker volumes for persistent storage
VOLUME ["/app/logs", "/app/output", "/home/appuser/.config"]

# Configure health check for container orchestration
# This allows Docker/Kubernetes to monitor application health
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${UVICORN_PORT}/health || exit 1

# =============================================================================
# STARTUP COMMAND
# =============================================================================

# Default command to start the MCP server
# Uses environment variables for configuration flexibility
# Can be overridden at runtime with different parameters
CMD ["sh", "-c", "uvicorn vmware_vra_cli.app:app --host ${UVICORN_HOST} --port ${UVICORN_PORT} --log-level ${UVICORN_LOG_LEVEL}"]

# =============================================================================
# BUILD INFORMATION
# =============================================================================

# Add build-time information (can be overridden during build)
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL org.opencontainers.image.created=${BUILD_DATE}
LABEL org.opencontainers.image.revision=${VCS_REF}
LABEL org.opencontainers.image.version=${VERSION}
