# Transkun Windows OneClick User Guide

Transkun Windows OneClick is a portable Windows x64 piano audio-to-MIDI package. It includes Python, FFmpeg, offline wheels, Transkun model files, and a simple GUI. Users do not need to install Python, FFmpeg, PyTorch, or Visual Studio Build Tools.

## Quick Start

1. Extract `Transkun-Windows-OneClick.7z`.
2. Open the extracted `Transkun-Windows-OneClick` folder.
3. Double-click `Transkun GUI.exe`.
4. Drag a piano audio file into the window, or click Browse.
5. Click Convert.
6. Click Open Output when conversion finishes.

Example output:

```text
output/song_raw.mid
output/song_baked.mid
```

## First Run

The first conversion creates a private runtime environment:

```text
runtime/venv
```

This can take several minutes. Later conversions reuse the initialized environment and start faster.

You do not need to run `setup_runtime.ps1` manually. The GUI and command-line launchers run setup automatically when needed.

## Example Audio Smoke Test

The package includes:

```text
example.mp3
```

Open `Transkun GUI.exe`, drag `example.mp3` into the window, then click Convert.

Expected output:

```text
output/example_raw.mid
output/example_baked.mid
```

## Output Files

- `<name>_raw.mid`
  - Raw Transkun MIDI.
  - Keeps sustain pedal CC64 events.

- `<name>_baked.mid`
  - Sustain pedal is baked into note durations.
  - CC64 is removed by default.
  - Better for piano-roll editing in DAWs such as FL Studio.

## Supported Input

Common audio formats usually work:

```text
.mp3
.wav
.flac
.m4a
```

File names may contain Chinese characters, spaces, and parentheses. The wrapper internally copies the input to a safe temporary file name before processing, while the output MIDI keeps the original file name.

## Other Ways To Run

GUI debug launcher:

```bat
run_transkun_gui.bat
```

PowerShell:

```powershell
Set-Location "C:\Path\To\Transkun-Windows-OneClick"
.\run_transkun.ps1 "C:\Path\To\audio.wav"
```

cmd:

```bat
cd /d "C:\Path\To\Transkun-Windows-OneClick"
run_transkun.bat "C:\Path\To\audio.wav"
```

## Logs and Troubleshooting

If something fails, check:

```text
logs/setup_runtime.log
logs/latest.log
logs/run_transkun.log
logs/gui_debug.log
```

Common fixes:

- Fully extract the package before running it. Do not run from inside archive preview.
- Allow `Transkun GUI.exe`, `runtime/python/python.exe`, and `runtime/ffmpeg/bin/ffmpeg.exe` if security software blocks them.
- Extract to a simple path such as `C:\Transkun-Windows-OneClick`.
- If the GUI cannot start, run `run_transkun_gui.bat` to see more information.
- If setup says Python is incomplete or `venv` is missing, re-extract the full package.
