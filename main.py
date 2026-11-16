"""TTS Studio application entry point."""

from interface import TTSApplication


def main() -> None:
    app = TTSApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
