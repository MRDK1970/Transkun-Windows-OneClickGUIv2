$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$RuntimeDir = Join-Path $Root "runtime"
$PortablePython = Join-Path $RuntimeDir "python\python.exe"
$VenvDir = Join-Path $RuntimeDir "venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$WheelsDir = Join-Path $RuntimeDir "wheels"
$FfmpegExe = Join-Path $RuntimeDir "ffmpeg\bin\ffmpeg.exe"
$FfprobeExe = Join-Path $RuntimeDir "ffmpeg\bin\ffprobe.exe"
$Requirements = Join-Path $Root "requirements.lock.txt"
$Stamp = Join-Path $Root ".transkun_runtime_ok"
$LogsDir = Join-Path $Root "logs"
$LogPath = Join-Path $LogsDir "setup_runtime.log"

New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null

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

function Invoke-Native {
    param([string[]]$Command)

    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & $Command[0] @($Command[1..($Command.Length - 1)]) 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }

    return @{
        ExitCode = $exitCode
        Output = $output
    }
}

function Run-Logged {
    param([string[]]$Command)
    Write-Log ("RUN: " + ($Command -join " "))
    $Result = Invoke-Native $Command
    foreach ($Line in $Result.Output) {
        Add-Content -Path $LogPath -Encoding UTF8 -Value $Line
        Write-Output $Line
    }
    if ($Result.ExitCode -ne 0) {
        Fail ("Command failed with exit code {0}: {1}" -f $Result.ExitCode, ($Command -join " "))
    }
}

function Test-Imports {
    if (-not (Test-Path $VenvPython)) {
        return $false
    }

    $Code = "import torch, torchaudio, ncls, pretty_midi, pydub, soxr, moduleconf, tkinterdnd2; print('imports ok')"
    $Result = Invoke-Native @($VenvPython, "-c", $Code)
    foreach ($Line in $Result.Output) {
        Write-Log $Line
    }
    return ($Result.ExitCode -eq 0)
}

function Test-Pip {
    if (-not (Test-Path $VenvPython)) {
        return $false
    }

    $Result = Invoke-Native @($VenvPython, "-m", "pip", "--version")
    foreach ($Line in $Result.Output) {
        Write-Log $Line
    }
    return ($Result.ExitCode -eq 0)
}

function Test-BundledPython {
    $VenvModule = Join-Path $RuntimeDir "python\Lib\venv\__init__.py"
    $EnsurePipModule = Join-Path $RuntimeDir "python\Lib\ensurepip\__init__.py"

    if (-not (Test-Path -LiteralPath $VenvModule -PathType Leaf)) {
        Fail "Bundled Python is incomplete: missing $VenvModule. Please extract the full package again."
    }
    if (-not (Test-Path -LiteralPath $EnsurePipModule -PathType Leaf)) {
        Fail "Bundled Python is incomplete: missing $EnsurePipModule. Please extract the full package again."
    }

    $Result = Invoke-Native @($PortablePython, "-c", "import venv, ensurepip; print('bundled python ok')")
    foreach ($Line in $Result.Output) {
        Write-Log $Line
    }
    if ($Result.ExitCode -ne 0) {
        Fail "Bundled Python cannot import venv/ensurepip. Please extract the full package again."
    }

    $Result = Invoke-Native @($PortablePython, "-m", "venv", "--help")
    if ($Result.ExitCode -ne 0) {
        foreach ($Line in $Result.Output) {
            Write-Log $Line
        }
        Fail "Bundled Python cannot run 'python -m venv'. Please extract the full package again."
    }
}

"" | Set-Content -Path $LogPath -Encoding UTF8
Write-Log "Starting Transkun runtime setup."
Write-Host "Transkun runtime setup"
Write-Host "Log: $LogPath"

Write-Step "[setup 1/6] Checking bundled runtime files..."
if (-not (Test-Path $PortablePython)) {
    Fail "Missing bundled Python: $PortablePython"
}
if (-not (Test-Path $WheelsDir)) {
    Fail "Missing wheelhouse directory: $WheelsDir"
}
if (-not (Test-Path $Requirements)) {
    Fail "Missing requirements lock file: $Requirements"
}
if (-not (Test-Path $FfmpegExe)) {
    Fail "Missing bundled FFmpeg: $FfmpegExe"
}
if (-not (Test-Path $FfprobeExe)) {
    Fail "Missing bundled FFprobe: $FfprobeExe"
}
Test-BundledPython

$FfmpegBin = Split-Path -Parent $FfmpegExe
$env:PATH = "$FfmpegBin;$env:PATH"
Write-Log "Prepended bundled FFmpeg to PATH: $FfmpegBin"

Write-Step "[setup 2/6] Checking existing runtime environment..."
if ((Test-Path $Stamp) -and (Test-Imports)) {
    Write-Log "Runtime already initialized and import validation passed."
    Write-Host "Runtime already initialized."
    exit 0
}

if (Test-Path $VenvDir) {
    Write-Log "Removing invalid or incomplete runtime venv: $VenvDir"
    Write-Host "Removing invalid or incomplete runtime venv..."
    Remove-Item -LiteralPath $VenvDir -Recurse -Force
}

Write-Step "[setup 3/6] Creating private Python venv..."
Run-Logged @($PortablePython, "-m", "venv", $VenvDir)

Write-Step "[setup 4/6] Checking pip in the private venv..."
if (-not (Test-Pip)) {
    Run-Logged @($VenvPython, "-m", "ensurepip", "--upgrade")
}

if (-not (Test-Pip)) {
    Fail "pip is not available in the runtime venv."
}

Write-Step "[setup 5/6] Installing dependencies from local wheels..."
Write-Host "This step can take several minutes on the first run."
Run-Logged @($VenvPython, "-m", "pip", "install", "--no-index", "--find-links", $WheelsDir, "-r", $Requirements)

Write-Step "[setup 6/6] Validating Python imports..."
if (-not (Test-Imports)) {
    Fail "Runtime import validation failed."
}

"ok $(Get-Date -Format o)" | Set-Content -Path $Stamp -Encoding UTF8
Write-Log "Runtime setup completed successfully."
Write-Host "Runtime setup completed successfully."
exit 0
