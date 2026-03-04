"""Controls module — event handling and UI input management."""

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False

from config import DEFAULT_GRID_SIZE, MIN_GRID_SIZE, MAX_GRID_SIZE


class Controls:
    """Translates raw pygame events into high-level action dictionaries."""

    # Action key constants
    ACTION_QUIT = "quit"
    ACTION_RESTART = "restart"
    ACTION_STEP = "step"
    ACTION_RUN = "run"
    ACTION_PAUSE = "pause"
    ACTION_GRID_SIZE = "grid_size"
    ACTION_NUM_PLAYERS = "num_players"
    ACTION_BUTTON = "button"
    ACTION_NONE = "none"

    def __init__(self) -> None:
        """Initialize default input state."""
        self._grid_size: int = DEFAULT_GRID_SIZE
        self._num_players: int = 2

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event) -> dict:
        """
        Translate a pygame event into an action dictionary.

        Returns a dict with at least an 'action' key.
        """
        if not _PYGAME_AVAILABLE:
            return {"action": self.ACTION_NONE}

        if event.type == pygame.QUIT:
            return {"action": self.ACTION_QUIT}

        if event.type == pygame.KEYDOWN:
            return self._handle_keydown(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Only left-click counts as UI click
            if getattr(event, "button", 1) == 1:
                return {"action": self.ACTION_BUTTON, "pos": event.pos}
            return {"action": self.ACTION_NONE}

        return {"action": self.ACTION_NONE}

    # ------------------------------------------------------------------
    # Input accessors
    # ------------------------------------------------------------------

    def get_grid_size_input(self) -> tuple[int, int]:
        """Return the current (width, height) chosen by the user."""
        return (self._grid_size, self._grid_size)

    def get_num_players_input(self) -> int:
        """Return the current player count chosen by the user."""
        return self._num_players

    def set_grid_size(self, size: int) -> None:
        """Set grid size, clamped to valid range."""
        self._grid_size = max(MIN_GRID_SIZE, min(MAX_GRID_SIZE, int(size)))

    def set_num_players(self, count: int) -> None:
        """Set number of players (clamped to 2..4 for this project spec)."""
        self._num_players = max(2, min(4, int(count)))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _handle_keydown(self, event) -> dict:
        """Map keyboard keys to actions."""
        key = event.key

        if key in (pygame.K_q, pygame.K_ESCAPE):
            return {"action": self.ACTION_QUIT}

        if key == pygame.K_r:
            return {"action": self.ACTION_RESTART}

        if key in (pygame.K_SPACE, pygame.K_s):
            return {"action": self.ACTION_STEP}

        if key == pygame.K_RETURN:
            return {"action": self.ACTION_RUN}

        if key == pygame.K_p:
            return {"action": self.ACTION_PAUSE}

        # Optional: quick setup shortcuts (teacher mode)
        # Arrow keys adjust grid size; number keys adjust players
        if key == pygame.K_UP:
            self.set_grid_size(self._grid_size + 1)
            return {"action": self.ACTION_GRID_SIZE, "size": self._grid_size}

        if key == pygame.K_DOWN:
            self.set_grid_size(self._grid_size - 1)
            return {"action": self.ACTION_GRID_SIZE, "size": self._grid_size}

        if key in (pygame.K_2, pygame.K_3, pygame.K_4):
            self.set_num_players(int(pygame.key.name(key)))
            return {"action": self.ACTION_NUM_PLAYERS, "count": self._num_players}

        return {"action": self.ACTION_NONE, "key": key}
