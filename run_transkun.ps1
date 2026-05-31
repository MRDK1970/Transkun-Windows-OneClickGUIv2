param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$AudioArgs
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogsDir = Join-Path $Root "logs"
$LogPath = Join-Path $LogsDir "run_transkun.log"
$SetupScript = Join-Path $Root "setup_runtime.ps1"
$VenvPython = Join-Path $Root "runtime\venv\Scripts\python.exe"
$Wrapper = Join-Path $Root "app\wrapper\transkun_wrapper.py"
$env:PYTHONIOENCODING = "utf-8"
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Log {
    param([string]$Message)
    $Time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogPath -Encoding UTF8 -Value "[$Time] $Message"
}

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host $Message -ForegroundColor Cyan
    Write-Log "STEP: $Message"
}

function Fail {
    param([string]$Message)
    Write-Log "ERROR: $Message"
    throw $Message
}

function Normalize-InputPath {
    param([string]$Value)
    if ($null -eq $Value) {
        return ""
    }

    $trimmed = $Value.Trim()
    if ($trimmed.Length -ge 2 -and $trimmed.StartsWith('"') -and $trimmed.EndsWith('"')) {
        $trimmed = $trimmed.Substring(1, $trimmed.Length - 2)
    }
    return $trimmed
}

function Invoke-Native {
    param([string[]]$Command)

    Write-Log ("RUN: " + ($Command -join " "))
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & $Command[0] @($Command[1..($Command.Length - 1)]) 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }

    foreach ($line in $output) {
        Add-Content -Path $LogPath -Encoding UTF8 -Value $line
        Write-Output $line
    }

    if ($exitCode -ne 0) {
        Fail ("Command failed with exit code {0}: {1}" -f $exitCode, ($Command -join " "))
    }
}

New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
"" | Set-Content -Path $LogPath -Encoding UTF8

Write-Host "========================================"
Write-Host "Transkun Windows OneClick"
Write-Host "========================================"
Write-Log "Transkun Windows OneClick started."
Write-Log "Root: $Root"

try {
    Write-Step "[1/4] Checking input file..."

    $audioPath = ""
    if ($AudioArgs -and $AudioArgs.Count -gt 0) {
        $audioPath = Normalize-InputPath ($AudioArgs -join " ")
    }

    if ([string]::IsNullOrWhiteSpace($audioPath)) {
        Write-Host "No dropped audio path was received."
        Write-Host "Paste the full audio file path, then press Enter."
        Write-Host "Press Enter without typing anything to cancel."
        $audioPath = Normalize-InputPath (Read-Host "Audio path")
    }

    if ([string]::IsNullOrWhiteSpace($audioPath)) {
        Fail "No input audio was provided."
    }

    $resolvedAudio = (Resolve-Path -LiteralPath $audioPath -ErrorAction Stop).Path
    if (-not (Test-Path -LiteralPath $resolvedAudio -PathType Leaf)) {
        Fail "Input audio file not found: $resolvedAudio"
    }
    Write-Log "Audio: $resolvedAudio"
    Write-Host "Input:"
    Write-Host "  $resolvedAudio"

    Write-Step "[2/4] Initializing runtime environment..."
    Write-Host "This can take several minutes on the first run."
    if (-not (Test-Path -LiteralPath $SetupScript -PathType Leaf)) {
        Fail "Missing setup_runtime.ps1. Please extract the full package again."
    }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $SetupScript
    if ($LASTEXITCODE -ne 0) {
        Fail "Runtime setup failed. See logs/setup_runtime.log."
    }

    Write-Step "[3/4] Running Transkun transcription..."
    Write-Host "This can also take a while for long audio."
    if (-not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
        Fail "Missing runtime Python venv: $VenvPython"
    }
    if (-not (Test-Path -LiteralPath $Wrapper -PathType Leaf)) {
        Fail "Missing wrapper script: $Wrapper"
    }
    Invoke-Native @($VenvPython, $Wrapper, $resolvedAudio)

    Write-Step "[4/4] Done. Check the output folder."
    Write-Host ""
    Write-Host "Output folder:"
    Write-Host "  $(Join-Path $Root 'output')"
    Write-Log "Done."
    exit 0
} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "See log:"
    Write-Host "  $LogPath"
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}
