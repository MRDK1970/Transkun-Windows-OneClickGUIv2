# Transkun Windows OneClick 使用指南

推荐入口是 `Transkun GUI.exe`。双击打开窗口后，可以把音频拖进窗口，也可以点击“选择文件”，然后点击“开始转换”。

## 快速使用

1. 解压 `Transkun-Windows-OneClick.7z`。
2. 打开解压后的文件夹。
3. 双击 `Transkun GUI.exe`。
4. 拖入钢琴音频，或点击“选择文件”。
5. 点击“开始转换”。
6. 转换完成后点击“打开输出”。

生成文件示例：

```text
output/song_raw.mid
output/song_baked.mid
```

## 首次运行

首次转换会自动创建：

```text
runtime/venv
```

这一步可能需要几分钟。之后再次运行会更快。

不要手动删除 `runtime/python`、`runtime/ffmpeg` 或 `runtime/wheels`。

## 命令行入口

仍然可以使用：

```powershell
.\run_transkun.ps1 ".\example.mp3"
```

或者：

```bat
run_transkun.bat "C:\path\to\audio.wav"
```

## 日志

失败时请查看：

```text
logs/setup_runtime.log
logs/latest.log
logs/run_transkun.log
logs/gui_debug.log
```

如果提示 bundled Python 不完整、缺少 `venv`，通常说明压缩包没有完整解压，请重新解压整个文件夹。
