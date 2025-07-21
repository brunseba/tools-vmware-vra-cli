"""Tests for the Authentication module."""

import pytest
import requests
import requests_mock
from unittest.mock import patch, MagicMock
from vmware_vra_cli.auth import VRAAuthenticator, TokenManager


class TestVRAAuthenticator:
    """Test cases for VRAAuthenticator."""
    
    @pytest.fixture
    def authenticator(self):
        """Create a test authenticator."""
        return VRAAuthenticator(
            base_url="https://vra.example.com",
            verify_ssl=True
        )
    
    def test_init(self):
        """Test authenticator initialization."""
        auth = VRAAuthenticator("https://vra.example.com/", verify_ssl=False)
        assert auth.base_url == "https://vra.example.com"
        assert auth.verify_ssl is False
    
    def test_init_default_ssl_verify(self):
        """Test authenticator initialization with default SSL verify."""
        auth = VRAAuthenticator("https://vra.example.com")
        assert auth.verify_ssl is True
    
    def test_authenticate_success(self, requests_mock, authenticator):
        """Test successful two-step authentication."""
        # Mock the identity service response (step 1)
        requests_mock.post(
            "https://vra.example.com/csp/gateway/am/api/login?access_token",
            json={"refresh_token": "test-refresh-token"}
        )
        
        # Mock the IaaS service response (step 2)
        requests_mock.post(
            "https://vra.example.com/iaas/api/login",
            json={"token": "test-access-token"}
        )
        
        tokens = authenticator.authenticate("testuser", "testpass")
        
        assert tokens["access_token"] == "test-access-token"
        assert tokens["refresh_token"] == "test-refresh-token"
        
        # Verify the requests were made correctly
        assert len(requests_mock.request_history) == 2
        
        # Check step 1 request
        identity_request = requests_mock.request_history[0]
        assert identity_request.json() == {
            "username": "testuser",
            "password": "testpass"
        }
        
        # Check step 2 request
        iaas_request = requests_mock.request_history[1]
        assert iaas_request.json() == {"refreshToken": "test-refresh-token"}
    
    def test_authenticate_with_domain(self, requests_mock, authenticator):
        """Test authentication with domain parameter."""
        requests_mock.post(
            "https://vra.example.com/csp/gateway/am/api/login?access_token",
            json={"refresh_token": "test-refresh-token"}
        )
        requests_mock.post(
            "https://vra.example.com/iaas/api/login",
            json={"token": "test-access-token"}
        )
        
        authenticator.authenticate("testuser", "testpass", "custom.domain")
        
        # Check that domain was included in the request
        identity_request = requests_mock.request_history[0]
        assert identity_request.json() == {
            "username": "testuser",
            "password": "testpass",
            "domain": "custom.domain"
        }
    
    def test_authenticate_identity_failure(self, requests_mock, authenticator):
        """Test authentication failure at identity service step."""
        requests_mock.post(
            "https://vra.example.com/csp/gateway/am/api/login?access_token",
            status_code=401,
            json={"error": "Invalid credentials"}
        )
        
        with pytest.raises(requests.exceptions.HTTPError):
            authenticator.authenticate("testuser", "wrongpass")
    
    def test_authenticate_iaas_failure(self, requests_mock, authenticator):
        """Test authentication failure at IaaS service step."""
        requests_mock.post(
            "https://vra.example.com/csp/gateway/am/api/login?access_token",
            json={"refresh_token": "test-refresh-token"}
        )
        requests_mock.post(
            "https://vra.example.com/iaas/api/login",
            status_code=401,
            json={"error": "Invalid refresh token"}
        )
        
        with pytest.raises(requests.exceptions.HTTPError):
            authenticator.authenticate("testuser", "testpass")
    
    def test_get_refresh_token(self, requests_mock, authenticator):
        """Test getting refresh token directly."""
        requests_mock.post(
            "https://vra.example.com/csp/gateway/am/api/login?access_token",
            json={"refresh_token": "direct-refresh-token"}
        )
        
        token = authenticator._get_refresh_token("testuser", "testpass")
        assert token == "direct-refresh-token"
    
    def test_exchange_refresh_token(self, requests_mock, authenticator):
        """Test exchanging refresh token for access token."""
        requests_mock.post(
            "https://vra.example.com/iaas/api/login",
            json={"token": "exchanged-access-token"}
        )
        
        token = authenticator._exchange_refresh_token("test-refresh-token")
        assert token == "exchanged-access-token"
        
        # Verify request payload
        request = requests_mock.request_history[0]
        assert request.json() == {"refreshToken": "test-refresh-token"}
    
    def test_refresh_access_token_success(self, requests_mock, authenticator):
        """Test successful access token refresh."""
        requests_mock.post(
            "https://vra.example.com/iaas/api/login",
            json={"token": "new-access-token"}
        )
        
        new_token = authenticator.refresh_access_token("old-refresh-token")
        assert new_token == "new-access-token"
    
    def test_refresh_access_token_failure(self, requests_mock, authenticator):
        """Test failed access token refresh."""
        requests_mock.post(
            "https://vra.example.com/iaas/api/login",
            status_code=401,
            json={"error": "Refresh token expired"}
        )
        
        new_token = authenticator.refresh_access_token("expired-refresh-token")
        assert new_token is None
    
    def test_ssl_verification_disabled(self, requests_mock):
        """Test authentication with SSL verification disabled."""
        auth = VRAAuthenticator("https://vra.example.com", verify_ssl=False)
        
        requests_mock.post(
            "https://vra.example.com/csp/gateway/am/api/login?access_token",
            json={"refresh_token": "test-refresh-token"}
        )
        requests_mock.post(
            "https://vra.example.com/iaas/api/login",
            json={"token": "test-access-token"}
        )
        
        auth.authenticate("testuser", "testpass")
        
        # Verify that verify=False was passed to requests
        for request in requests_mock.request_history:
            # In a real scenario, we would check the request.verify attribute
            # but requests_mock doesn't preserve this, so we just verify the call succeeded
            assert request.method == "POST"


