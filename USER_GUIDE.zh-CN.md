# Transkun Windows OneClick 用户指南

Transkun Windows OneClick 是一个 Windows x64 便携式钢琴音频转 MIDI 工具。它已经包含 Python、FFmpeg、离线依赖 wheel、Transkun 模型文件和一个简单图形界面。用户不需要额外安装 Python、FFmpeg、PyTorch 或 Visual Studio Build Tools。

## 快速开始

1. 解压 `Transkun-Windows-OneClick.7z`。
2. 打开解压后的 `Transkun-Windows-OneClick` 文件夹。
3. 双击 `Transkun GUI.exe`。
4. 把钢琴音频拖进窗口，或点击“选择文件”。
5. 点击“开始转换”。
6. 转换完成后点击“打开输出”。

输出示例：

```text
output/song_raw.mid
output/song_baked.mid
```

## 首次运行

首次转换会自动创建私有运行环境：

```text
runtime/venv
```

这个过程可能需要几分钟。之后再次转换会复用已经初始化好的环境，速度会更快。

正常使用不需要手动运行 `setup_runtime.ps1`。GUI 和命令行入口会在需要时自动初始化环境。

## 示例音频测试

包内包含一个小型示例音频：

```text
example.mp3
```

打开 `Transkun GUI.exe`，把 `example.mp3` 拖进窗口，然后点击“开始转换”。

预期输出：

```text
output/example_raw.mid
output/example_baked.mid
```

## 输出文件说明

- `<文件名>_raw.mid`
  - Transkun 原始 MIDI。
  - 保留 sustain pedal 的 CC64 控制信息。

- `<文件名>_baked.mid`
  - 已把 sustain pedal 效果烘焙进音符长度。
  - 默认移除 CC64。
  - 更适合在 FL Studio 等 DAW 的钢琴卷帘中编辑。

## 支持的输入

常见音频格式通常都可以使用：

```text
.mp3
.wav
.flac
.m4a
```

文件名可以包含中文、空格和括号。程序内部会先复制到安全临时文件名再处理，输出 MIDI 仍会保留原始文件名。

## 其他运行方式

GUI 调试入口：

```bat
run_transkun_gui.bat
```

PowerShell：

```powershell
Set-Location "C:\Path\To\Transkun-Windows-OneClick"
.\run_transkun.ps1 "C:\Path\To\audio.wav"
```

cmd：

```bat
cd /d "C:\Path\To\Transkun-Windows-OneClick"
run_transkun.bat "C:\Path\To\audio.wav"
```

## 日志与排错

如果运行失败，请查看：

```text
logs/setup_runtime.log
logs/latest.log
logs/run_transkun.log
logs/gui_debug.log
```

常见解决办法：

- 请先完整解压整个压缩包，不要在压缩包预览窗口中直接运行。
- 如果安全软件拦截，请允许 `Transkun GUI.exe`、`runtime/python/python.exe` 和 `runtime/ffmpeg/bin/ffmpeg.exe` 运行。
- 建议解压到简单路径，例如 `C:\Transkun-Windows-OneClick`。
- 如果 GUI 无法启动，可以运行 `run_transkun_gui.bat` 查看更多信息。
- 如果 setup 提示 Python 不完整或缺少 `venv`，请重新完整解压包。
