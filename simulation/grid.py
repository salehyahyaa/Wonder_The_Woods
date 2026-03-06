"""Grid module for the Wandering in the Woods Simulation."""

from config import MIN_GRID_SIZE, MAX_GRID_SIZE


class Grid:
    """Represents the rectangular game grid (the 'woods')."""

    def __init__(self, width, height):
        self._width = max(MIN_GRID_SIZE, min(MAX_GRID_SIZE, width))
        self._height = max(MIN_GRID_SIZE, min(MAX_GRID_SIZE, height))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_valid_position(self, x, y):
        """Return True if (x, y) lies inside the grid."""
        return 0 <= x < self._width and 0 <= y < self._height

    def get_dimensions(self):
        """Return (width, height) of the grid."""
        return (self._width, self._height)

    def clamp_position(self, x, y):
        """Clamp (x, y) so it stays inside the grid boundaries."""
        clamped_x = max(0, min(self._width - 1, x))
        clamped_y = max(0, min(self._height - 1, y))
        return (clamped_x, clamped_y)

    @property
    def width(self):
        """Number of columns."""
        return self._width

    @property
    def height(self):
        """Number of rows."""
        return self._height

    def __repr__(self) -> str:
        return f"Grid(width={self._width}, height={self._height})"
