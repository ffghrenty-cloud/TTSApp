"""Application settings and supported Silero voices."""

APP_NAME = "TTS Studio"
APP_VERSION = "0.1.0"

# Silero multi_v2 includes Russian and English speakers in one model.
MODEL_REPOSITORY = "snakers4/silero-models"
MODEL_NAME = "silero_tts"
MODEL_LANGUAGE = "multi"
MODEL_CHECKPOINT = "multi_v2"
SAMPLE_RATE = 48000
DEVICE = "cpu"

LANGUAGES = {
    "Русский": {
        "code": "ru",
        "voices": {
            "Аидар (мужской)": "aidar",
            "Бая (женский)": "baya",
            "Ксения (женский)": "kseniya",
            "Ирина (женский)": "irina",
            "Руслан (мужской)": "ruslan",
            "Наташа (женский)": "natasha",
        },
        "default": "Бая (женский)",
    },
    "English": {
        "code": "en",
        "voices": {
            "Larry (male)": "lj",
        },
        "default": "Larry (male)",
    },
}
