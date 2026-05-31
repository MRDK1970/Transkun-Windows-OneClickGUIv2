# FFmpeg Compliance Notes

This repository is source-only. FFmpeg binaries are distributed through GitHub Release assets, not committed to git history.

## Current FFmpeg Asset Baseline

- Runtime binary path after asset extraction: `runtime/ffmpeg/bin/ffmpeg.exe`, `runtime/ffmpeg/bin/ffprobe.exe`
- Version string baseline: `ffmpeg version 7.1-full_build-www.gyan.dev`
- Build family: Gyan full build for Windows
- Observed configure flags include GPL-path options (for example `--enable-gpl`, `--enable-version3`, static/full feature build flags).

## How This Project Uses FFmpeg

- Project code calls FFmpeg via subprocess/command-line invocation.
- Project code does not directly link FFmpeg libraries.
- Release assets still redistribute FFmpeg binaries; license obligations therefore apply to release distribution.

## Redistribution Obligations (Practical Checklist)

1. Keep FFmpeg attribution and licensing information available to downstream users.
2. Clearly disclose the exact FFmpeg build/version shipped in the release.
3. Provide or point to corresponding source-access information required by the selected FFmpeg license path.
4. Ensure docs do not misstate this build as LGPL-only when it is GPL-path.

## Official Upstream References

- FFmpeg legal/compliance page: https://www.ffmpeg.org/legal.html
- FFmpeg license overview: https://www.ffmpeg.org/doxygen/trunk/md_LICENSE.html
- FFmpeg project home: https://ffmpeg.org/

## Notes and Limits

- This document is engineering guidance for repository compliance hygiene, not legal advice.
- If FFmpeg binaries are replaced (version, vendor, build flags), update this file and related notice files in the same commit and release.
