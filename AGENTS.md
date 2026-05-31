# Agent Instructions

## Goal

This project wraps Transkun as a Windows x64 one-click piano audio-to-MIDI tool. Keep Transkun itself as a black box unless explicitly asked otherwise.

## Entry Points

- Recommended GUI entry: `Transkun GUI.exe`
- GUI compatibility/debug launcher: `run_transkun_gui.bat`
- GUI implementation: `app/gui/transkun_gui.py`
- Legacy drag-and-drop entry: `run_transkun.bat`
- Main CLI orchestration entry: `run_transkun.ps1`
- Runtime setup: `setup_runtime.ps1`
- Core wrapper: `app/wrapper/transkun_wrapper.py`
- Sustain baking: `tools/bake_sustain.py`
- Lightweight GUI launcher source: `tools/TranskunGuiLauncher.cs`

Preferred automation call:

```powershell
.\run_transkun.ps1 "path\to\audio.wav"
```

Lower-level automation call after runtime setup:

```powershell
runtime\venv\Scripts\python.exe app\wrapper\transkun_wrapper.py "path\to\audio.wav"
```

## Runtime Model

- `runtime/python` contains Python 3.11.9 x64 and must include `Lib/venv` and `Lib/ensurepip`.
- `runtime/python` also includes `tkinterdnd2` so the GUI can support window drag-and-drop before `runtime/venv` exists.
- `runtime/ffmpeg/bin` contains FFmpeg and FFprobe.
- `runtime/wheels` contains offline wheels, including `tkinterdnd2-0.4.3-py3-none-any.whl`.
- `runtime/venv` is generated and should not be packaged as source state.
- `.transkun_runtime_ok` is generated and should not be packaged as source state.

## Output Contract

For input `song.wav`, the wrapper writes:

```text
output/song_raw.mid
output/song_baked.mid
```

The raw MIDI keeps CC64 sustain data. The baked MIDI extends note durations according to sustain and removes CC64 by default.

## Generated Files

Do not treat these as source:

```text
logs/
output/
temp/
runtime/venv/
.transkun_runtime_ok
dist/
__pycache__/
*.pyc
```

## Tests

GUI smoke test:

```powershell
.\Transkun GUI.exe
```

Then drag `example.mp3` into the window or use Browse, click Convert, and expect:

```text
output/example_raw.mid
output/example_baked.mid
```

CLI smoke test:

```powershell
.\run_transkun.ps1 ".\example.mp3"
```

First-run setup test:

```powershell
Remove-Item runtime\venv -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item .transkun_runtime_ok -Force -ErrorAction SilentlyContinue
.\run_transkun.ps1 ".\example.mp3"
```

Clean-machine runtime checks:

```powershell
runtime\python\python.exe -c "import venv, ensurepip, tkinterdnd2; print('ok')"
runtime\python\python.exe -m venv --help
```

## Packaging

Use 7-Zip rather than PowerShell `Compress-Archive`.

```powershell
& "C:\Program Files\7-Zip\7z.exe" a -t7z "C:\Users\MRDK_GAMING\Desktop\Transkun-Windows-OneClick.7z" "C:\Users\MRDK_GAMING\Desktop\Transkun-Windows-OneClick\*" "-xr!logs" "-xr!output" "-xr!temp" "-xr!runtime\venv" "-x!.transkun_runtime_ok" "-xr!__pycache__" "-xr!*.pyc"
```

Before packaging, remove generated artifacts and verify the archive contains:

- `Transkun GUI.exe`
- `app/gui/transkun_gui.py`
- `runtime/python/Lib/venv/__init__.py`
- `runtime/wheels/tkinterdnd2-0.4.3-py3-none-any.whl`
- `transkun/pretrained/2.0.pt`

## Development Notes

- Avoid putting complex logic back into `run_transkun.bat`; keep it as a thin compatibility shim.
- `run_transkun.ps1` is the stable CLI orchestration layer.
- `transkun_wrapper.py` is the best integration boundary for GUI or agent workflows.
- The GUI should continue to use `tkinterdnd2` for window drag-and-drop. Do not reintroduce the old ctypes window-proc hook.
- The wrapper copies the input to a safe ASCII temp file before FFmpeg normalization, so special characters in the original path should be preserved only in output names.
