import argparse
import datetime as dt
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs"
OUTPUT_DIR = ROOT / "output"
TEMP_DIR = ROOT / "temp"
FFMPEG_BIN = ROOT / "runtime" / "ffmpeg" / "bin"
FFMPEG_EXE = FFMPEG_BIN / "ffmpeg.exe"
FFPROBE_EXE = FFMPEG_BIN / "ffprobe.exe"


class WrapperError(RuntimeError):
    pass


def ensure_dirs():
    for path in (LOG_DIR, OUTPUT_DIR, TEMP_DIR):
        path.mkdir(parents=True, exist_ok=True)


def quote_command(command):
    return " ".join(f'"{part}"' if " " in str(part) else str(part) for part in command)


def write_log(log_path, message):
    timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {message}\n")


def run_logged(command, log_path, env):
    write_log(log_path, f"RUN: {quote_command(command)}")
    result = subprocess.run(
        [str(part) for part in command],
        cwd=str(ROOT),
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    write_log(log_path, f"EXIT CODE: {result.returncode}")
    if result.stdout:
        write_log(log_path, "STDOUT:\n" + result.stdout.rstrip())
    if result.stderr:
        write_log(log_path, "STDERR:\n" + result.stderr.rstrip())
    if result.returncode != 0:
        raise WrapperError(f"Command failed with exit code {result.returncode}: {quote_command(command)}")


def build_env():
    if not FFMPEG_EXE.exists():
        raise WrapperError(f"Missing FFmpeg: {FFMPEG_EXE}")
    if not FFPROBE_EXE.exists():
        raise WrapperError(f"Missing FFprobe: {FFPROBE_EXE}")

    env = os.environ.copy()
    env["PATH"] = str(FFMPEG_BIN) + os.pathsep + env.get("PATH", "")
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def normalize_audio(input_path, normalized_path, log_path, env):
    command = [
        FFMPEG_EXE,
        "-y",
        "-hide_banner",
        "-i",
        input_path,
        "-vn",
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "192k",
        normalized_path,
    ]
    run_logged(command, log_path, env)


def safe_suffix(path):
    suffix = path.suffix.lower()
    if not suffix or any(char in suffix for char in '<>:"/\\|?*() '):
        return ".audio"
    return suffix


def copy_to_safe_temp(input_path, log_path):
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    token = uuid.uuid4().hex[:8]
    safe_input_path = TEMP_DIR / f"input_{stamp}_{token}{safe_suffix(input_path)}"
    shutil.copy2(input_path, safe_input_path)
    write_log(log_path, f"Safe temp input: {safe_input_path}")
    return safe_input_path


def transcribe(normalized_path, raw_midi_path, log_path, env):
    command = [
        sys.executable,
        "-m",
        "transkun.transcribe",
        normalized_path,
        raw_midi_path,
        "--device",
        "cpu",
    ]
    run_logged(command, log_path, env)


def bake_sustain(raw_midi_path, baked_midi_path, log_path, env):
    command = [
        sys.executable,
        str(ROOT / "tools" / "bake_sustain.py"),
        raw_midi_path,
        baked_midi_path,
    ]
    run_logged(command, log_path, env)


def latest_log_path():
    return LOG_DIR / "latest.log"


def timestamped_log_path(stem):
    safe_stem = "".join(char if char not in '<>:"/\\|?*' else "_" for char in stem)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    return LOG_DIR / f"{safe_stem}_{stamp}.log"


def main():
    parser = argparse.ArgumentParser(description="Run Transkun with bundled Windows runtime.")
    parser.add_argument("audio_path", help="Path to the input piano audio file.")
    args = parser.parse_args()

    ensure_dirs()
    input_path = Path(args.audio_path).expanduser().resolve()
    log_path = timestamped_log_path(input_path.stem)
    latest_path = latest_log_path()

    try:
        if not input_path.exists():
            raise WrapperError(f"Input audio does not exist: {input_path}")
        if not input_path.is_file():
            raise WrapperError(f"Input path is not a file: {input_path}")

        latest_path.write_text("", encoding="utf-8")
        write_log(log_path, f"Input: {input_path}")
        write_log(latest_path, f"Input: {input_path}")

        env = build_env()
        safe_input_path = copy_to_safe_temp(input_path, log_path)
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        token = uuid.uuid4().hex[:8]
        normalized_path = TEMP_DIR / f"normalized_{stamp}_{token}.mp3"
        raw_midi_path = OUTPUT_DIR / f"{input_path.stem}_raw.mid"
        baked_midi_path = OUTPUT_DIR / f"{input_path.stem}_baked.mid"

        normalize_audio(safe_input_path, normalized_path, log_path, env)
        transcribe(normalized_path, raw_midi_path, log_path, env)
        bake_sustain(raw_midi_path, baked_midi_path, log_path, env)

        latest_path.write_text(log_path.read_text(encoding="utf-8"), encoding="utf-8")
        print("Done.")
        print(f"Raw MIDI:   {raw_midi_path}")
        print(f"Baked MIDI: {baked_midi_path}")
        print(f"Log:        {log_path}")
        return 0
    except Exception as exc:
        message = f"ERROR: {exc}"
        write_log(log_path, message)
        latest_path.write_text(log_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(message, file=sys.stderr)
        print(f"See log: {latest_path}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
