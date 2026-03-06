"""Statistics engine for recording and summarising simulation runs."""


class StatsEngine:
    """Records results from individual simulation runs and computes summary statistics."""

    def __init__(self):
        self._runs = []

    # ------------------------------------------------------------------
    # Data collection
    # ------------------------------------------------------------------

    def record_run(self, steps):
        """Append the step count from a completed run."""
        self._runs.append(steps)

    def reset(self):
        """Clear all recorded run data."""
        self._runs = []

    # ------------------------------------------------------------------
    # Derived statistics
    # ------------------------------------------------------------------

    def get_shortest(self):
        """Return the minimum steps across all recorded runs (0 if none)."""
        return min(self._runs) if self._runs else 0

    def get_longest(self):
        return max(self._runs) if self._runs else 0

    def get_average(self):
        if not self._runs:
            return 0.0
        return sum(self._runs) / len(self._runs)

    def get_all_runs(self):
        return list(self._runs)

    def get_run_count(self):
        return len(self._runs)

    def get_summary(self):
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
