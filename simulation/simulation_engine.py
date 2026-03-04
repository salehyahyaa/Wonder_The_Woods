"""Simulation engine for the Wandering in the Woods project."""

from simulation.movement import BoundedRandomMovement


class SimulationEngine:
    """
    Orchestrates the wandering simulation.

    Supports two movement modes:
    * **Independent** (Version 1): every player moves on their own each step.
    * **Group movement** (Version 2+): when players meet, they merge into a
      group and move as one unit until all players have merged.
    """

    def __init__(self, grid, players: list, movement_strategy=None) -> None:
        """
        Initialise the engine.

        Args:
            grid:               The Grid in which players wander.
            players:            List of Player objects.
            movement_strategy:  A MovementStrategy instance (defaults to
                                BoundedRandomMovement).
        """
        self._grid = grid
        self._players = players
        self._strategy = movement_strategy or BoundedRandomMovement()
        self._step_count = 0

        # Groups: a list of sets, each set holds player ids that travel together.
        self._groups: list[set] = [{p.get_id()} for p in players]

        # Map player_id -> Player for fast lookup
        self._player_map: dict = {p.get_id(): p for p in players}

        # Positions where meetings happened (for rendering highlights)
        self._meeting_positions: list = []

        # Merge any players that start on the same cell
        self._merge_groups()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def step(self) -> bool:
        """
        Advance the simulation by one step.

        Each group chooses one random move; all members of the group move
        to the new position together.  After moving, overlapping groups
        are merged.

        Returns:
            True if a new meeting (group merge) occurred this step.
        """
        self._step_count += 1
        self._meeting_positions = []

        # Move each group as a unit
        for group in self._groups:
            # Use the position of any member as the group's reference position
            rep_id = next(iter(group))
            rep = self._player_map[rep_id]
            nx, ny = self._strategy.get_next_position(rep.x, rep.y, self._grid)
            # BoundedRandomMovement guarantees validity; extra safety clamp
            nx, ny = self._grid.clamp_position(nx, ny)
            for pid in group:
                self._player_map[pid].move_to(nx, ny)

        # Merge groups that now share the same position
        meeting_occurred = self._merge_groups()
        return meeting_occurred

    def run(self) -> int:
        """
        Run the simulation until all players have met (one group remaining).

        Returns:
            The total number of steps taken.
        """
        max_steps = 10_000_000  # safety cap
        while len(self._groups) > 1 and self._step_count < max_steps:
            self.step()
        return self._step_count

    def get_step_count(self) -> int:
        """Return the number of steps executed so far."""
        return self._step_count

    def reset(self) -> None:
        """Reset the simulation: restore all players and clear state."""
        self._step_count = 0
        self._meeting_positions = []
        for player in self._players:
            player.reset()
        self._groups = [{p.get_id()} for p in self._players]
        self._merge_groups()

    def get_players(self) -> list:
        """Return the list of Player objects."""
        return self._players

    def check_meetings(self) -> list:
        """
        Return the current groups that contain more than one player.

        Returns:
            List of sets, each set containing the ids of players that share
            a position.
        """
        return [g for g in self._groups if len(g) > 1]

    def get_meeting_positions(self) -> list:
        """Return positions where group merges occurred in the last step."""
        return list(self._meeting_positions)

    def is_finished(self) -> bool:
        """Return True when all players are in a single group."""
        return len(self._groups) <= 1

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _merge_groups(self) -> bool:
        """
        Merge any groups that currently share the same grid position.

        Returns:
            True if at least one merge happened.
        """
        merged = False
        changed = True
        while changed:
            changed = False
            new_groups: list[set] = []
            used = [False] * len(self._groups)
            for i, group_a in enumerate(self._groups):
                if used[i]:
                    continue
                pos_a = self._get_group_position(group_a)
                merged_group = set(group_a)
                for j, group_b in enumerate(self._groups):
                    if i == j or used[j]:
                        continue
                    pos_b = self._get_group_position(group_b)
                    if pos_a == pos_b:
                        merged_group |= group_b
                        used[j] = True
                        merged = True
                        changed = True
                        self._meeting_positions.append(pos_a)
                used[i] = True
                new_groups.append(merged_group)
            self._groups = new_groups
        return merged

    def _get_group_position(self, group: set) -> tuple:
        """Return the current position of the representative player in *group*."""
        rep_id = next(iter(group))
        p = self._player_map[rep_id]
        return p.position
