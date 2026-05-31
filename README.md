# Transkun Windows OneClick GUI v2

Windows x64 one-click wrapper for Transkun piano audio-to-MIDI conversion.

## Quick Start (Source Repo + Release Assets)

This GitHub repository is **source-only**. Runtime binaries and model weights are published as Release assets.

1. Clone this repository.
2. Download release assets into the project root:
   - `runtime-windows-x64.7z` (contains `runtime/python`, `runtime/ffmpeg`, `runtime/wheels`)
   - `2.0.pt` (place into `transkun/pretrained/2.0.pt`)
   - Optional: `Transkun GUI.exe`
3. Extract `runtime-windows-x64.7z` so `runtime/` exists beside this README.
4. Run:
   - GUI: `Transkun GUI.exe` (if downloaded)
   - CLI: `./run_transkun.ps1 ".\\example.mp3"`

Outputs for `song.wav`:

- `output/song_raw.mid`
- `output/song_baked.mid`

## Source-Only Repository Policy

- Included in source repo: code, scripts, docs, compliance files.
- Excluded from source repo: `runtime/` binaries, pretrained `.pt` weights, generated outputs/logs/temp, and optional packaged GUI executable.
- Release assets carry runtime and model files needed for runnable offline usage.

## Runtime Asset Version Anchors

- Python runtime: 3.11.9 x64
- FFmpeg runtime: `7.1-full_build-www.gyan.dev`
- Core ML runtime: `torch 2.12.0+cpu`, `torchaudio 2.11.0+cpu`

## Third-Party Licenses / 第三方许可

This repository and its release assets redistribute third-party software and model/runtime assets.

- Notices: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
- Key license texts: [LICENSES/](LICENSES/)
- FFmpeg-specific compliance notes: [FFMPEG_COMPLIANCE.md](FFMPEG_COMPLIANCE.md)

### FFmpeg Note

- This project invokes FFmpeg via subprocess / command-line tools; it does **not** link FFmpeg libraries directly in project code.
- Release assets redistribute FFmpeg binaries, so FFmpeg license obligations still apply to distribution.
- Current FFmpeg build path is GPL-feature full build (`7.1-full_build-www.gyan.dev`), and release documentation must include corresponding license/source-access information.

### Model Weights Note

- `transkun/pretrained/2.0.pt` is distributed as a release asset, not embedded in source repository history.
- Code license and weight/license terms should be reviewed separately; do not assume model weights automatically follow this wrapper repository's root `LICENSE`.

## Maintenance Rule

When replacing bundled binaries or upgrading wheel/runtime versions, update these files in the same change:

- `THIRD_PARTY_NOTICES.md`
- `FFMPEG_COMPLIANCE.md`
- `LICENSES/` relevant texts
- Release notes / release asset names
