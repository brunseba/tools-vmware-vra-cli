#!/bin/bash

# Script to install GitHub CLI and go-task on Unix-like systems (Linux/macOS)
# Supports multiple package managers and platforms

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions for colored output
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect OS and architecture
detect_os() {
    case "$OSTYPE" in
        linux*)
            OS="linux"
            if command -v apt-get >/dev/null 2>&1; then
                PKG_MANAGER="apt"
            elif command -v yum >/dev/null 2>&1; then
                PKG_MANAGER="yum"
            elif command -v dnf >/dev/null 2>&1; then
                PKG_MANAGER="dnf"
            elif command -v pacman >/dev/null 2>&1; then
                PKG_MANAGER="pacman"
            elif command -v zypper >/dev/null 2>&1; then
                PKG_MANAGER="zypper"
            else
                PKG_MANAGER="generic"
            fi
            ;;
        darwin*)
            OS="macos"
            if command -v brew >/dev/null 2>&1; then
                PKG_MANAGER="brew"
            else
                PKG_MANAGER="generic"
            fi
            ;;
        *)
            OS="unknown"
            PKG_MANAGER="generic"
            ;;
    esac

    ARCH=$(uname -m)
    case $ARCH in
        x86_64) ARCH="amd64" ;;
        aarch64|arm64) ARCH="arm64" ;;
        armv7l) ARCH="arm" ;;
        *) ARCH="amd64" ;; # Default fallback
    esac
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install GitHub CLI
install_gh() {
    info "Installing GitHub CLI..."

    if command_exists gh; then
        success "GitHub CLI is already installed: $(gh --version)"
        return 0
    fi

    case $PKG_MANAGER in
        brew)
            info "Installing via Homebrew..."
            brew install gh
            ;;
        apt)
            info "Installing via APT..."
            # Add GitHub CLI repository
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
            chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
            sudo apt update
            sudo apt install -y gh
            ;;
        yum|dnf)
            info "Installing via $PKG_MANAGER..."
            sudo $PKG_MANAGER install -y 'dnf-command(config-manager)'
            sudo $PKG_MANAGER config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
            sudo $PKG_MANAGER install -y gh
            ;;
        pacman)
            info "Installing via Pacman..."
            sudo pacman -S --noconfirm github-cli
            ;;
        zypper)
            info "Installing via Zypper..."
            sudo zypper addrepo https://cli.github.com/packages/rpm/gh-cli.repo
            sudo zypper ref
            sudo zypper install -y gh
            ;;
        *)
            info "Installing via direct download..."
            install_gh_generic
            ;;
    esac

    if command_exists gh; then
        success "GitHub CLI installed successfully: $(gh --version)"
    else
        error "Failed to install GitHub CLI"
        return 1
    fi
}

# Generic GitHub CLI installation
install_gh_generic() {
    local version="2.40.1"  # Update this to latest version
    local download_url="https://github.com/cli/cli/releases/download/v${version}/gh_${version}_${OS}_${ARCH}.tar.gz"
    local temp_dir=$(mktemp -d)
    
    info "Downloading from: $download_url"
    curl -L "$download_url" -o "$temp_dir/gh.tar.gz"
    tar -xzf "$temp_dir/gh.tar.gz" -C "$temp_dir"
    
    # Find the extracted directory (it might have different naming)
    local extracted_dir=$(find "$temp_dir" -name "gh_*" -type d | head -n 1)
    
    if [ -d "$extracted_dir" ]; then
        sudo cp "$extracted_dir/bin/gh" /usr/local/bin/
        sudo chmod +x /usr/local/bin/gh
    else
        error "Could not find extracted GitHub CLI directory"
        return 1
    fi
    
    rm -rf "$temp_dir"
}

# Install Task (go-task)
install_task() {
    info "Installing Task (go-task)..."

    if command_exists task; then
        success "Task is already installed: $(task --version)"
        return 0
    fi

    case $PKG_MANAGER in
        brew)
            info "Installing via Homebrew..."
            brew install go-task/tap/go-task
            ;;
        apt)
            info "Installing via APT (Snapcraft)..."
            if command_exists snap; then
                sudo snap install task --classic
            else
                install_task_generic
            fi
            ;;
        pacman)
            info "Installing via AUR..."
            if command_exists yay; then
                yay -S --noconfirm go-task-bin
            elif command_exists paru; then
                paru -S --noconfirm go-task-bin
            else
                install_task_generic
            fi
            ;;
        *)
            info "Installing via direct download..."
            install_task_generic
            ;;
    esac

    if command_exists task; then
        success "Task installed successfully: $(task --version)"
    else
        error "Failed to install Task"
        return 1
    fi
}

# Generic Task installation
install_task_generic() {
    local version="3.33.1"  # Update this to latest version
    local download_url="https://github.com/go-task/task/releases/download/v${version}/task_${OS}_${ARCH}.tar.gz"
    local temp_dir=$(mktemp -d)
    
    info "Downloading from: $download_url"
    curl -L "$download_url" -o "$temp_dir/task.tar.gz"
    tar -xzf "$temp_dir/task.tar.gz" -C "$temp_dir"
    
    sudo cp "$temp_dir/task" /usr/local/bin/
    sudo chmod +x /usr/local/bin/task
    
    rm -rf "$temp_dir"
}

# Verify installations
verify_installations() {
    info "Verifying installations..."
    
    local all_good=true
    
    if command_exists gh; then
        success "✅ GitHub CLI: $(gh --version | head -n 1)"
    else
        error "❌ GitHub CLI not found"
        all_good=false
    fi
    
    if command_exists task; then
        success "✅ Task: $(task --version)"
    else
        error "❌ Task not found"
        all_good=false
    fi
    
    if $all_good; then
        success "🎉 All tools installed successfully!"
        info "You may need to restart your shell or run 'source ~/.bashrc' to use the tools."
    else
        error "Some tools failed to install. Please check the errors above."
        return 1
    fi
}

# Main installation function
main() {
    info "🚀 Installing development tools..."
    info "OS: $OS, Package Manager: $PKG_MANAGER, Architecture: $ARCH"
    
    detect_os
    
    # Check for required tools
    if ! command_exists curl; then
        error "curl is required but not installed. Please install curl first."
        exit 1
    fi
    
    if ! command_exists tar; then
        error "tar is required but not installed. Please install tar first."
        exit 1
    fi
    
    # Install tools
    install_gh
    install_task
    
    # Verify installations
    verify_installations
    
    info "🎯 Next steps:"
    info "1. Authenticate with GitHub: gh auth login"
    info "2. Run tasks in your project: task --list"
    info "3. Create GitHub labels: task labels:create"
}

# Run main function
main "$@"
