"""Experiment runner for automated multi-simulation data collection."""

from simulation.grid import Grid
from simulation.player import Player
from simulation.simulation_engine import SimulationEngine
from simulation.movement import BoundedRandomMovement
from statistics.stats_engine import StatsEngine
from config import DEFAULT_GRID_SIZE


class ExperimentRunner:
    """Runs batches of simulations and organises results for analysis."""

    def __init__(self, stats_engine: StatsEngine) -> None:
        """
        Initialize the runner.

        Args:
            stats_engine: A StatsEngine that will accumulate results.
        """
        self._stats = stats_engine

    # ------------------------------------------------------------------
    # Core experiment
    # ------------------------------------------------------------------

    def run_experiment(
        self,
        grid_width: int,
        grid_height: int,
        num_players: int,
        num_simulations: int,
        movement_strategy=None,
    ) -> dict:
        """
        Run *num_simulations* independent simulations and return aggregated stats.

        Args:
            grid_width:         Width of the grid.
            grid_height:        Height of the grid.
            num_players:        Number of players (≥ 2).
            num_simulations:    How many independent runs to execute.
            movement_strategy:  Optional MovementStrategy override.

        Returns:
            A summary dict from StatsEngine.get_summary() plus a 'runs' key
            containing the raw step list.
        """
        strategy = movement_strategy or BoundedRandomMovement()
        local_stats = StatsEngine()

        for _ in range(num_simulations):
            grid = Grid(grid_width, grid_height)
            players = self._create_players(num_players, grid)
            engine = SimulationEngine(grid, players, strategy)
            steps = engine.run()
            local_stats.record_run(steps)
            self._stats.record_run(steps)

        summary = local_stats.get_summary()
        summary["runs"] = local_stats.get_all_runs()
        return summary

    # ------------------------------------------------------------------
    # Convenience experiments
    # ------------------------------------------------------------------

    def run_grid_size_experiment(
        self,
        sizes: list,
        num_players: int = 2,
        num_simulations: int = 50,
    ) -> dict:
        """
        Compare meeting times across different (square) grid sizes.

        Args:
            sizes:           List of integer grid side-lengths to test.
            num_players:     Number of players per run.
            num_simulations: Runs per grid size.

        Returns:
            Dict mapping each size to its summary dict.
        """
        results = {}
        for size in sizes:
            self._stats.reset()
            summary = self.run_experiment(
                size, size, num_players, num_simulations
            )
            results[size] = summary
        return results

    def run_player_count_experiment(
        self,
        num_players_list: list,
        grid_size: int = DEFAULT_GRID_SIZE,
        num_simulations: int = 50,
    ) -> dict:
        """
        Compare meeting times with varying numbers of players.

        Args:
            num_players_list: List of player counts to test.
            grid_size:        Side-length of the (square) grid.
            num_simulations:  Runs per player count.

        Returns:
            Dict mapping each player count to its summary dict.
        """
        results = {}
        for count in num_players_list:
            self._stats.reset()
            summary = self.run_experiment(
                grid_size, grid_size, count, num_simulations
            )
            results[count] = summary
        return results

    def run_strategy_comparison(
        self,
        grid_size: int = DEFAULT_GRID_SIZE,
        num_players: int = 2,
        num_simulations: int = 50,
    ) -> dict:
        """
        Compare meeting times for different movement strategies.

        Returns:
            Dict mapping strategy name to its summary dict.
        """
        from simulation.movement import RandomMovement

        strategies = {
            "BoundedRandom": BoundedRandomMovement(),
            "Random": RandomMovement(),
        }
        results = {}
        for name, strategy in strategies.items():
            self._stats.reset()
            summary = self.run_experiment(
                grid_size, grid_size, num_players, num_simulations, strategy
            )
            results[name] = summary
        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _create_players(num_players: int, grid: Grid) -> list:
        """
        Spread *num_players* evenly across the grid for a balanced start.

        The first player is placed at (0, 0) and the last at the opposite
        corner; others are distributed along the diagonal.
        """
        w, h = grid.get_dimensions()
        players = []
        for i in range(num_players):
            if num_players == 1:
                x, y = 0, 0
            else:
                frac = i / (num_players - 1)
                x = int(round(frac * (w - 1)))
                y = int(round(frac * (h - 1)))
            players.append(Player(i, x, y))
        return players
