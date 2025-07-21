# PowerShell script to install GitHub CLI and go-task on Windows systems
# Supports multiple package managers: Winget, Chocolatey, Scoop, and direct download
# Requires execution policy to be set to allow running scripts

param(
    [Parameter()]
    [ValidateSet('winget', 'chocolatey', 'scoop', 'direct')]
    [string]$Method = 'auto'
)

# Color functions
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

# Check if command exists
function Test-Command {
    param($CommandName)
    return [bool](Get-Command $CommandName -ErrorAction SilentlyContinue)
}

# Detect best installation method
function Get-InstallationMethod {
    if ($Method -ne 'auto') {
        return $Method
    }
    
    if (Test-Command 'winget') {
        Write-Info "Detected Windows Package Manager (winget)"
        return 'winget'
    }
    elseif (Test-Command 'choco') {
        Write-Info "Detected Chocolatey"
        return 'chocolatey'
    }
    elseif (Test-Command 'scoop') {
        Write-Info "Detected Scoop"
        return 'scoop'
    }
    else {
        Write-Info "No package manager detected, using direct download"
        return 'direct'
    }
}

# Install GitHub CLI
function Install-GitHubCli {
    param($InstallMethod)
    
    Write-Info "Installing GitHub CLI..."
    
    if (Test-Command 'gh') {
        $version = gh --version 2>$null | Select-Object -First 1
        Write-Success "GitHub CLI is already installed: $version"
        return $true
    }

    try {
        switch ($InstallMethod) {
            'winget' {
                Write-Info "Installing via Windows Package Manager..."
                winget install --id GitHub.cli --exact --accept-package-agreements --accept-source-agreements
            }
            'chocolatey' {
                Write-Info "Installing via Chocolatey..."
                choco install gh -y
            }
            'scoop' {
                Write-Info "Installing via Scoop..."
                scoop install gh
            }
            'direct' {
                Write-Info "Installing via direct download..."
                Install-GitHubCliDirect
            }
        }
        
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine') + ';' + [System.Environment]::GetEnvironmentVariable('PATH', 'User')
        
        if (Test-Command 'gh') {
            $version = gh --version 2>$null | Select-Object -First 1
            Write-Success "GitHub CLI installed successfully: $version"
            return $true
        } else {
            Write-Error "GitHub CLI installation failed"
            return $false
        }
    }
    catch {
        Write-Error "Failed to install GitHub CLI: $($_.Exception.Message)"
        return $false
    }
}

# Direct GitHub CLI installation
function Install-GitHubCliDirect {
    $version = "2.40.1"
    $downloadUrl = "https://github.com/cli/cli/releases/download/v$version/gh_${version}_windows_amd64.msi"
    $installerPath = "$env:TEMP\gh-cli.msi"
    
    Write-Info "Downloading GitHub CLI from: $downloadUrl"
    
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
    
    Write-Info "Installing GitHub CLI..."
    Start-Process msiexec.exe -ArgumentList "/i `"$installerPath`" /quiet /norestart" -NoNewWindow -Wait
    
    Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
}

# Install Task (go-task)
function Install-GoTask {
    param($InstallMethod)
    
    Write-Info "Installing Task (go-task)..."
    
    if (Test-Command 'task') {
        $version = task --version 2>$null
        Write-Success "Task is already installed: $version"
        return $true
    }

    try {
        switch ($InstallMethod) {
            'winget' {
                Write-Info "Installing via Windows Package Manager..."
                winget install --id Task.Task --exact --accept-package-agreements --accept-source-agreements
            }
            'chocolatey' {
                Write-Info "Installing via Chocolatey..."
                choco install go-task -y
            }
            'scoop' {
                Write-Info "Installing via Scoop..."
                scoop install task
            }
            'direct' {
                Write-Info "Installing via direct download..."
                Install-GoTaskDirect
            }
        }
        
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine') + ';' + [System.Environment]::GetEnvironmentVariable('PATH', 'User')
        
        if (Test-Command 'task') {
            $version = task --version 2>$null
            Write-Success "Task installed successfully: $version"
            return $true
        } else {
            Write-Error "Task installation failed"
            return $false
        }
    }
    catch {
        Write-Error "Failed to install Task: $($_.Exception.Message)"
        return $false
    }
}

# Direct Task installation
function Install-GoTaskDirect {
    $version = "3.33.1"
    $downloadUrl = "https://github.com/go-task/task/releases/download/v$version/task_windows_amd64.zip"
    $zipPath = "$env:TEMP\task.zip"
    $extractPath = "$env:TEMP\task-extract"
    $installPath = "$env:LOCALAPPDATA\Programs\Task"
    
    Write-Info "Downloading Task from: $downloadUrl"
    
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing
    
    Write-Info "Extracting Task..."
    if (Test-Path $extractPath) { Remove-Item $extractPath -Recurse -Force }
    Expand-Archive $zipPath -DestinationPath $extractPath
    
    Write-Info "Installing Task to: $installPath"
    if (-not (Test-Path $installPath)) { New-Item -ItemType Directory -Path $installPath -Force }
    
    Copy-Item "$extractPath\task.exe" "$installPath\task.exe" -Force
    
    # Add to PATH
    $userPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
    if ($userPath -notlike "*$installPath*") {
        [Environment]::SetEnvironmentVariable('PATH', "$userPath;$installPath", 'User')
        $env:PATH += ";$installPath"
    }
    
    # Cleanup
    Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
    Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue
}

# Verify installations
function Test-Installations {
    Write-Info "Verifying installations..."
    
    $allGood = $true
    
    if (Test-Command 'gh') {
        $version = gh --version 2>$null | Select-Object -First 1
        Write-Success "✅ GitHub CLI: $version"
    } else {
        Write-Error "❌ GitHub CLI not found"
        $allGood = $false
    }
    
    if (Test-Command 'task') {
        $version = task --version 2>$null
        Write-Success "✅ Task: $version"
    } else {
        Write-Error "❌ Task not found"
        $allGood = $false
    }
    
    if ($allGood) {
        Write-Success "🎉 All tools installed successfully!"
        Write-Info "You may need to restart your terminal to use the tools."
    } else {
        Write-Error "Some tools failed to install. Please check the errors above."
        return $false
    }
    
    return $true
}

# Main installation function
function Main {
    Write-Info "🚀 Installing development tools for Windows..."
    
    # Check if running as administrator for some operations
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin -and $Method -eq 'direct') {
        Write-Warning "Running without administrator privileges. Some operations may fail."
    }
    
    # Detect installation method
    $installMethod = Get-InstallationMethod
    Write-Info "Using installation method: $installMethod"
    
    # Set execution policy for current session
    Set-ExecutionPolicy Bypass -Scope Process -Force
    
    # Install tools
    $ghSuccess = Install-GitHubCli -InstallMethod $installMethod
    $taskSuccess = Install-GoTask -InstallMethod $installMethod
    
    # Verify installations
    $verifySuccess = Test-Installations
    
    if ($verifySuccess) {
        Write-Info "🎯 Next steps:"
        Write-Info "1. Authenticate with GitHub: gh auth login"
        Write-Info "2. Run tasks in your project: task --list"
        Write-Info "3. Create GitHub labels: task labels:create"
    }
    
    return $verifySuccess
}

# Run main function
if ($MyInvocation.InvocationName -ne '.') {
    Main
}

