# Installation

This guide will help you install VMware vRA CLI on your system.

## Prerequisites

!!! info "System Requirements"
    - Python 3.10 or higher
    - Network access to your VMware vRA 8 environment
    - Valid vRA user credentials

## Installation Methods

### Option 1: Install with pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) is the recommended way to install Python CLI applications:

```bash
# Install pipx if you haven't already
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install VMware vRA CLI
pipx install vmware-vra-cli
```

### Option 2: Install with pip

```bash
pip install vmware-vra-cli
```

### Option 3: Install from source

For development or the latest features:

```bash
# Clone the repository
git clone https://github.com/brun_s/vmware-vra-cli.git
cd vmware-vra-cli

# Install with uv (recommended)
uv sync --extra dev
uv run vra --help

# Or install with pip
pip install -e .
```

## Verification

Verify your installation:

```bash
vra --version
```

You should see output similar to:

```
VMware vRA CLI v0.1.0
```

## Next Steps

Now that you have the CLI installed, you can:

1. **[Configure your environment](configuration.md)** - Set up your vRA connection
2. **[Try the Quick Start guide](quick-start.md)** - Create your first VM
3. **[Read the User Guide](../user-guide/authentication.md)** - Learn about advanced features

## Troubleshooting

### Common Issues

#### Python Version Error

```bash
ERROR: Python 3.10 or higher is required
```

**Solution**: Upgrade your Python version or use a virtual environment with Python 3.10+.

#### Permission Denied

```bash
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solution**: Use `--user` flag or install in a virtual environment:

```bash
pip install --user vmware-vra-cli
```

#### Command Not Found

```bash
vra: command not found
```

**Solution**: Ensure your PATH includes the Python scripts directory:

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export PATH="$PATH:$HOME/.local/bin"
```

### Getting Help

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/brun_s/vmware-vra-cli/issues)
2. Create a new issue with:
   - Your operating system
   - Python version (`python --version`)
   - Error message or unexpected behavior
   - Steps to reproduce
