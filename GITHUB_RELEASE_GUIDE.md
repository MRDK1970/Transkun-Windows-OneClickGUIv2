# GitHub Upload Guide (Source Repo + Release Assets)

This file describes how to publish this project as a lightweight source repository and attach runtime/model assets in GitHub Releases.

## 1) Initialize and commit source repository

Run in project root:

```powershell
git init
git add .
git status
```

Before commit, confirm these are NOT staged:

- `runtime/`
- `transkun/pretrained/*.pt`
- `logs/`, `output/`, `temp/`
- `Transkun GUI.exe`

Then commit:

```powershell
git commit -m "chore: prepare source-only open-source repository"
```

## 2) Create GitHub repository and push

```powershell
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

## 3) Build release assets locally (no file deletion)

### 3.1 Runtime package

Use 7-Zip:

```powershell
& "C:\Program Files\7-Zip\7z.exe" a -t7z \
  ".\runtime-windows-x64.7z" \
  ".\runtime\*" \
  "-xr!venv" \
  "-xr!__pycache__" \
  "-xr!*.pyc"
```

### 3.2 Model weight package

Upload `transkun/pretrained/2.0.pt` as a separate release asset.

### 3.3 Optional GUI executable

Upload `Transkun GUI.exe` if you want one-click GUI entry in releases.

## 4) Create first Release

Recommended tag: `v0.1.0-source-assets`

Attach assets:

- `runtime-windows-x64.7z`
- `2.0.pt`
- Optional: `Transkun GUI.exe`

In release notes, include version anchors:

- Python 3.11.9
- FFmpeg `7.1-full_build-www.gyan.dev`
- torch `2.12.0+cpu`
- torchaudio `2.11.0+cpu`

## 5) Post-release validation

In a clean folder:

1. Clone source repo.
2. Download and extract release assets into expected paths.
3. Run:

```powershell
.\run_transkun.ps1 ".\example.mp3"
```

4. Verify outputs:

- `output/example_raw.mid`
- `output/example_baked.mid`

