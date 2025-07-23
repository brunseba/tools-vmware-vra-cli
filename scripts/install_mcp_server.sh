#!/bin/bash

# VMware vRA MCP Server Installation Script
# This script installs and configures the VMware vRA MCP Server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Install Python package manager
install_uv() {
    log_info "Installing uv package manager..."
    
    if command_exists uv; then
        log_info "uv already installed: $(uv --version)"
        return 0
    fi
    
    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh || {
        log_error "Failed to install uv"
        return 1
    }
    
    # Add to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if command_exists uv; then
        log_success "uv installed successfully: $(uv --version)"
    else
        log_error "uv installation failed"
        return 1
    fi
}

# Install via pip
install_via_pip() {
    log_info "Installing VMware vRA CLI via pip..."
    
    if command_exists pip; then
        pip install vmware-vra-cli
    elif command_exists pip3; then
        pip3 install vmware-vra-cli
    else
        log_error "Neither pip nor pip3 found. Please install Python first."
        return 1
    fi
}

# Install from source
install_from_source() {
    log_info "Installing VMware vRA CLI from source..."
    
    # Check if we're already in the project directory
    if [[ -f "pyproject.toml" ]] && grep -q "vmware-vra-cli" pyproject.toml; then
        log_info "Already in project directory"
        PROJECT_DIR="."
    else
        log_info "Cloning repository..."
        git clone https://github.com/brun_s/vmware-vra-cli.git || {
            log_error "Failed to clone repository"
            return 1
        }
        PROJECT_DIR="vmware-vra-cli"
        cd "$PROJECT_DIR"
    fi
    
    # Install with uv
    if command_exists uv; then
        log_info "Installing with uv..."
        uv sync --extra dev
        log_success "Installation completed with uv"
    else
        log_info "Installing with pip..."
        pip install -e .
        log_success "Installation completed with pip"
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    if command_exists vra-mcp-server; then
        local version
        version=$(vra-mcp-server --help 2>&1 | head -1)
        log_success "MCP server installed successfully"
        log_info "Command: vra-mcp-server"
        
        # Test basic functionality
        log_info "Testing MCP server..."
        echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | timeout 5s vra-mcp-server 2>/dev/null && {
            log_success "MCP server responds correctly"
        } || {
            log_warning "MCP server test failed (this might be normal if vRA server is not configured)"
        }
    else
        log_error "MCP server not found in PATH"
        return 1
    fi
}

# Configure Claude Desktop
configure_claude() {
    local os_type
    os_type=$(detect_os)
    
    case $os_type in
        "macos")
            CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
            ;;
        "linux")
            CLAUDE_CONFIG_DIR="$HOME/.config/claude"
            ;;
        "windows")
            CLAUDE_CONFIG_DIR="$APPDATA/Claude"
            ;;
        *)
            log_warning "Unknown OS, skipping Claude Desktop configuration"
            return 0
            ;;
    esac
    
    log_info "Configuring Claude Desktop..."
    
    # Create config directory if it doesn't exist
    mkdir -p "$CLAUDE_CONFIG_DIR"
    
    local config_file="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
    
    # Check if config already exists
    if [[ -f "$config_file" ]]; then
        log_warning "Claude Desktop config already exists at: $config_file"
        read -p "Do you want to backup and replace it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp "$config_file" "$config_file.backup.$(date +%Y%m%d_%H%M%S)"
            log_info "Backed up existing config"
        else
            log_info "Skipping Claude Desktop configuration"
            return 0
        fi
    fi
    
    # Create configuration
    cat > "$config_file" << 'EOF'
{
  "mcpServers": {
    "vmware-vra": {
      "command": "vra-mcp-server",
      "args": ["--transport", "stdio"],
      "env": {
        "VRA_URL": "https://your-vra-server.com",
        "VRA_TENANT": "vsphere.local",
        "VRA_VERIFY_SSL": "true"
      }
    }
  }
}
EOF
    
    log_success "Claude Desktop configured at: $config_file"
    log_warning "Please update the VRA_URL and other settings in the config file"
}

# Main installation function
main() {
    echo "=============================================="
    echo "VMware vRA MCP Server Installation Script"
    echo "=============================================="
    echo
    
    log_info "Detected OS: $(detect_os)"
    
    # Parse command line arguments
    local install_method="auto"
    local configure_claude_flag=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --method)
                install_method="$2"
                shift 2
                ;;
            --configure-claude)
                configure_claude_flag=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo
                echo "OPTIONS:"
                echo "  --method METHOD     Installation method: auto, pip, source"
                echo "  --configure-claude  Configure Claude Desktop integration"
                echo "  --help             Show this help message"
                echo
                echo "EXAMPLES:"
                echo "  $0                          # Auto-detect best installation method"
                echo "  $0 --method pip             # Install via pip"
                echo "  $0 --method source          # Install from source"
                echo "  $0 --configure-claude       # Also configure Claude Desktop"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Check Python installation
    if ! command_exists python && ! command_exists python3; then
        log_error "Python is required but not installed. Please install Python 3.10+ first."
        exit 1
    fi
    
    local python_cmd
    if command_exists python3; then
        python_cmd="python3"
    else
        python_cmd="python"
    fi
    
    local python_version
    python_version=$($python_cmd --version 2>&1 | cut -d' ' -f2)
    log_info "Found Python: $python_version"
    
    # Determine installation method
    case $install_method in
        "auto")
            if [[ -f "pyproject.toml" ]] && grep -q "vmware-vra-cli" pyproject.toml; then
                log_info "Project directory detected, installing from source"
                install_method="source"
            else
                log_info "Installing via pip"
                install_method="pip"
            fi
            ;;
        "pip"|"source")
            log_info "Using specified method: $install_method"
            ;;
        *)
            log_error "Invalid installation method: $install_method"
            exit 1
            ;;
    esac
    
    # Install based on method
    case $install_method in
        "pip")
            install_via_pip || exit 1
            ;;
        "source")
            # Install uv for better source installation
            if ! command_exists uv; then
                install_uv || {
                    log_warning "Failed to install uv, falling back to pip"
                }
            fi
            install_from_source || exit 1
            ;;
    esac
    
    # Verify installation
    verify_installation || exit 1
    
    # Configure Claude Desktop if requested
    if [[ "$configure_claude_flag" == true ]]; then
        configure_claude
    fi
    
    echo
    echo "=============================================="
    log_success "Installation completed successfully!"
    echo "=============================================="
    echo
    log_info "Next steps:"
    echo "  1. Configure your vRA server settings"
    echo "  2. Test the installation:"
    echo "     vra-mcp-server --help"
    echo "  3. Check out examples:"
    echo "     python examples/mcp_client_examples.py"
    echo
    
    if [[ "$configure_claude_flag" != true ]]; then
        echo "  4. Configure Claude Desktop (optional):"
        echo "     $0 --configure-claude"
        echo
    fi
    
    log_info "Documentation: https://brun_s.github.io/vmware-vra-cli"
    log_info "Issues: https://github.com/brun_s/vmware-vra-cli/issues"
}

# Run main function with all arguments
main "$@"
