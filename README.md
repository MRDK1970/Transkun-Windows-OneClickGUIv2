# Transkun Windows OneClick GUI v2

Windows x64 one-click wrapper for Transkun piano audio-to-MIDI conversion.

> [!IMPORTANT]
> ## 新手必读（中文）
> - 对于绝大多数用户（尤其是小白用户），请直接前往 [Releases](../../releases) 下载一键使用包。  
> - 下载并解压后，直接双击 `Transkun GUI.exe` 即可运行。  
> - 初次运行时程序会自动创建运行环境；根据电脑配置不同，这一步可能需要数十分钟。  
> - 项目目录内提供 `example.mp3` 样例音频，可直接用于测试。  
> - 生成的 MIDI 通常包含两份：`*_raw.mid`（原始 MIDI）和 `*_baked.mid`（已将延音应用到音符的版本），请按需使用。  
> - 本项目依赖高质量、纯净的原始钢琴音频输入；音频纯净度会直接决定转录效果。  
> - 任何其他乐器或人声都会严重影响最终转录效果。  
>
> ## Beginner Notice (English)
> - For most users (especially beginners), please go to [Releases](../../releases) and download the one-click package.  
> - After downloading and extracting, just double-click `Transkun GUI.exe` to run.  
> - On first launch, the app will automatically create the runtime environment; depending on your PC, this can take up to tens of minutes.  
> - A sample audio file `example.mp3` is included for quick testing.  
> - Output MIDI files usually include both `*_raw.mid` (original MIDI) and `*_baked.mid` (sustain-applied MIDI). Use either as needed.  
> - This project requires high-quality, clean solo piano audio input; input cleanliness directly determines transcription quality.  
> - Any other instruments or vocals will significantly degrade transcription results.  
> - **Input quality directly determines transcription quality.**

## Quick Start for Advanced Users / Developers (Source Repo + Release Assets)

This GitHub repository is **source-only**. Runtime binaries and model weights are published as Release assets.
This section is the advanced/developer setup path.

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
