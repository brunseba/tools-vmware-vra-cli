"""VMware vRA Authentication Module

This module implements the proper two-step authentication procedure for VMware vRealize Automation 8.x
as documented in the official VMware documentation.

Step 1: Obtain refresh token from Identity Service API
Step 2: Exchange refresh token for access token via IaaS API

The refresh token is valid for 90 days and the access token is valid for 8 hours.
"""

import requests
from typing import Optional, Dict, Any
from rich.console import Console
import keyring

console = Console()


class VRAAuthenticator:
    """VMware vRA Authentication handler implementing the two-step procedure."""
    
    def __init__(self, base_url: str, verify_ssl: bool = True):
        """Initialize the authenticator.
        
        Args:
            base_url: Base URL of the vRA instance (e.g., https://vra.company.com)
            verify_ssl: Whether to verify SSL certificates
        """
        # Validate and normalize base URL
        if not base_url:
            raise ValueError("Base URL cannot be empty")
        
        # Ensure proper protocol
        if not base_url.startswith(('http://', 'https://')):
            base_url = f'https://{base_url}'
        
        # Fix common URL malformations
        if base_url.startswith('https:/') and not base_url.startswith('https://'):
            base_url = base_url.replace('https:/', 'https://')
        elif base_url.startswith('http:/') and not base_url.startswith('http://'):
            base_url = base_url.replace('http:/', 'http://')
        
        self.base_url = base_url.rstrip('/')
        self.verify_ssl = verify_ssl
    
    def authenticate(self, username: str, password: str, domain: Optional[str] = None) -> Dict[str, str]:
        """Perform two-step authentication to obtain both refresh and access tokens.
        
        Args:
            username: Username for vRA access
            password: Password for vRA access
            domain: Optional domain for multiple identity sources
            
        Returns:
            Dictionary containing 'access_token' and 'refresh_token'
            
        Raises:
            requests.RequestException: If authentication fails
        """
        # Step 1: Obtain refresh token from Identity Service API
        refresh_token = self._get_refresh_token(username, password, domain)
        
        # Step 2: Exchange refresh token for access token via IaaS API
        access_token = self._exchange_refresh_token(refresh_token)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    
    def _get_refresh_token(self, username: str, password: str, domain: Optional[str] = None) -> str:
        """Step 1: Get refresh token from Identity Service API.
        
        Args:
            username: Username for vRA access
            password: Password for vRA access
            domain: Optional domain for multiple identity sources
            
        Returns:
            Refresh token (valid for 90 days)
            
        Raises:
            requests.RequestException: If the request fails
        """
        auth_url = f"{self.base_url}/csp/gateway/am/api/login?access_token"
        
        payload = {
            "username": username,
            "password": password
        }
        
        # Add domain if specified for multiple identity sources
        if domain:
            payload["domain"] = domain
        
        response = requests.post(
            auth_url,
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            verify=self.verify_ssl
        )
        response.raise_for_status()
        
        return response.json()['refresh_token']
    
    def _exchange_refresh_token(self, refresh_token: str) -> str:
        """Step 2: Exchange refresh token for access token via IaaS API.
        
        Args:
            refresh_token: The refresh token from step 1
            
        Returns:
            Access token (valid for 8 hours)
            
        Raises:
            requests.RequestException: If the request fails
        """
        iaas_url = f"{self.base_url}/iaas/api/login"
        
        response = requests.post(
            iaas_url,
            json={"refreshToken": refresh_token},
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            verify=self.verify_ssl
        )
        response.raise_for_status()
        
        return response.json()['token']
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh the access token using a stored refresh token.
        
        Args:
            refresh_token: The stored refresh token
            
        Returns:
            New access token if successful, None otherwise
        """
        try:
            return self._exchange_refresh_token(refresh_token)
        except requests.RequestException:
            return None


class TokenManager:
    """Secure token storage and management using the system keyring."""
    
    SERVICE_NAME = "vmware-vra-cli"
    ACCESS_TOKEN_KEY = "access_token"
    REFRESH_TOKEN_KEY = "refresh_token"
    
    @classmethod
    def store_tokens(cls, access_token: str, refresh_token: str) -> None:
        """Store authentication tokens securely in the system keyring.
        
        Args:
            access_token: The access token to store
            refresh_token: The refresh token to store
        """
        try:
            keyring.set_password(cls.SERVICE_NAME, cls.ACCESS_TOKEN_KEY, access_token)
            keyring.set_password(cls.SERVICE_NAME, cls.REFRESH_TOKEN_KEY, refresh_token)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not store tokens securely: {e}[/yellow]")
    
    @classmethod
    def get_access_token(cls) -> Optional[str]:
        """Retrieve the stored access token.
        
        Returns:
            Access token if available, None otherwise
        """
        try:
            return keyring.get_password(cls.SERVICE_NAME, cls.ACCESS_TOKEN_KEY)
        except Exception:
            return None
    
    @classmethod
    def get_refresh_token(cls) -> Optional[str]:
        """Retrieve the stored refresh token.
        
        Returns:
            Refresh token if available, None otherwise
        """
        try:
            return keyring.get_password(cls.SERVICE_NAME, cls.REFRESH_TOKEN_KEY)
        except Exception:
            return None
    
    @classmethod
    def clear_tokens(cls) -> None:
        """Clear all stored authentication tokens."""
        try:
            keyring.delete_password(cls.SERVICE_NAME, cls.ACCESS_TOKEN_KEY)
        except Exception:
            pass
        try:
            keyring.delete_password(cls.SERVICE_NAME, cls.REFRESH_TOKEN_KEY)
        except Exception:
            pass
    
    @classmethod
    def refresh_access_token(cls, base_url: str, verify_ssl: bool = True) -> Optional[str]:
        """Refresh the access token using the stored refresh token.
        
        Args:
            base_url: Base URL of the vRA instance
            verify_ssl: Whether to verify SSL certificates
            
        Returns:
            New access token if successful, None otherwise
        """
        refresh_token = cls.get_refresh_token()
        if not refresh_token:
            return None
        
        authenticator = VRAAuthenticator(base_url, verify_ssl)
        new_access_token = authenticator.refresh_access_token(refresh_token)
        
        if new_access_token:
            # Store the new access token
            keyring.set_password(cls.SERVICE_NAME, cls.ACCESS_TOKEN_KEY, new_access_token)
            return new_access_token
        else:
            # Refresh token might be expired, clear stored tokens
            cls.clear_tokens()
        
        return None
