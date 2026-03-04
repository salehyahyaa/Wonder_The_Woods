"""Statistics engine for recording and summarising simulation runs."""


class StatsEngine:
    """Records results from individual simulation runs and computes summary statistics."""

    def __init__(self) -> None:
        """Initialize with an empty run history."""
        self._runs: list[int] = []

    # ------------------------------------------------------------------
    # Data collection
    # ------------------------------------------------------------------

    def record_run(self, steps: int) -> None:
        """
        Append the step count from a completed run.

        Args:
            steps: Number of steps the simulation took to finish.
        """
        self._runs.append(steps)

    def reset(self) -> None:
        """Clear all recorded run data."""
        self._runs = []

    # ------------------------------------------------------------------
    # Derived statistics
    # ------------------------------------------------------------------

    def get_shortest(self) -> int:
        """Return the minimum steps across all recorded runs (0 if none)."""
        return min(self._runs) if self._runs else 0

    def get_longest(self) -> int:
        """Return the maximum steps across all recorded runs (0 if none)."""
        return max(self._runs) if self._runs else 0

    def get_average(self) -> float:
        """Return the mean step count across all recorded runs (0.0 if none)."""
        if not self._runs:
            return 0.0
        return sum(self._runs) / len(self._runs)

    def get_all_runs(self) -> list:
        """Return a copy of all recorded step counts."""
        return list(self._runs)

    def get_run_count(self) -> int:
        """Return the number of recorded runs."""
        return len(self._runs)

    def get_summary(self) -> dict:
        """
        Return a summary dictionary with key statistics.

        Keys: count, shortest, longest, average.
        """
        return {
            "count": self.get_run_count(),
            "shortest": self.get_shortest(),
            "longest": self.get_longest(),
            "average": round(self.get_average(), 2),
        }

    def __repr__(self) -> str:
        return (
            f"StatsEngine(runs={self.get_run_count()}, "
            f"avg={self.get_average():.1f})"
        )