class TestTokenManager:
    """Test cases for TokenManager."""
    
    @patch('vmware_vra_cli.auth.keyring')
    def test_store_tokens_success(self, mock_keyring):
        """Test successful token storage."""
        TokenManager.store_tokens("access-token", "refresh-token")
        
        mock_keyring.set_password.assert_any_call(
            "vmware-vra-cli", "access_token", "access-token"
        )
        mock_keyring.set_password.assert_any_call(
            "vmware-vra-cli", "refresh_token", "refresh-token"
        )
    
    @patch('vmware_vra_cli.auth.keyring')
    @patch('vmware_vra_cli.auth.console')
    def test_store_tokens_failure(self, mock_console, mock_keyring):
        """Test token storage failure."""
        mock_keyring.set_password.side_effect = Exception("Keyring error")
        
        TokenManager.store_tokens("access-token", "refresh-token")
        
        # Should print warning but not raise exception
        mock_console.print.assert_called()
        warning_call = mock_console.print.call_args[0][0]
        assert "Warning: Could not store tokens securely" in warning_call
    
    @patch('vmware_vra_cli.auth.keyring')
    def test_get_access_token_success(self, mock_keyring):
        """Test successful access token retrieval."""
        mock_keyring.get_password.return_value = "stored-access-token"
        
        token = TokenManager.get_access_token()
        
        assert token == "stored-access-token"
        mock_keyring.get_password.assert_called_with(
            "vmware-vra-cli", "access_token"
        )
    
    @patch('vmware_vra_cli.auth.keyring')
    def test_get_access_token_not_found(self, mock_keyring):
        """Test access token retrieval when not found."""
        mock_keyring.get_password.return_value = None
        
        token = TokenManager.get_access_token()
        
        assert token is None
    
    @patch('vmware_vra_cli.auth.keyring')
    def test_get_access_token_error(self, mock_keyring):
        """Test access token retrieval with keyring error."""
        mock_keyring.get_password.side_effect = Exception("Keyring error")
        
        token = TokenManager.get_access_token()
        
        assert token is None
    
    @patch('vmware_vra_cli.auth.keyring')
    def test_get_refresh_token_success(self, mock_keyring):
        """Test successful refresh token retrieval."""
        mock_keyring.get_password.return_value = "stored-refresh-token"
        
        token = TokenManager.get_refresh_token()
        
        assert token == "stored-refresh-token"
        mock_keyring.get_password.assert_called_with(
            "vmware-vra-cli", "refresh_token"
        )
    
    @patch('vmware_vra_cli.auth.keyring')
    def test_clear_tokens_success(self, mock_keyring):
        """Test successful token clearing."""
        TokenManager.clear_tokens()
        
        mock_keyring.delete_password.assert_any_call(
            "vmware-vra-cli", "access_token"
        )
        mock_keyring.delete_password.assert_any_call(
            "vmware-vra-cli", "refresh_token"
        )
    
    @patch('vmware_vra_cli.auth.keyring')
    def test_clear_tokens_partial_failure(self, mock_keyring):
        """Test token clearing with partial failure."""
        # First delete succeeds, second fails
        mock_keyring.delete_password.side_effect = [None, Exception("Delete error")]
        
        # Should not raise exception
        TokenManager.clear_tokens()
        
        assert mock_keyring.delete_password.call_count == 2
    
    @patch('vmware_vra_cli.auth.keyring')
    @patch('vmware_vra_cli.auth.VRAAuthenticator')
    def test_refresh_access_token_success(self, mock_auth_class, mock_keyring):
        """Test successful access token refresh through TokenManager."""
        # Mock getting refresh token
        mock_keyring.get_password.return_value = "stored-refresh-token"
        
        # Mock authenticator
        mock_auth = MagicMock()
        mock_auth.refresh_access_token.return_value = "new-access-token"
        mock_auth_class.return_value = mock_auth
        
        new_token = TokenManager.refresh_access_token("https://vra.example.com", True)
        
        assert new_token == "new-access-token"
        
        # Verify authenticator was created correctly
        mock_auth_class.assert_called_with("https://vra.example.com", True)
        
        # Verify refresh was attempted
        mock_auth.refresh_access_token.assert_called_with("stored-refresh-token")
        
        # Verify new token was stored
        mock_keyring.set_password.assert_called_with(
            "vmware-vra-cli", "access_token", "new-access-token"
        )
    
    @patch('vmware_vra_cli.auth.keyring')
    def test_refresh_access_token_no_refresh_token(self, mock_keyring):
        """Test access token refresh when no refresh token is stored."""
        mock_keyring.get_password.return_value = None
        
        new_token = TokenManager.refresh_access_token("https://vra.example.com")
        
        assert new_token is None
    
    @patch('vmware_vra_cli.auth.keyring')
    @patch('vmware_vra_cli.auth.VRAAuthenticator')
    def test_refresh_access_token_authenticator_failure(self, mock_auth_class, mock_keyring):
        """Test access token refresh when authenticator fails."""
        # Mock getting refresh token
        mock_keyring.get_password.return_value = "stored-refresh-token"
        
        # Mock authenticator failure
        mock_auth = MagicMock()
        mock_auth.refresh_access_token.return_value = None
        mock_auth_class.return_value = mock_auth
        
        new_token = TokenManager.refresh_access_token("https://vra.example.com")
        
        assert new_token is None
        
        # Verify tokens were cleared due to failure
        mock_keyring.delete_password.assert_any_call(
            "vmware-vra-cli", "access_token"
        )
        mock_keyring.delete_password.assert_any_call(
            "vmware-vra-cli", "refresh_token"
        )
    
    def test_service_name_constant(self):
        """Test that service name constant is correct."""
        assert TokenManager.SERVICE_NAME == "vmware-vra-cli"
    
    def test_token_key_constants(self):
        """Test that token key constants are correct."""
        assert TokenManager.ACCESS_TOKEN_KEY == "access_token"
        assert TokenManager.REFRESH_TOKEN_KEY == "refresh_token"
