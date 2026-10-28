# Common.psm1 — shared helpers for RS Windows Cloud Workspace PowerShell scripts.
# Provides repo-relative paths, structured logging, JSON report writing and
# desktop screenshot capture. Loaded by every task script via Import-Module.
Set-StrictMode -Version Latest

function Get-RsRepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}

function Get-RsReportDir {
    $dir = Join-Path (Get-RsRepoRoot) 'reports'
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    return $dir
}

function Get-RsArtifactDir {
    $dir = Join-Path (Get-RsRepoRoot) 'artifacts'
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    return $dir
}

function Write-RsLog {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [string]$Level = 'INFO',
        [string]$LogPath
    )
    $line = '{0} [{1}] {2}' -f (Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK'), $Level, $Message
    Write-Host $line
    if ($LogPath) {
        $dir = Split-Path -Parent $LogPath
        if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        Add-Content -Path $LogPath -Value $line -Encoding UTF8
    }
}

function ConvertTo-RsJsonFile {
    param(
        [Parameter(Mandatory = $true)]$Data,
        [Parameter(Mandatory = $true)][string]$Path
    )
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $Data | ConvertTo-Json -Depth 10 | Set-Content -Path $Path -Encoding UTF8
}

function Capture-RsScreen {
    param(
        [string]$Name = 'screenshot',
        [string]$OutDir
    )
    if (-not $OutDir) { $OutDir = Join-Path (Get-RsArtifactDir) 'screenshots' }
    if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    $bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $bmp = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bmp)
    try {
        $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        $path = Join-Path $OutDir ('{0}-{1}.png' -f $Name, $stamp)
        $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
        return $path
    }
    finally {
        $graphics.Dispose()
        $bmp.Dispose()
    }
}

Export-ModuleMember -Function Get-RsRepoRoot, Get-RsReportDir, Get-RsArtifactDir, Write-RsLog, ConvertTo-RsJsonFile, Capture-RsScreen
