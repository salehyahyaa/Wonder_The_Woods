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

    def __init__(self, grid, players, movement_strategy=None):
        self._grid = grid
        self._players = players
        self._strategy = movement_strategy or BoundedRandomMovement()
        self._step_count = 0

        self._groups = [{p.get_id()} for p in players]

        self._player_map = {p.get_id(): p for p in players}

        self._meeting_positions = []

        self._merge_groups()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def step(self):
        """Advance the simulation by one step."""
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

    def run(self):
        """Run the simulation until all players have met."""
        max_steps = 10_000_000  # safety cap
        while len(self._groups) > 1 and self._step_count < max_steps:
            self.step()
        return self._step_count

    def get_step_count(self):
        """Return the number of steps executed so far."""
        return self._step_count

    def reset(self):
        """Reset the simulation: restore all players and clear state."""
        self._step_count = 0
        self._meeting_positions = []
        for player in self._players:
            player.reset()
        self._groups = [{p.get_id()} for p in self._players]
        self._merge_groups()

    def get_players(self):
        """Return the list of Player objects."""
        return self._players

    def check_meetings(self):
        """Return the current groups that contain more than one player."""
        return [g for g in self._groups if len(g) > 1]

    def get_meeting_positions(self):
        """Return positions where group merges occurred in the last step."""
        return list(self._meeting_positions)

    def is_finished(self):
        """Return True when all players are in a single group."""
        return len(self._groups) <= 1

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _merge_groups(self):
        """Merge any groups that currently share the same grid position."""
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

    def _get_group_position(self, group):
        """Return the current position of the representative player in *group*."""
        rep_id = next(iter(group))
        p = self._player_map[rep_id]
        return p.position
