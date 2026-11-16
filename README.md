# TTS Studio

Настольное приложение для локального преобразования текста в речь на русском и английском языках.

## Технологии

- Python 3.11+
- CustomTkinter
- Silero TTS (multilingual checkpoint)
- PyTorch
- SoundDevice и SoundFile

## Возможности первой версии

- Современный интерфейс на CustomTkinter.
- Русский и английский языки.
- Выбор доступного голоса Silero.
- Локальная генерация речи на CPU.
- Прослушивание результата.
- Сохранение в WAV.
- Экспорт в MP3 при установленном FFmpeg и pydub.

## Установка в Windows

Рекомендуется Python 3.11 (64-bit).

```powershell
git clone https://github.com/ffghrenty-cloud/TTSApp.git
cd TTSApp

py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
```

Установите PyTorch и torchaudio. Для CPU используйте официальную команду с сайта PyTorch:
https://pytorch.org/get-started/locally/

Затем установите остальные зависимости:

```powershell
pip install -r requirements.txt
python main.py
```

## Первая загрузка модели

При первом нажатии «Создать аудио» Silero загружает модель через PyTorch Hub. Для этого первого запуска необходимо подключение к интернету. После загрузки модель остаётся в локальном кэше PyTorch и синтез выполняется на компьютере.

## Структура проекта

```text
TTSApp/
├── main.py
├── interface.py
├── tts_engine.py
├── audio_player.py
├── audio_export.py
├── config.py
├── requirements.txt
└── .gitignore
```

## Статус

Версия 0.1.0 — начальный каркас интерфейса и интеграция локального движка. Реальный запуск и проверка синтеза выполняются на целевом Windows-компьютере.

## Лицензии

Silero TTS и PyTorch являются сторонними проектами. Перед распространением собранного приложения проверьте условия лицензирования используемых моделей и зависимостей.
