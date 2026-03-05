from __future__ import annotations

import os

try:
    import pygame
except Exception:
    pygame = None


class AudioManager:
    """
    Simple audio manager:
    - pygame.mixer music + sfx
    - optional "speak" placeholder that uses on-screen only unless you add TTS
    """

    def __init__(self) -> None:
        self._ready = False
        self._spoken_once: set[str] = set()

        # Map logical names to files (put your files under assets/audio/)
        self._music = {
            "k2_music": "assets/audio/k2_music.ogg",
            "setup_music": "assets/audio/setup_music.ogg",
            "v2_music": "assets/audio/v2_music.ogg",
            "v3_music": "assets/audio/v3_music.ogg",
        }
        self._sfx = {
            "click": "assets/audio/click.wav",
            "place": "assets/audio/place.wav",
            "start": "assets/audio/start.wav",
            "meet": "assets/audio/meet.wav",
            "error": "assets/audio/error.wav",
        }
        self._cache = {}

    def initialize(self) -> None:
        if pygame is None:
            return
        try:
            pygame.mixer.init()
            self._ready = True
        except Exception:
            self._ready = False

    def play_music(self, name: str, loop: bool = True) -> None:
        if not self._ready:
            return
        path = self._music.get(name)
        if not path or not os.path.exists(path):
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception:
            pass

    def play_sfx(self, name: str) -> None:
        if not self._ready:
            return
        path = self._sfx.get(name)
        if not path or not os.path.exists(path):
            return
        try:
            if path not in self._cache:
                self._cache[path] = pygame.mixer.Sound(path)
            self._cache[path].play()
        except Exception:
            pass

    def speak(self, text: str) -> None:
        # Placeholder: you can upgrade this to pyttsx3 later.
        # For grading, the simplest is to ship prerecorded prompts as audio files.
        # If you want TTS, ask me and I’ll add it safely.
        return

    def speak_once(self, key: str, text: str) -> None:
        if key in self._spoken_once:
            return
        self._spoken_once.add(key)
        self.speak(text)