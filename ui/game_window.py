"""Main game window — ties together all UI components for each version."""

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, CELL_SIZE,
    DEFAULT_GRID_SIZE, WHITE, GREEN, YELLOW, ORANGE, GRAY, BLACK,
    VERSION_K2, VERSION_35, VERSION_68,
)
from simulation.grid import Grid
from simulation.player import Player
from simulation.simulation_engine import SimulationEngine
from simulation.movement import BoundedRandomMovement
from statistics.stats_engine import StatsEngine
from statistics.experiment_runner import ExperimentRunner
from statistics.graph_generator import GraphGenerator


class GameWindow:
    """Main game window that manages the pygame display and game loop."""

    def __init__(self, version: int = VERSION_K2) -> None:
        """
        Initialise the window for the given version.

        Args:
            version: One of VERSION_K2 (1), VERSION_35 (2), VERSION_68 (3).
        """
        self._version = version
        self._screen = None
        self._clock = None
        self._running = False
        self._stats = StatsEngine()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Set up pygame and create the display window."""
        if not _PYGAME_AVAILABLE:
            raise RuntimeError("pygame is not installed.")
        pygame.init()
        pygame.display.set_caption(f"Wandering in the Woods — Version {self._version}")
        self._screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self._clock = pygame.time.Clock()
        self._running = True

    def run(self, version: int = None) -> None:
        """
        Launch the appropriate version loop.

        Args:
            version: Override the version set at construction (optional).
        """
        if version is not None:
            self._version = version
        self.initialize()
        if self._version == VERSION_K2:
            self.run_version1()
        elif self._version == VERSION_35:
            self.run_version2()
        else:
            self.run_version3()
        if _PYGAME_AVAILABLE:
            pygame.quit()

    # ------------------------------------------------------------------
    # Version loops
    # ------------------------------------------------------------------

    def run_version1(self) -> None:
        """
        Version 1 (K–2): Fixed 10×10 grid, 2 players at opposite corners.
        Players step automatically; pressing R resets.
        """
        from ui.renderer import Renderer
        from ui.controls import Controls

        grid = Grid(DEFAULT_GRID_SIZE, DEFAULT_GRID_SIZE)
        players = self._make_corner_players(grid)
        engine = SimulationEngine(grid, players)
        renderer = Renderer(self._screen, CELL_SIZE)
        controls = Controls()
        finished = False

        while self._running:
            for event in pygame.event.get():
                action = controls.handle_event(event)
                if action["action"] == "quit":
                    self._running = False
                elif action["action"] == "restart":
                    engine.reset()
                    finished = False

            if not finished:
                finished = engine.step()
                if finished:
                    self._stats.record_run(engine.get_step_count())

            self._screen.fill(WHITE)
            renderer.draw_grid(grid)
            renderer.draw_players(players, grid)

            # Step counter
            self._blit_text(f"Steps: {engine.get_step_count()}", 10, 10)

            if finished:
                renderer.draw_celebration(self._screen, engine.get_step_count())
                renderer.draw_button(
                    self._screen, (WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT - 60, 120, 40),
                    "Restart (R)", GREEN,
                )

            pygame.display.flip()
            self._clock.tick(FPS)

    def run_version2(self) -> None:
        """
        Version 2 (3–5): Configurable grid, 2–4 players, multiple runs with stats.
        Press Enter to run automatically; Space to step; R to restart.
        """
        from ui.renderer import Renderer
        from ui.controls import Controls

        controls = Controls()
        grid_size = DEFAULT_GRID_SIZE
        num_players = 2
        grid = Grid(grid_size, grid_size)
        players = self._make_spread_players(num_players, grid)
        engine = SimulationEngine(grid, players)
        renderer = Renderer(self._screen, CELL_SIZE)
        finished = False
        auto_run = False

        btn_run = pygame.Rect(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 110, 160, 36)
        btn_step = pygame.Rect(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 60, 160, 36)

        while self._running:
            for event in pygame.event.get():
                action = controls.handle_event(event)
                a = action["action"]
                if a == "quit":
                    self._running = False
                elif a == "restart":
                    engine.reset()
                    finished = False
                    auto_run = False
                elif a == "step" and not finished:
                    finished = engine.step()
                    if finished:
                        self._stats.record_run(engine.get_step_count())
                elif a == "run":
                    auto_run = not auto_run
                elif a == "button":
                    if btn_run.collidepoint(action["pos"]):
                        auto_run = not auto_run
                    elif btn_step.collidepoint(action["pos"]) and not finished:
                        finished = engine.step()
                        if finished:
                            self._stats.record_run(engine.get_step_count())

            if auto_run and not finished:
                finished = engine.step()
                if finished:
                    self._stats.record_run(engine.get_step_count())

            self._screen.fill(WHITE)
            renderer.draw_grid(grid)
            renderer.draw_players(players, grid)
            self._blit_text(f"Steps: {engine.get_step_count()}", 10, 10)
            renderer.draw_stats(self._screen, self._stats.get_summary())
            renderer.draw_button(self._screen, btn_run, "Run (Enter)", YELLOW)
            renderer.draw_button(self._screen, btn_step, "Step (Space)", ORANGE)

            if finished:
                renderer.draw_celebration(self._screen, engine.get_step_count())

            pygame.display.flip()
            self._clock.tick(FPS)

    def run_version3(self) -> None:
        """
        Version 3 (6–8): Experiment mode — runs 50 simulations automatically
        and offers to generate graphs.
        """
        from ui.renderer import Renderer

        runner = ExperimentRunner(self._stats)
        grapher = GraphGenerator()
        renderer = Renderer(self._screen, CELL_SIZE)

        # Run the experiment in background (non-blocking via generator steps)
        num_sims = 50
        grid_size = DEFAULT_GRID_SIZE
        results = runner.run_experiment(grid_size, grid_size, 2, num_sims)
        summary = self._stats.get_summary()

        btn_graph = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 70, 200, 40)

        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_q, pygame.K_ESCAPE
                ):
                    self._running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_graph.collidepoint(event.pos):
                        grapher.plot_run_distribution(
                            results.get("runs", []),
                            title=f"Meeting Time ({grid_size}×{grid_size}, 2 players)",
                        )

            self._screen.fill(WHITE)
            y = 40
            lines = [
                "Experiment Results",
                f"Grid: {grid_size}×{grid_size}  |  Players: 2  |  Runs: {num_sims}",
                f"Shortest: {summary['shortest']} steps",
                f"Longest:  {summary['longest']} steps",
                f"Average:  {summary['average']:.1f} steps",
                "",
                "Press Q to quit",
            ]
            for line in lines:
                self._blit_text(line, WINDOW_WIDTH // 2, y, center=True)
                y += 36

            renderer.draw_button(self._screen, btn_graph, "Show Distribution Graph", GREEN)
            pygame.display.flip()
            self._clock.tick(FPS)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _blit_text(self, text: str, x: int, y: int, center: bool = False) -> None:
        """Render *text* directly onto the screen at (x, y)."""
        if not _PYGAME_AVAILABLE or self._screen is None:
            return
        font = pygame.font.SysFont("Arial", 20)
        surf = font.render(text, True, BLACK)
        if center:
            x -= surf.get_width() // 2
        self._screen.blit(surf, (x, y))

    @staticmethod
    def _make_corner_players(grid: Grid) -> list:
        """Place two players at diagonally opposite corners."""
        w, h = grid.get_dimensions()
        return [Player(0, 0, 0), Player(1, w - 1, h - 1)]

    @staticmethod
    def _make_spread_players(num_players: int, grid: Grid) -> list:
        """Distribute players evenly across the grid diagonal."""
        w, h = grid.get_dimensions()
        players = []
        for i in range(num_players):
            frac = i / max(1, num_players - 1)
            x = int(round(frac * (w - 1)))
            y = int(round(frac * (h - 1)))
            players.append(Player(i, x, y))
        return players
