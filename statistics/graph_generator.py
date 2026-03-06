"""Graph generator — creates matplotlib charts from experiment data."""


class GraphGenerator:

    def __init__(self):
        pass

    def plot_grid_size_vs_meeting_time(self, data, save_path=None):
        """Bar chart of average meeting time vs. grid size."""

        import matplotlib.pyplot as plt

        sizes = sorted(data.keys())
        averages = [data[s]["average"] for s in sizes]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar([str(s) for s in sizes], averages, color="steelblue")
        ax.set_xlabel("Grid Size (N×N)")
        ax.set_ylabel("Average Steps to Meet")
        ax.set_title("Grid Size vs. Average Meeting Time")
        ax.grid(axis="y", alpha=0.4)
        self._save_or_show(fig, save_path)

    def plot_player_count_vs_meeting_time(self, data, save_path=None):
        import matplotlib.pyplot as plt

        counts = sorted(data.keys())
        averages = [data[c]["average"] for c in counts]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar([str(c) for c in counts], averages, color="coral")
        ax.set_xlabel("Number of Players")
        ax.set_ylabel("Average Steps to Meet")
        ax.set_title("Player Count vs. Average Meeting Time")
        ax.grid(axis="y", alpha=0.4)
        self._save_or_show(fig, save_path)

    def plot_strategy_comparison(self, data, save_path=None):
        import matplotlib.pyplot as plt

        names = list(data.keys())
        averages = [data[n]["average"] for n in names]
        colors = ["mediumseagreen", "mediumpurple", "goldenrod", "tomato"]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(names, averages, color=colors[: len(names)])
        ax.set_xlabel("Movement Strategy")
        ax.set_ylabel("Average Steps to Meet")
        ax.set_title("Strategy Comparison")
        ax.grid(axis="y", alpha=0.4)
        self._save_or_show(fig, save_path)

    def plot_run_distribution(
        self,
        runs,
        title="Meeting Time Distribution",
        save_path=None,
    ):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(runs, bins=20, color="teal", edgecolor="white", alpha=0.85)
        ax.set_xlabel("Steps to Meet")
        ax.set_ylabel("Frequency")
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.4)
        self._save_or_show(fig, save_path)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _save_or_show(fig, save_path):
        """Save the figure if *save_path* is provided, otherwise display it."""
        import matplotlib.pyplot as plt

        if save_path:
            fig.savefig(save_path, bbox_inches="tight", dpi=150)
            print(f"Chart saved to {save_path}")
        else:
            plt.show()
        plt.close(fig)
