"""Tests for the Wandering in the Woods Simulation."""

import sys
import os

# Ensure the project root is on the path so imports resolve correctly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from simulation.grid import Grid
from simulation.player import Player
from simulation.movement import RandomMovement, BoundedRandomMovement
from simulation.simulation_engine import SimulationEngine
from statistics.stats_engine import StatsEngine
from statistics.experiment_runner import ExperimentRunner


# ---------------------------------------------------------------------------
# Grid tests
# ---------------------------------------------------------------------------

def test_grid_valid_position_inside():
    grid = Grid(10, 10)
    assert grid.is_valid_position(0, 0) is True
    assert grid.is_valid_position(9, 9) is True
    assert grid.is_valid_position(5, 5) is True


def test_grid_valid_position_outside():
    grid = Grid(10, 10)
    assert grid.is_valid_position(-1, 0) is False
    assert grid.is_valid_position(0, -1) is False
    assert grid.is_valid_position(10, 0) is False
    assert grid.is_valid_position(0, 10) is False


def test_grid_get_dimensions():
    grid = Grid(8, 6)
    assert grid.get_dimensions() == (8, 6)


def test_grid_clamp_position():
    grid = Grid(10, 10)
    assert grid.clamp_position(-3, 5) == (0, 5)
    assert grid.clamp_position(15, 5) == (9, 5)
    assert grid.clamp_position(5, -1) == (5, 0)
    assert grid.clamp_position(5, 20) == (5, 9)
    assert grid.clamp_position(3, 3) == (3, 3)


def test_grid_enforces_min_size():
    grid = Grid(1, 1)
    w, h = grid.get_dimensions()
    assert w >= 5
    assert h >= 5


def test_grid_enforces_max_size():
    grid = Grid(9999, 9999)
    w, h = grid.get_dimensions()
    assert w <= 50
    assert h <= 50


# ---------------------------------------------------------------------------
# Player tests
# ---------------------------------------------------------------------------

def test_player_initial_position():
    player = Player(0, 3, 7)
    assert player.position == (3, 7)
    assert player.x == 3
    assert player.y == 7


def test_player_move_to():
    player = Player(1, 0, 0)
    player.move_to(4, 6)
    assert player.position == (4, 6)


def test_player_get_id():
    player = Player(42, 0, 0)
    assert player.get_id() == 42


def test_player_get_color_default():
    player = Player(0, 0, 0)
    color = player.get_color()
    assert isinstance(color, tuple)
    assert len(color) == 3


def test_player_get_color_custom():
    custom = (123, 200, 50)
    player = Player(0, 0, 0, color=custom)
    assert player.get_color() == custom


def test_player_reset():
    player = Player(0, 2, 3)
    player.move_to(8, 9)
    player.reset()
    assert player.position == (2, 3)


# ---------------------------------------------------------------------------
# Movement strategy tests
# ---------------------------------------------------------------------------

def test_bounded_random_movement_stays_in_grid():
    grid = Grid(10, 10)
    strategy = BoundedRandomMovement()
    for _ in range(200):
        nx, ny = strategy.get_next_position(5, 5, grid)
        assert grid.is_valid_position(nx, ny)


def test_bounded_random_movement_corner():
    grid = Grid(10, 10)
    strategy = BoundedRandomMovement()
    for _ in range(100):
        nx, ny = strategy.get_next_position(0, 0, grid)
        assert grid.is_valid_position(nx, ny)


def test_random_movement_returns_tuple():
    grid = Grid(10, 10)
    strategy = RandomMovement()
    result = strategy.get_next_position(5, 5, grid)
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_movement_strategy_base_raises():
    from simulation.movement import MovementStrategy
    strategy = MovementStrategy()
    with pytest.raises(NotImplementedError):
        strategy.get_next_position(0, 0, Grid(10, 10))


# ---------------------------------------------------------------------------
# SimulationEngine tests
# ---------------------------------------------------------------------------

def test_simulation_engine_runs_to_completion():
    grid = Grid(10, 10)
    players = [Player(0, 0, 0), Player(1, 9, 9)]
    engine = SimulationEngine(grid, players)
    steps = engine.run()
    assert steps > 0
    assert engine.is_finished()


def test_simulation_engine_step_increments():
    grid = Grid(10, 10)
    players = [Player(0, 0, 0), Player(1, 9, 9)]
    engine = SimulationEngine(grid, players)
    engine.step()
    assert engine.get_step_count() == 1
    engine.step()
    assert engine.get_step_count() == 2


def test_simulation_engine_reset():
    grid = Grid(10, 10)
    players = [Player(0, 0, 0), Player(1, 9, 9)]
    engine = SimulationEngine(grid, players)
    engine.run()
    engine.reset()
    assert engine.get_step_count() == 0
    assert not engine.is_finished()


