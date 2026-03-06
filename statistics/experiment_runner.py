"""Experiment runner for automated multi-simulation data collection."""

from simulation.grid import Grid
from simulation.player import Player
from simulation.simulation_engine import SimulationEngine
from simulation.movement import BoundedRandomMovement
from statistics.stats_engine import StatsEngine
from config import DEFAULT_GRID_SIZE


class ExperimentRunner:
    """Runs batches of simulations and organises results for analysis."""

    def __init__(self, stats_engine):
        self._stats = stats_engine

    # ------------------------------------------------------------------
    # Core experiment
    # ------------------------------------------------------------------

    def run_experiment(
        self,
        grid_width,
        grid_height,
        num_players,
        num_simulations,
        movement_strategy=None,
    ):
        """Run multiple simulations and return aggregated statistics."""
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
        sizes,
        num_players=2,
        num_simulations=50,
    ):
        """Compare meeting times across different (square) grid sizes."""
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
        num_players_list,
        grid_size=DEFAULT_GRID_SIZE,
        num_simulations=50,
    ):
        """Compare meeting times with varying numbers of players."""
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
        grid_size=DEFAULT_GRID_SIZE,
        num_players=2,
        num_simulations=50,
    ):
        """Compare meeting times for different movement strategies."""
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
    def _create_players(num_players, grid):
        """Create players spread along the diagonal of the grid."""
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
