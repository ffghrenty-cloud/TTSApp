"""CustomTkinter user interface for TTS Studio."""

from __future__ import annotations

import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from audio_export import save_mp3, save_wav
from audio_player import play_audio, stop_audio
from config import APP_NAME, APP_VERSION, LANGUAGES
from tts_engine import SileroTTSEngine


class TTSApplication(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} — {APP_VERSION}")
        self.geometry("1080x720")
        self.minsize(900, 620)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.engine = SileroTTSEngine()
        self.audio = None
        self.sample_rate = None
        self.busy = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_workspace()
        self._update_counter()

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="◉  TTS Studio",
            font=ctk.CTkFont(size=23, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(30, 4))
        ctk.CTkLabel(
            sidebar, text="Локальный синтез речи",
            text_color="gray",
        ).pack(anchor="w", padx=24, pady=(0, 35))

        ctk.CTkLabel(
            sidebar, text="РАБОЧЕЕ ПРОСТРАНСТВО",
            text_color="gray", font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(0, 12))

        ctk.CTkLabel(
            sidebar, text="✎  Преобразование текста",
            anchor="w", fg_color=("#dceafe", "#203c60"),
            text_color=("#14243a", "#ffffff"), corner_radius=8,
            height=38,
        ).pack(fill="x", padx=14)

        ctk.CTkFrame(sidebar, height=2, fg_color=("gray85", "gray25")).pack(
            fill="x", padx=18, pady=22
        )
        ctk.CTkLabel(
            sidebar, text="ДВИЖОК",
            text_color="gray", font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(0, 8))
        ctk.CTkLabel(
            sidebar, text="Silero TTS · CPU",
            text_color=("gray25", "gray75"),
        ).pack(anchor="w", padx=22)
        ctk.CTkLabel(
            sidebar, text="Модель загружается при первом синтезе",
            text_color="gray", wraplength=175, justify="left",
        ).pack(anchor="w", padx=22, pady=(6, 0))

        ctk.CTkLabel(
            sidebar, text=f"Версия {APP_VERSION}",
            text_color="gray",
        ).pack(side="bottom", anchor="w", padx=22, pady=20)

    def _build_workspace(self) -> None:
        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.grid(row=0, column=1, sticky="nsew", padx=30, pady=26)
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(workspace, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 22))
        ctk.CTkLabel(
            header, text="Преобразование текста в речь",
            font=ctk.CTkFont(size=27, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="Введите текст, выберите язык и голос, затем создайте аудио.",
            text_color="gray",
        ).pack(anchor="w", pady=(5, 0))

        settings = ctk.CTkFrame(workspace, corner_radius=14)
        settings.grid(row=1, column=0, sticky="ew", pady=(0, 18))
        settings.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(settings, text="Язык").grid(
            row=0, column=0, sticky="w", padx=18, pady=(15, 6)
        )
        ctk.CTkLabel(settings, text="Голос").grid(
            row=0, column=1, sticky="w", padx=18, pady=(15, 6)
        )

        self.language_var = ctk.StringVar(value="Русский")
        self.voice_var = ctk.StringVar(value=LANGUAGES["Русский"]["default"])

        self.language_menu = ctk.CTkOptionMenu(
            settings, values=list(LANGUAGES),
            variable=self.language_var, command=self._on_language_change,
        )
        self.language_menu.grid(
            row=1, column=0, sticky="ew", padx=18, pady=(0, 16)
        )

        self.voice_menu = ctk.CTkOptionMenu(
            settings, values=list(LANGUAGES["Русский"]["voices"]),
            variable=self.voice_var,
        )
        self.voice_menu.grid(
            row=1, column=1, sticky="ew", padx=18, pady=(0, 16)
        )

        editor = ctk.CTkFrame(workspace, corner_radius=14)
        editor.grid(row=2, column=0, sticky="nsew", pady=(0, 18))
        editor.grid_columnconfigure(0, weight=1)
        editor.grid_rowconfigure(1, weight=1)

        editor_header = ctk.CTkFrame(editor, fg_color="transparent")
        editor_header.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 8))
        ctk.CTkLabel(
            editor_header, text="Текст для озвучивания",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(side="left")
        self.counter_label = ctk.CTkLabel(editor_header, text="0 символов", text_color="gray")
        self.counter_label.pack(side="right")

        self.text_box = ctk.CTkTextbox(
            editor, wrap="word", font=ctk.CTkFont(size=15),
            corner_radius=9, border_width=1,
        )
        self.text_box.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self.text_box.insert(
            "1.0",
            "Добро пожаловать в TTS Studio! Введите свой текст, "
            "выберите голос и нажмите кнопку «Создать аудио».",
        )
        self.text_box.bind("<KeyRelease>", self._update_counter)

        footer = ctk.CTkFrame(workspace, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            footer, text="Готово к работе", text_color="gray"
        )
        self.status_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.progress = ctk.CTkProgressBar(footer, mode="indeterminate")
        self.progress.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self.progress.set(0)

        actions = ctk.CTkFrame(footer, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew")
        actions.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.generate_button = ctk.CTkButton(
            actions, text="▶  Создать аудио", height=42,
            command=self._generate,
        )
        self.generate_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.play_button = ctk.CTkButton(
            actions, text="Прослушать", height=42,
            fg_color=("gray75", "gray25"), text_color=("gray10", "white"),
            command=self._play,
        )
        self.play_button.grid(row=0, column=1, sticky="ew", padx=4)

        self.stop_button = ctk.CTkButton(
            actions, text="Остановить", height=42,
            fg_color=("gray75", "gray25"), text_color=("gray10", "white"),
            command=self._stop,
        )
        self.stop_button.grid(row=0, column=2, sticky="ew", padx=4)

        self.save_button = ctk.CTkButton(
            actions, text="Сохранить WAV", height=42,
            command=self._save,
        )
        self.save_button.grid(row=0, column=3, sticky="ew", padx=(8, 0))

    def _on_language_change(self, language: str) -> None:
        voices = LANGUAGES[language]["voices"]
        default_voice = LANGUAGES[language]["default"]
        self.voice_menu.configure(values=list(voices))
        self.voice_var.set(default_voice)

    def _update_counter(self, _event=None) -> None:
        text = self.text_box.get("1.0", "end-1c")
        self.counter_label.configure(text=f"{len(text)} символов")

    def _generate(self) -> None:
        if self.busy:
            return

        text = self.text_box.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Нет текста", "Сначала введите текст для озвучивания.")
            return

        language = self.language_var.get()
        voice_name = self.voice_var.get()
        speaker = LANGUAGES[language]["voices"][voice_name]

        self.busy = True
        self.generate_button.configure(state="disabled")
        self.status_label.configure(text="Подготовка модели и генерация аудио…")
        self.progress.start()

        threading.Thread(
            target=self._generate_worker,
            args=(text, speaker),
            daemon=True,
        ).start()

    def _generate_worker(self, text: str, speaker: str) -> None:
        try:
            audio, sample_rate = self.engine.synthesize(text, speaker)
            self.after(0, lambda: self._generation_complete(audio, sample_rate))
        except Exception as exc:
            self.after(0, lambda error=str(exc): self._generation_failed(error))

    def _generation_complete(self, audio, sample_rate: int) -> None:
        self.audio = audio
        self.sample_rate = sample_rate
        self._finish_busy()
        self.status_label.configure(
            text=f"Готово · {len(audio) / sample_rate:.1f} сек."
        )

    def _generation_failed(self, error: str) -> None:
        self._finish_busy()
        self.status_label.configure(text="Не удалось создать аудио")
        messagebox.showerror("Ошибка синтеза", error)

    def _finish_busy(self) -> None:
        self.progress.stop()
        self.progress.set(0)
        self.generate_button.configure(state="normal")
        self.busy = False

    def _play(self) -> None:
        if self.audio is None:
            messagebox.showinfo("Нет аудио", "Сначала создайте аудиозапись.")
            return
        try:
            play_audio(self.audio, self.sample_rate)
            self.status_label.configure(text="Воспроизведение…")
        except Exception as exc:
            messagebox.showerror("Ошибка воспроизведения", str(exc))

    def _stop(self) -> None:
        stop_audio()
        self.status_label.configure(text="Воспроизведение остановлено")

    def _save(self) -> None:
        if self.audio is None:
            messagebox.showinfo("Нет аудио", "Сначала создайте аудиозапись.")
            return

        path = filedialog.asksaveasfilename(
            title="Сохранить аудио",
            defaultextension=".wav",
            filetypes=[("WAV audio", "*.wav"), ("MP3 audio", "*.mp3")],
            initialfile="tts_audio.wav",
        )
        if not path:
            return

        try:
            if Path(path).suffix.lower() == ".mp3":
                save_mp3(path, self.audio, self.sample_rate)
            else:
                save_wav(path, self.audio, self.sample_rate)
            self.status_label.configure(text=f"Файл сохранён: {Path(path).name}")
            messagebox.showinfo("Сохранено", f"Аудиофайл сохранён:\n{path}")
        except Exception as exc:
            messagebox.showerror("Ошибка сохранения", str(exc))
