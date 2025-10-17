"""Authentication endpoints for MCP server."""

from fastapi import APIRouter, HTTPException, status
from vmware_vra_cli.rest_server.models import (
    AuthRequest,
    AuthResponse,
    BaseResponse,
    ErrorResponse,
)
from vmware_vra_cli.auth import VRAAuthenticator, TokenManager
from vmware_vra_cli.config import save_login_config, get_config
import requests

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=AuthResponse)
async def login(auth_request: AuthRequest):
    """Authenticate to vRA and store tokens."""
    try:
        config = get_config()
        
        authenticator = VRAAuthenticator(auth_request.url, config["verify_ssl"])
        tokens = authenticator.authenticate(
            auth_request.username, 
            auth_request.password, 
            auth_request.domain
        )
        
        # Store tokens securely
        TokenManager.store_tokens(
            tokens['access_token'], 
            tokens['refresh_token']
        )
        
        # Save configuration parameters for future use
        save_login_config(
            api_url=auth_request.url, 
            tenant=auth_request.tenant, 
            domain=auth_request.domain
        )
        
        return AuthResponse(
            success=True,
            message="Authentication successful",
            token_stored=True,
            config_saved=True
        )
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


@router.post("/logout", response_model=BaseResponse)
async def logout():
    """Clear stored authentication tokens."""
    try:
        TokenManager.clear_tokens()
        return BaseResponse(
            success=True,
            message="Logged out successfully"
        )
    except Exception as e:
        return BaseResponse(
            success=True,
            message="No stored credentials found"
        )


@router.get("/status", response_model=BaseResponse)
async def status():
    """Check authentication status."""
    try:
        access_token = TokenManager.get_access_token()
        refresh_token = TokenManager.get_refresh_token()
        
        if access_token:
            message = "Authenticated (Access token available)"
            if refresh_token:
                message += " with refresh token for automatic renewal"
        elif refresh_token:
            message = "Only refresh token available - will obtain new access token on next use"
        else:
            message = "Not authenticated"
            
        return BaseResponse(
            success=bool(access_token or refresh_token),
            message=message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking authentication status: {str(e)}"
        )


@router.post("/refresh", response_model=BaseResponse)
async def refresh():
    """Manually refresh the access token."""
    try:
        config = get_config()
        new_token = TokenManager.refresh_access_token(
            config["api_url"], 
            config["verify_ssl"]
        )
        
        if new_token:
            return BaseResponse(
                success=True,
                message="Access token refreshed successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to refresh token. Please login again."
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing token: {str(e)}"
        )
