"""Player module for the Wandering in the Woods Simulation."""

from config import PLAYER_COLORS


class Player:
    """Represents a player (wanderer) inside the woods."""

    def __init__(self, player_id: int, x: int, y: int, color=None) -> None:
        """
        Initialize a player.

        Args:
            player_id: Unique integer identifier.
            x:         Initial column position.
            y:         Initial row position.
            color:     RGB tuple for rendering; defaults to a palette colour.
        """
        self._id = player_id
        self._x = x
        self._y = y

        if color is None:
            index = player_id % len(PLAYER_COLORS)
            self._color = PLAYER_COLORS[index]
        else:
            self._color = color

        # Track starting position
        self._start_x = x
        self._start_y = y

        # NEW: per-player movement counter
        self._steps_taken = 0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def position(self) -> tuple:
        """Current (x, y) position."""
        return (self._x, self._y)

    @property
    def x(self) -> int:
        """Current column."""
        return self._x

    @property
    def y(self) -> int:
        """Current row."""
        return self._y

    @property
    def steps_taken(self) -> int:
        """Return how many moves this player has made."""
        return self._steps_taken

    # ------------------------------------------------------------------
    # Mutators
    # ------------------------------------------------------------------

    def move_to(self, x: int, y: int) -> None:
        """Move the player to the given grid coordinates."""
        self._x = x
        self._y = y

        # Increment move counter
        self._steps_taken += 1

    def reset(self) -> None:
        """Return the player to their starting position."""
        self._x = self._start_x
        self._y = self._start_y
        self._steps_taken = 0

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_id(self) -> int:
        """Return the player's unique identifier."""
        return self._id

    def get_color(self) -> tuple:
        """Return the player's display colour as an RGB tuple."""
        return self._color

    def get_steps(self) -> int:
        """Return how many steps the player has taken."""
        return self._steps_taken

    def __repr__(self) -> str:
        return f"Player(id={self._id}, pos=({self._x}, {self._y}), steps={self._steps_taken})"