import json
import locale
import os
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    DND_FILES = None
    TkinterDnD = None


ROOT = Path(__file__).resolve().parents[2]
SETUP_SCRIPT = ROOT / "setup_runtime.ps1"
VENV_PYTHON = ROOT / "runtime" / "venv" / "Scripts" / "python.exe"
WRAPPER = ROOT / "app" / "wrapper" / "transkun_wrapper.py"
LOG_DIR = ROOT / "logs"
OUTPUT_DIR = ROOT / "output"
LATEST_LOG = LOG_DIR / "latest.log"
GUI_DEBUG_LOG = LOG_DIR / "gui_debug.log"
GUI_SETTINGS = LOG_DIR / "gui_settings.json"

SUPPORTED_EXTENSIONS = (".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma")
BUTTON_COLORS = {
    "idle": ("#4b5563", "#374151", "white"),
    "ready": ("#2da44e", "#238636", "white"),
    "running": ("#8c959f", "#8c959f", "white"),
    "success": ("#2da44e", "#238636", "white"),
}

LANGUAGES = {
    "en": "English",
    "zh-CN": "简体中文",
}

TRANSLATIONS = {
    "en": {
        "title": "Transkun Windows OneClick",
        "status_ready": "Ready",
        "status_ready_convert": "Ready to convert",
        "status_working": "Working",
        "status_done": "Done",
        "status_failed": "Failed",
        "drop_empty": "Drop audio here or choose a file",
        "drop_loaded": "File loaded",
        "browse": "Browse",
        "convert": "Convert",
        "cancel": "Cancel",
        "open_output": "Open Output",
        "language": "Language",
        "log_initial": "Select an audio file, then click Convert.",
        "dnd_unavailable": "Window drag and drop is unavailable. Use Browse instead.",
        "choose_audio": "Choose audio file",
        "audio_files": "Audio files",
        "all_files": "All files",
        "no_audio_title": "No audio selected",
        "no_audio": "Choose an audio file first.",
        "file_not_found": "File not found",
        "new_conversion": "New conversion",
        "input": "Input",
        "phase_idle": "Waiting for an audio file",
        "phase_setup": "Checking runtime",
        "phase_normalize": "Normalizing audio",
        "phase_transcribe": "Running Transkun",
        "phase_bake": "Baking sustain",
        "phase_done": "Finished",
        "phase_failed": "Failed",
        "log_setup": "Starting runtime setup...",
        "log_normalize": "Normalizing audio...",
        "log_transcribe": "Running Transkun transcription...",
        "log_bake": "Baking sustain...",
        "log_completed": "Conversion completed.",
        "done_dialog_title": "Done",
        "done_dialog": "MIDI files were written to the output folder.",
        "failed_dialog_title": "Conversion failed",
        "latest_log": "Latest log",
        "quit_title": "Quit",
        "quit_running": "A conversion is still running. Quit anyway?",
        "cancel_log": "Cancelling current process...",
        "cancel_failed": "Cancel failed",
        "raw_midi": "Raw MIDI",
        "baked_midi": "Baked MIDI",
    },
    "zh-CN": {
        "title": "Transkun Windows 一键转 MIDI",
        "status_ready": "就绪",
        "status_ready_convert": "已导入，等待转换",
        "status_working": "正在处理",
        "status_done": "完成",
        "status_failed": "失败",
        "drop_empty": "把音频拖到这里，或点击选择文件",
        "drop_loaded": "文件已导入",
        "browse": "选择文件",
        "convert": "开始转换",
        "cancel": "取消",
        "open_output": "打开输出",
        "language": "语言",
        "log_initial": "请选择音频文件，然后点击开始转换。",
        "dnd_unavailable": "窗口拖拽不可用，请使用选择文件。",
        "choose_audio": "选择音频文件",
        "audio_files": "音频文件",
        "all_files": "所有文件",
        "no_audio_title": "未选择音频",
        "no_audio": "请先选择一个音频文件。",
        "file_not_found": "文件不存在",
        "new_conversion": "新的转换任务",
        "input": "输入",
        "phase_idle": "等待音频文件",
        "phase_setup": "检查运行环境",
        "phase_normalize": "规范化音频",
        "phase_transcribe": "运行 Transkun",
        "phase_bake": "烘焙延音",
        "phase_done": "已完成",
        "phase_failed": "失败",
        "log_setup": "开始检查运行环境...",
        "log_normalize": "正在规范化音频...",
        "log_transcribe": "正在运行 Transkun 转录...",
        "log_bake": "正在烘焙 sustain 延音...",
        "log_completed": "转换已完成。",
        "done_dialog_title": "完成",
        "done_dialog": "MIDI 文件已写入 output 文件夹。",
        "failed_dialog_title": "转换失败",
        "latest_log": "最新日志",
        "quit_title": "退出",
        "quit_running": "转换仍在运行，确定要退出吗？",
        "cancel_log": "正在取消当前进程...",
        "cancel_failed": "取消失败",
        "raw_midi": "原始 MIDI",
        "baked_midi": "烘焙 MIDI",
    },
}


