"""
main.py — Entry point for the Wandering in the Woods Simulation.

Usage:
    python main.py [--version {1,2,3}] [--headless]

Options:
    --version   Which version of the simulation to run (default: 1).
    --headless  Run a text-based simulation without any graphical display.
"""

import argparse
import sys

# ---------------------------------------------------------------------------
# Try to import pygame; fall back gracefully if unavailable.
# ---------------------------------------------------------------------------
try:
    import pygame  # noqa: F401 — we only test availability here
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False


def run_headless(version: int = 1) -> None:
    """Execute a text-based simulation and print results to stdout."""
    from simulation.grid import Grid
    from simulation.player import Player
    from simulation.simulation_engine import SimulationEngine
    from simulation.movement import BoundedRandomMovement
    from statistics.stats_engine import StatsEngine
    from statistics.experiment_runner import ExperimentRunner
    from config import DEFAULT_GRID_SIZE

    print(f"=== Wandering in the Woods — Headless Mode (Version {version}) ===\n")

    if version == 1:
        # Single run on a 10×10 grid with 2 players at opposite corners
        grid = Grid(DEFAULT_GRID_SIZE, DEFAULT_GRID_SIZE)
        players = [Player(0, 0, 0), Player(1, 9, 9)]
        engine = SimulationEngine(grid, players, BoundedRandomMovement())
        steps = engine.run()
        print(f"Players met after {steps} steps.")

    elif version == 2:
        # Multiple runs with statistics
        stats = StatsEngine()
        num_runs = 20
        grid_size = DEFAULT_GRID_SIZE
        print(f"Running {num_runs} simulations on a {grid_size}×{grid_size} grid …")
        for i in range(num_runs):
            grid = Grid(grid_size, grid_size)
            players = [Player(0, 0, 0), Player(1, grid_size - 1, grid_size - 1)]
            engine = SimulationEngine(grid, players, BoundedRandomMovement())
            steps = engine.run()
            stats.record_run(steps)
            print(f"  Run {i + 1:>3}: {steps} steps")
        summary = stats.get_summary()
        print(f"\nSummary over {summary['count']} runs:")
        print(f"  Shortest : {summary['shortest']}")
        print(f"  Longest  : {summary['longest']}")
        print(f"  Average  : {summary['average']:.2f}")

    else:
        # Version 3 — experiment mode
        stats = StatsEngine()
        runner = ExperimentRunner(stats)
        print("Running grid-size experiment (sizes 5, 10, 15, 20; 20 sims each) …")
        results = runner.run_grid_size_experiment(
            sizes=[5, 10, 15, 20], num_players=2, num_simulations=20
        )
        for size, summary in results.items():
            print(
                f"  {size}×{size}: avg={summary['average']:.1f}  "
                f"min={summary['shortest']}  max={summary['longest']}"
            )
        print("\nRunning player-count experiment (2–4 players, 20 sims each) …")
        stats2 = StatsEngine()
        runner2 = ExperimentRunner(stats2)
        results2 = runner2.run_player_count_experiment(
            num_players_list=[2, 3, 4], grid_size=10, num_simulations=20
        )
        for count, summary in results2.items():
            print(
                f"  {count} players: avg={summary['average']:.1f}  "
                f"min={summary['shortest']}  max={summary['longest']}"
            )

    print("\nDone.")


def main() -> None:
    """Parse CLI arguments and launch the appropriate simulation mode."""
    parser = argparse.ArgumentParser(
        description="Wandering in the Woods Simulation"
    )
    parser.add_argument(
        "--version",
        type=int,
        choices=[1, 2, 3],
        default=1,
        help="Simulation version: 1=K-2, 2=Grades 3-5, 3=Grades 6-8 (default: 1)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without a graphical display (text output only)",
    )
    args = parser.parse_args()

    if args.headless or not _PYGAME_AVAILABLE:
        if not args.headless and not _PYGAME_AVAILABLE:
            print("pygame is not available — falling back to headless mode.\n")
        run_headless(args.version)
    else:
        from ui.game_window import GameWindow
        window = GameWindow(version=args.version)
        window.run()


if __name__ == "__main__":
    main()
