# Architecture Notes

## Overview

The project is a Windows portable wrapper around Transkun. The wrapper avoids modifying Transkun internals and instead prepares a private runtime, normalizes audio, runs transcription, and post-processes sustain pedal data.

```text
Transkun GUI.exe
  -> runtime/python/pythonw.exe app/gui/transkun_gui.py
    -> setup_runtime.ps1
    -> runtime/venv/Scripts/python.exe app/wrapper/transkun_wrapper.py
      -> FFmpeg normalization
      -> python -m transkun.transcribe
      -> tools/bake_sustain.py
```

Legacy CLI flow remains available:

```text
run_transkun.bat
  -> run_transkun.ps1
    -> setup_runtime.ps1
    -> runtime/venv/Scripts/python.exe app/wrapper/transkun_wrapper.py
```

## Current Entry Design

- `Transkun GUI.exe` is the recommended user entry.
- `run_transkun_gui.bat` is a GUI compatibility/debug launcher.
- `run_transkun.bat` is a legacy drag-to-bat compatibility shim.
- `run_transkun.ps1` is the stable CLI orchestration layer.
- `setup_runtime.ps1` creates `runtime/venv` from local wheels and validates imports.
- `transkun_wrapper.py` performs the actual conversion workflow.

## GUI

The GUI is implemented with Tkinter in `app/gui/transkun_gui.py`.

- Window drag-and-drop uses `tkinterdnd2`, not a custom ctypes hook.
- `tkinterdnd2` is installed into bundled base Python for clean first-run GUI drag-and-drop.
- `tkinterdnd2` is also in `runtime/wheels` and `requirements.lock.txt` for generated venv consistency.
- The GUI shows phase-based progress for setup, normalization, transcription, sustain baking, and completion.

## Runtime Model

- `runtime/python` is a full Python 3.11.9 x64 runtime and must include `Lib/venv` and `Lib/ensurepip`.
- `runtime/ffmpeg/bin` contains FFmpeg and FFprobe.
- `runtime/wheels` contains offline wheels.
- `runtime/venv` is generated and excluded from release packages.
- `.transkun_runtime_ok` is generated and excluded from release packages.

## Acceptance State

The release package should include:

- `Transkun GUI.exe`
- runtime Python
- runtime FFmpeg
- offline wheels
- Transkun source and pretrained files
- wrapper, GUI, setup scripts, and launcher source
- user guides
- `example.mp3`

It should exclude generated logs, outputs, temporary files, generated venvs, and test artifacts.

## Future Work

- Add structured JSON/progress output to `transkun_wrapper.py`.
- Add configurable output directory.
- Add optional `--keep-sustain` mode for baked MIDI.
- Add an automated release verification script.