def write_gui_debug(message):
    try:
        GUI_DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with GUI_DEBUG_LOG.open("a", encoding="utf-8") as handle:
            handle.write(message + "\n")
    except Exception:
        pass


class TranskunGui:
    def __init__(self, root):
        self.root = root
        self.language = self.load_language()
        self.root.title(self.tr("title"))
        self.root.geometry("840x610")
        self.root.minsize(760, 540)

        self.audio_path = tk.StringVar()
        self.status = tk.StringVar(value=self.tr("status_ready"))
        self.phase_text = tk.StringVar(value=self.tr("phase_idle"))
        self.language_label_text = tk.StringVar(value=self.tr("language"))
        self.language_choice = tk.StringVar(value=LANGUAGES[self.language])
        self.progress_value = tk.DoubleVar(value=0)
        self.running = False
        self.current_process = None
        self.worker = None
        self.events = queue.Queue()
        self.drop_enabled = False
        self.selected_path = None
        self.phase_key = "phase_idle"
        self.drop_state = "empty"
        self.progress_active = False
        self.convert_style = "idle"
        self.output_style = "idle"

        self._build_ui()
        self._install_drop_target()
        self._load_initial_path()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(100, self._drain_events)

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)

        style = ttk.Style()
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Drop.TLabel", font=("Segoe UI", 13))
        style.configure("Status.TLabel", font=("Segoe UI", 10))
        style.configure("Loaded.TLabel", font=("Segoe UI", 10, "bold"))

        header = ttk.Frame(self.root, padding=(18, 16, 18, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        self.title_label = ttk.Label(header, style="Title.TLabel")
        self.title_label.grid(row=0, column=0, sticky="w")

        language_frame = ttk.Frame(header)
        language_frame.grid(row=0, column=1, sticky="e", padx=(12, 16))
        self.language_label = ttk.Label(language_frame, textvariable=self.language_label_text)
        self.language_label.grid(row=0, column=0, padx=(0, 6))
        self.language_combo = ttk.Combobox(
            language_frame,
            textvariable=self.language_choice,
            values=list(LANGUAGES.values()),
            width=12,
            state="readonly",
        )
        self.language_combo.grid(row=0, column=1)
        self.language_combo.bind("<<ComboboxSelected>>", self.on_language_selected)

        self.status_label = ttk.Label(header, textvariable=self.status, style="Status.TLabel")
        self.status_label.grid(row=0, column=2, sticky="e")

        controls = ttk.Frame(self.root, padding=(18, 8, 18, 8))
        controls.grid(row=1, column=0, sticky="ew")
        controls.columnconfigure(0, weight=1)

        self.drop_frame = tk.Frame(
            controls,
            background="#f6f8fa",
            highlightbackground="#8aa4bf",
            highlightthickness=2,
            height=112,
        )
        self.drop_frame.grid(row=0, column=0, columnspan=5, sticky="ew", pady=(0, 12))
        self.drop_frame.grid_propagate(False)
        self.drop_frame.columnconfigure(0, weight=1)
        self.drop_frame.rowconfigure(0, weight=1)

        self.drop_label = ttk.Label(
            self.drop_frame,
            style="Drop.TLabel",
            background="#f6f8fa",
            anchor="center",
        )
        self.drop_label.grid(row=0, column=0, sticky="nsew")

        self.path_entry = ttk.Entry(controls, textvariable=self.audio_path)
        self.path_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        self.browse_button = ttk.Button(controls, command=self.browse)
        self.browse_button.grid(row=1, column=1, padx=(0, 8))

        self.convert_button = tk.Button(
            controls,
            command=self.convert,
            relief="raised",
            bd=1,
            padx=14,
            pady=4,
            background="#4b5563",
            foreground="white",
            activebackground="#374151",
            activeforeground="white",
            disabledforeground="#7d8590",
        )
        self.convert_button.grid(row=1, column=2, padx=(0, 8))

        self.cancel_button = ttk.Button(controls, command=self.cancel, state="disabled")
        self.cancel_button.grid(row=1, column=3, padx=(0, 8))

        self.output_button = tk.Button(
            controls,
            command=self.open_output,
            relief="raised",
            bd=1,
            padx=12,
            pady=4,
            background="#4b5563",
            foreground="white",
            activebackground="#374151",
            activeforeground="white",
            disabledforeground="#7d8590",
        )
        self.output_button.grid(row=1, column=4)

        progress_frame = ttk.Frame(self.root, padding=(18, 4, 18, 6))
        progress_frame.grid(row=2, column=0, sticky="ew")
        progress_frame.columnconfigure(1, weight=1)
        self.phase_label = ttk.Label(progress_frame, textvariable=self.phase_text)
        self.phase_label.grid(row=0, column=0, sticky="w", padx=(0, 12))
        self.progress = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            variable=self.progress_value,
        )
        self.progress.grid(row=0, column=1, sticky="ew")

        log_frame = ttk.Frame(self.root, padding=(18, 8, 18, 16))
        log_frame.grid(row=3, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log = tk.Text(
            log_frame,
            wrap="word",
            state="disabled",
            height=14,
            font=("Consolas", 10),
            background="#0f1720",
            foreground="#dbe7f3",
            insertbackground="#dbe7f3",
            relief="flat",
        )
        self.log.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scrollbar.set)

        self.refresh_texts()
        self._append_log(self.tr("log_initial") + "\n")

    def tr(self, key):
        return TRANSLATIONS.get(self.language, TRANSLATIONS["en"]).get(
            key, TRANSLATIONS["en"].get(key, key)
        )

    def load_language(self):
        try:
            data = json.loads(GUI_SETTINGS.read_text(encoding="utf-8"))
            language = data.get("language")
            if language in LANGUAGES:
                return language
        except Exception:
            pass

        system_locale = (locale.getlocale()[0] or "").lower()
        return "zh-CN" if system_locale.startswith("zh") else "en"

    def save_language(self):
        try:
            GUI_SETTINGS.parent.mkdir(parents=True, exist_ok=True)
            GUI_SETTINGS.write_text(
                json.dumps({"language": self.language}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            write_gui_debug(f"Failed to save GUI settings: {exc!r}")

    def on_language_selected(self, _event=None):
        label = self.language_choice.get()
        for code, display in LANGUAGES.items():
            if display == label:
                self.set_language(code)
                break

    def set_language(self, code):
        if code not in LANGUAGES:
            return
        self.language = code
        self.save_language()
        self.refresh_texts()

    def refresh_texts(self):
        self.root.title(self.tr("title"))
        self.title_label.configure(text=self.tr("title"))
        self.language_label_text.set(self.tr("language"))
        self.language_choice.set(LANGUAGES[self.language])
        self.browse_button.configure(text=self.tr("browse"))
        self.convert_button.configure(text=self.tr("convert"))
        self.cancel_button.configure(text=self.tr("cancel"))
        self.output_button.configure(text=self.tr("open_output"))
        self.status.set(self.tr(self.current_status_key()))
        self.phase_text.set(self.tr(self.phase_key))
        if self.drop_state == "empty":
            self.drop_label.configure(text=self.tr("drop_empty"))
        elif self.selected_path:
            self.drop_label.configure(text=f"{self.tr('drop_loaded')}: {self.selected_path.name}")

    def current_status_key(self):
        if self.running:
            return "status_working"
        if self.phase_key == "phase_done":
            return "status_done"
        if self.phase_key == "phase_failed":
            return "status_failed"
        if self.selected_path:
            return "status_ready_convert"
        return "status_ready"

    def _install_drop_target(self):
        if DND_FILES is None or TkinterDnD is None:
            self._append_log(self.tr("dnd_unavailable") + "\n")
            write_gui_debug("tkinterdnd2 is not available.")
            return
        try:
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind("<<Drop>>", self.on_drop_event)
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<Drop>>", self.on_drop_event)
            self.drop_enabled = True
            write_gui_debug("tkinterdnd2 drop target registered.")
        except Exception as exc:
            self._append_log(self.tr("dnd_unavailable") + "\n")
            write_gui_debug(f"tkinterdnd2 registration failed: {exc!r}")

    def _load_initial_path(self):
        if len(sys.argv) > 1:
            self.set_audio_path(sys.argv[1])

    def browse(self):
        path = filedialog.askopenfilename(
            title=self.tr("choose_audio"),
            filetypes=[
                (self.tr("audio_files"), "*.mp3 *.wav *.flac *.m4a *.aac *.ogg *.wma"),
                (self.tr("all_files"), "*.*"),
            ],
        )
        if path:
            self.set_audio_path(path)

    def on_drop(self, paths):
        first_file = next((path for path in paths if Path(path).is_file()), None)
        if first_file:
            self.set_audio_path(first_file)

    def on_drop_event(self, event):
        paths = self.parse_drop_data(event.data)
        write_gui_debug(f"tkinterdnd2 dropped files: {paths!r}")
        self.on_drop(paths)

    def parse_drop_data(self, data):
        try:
            return list(self.root.tk.splitlist(data))
        except Exception:
            return [data.strip("{}")]

    def set_audio_path(self, path):
        clean_path = str(Path(path).expanduser())
        self.audio_path.set(clean_path)
        self.selected_path = Path(clean_path)
        self.set_selected_state()

    def set_selected_state(self):
        self.drop_state = "loaded"
        self.phase_key = "phase_idle"
        self.progress_value.set(0)
        self.progress.configure(mode="determinate")
        self.drop_frame.configure(background="#eef8f1", highlightbackground="#2da44e")
        self.drop_label.configure(
            text=f"{self.tr('drop_loaded')}: {self.selected_path.name}",
            background="#eef8f1",
        )
        self.status.set(self.tr("status_ready_convert"))
        self.convert_button.focus_set()
        self.set_convert_style("ready")
        self.set_output_style("idle")

    def set_convert_style(self, state):
        self.convert_style = state
        background, activebackground, foreground = BUTTON_COLORS[state]
        self.convert_button.configure(
            background=background,
            activebackground=activebackground,
            foreground=foreground,
            activeforeground=foreground,
        )

    def set_output_style(self, state):
        self.output_style = state
        background, activebackground, foreground = BUTTON_COLORS[state]
        self.output_button.configure(
            background=background,
            activebackground=activebackground,
            foreground=foreground,
            activeforeground=foreground,
        )

    def convert(self):
        if self.running:
            return

        audio_value = self.audio_path.get().strip().strip('"')
        if not audio_value:
            messagebox.showwarning(self.tr("no_audio_title"), self.tr("no_audio"))
            return
        audio = Path(audio_value)
        if not audio.exists() or not audio.is_file():
            messagebox.showerror(self.tr("file_not_found"), str(audio))
            return

        self.running = True
        self._set_running_state(True)
        self.set_output_style("idle")
        self.status.set(self.tr("status_working"))
        self._append_log(f"\n=== {self.tr('new_conversion')} ===\n")
        self._append_log(f"{self.tr('input')}: {audio}\n")

        self.worker = threading.Thread(target=self._run_pipeline, args=(audio,), daemon=True)
        self.worker.start()

    def _run_pipeline(self, audio):
        try:
            self._emit("phase", ("phase_setup", 10, True))
            self._emit("log", self.tr("log_setup") + "\n")
            self._run_command(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(SETUP_SCRIPT),
                ]
            )

            if not VENV_PYTHON.exists():
                raise RuntimeError(f"Missing runtime Python venv: {VENV_PYTHON}")

            stop_monitor = threading.Event()
            monitor = threading.Thread(
                target=self._monitor_wrapper_log,
                args=(audio, stop_monitor),
                daemon=True,
            )
            monitor.start()
            self._emit("phase", ("phase_normalize", 30, True))
            self._emit("log", self.tr("log_normalize") + "\n")
            try:
                self._run_command([str(VENV_PYTHON), str(WRAPPER), str(audio.resolve())])
            finally:
                stop_monitor.set()
                monitor.join(timeout=1.0)

            raw_midi = OUTPUT_DIR / f"{audio.stem}_raw.mid"
            baked_midi = OUTPUT_DIR / f"{audio.stem}_baked.mid"
            if raw_midi.exists() and baked_midi.exists():
                self._emit("log", f"\n{self.tr('raw_midi')}:   {raw_midi}\n")
                self._emit("log", f"{self.tr('baked_midi')}: {baked_midi}\n")
            self._emit("done", "Done")
        except Exception as exc:
            self._emit("failed", str(exc))
        finally:
            self.current_process = None

    def _monitor_wrapper_log(self, audio, stop_event):
        start_time = time.time()
        seen_normalize = False
        seen_transcribe = False
        seen_bake = False
        log_path = None
        offset = 0

        while not stop_event.is_set():
            if log_path is None:
                log_path = self._find_recent_wrapper_log(audio, start_time)
                if log_path is None:
                    time.sleep(0.25)
                    continue

            try:
                text = log_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                time.sleep(0.25)
                continue

            chunk = text[offset:]
            offset = len(text)
            if chunk:
                if not seen_normalize and "ffmpeg.exe" in chunk:
                    seen_normalize = True
                    self._emit("phase", ("phase_normalize", 35, True))
                    self._emit("log", self.tr("log_normalize") + "\n")
                if not seen_transcribe and "transkun.transcribe" in chunk:
                    seen_transcribe = True
                    self._emit("phase", ("phase_transcribe", 70, True))
                    self._emit("log", self.tr("log_transcribe") + "\n")
                if not seen_bake and "bake_sustain.py" in chunk:
                    seen_bake = True
                    self._emit("phase", ("phase_bake", 90, True))
                    self._emit("log", self.tr("log_bake") + "\n")
            time.sleep(0.25)

    def _find_recent_wrapper_log(self, audio, start_time):
        if not LOG_DIR.exists():
            return None
        candidates = []
        for path in LOG_DIR.glob("*.log"):
            if path.name in {"latest.log", "run_transkun.log", "setup_runtime.log", "gui_debug.log"}:
                continue
            try:
                if path.stat().st_mtime >= start_time - 2:
                    candidates.append(path)
            except OSError:
                continue
        if not candidates:
            return None
        return max(candidates, key=lambda item: item.stat().st_mtime)

    def _run_command(self, command):
        self._emit("log", "\n> " + self._format_command(command) + "\n")
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        self.current_process = subprocess.Popen(
            command,
            cwd=str(ROOT),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creationflags,
        )

        assert self.current_process.stdout is not None
        for line in self.current_process.stdout:
            self._emit("log", line)

        exit_code = self.current_process.wait()
        if exit_code != 0:
            raise RuntimeError(
                f"Command failed with exit code {exit_code}: {self._format_command(command)}"
            )

    def _format_command(self, command):
        return " ".join(f'"{part}"' if " " in str(part) else str(part) for part in command)

    def cancel(self):
        if not self.running or not self.current_process:
            return
        self._append_log("\n" + self.tr("cancel_log") + "\n")
        try:
            self.current_process.terminate()
        except Exception as exc:
            self._append_log(f"{self.tr('cancel_failed')}: {exc}\n")

    def open_output(self):
        OUTPUT_DIR.mkdir(exist_ok=True)
        os.startfile(str(OUTPUT_DIR))

    def _emit(self, kind, value):
        self.events.put((kind, value))

    def _drain_events(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self._append_log(value)
                elif kind == "phase":
                    phase_key, percent, active = value
                    self.set_phase(phase_key, percent, active)
                elif kind == "done":
                    self.running = False
                    self._set_running_state(False)
                    self.set_phase("phase_done", 100, False)
                    self.status.set(self.tr("status_done"))
                    self.set_output_style("success")
                    self._append_log("\n" + self.tr("log_completed") + "\n")
                    messagebox.showinfo(self.tr("done_dialog_title"), self.tr("done_dialog"))
                elif kind == "failed":
                    self.running = False
                    self._set_running_state(False)
                    self.set_phase("phase_failed", 0, False)
                    self.status.set(self.tr("status_failed"))
                    self.set_output_style("idle")
                    self._append_log(f"\nERROR: {value}\n")
                    if LATEST_LOG.exists():
                        self._append_log(f"{self.tr('latest_log')}: {LATEST_LOG}\n")
                    messagebox.showerror(self.tr("failed_dialog_title"), value)
        except queue.Empty:
            pass
        self.root.after(100, self._drain_events)

    def set_phase(self, phase_key, percent, active=True):
        self.phase_key = phase_key
        self.phase_text.set(self.tr(phase_key))
        if active:
            if not self.progress_active:
                self.progress.configure(mode="indeterminate")
                self.progress.start(10)
                self.progress_active = True
        else:
            if self.progress_active:
                self.progress.stop()
                self.progress_active = False
            self.progress.configure(mode="determinate")
        self.progress_value.set(percent)

    def _append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_running_state(self, running):
        state = "disabled" if running else "normal"
        self.browse_button.configure(state=state)
        self.path_entry.configure(state=state)
        self.language_combo.configure(state="disabled" if running else "readonly")
        self.cancel_button.configure(state="normal" if running else "disabled")
        self.convert_button.configure(state=state)
        if running:
            self.set_convert_style("running")
        else:
            self.set_convert_style("ready" if self.selected_path else "idle")

    def on_close(self):
        if self.running:
            if not messagebox.askyesno(self.tr("quit_title"), self.tr("quit_running")):
                return
            self.cancel()
        self.root.destroy()


def create_root():
    if TkinterDnD is None:
        return tk.Tk()
    try:
        return TkinterDnD.Tk()
    except Exception as exc:
        write_gui_debug(f"TkinterDnD.Tk failed, falling back to tk.Tk: {exc!r}")
        return tk.Tk()


def main():
    root = create_root()
    TranskunGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
