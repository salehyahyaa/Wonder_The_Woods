import os

try:
    import pygame
except Exception:
    pygame = None


class AudioManager:
    def __init__(self):
        self._ready = False
        self._spoken_once = set()

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

    def initialize(self):
        if pygame is None:
            return
        try:
            pygame.mixer.init()
            self._ready = True
        except Exception:
            self._ready = False

    def play_music(self, name, loop=True):
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

    def play_sfx(self, name):
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

    def speak(self, text):
        """Optional hook for text-to-speech or other audio prompts."""
        return

    def speak_once(self, key, text):
        if key in self._spoken_once:
            return
        self._spoken_once.add(key)
        self.speak(text)