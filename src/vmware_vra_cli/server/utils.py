"""Utility functions for MCP server."""

from fastapi import HTTPException, status
from vmware_vra_cli.api.catalog import CatalogClient
from vmware_vra_cli.auth import TokenManager
from vmware_vra_cli.config import get_config


def get_catalog_client(verbose: bool = False) -> CatalogClient:
    """Get configured catalog client with automatic token refresh.
    
    Args:
        verbose: Whether to enable verbose HTTP logging
        
    Returns:
        CatalogClient instance
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        config = get_config()
        token = TokenManager.get_access_token()
        
        # Try to refresh token if access token is not available or expired
        if not token:
            token = TokenManager.refresh_access_token(
                config["api_url"], 
                config["verify_ssl"]
            )
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No valid authentication token found. Please authenticate first."
            )
        
        return CatalogClient(
            base_url=config["api_url"],
            token=token,
            verify_ssl=config["verify_ssl"],
            verbose=verbose
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating catalog client: {str(e)}"
        )


def handle_client_error(operation: str, error: Exception) -> HTTPException:
    """Handle client errors and convert to appropriate HTTP exceptions.
    
    Args:
        operation: Description of the operation that failed
        error: The original exception
        
    Returns:
        HTTPException with appropriate status code and message
    """
    if "401" in str(error) or "unauthorized" in str(error).lower():
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed during {operation}: {str(error)}"
        )
    elif "403" in str(error) or "forbidden" in str(error).lower():
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden during {operation}: {str(error)}"
        )
    elif "404" in str(error) or "not found" in str(error).lower():
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource not found during {operation}: {str(error)}"
        )
    elif "400" in str(error) or "bad request" in str(error).lower():
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bad request during {operation}: {str(error)}"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during {operation}: {str(error)}"
        )
