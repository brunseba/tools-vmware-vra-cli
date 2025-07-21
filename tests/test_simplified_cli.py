"""Tests for a simplified CLI module."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from vmware_vra_cli.cli import main, auth


class TestSimplifiedCLI:
    """Simple test cases for main CLI."""
    
    def test_main_help(self):
        """Test CLI main help output."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert 'CLI tool to interact with VMware vRealize Automation' in result.output

    @patch('vmware_vra_cli.cli.save_login_config')
    @patch('vmware_vra_cli.cli.TokenManager')
    @patch('vmware_vra_cli.cli.get_config')
    @patch('vmware_vra_cli.cli.VRAAuthenticator')
    def test_auth_login_command(self, mock_authenticator, mock_get_config, mock_token_manager, mock_save_login):
        """Test simplified login command."""
        # Setup mocks
        mock_get_config.return_value = {'verify_ssl': True}
        
        mock_instance = MagicMock()
        mock_instance.authenticate.return_value = {
            'access_token': 'test-access-token',
            'refresh_token': 'test-refresh-token'
        }
        mock_authenticator.return_value = mock_instance
        
        runner = CliRunner()
        result = runner.invoke(auth, ['login', '--username=test', '--password=test', '--url=https://test.com', '--tenant=test'])
        
        # Check if command succeeded or print error for debugging
        if result.exit_code != 0:
            print(f"Command output: {result.output}")
            print(f"Exception: {result.exception}")
        
        assert result.exit_code == 0
        mock_instance.authenticate.assert_called_once_with('test', 'test', None)