def test_simulation_engine_get_players():
    grid = Grid(10, 10)
    players = [Player(0, 0, 0), Player(1, 5, 5)]
    engine = SimulationEngine(grid, players)
    assert engine.get_players() is players


def test_simulation_engine_immediate_meeting():
    """Players that start on the same cell are already meeting."""
    grid = Grid(10, 10)
    players = [Player(0, 5, 5), Player(1, 5, 5)]
    engine = SimulationEngine(grid, players)
    # After one step both groups will merge (they share position each step)
    steps = engine.run()
    assert steps >= 0


def test_simulation_engine_group_movement():
    """Once merged, players should share the same position every step."""
    grid = Grid(10, 10)
    # Players start at the same cell — they should be merged immediately at init
    players = [Player(0, 5, 5), Player(1, 5, 5)]
    engine = SimulationEngine(grid, players)
    # Should be merged at init since they share a cell
    assert engine.is_finished()
    # Take a step — both players must remain together
    engine.step()
    pos_a = players[0].position
    pos_b = players[1].position
    assert pos_a == pos_b


def test_simulation_check_meetings():
    grid = Grid(10, 10)
    players = [Player(0, 5, 5), Player(1, 5, 5)]
    engine = SimulationEngine(grid, players)
    engine.step()
    meetings = engine.check_meetings()
    # Both players at the same spot — should be one group of 2
    assert any(len(g) >= 2 for g in meetings)


def test_simulation_three_players():
    grid = Grid(10, 10)
    players = [Player(0, 0, 0), Player(1, 9, 9), Player(2, 0, 9)]
    engine = SimulationEngine(grid, players)
    steps = engine.run()
    assert steps > 0
    assert engine.is_finished()


# ---------------------------------------------------------------------------
# StatsEngine tests
# ---------------------------------------------------------------------------

def test_stats_engine_record_and_count():
    stats = StatsEngine()
    stats.record_run(10)
    stats.record_run(20)
    assert stats.get_run_count() == 2


def test_stats_engine_shortest_longest():
    stats = StatsEngine()
    for v in [5, 15, 10]:
        stats.record_run(v)
    assert stats.get_shortest() == 5
    assert stats.get_longest() == 15


def test_stats_engine_average():
    stats = StatsEngine()
    for v in [10, 20, 30]:
        stats.record_run(v)
    assert abs(stats.get_average() - 20.0) < 1e-9


def test_stats_engine_empty():
    stats = StatsEngine()
    assert stats.get_shortest() == 0
    assert stats.get_longest() == 0
    assert stats.get_average() == 0.0
    assert stats.get_run_count() == 0


def test_stats_engine_reset():
    stats = StatsEngine()
    stats.record_run(42)
    stats.reset()
    assert stats.get_run_count() == 0


def test_stats_engine_get_all_runs():
    stats = StatsEngine()
    data = [3, 7, 12]
    for v in data:
        stats.record_run(v)
    assert stats.get_all_runs() == data


def test_stats_engine_get_summary_keys():
    stats = StatsEngine()
    stats.record_run(10)
    summary = stats.get_summary()
    assert "count" in summary
    assert "shortest" in summary
    assert "longest" in summary
    assert "average" in summary


# ---------------------------------------------------------------------------
# ExperimentRunner tests
# ---------------------------------------------------------------------------

def test_experiment_runner_basic():
    stats = StatsEngine()
    runner = ExperimentRunner(stats)
    result = runner.run_experiment(10, 10, 2, 5)
    assert result["count"] == 5
    assert result["shortest"] > 0
    assert result["longest"] >= result["shortest"]
    assert "runs" in result
    assert len(result["runs"]) == 5


def test_experiment_runner_grid_size():
    stats = StatsEngine()
    runner = ExperimentRunner(stats)
    results = runner.run_grid_size_experiment([5, 10], num_players=2, num_simulations=5)
    assert 5 in results
    assert 10 in results
    # Larger grids should generally take longer on average (probabilistic — just check structure)
    assert results[5]["count"] == 5
    assert results[10]["count"] == 5


def test_experiment_runner_player_count():
    stats = StatsEngine()
    runner = ExperimentRunner(stats)
    results = runner.run_player_count_experiment([2, 3], grid_size=10, num_simulations=5)
    assert 2 in results
    assert 3 in results


def test_experiment_runner_strategy_comparison():
    stats = StatsEngine()
    runner = ExperimentRunner(stats)
    results = runner.run_strategy_comparison(grid_size=10, num_players=2, num_simulations=5)
    assert "BoundedRandom" in results
    assert "Random" in results
