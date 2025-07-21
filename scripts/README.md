# Installation Scripts

This directory contains scripts to install the required development tools for the VMware vRA CLI project.

## Required Tools

The scripts install the following tools:

- **GitHub CLI (gh)** - Command-line interface for GitHub operations
- **Task (go-task)** - Task runner and build automation tool

## Usage

### Linux/macOS (Bash Script)

The bash script automatically detects your operating system and package manager:

```bash
# Make executable and run
chmod +x scripts/install-tools.sh
./scripts/install-tools.sh
```

#### Supported Package Managers (Linux/macOS)

- **macOS**: Homebrew
- **Ubuntu/Debian**: APT
- **RHEL/CentOS/Fedora**: YUM/DNF
- **Arch Linux**: Pacman (with AUR support)
- **openSUSE**: Zypper
- **Generic**: Direct download fallback

### Windows (PowerShell Script)

The PowerShell script supports multiple installation methods:

```powershell
# Run with default (auto-detect) method
.\scripts\install-tools.ps1

# Or specify a specific method
.\scripts\install-tools.ps1 -Method winget
.\scripts\install-tools.ps1 -Method chocolatey
.\scripts\install-tools.ps1 -Method scoop
.\scripts\install-tools.ps1 -Method direct
```

#### Supported Package Managers (Windows)

- **Windows Package Manager (winget)** - Recommended for Windows 10/11
- **Chocolatey** - Popular Windows package manager
- **Scoop** - Lightweight package manager
- **Direct Download** - Fallback method

#### Execution Policy

If you encounter execution policy errors, run PowerShell as Administrator and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Features

### Bash Script Features

- ✅ **Multi-platform support** (Linux distros + macOS)
- ✅ **Automatic OS and architecture detection**
- ✅ **Package manager auto-detection**
- ✅ **Colored output** for better readability
- ✅ **Error handling** and verification
- ✅ **Direct download fallback** when package managers aren't available

### PowerShell Script Features

- ✅ **Multiple installation methods** (Winget, Chocolatey, Scoop, Direct)
- ✅ **Automatic method detection**
- ✅ **Administrator privilege detection**
- ✅ **PATH management** for direct installations
- ✅ **Colored output** with status indicators
- ✅ **Error handling** and rollback

## After Installation

Once the tools are installed, you can:

1. **Authenticate with GitHub**:
   ```bash
   gh auth login
   ```

2. **List available tasks**:
   ```bash
   task --list
   ```

3. **Create GitHub labels**:
   ```bash
   task labels:create
   ```

4. **Setup development environment**:
   ```bash
   task setup
   ```

## Troubleshooting

### Common Issues

#### Linux/macOS

- **Permission denied**: Make sure the script is executable (`chmod +x scripts/install-tools.sh`)
- **Package manager not found**: The script will fallback to direct download
- **sudo required**: Some package managers require sudo privileges

#### Windows

- **Execution policy error**: 
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **Administrator privileges**: Some installation methods may require admin rights
- **PATH not updated**: Restart your terminal or PowerShell session

### Manual Installation

If the scripts fail, you can install the tools manually:

#### GitHub CLI
- **Linux/macOS**: Visit [GitHub CLI installation guide](https://github.com/cli/cli#installation)
- **Windows**: Download from [GitHub CLI releases](https://github.com/cli/cli/releases)

#### Task (go-task)
- **Linux/macOS**: Visit [Task installation guide](https://taskfile.dev/installation/)
- **Windows**: Download from [Task releases](https://github.com/go-task/task/releases)

## Version Information

The scripts install the following versions (update as needed):

- **GitHub CLI**: v2.40.1+
- **Task**: v3.33.1+

## Contributing

If you encounter issues or want to add support for additional package managers:

1. Test the script on your system
2. Report issues with OS/distribution details
3. Submit pull requests with improvements

## Security Note

These scripts download and install software from external sources. Always review the scripts before running them, especially in production environments.

---

*These installation scripts ensure all developers have the same tools and can quickly get started with the VMware vRA CLI project.*
