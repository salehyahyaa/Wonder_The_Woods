"""Movement strategy module for the Wandering in the Woods Simulation."""

import random
from config import DIRECTIONS


class MovementStrategy:
    """Base class for all movement strategies (strategy pattern)."""

    def get_next_position(self, current_x, current_y, grid):
        """Compute the next (x, y) position for a player."""
        raise NotImplementedError("Subclasses must implement get_next_position().")


class RandomMovement(MovementStrategy):
    """
    Pure random walk.

    Picks a random direction from DIRECTIONS; does *not* guarantee the
    resulting position is inside the grid (caller should verify/clamp).
    """

    def get_next_position(self, current_x, current_y, grid):
        """Return a randomly chosen adjacent position (may be out of bounds)."""
        dx, dy = random.choice(DIRECTIONS)
        return (current_x + dx, current_y + dy)


class BoundedRandomMovement(MovementStrategy):
    """
    Random walk that always stays within the grid boundaries.

    Builds a list of valid neighbouring cells (including the current position
    as a "stay" option) and picks one at random.  The stay option breaks the
    bipartite (checkerboard) parity constraint on grid graphs, ensuring that
    any two players can eventually share a cell regardless of starting parity.
    """

    def get_next_position(self, current_x, current_y, grid):
        """Return a randomly chosen, in-bounds adjacent position (or stay)."""
        # Include the current cell so the walk is aperiodic (breaks bipartiteness)
        candidates = [(current_x, current_y)]
        for dx, dy in DIRECTIONS:
            nx, ny = current_x + dx, current_y + dy
            if grid.is_valid_position(nx, ny):
                candidates.append((nx, ny))

        return random.choice(candidates)
