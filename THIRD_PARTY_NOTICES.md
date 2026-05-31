# Third-Party Notices

This repository is source-only. Runtime binaries and model assets are distributed via GitHub Releases. This document tracks core components, version anchors, licenses, source links, and usage.

## Version Anchors

- Bundled Python runtime: 3.11.9 x64
- Bundled FFmpeg: 7.1-full_build-www.gyan.dev
- Core ML runtime: torch 2.12.0+cpu, torchaudio 2.11.0+cpu

## Core Components

| Component | Version | License | Source | Used For |
|---|---|---|---|---|
| Transkun upstream code | repository snapshot used in this project | MIT | https://github.com/yujia-yan/transkun | Piano transcription model code and CLI modules |
| Transkun pretrained weight | `2.0.pt` (Release asset) | See upstream model/repo terms | https://github.com/yujia-yan/transkun | Pretrained inference weight |
| Python runtime | 3.11.9 | PSF License | https://www.python.org/downloads/windows/ | Runtime interpreter (Release asset) |
| FFmpeg / FFprobe binaries | 7.1 full build (Gyan) | FFmpeg license path depends on build options; current build is GPL-path | https://www.gyan.dev/ffmpeg/builds/ and https://ffmpeg.org/ | Audio normalization/transcoding |
| PyTorch (`torch`) | 2.12.0+cpu | BSD-3-Clause | https://pypi.org/project/torch/ and https://github.com/pytorch/pytorch | Core inference framework |
| Torchaudio (`torchaudio`) | 2.11.0+cpu | BSD-style (project declares BSD) | https://pypi.org/project/torchaudio/ and https://github.com/pytorch/audio | Audio I/O/runtime support |
| TkinterDnD2 (`tkinterdnd2`) | 0.4.3 | MIT | https://pypi.org/project/tkinterdnd2/ | GUI drag-and-drop |
| Mido (`mido`) | 1.3.3 | MIT | https://pypi.org/project/mido/ | MIDI data handling |
| PrettyMIDI (`pretty_midi`) | 0.2.11 | MIT | https://pypi.org/project/pretty-midi/ | MIDI processing utilities |
| PyDub (`pydub`) | 0.25.1 | MIT | https://pypi.org/project/pydub/ | Audio utility dependency |
| NumPy | 2.4.6 | BSD-style | https://pypi.org/project/numpy/ | Numerical compute dependencies |
| SciPy | 1.17.1 | BSD-style | https://pypi.org/project/scipy/ | Signal-processing/numerical dependencies |
| pandas | 3.0.3 | BSD-3-Clause | https://pypi.org/project/pandas/ | Data utility dependency |
| matplotlib | 3.10.9 | Matplotlib license (PSF-compatible/BSD-style) | https://pypi.org/project/matplotlib/ | Plotting utility dependency |

## License Text Locations

- Repository root project license: `LICENSE`
- Collected key third-party texts: `LICENSES/`
- FFmpeg-specific compliance details: `FFMPEG_COMPLIANCE.md`

## Distribution Notes

- Source repository does not embed runtime binaries or model weights in git history.
- Release assets provide runtime/model files for runnable offline usage.
- FFmpeg binaries are still redistributed via releases and remain subject to FFmpeg license obligations.

## Maintenance Rule

If you change runtime/model asset versions, update all related compliance files in the same commit:

- `THIRD_PARTY_NOTICES.md`
- `FFMPEG_COMPLIANCE.md`
- `LICENSES/` (added/updated texts)
- Relevant README and release notes
