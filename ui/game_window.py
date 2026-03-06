"""Main game window — ties together all UI components for each version."""

from __future__ import annotations

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False

from dataclasses import dataclass
from typing import Optional

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, CELL_SIZE,
    DEFAULT_GRID_SIZE, WHITE, GREEN, YELLOW, ORANGE, GRAY, BLACK,
    VERSION_K2, VERSION_35, VERSION_68,
)

from simulation.grid import Grid
from simulation.player import Player
from simulation.simulation_engine import SimulationEngine
from statistics.stats_engine import StatsEngine
from statistics.experiment_runner import ExperimentRunner
from statistics.graph_generator import GraphGenerator

from ui.audio import AudioManager


# -------------------------------
# Small UI state helpers
# -------------------------------

@dataclass
class SetupState:
    width: int = DEFAULT_GRID_SIZE
    height: int = DEFAULT_GRID_SIZE
    num_players: int = 2
    placements: Optional[list[tuple[int, int]]] = None  # list of (x,y) in order
    placing_index: int = 0
    error_msg: str = ""

    def reset_placements(self) -> None:
        self.placements = []
        self.placing_index = 0
        self.error_msg = ""


class GameWindow:
    """Main game window that manages the pygame display and game loop."""

    def __init__(self, version: int = VERSION_K2) -> None:
        self._version = version
        self._screen = None
        self._clock = None
        self._running = False

        self._stats = StatsEngine()

        self._audio = AudioManager()

        self._per_player_steps: dict[int, int] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        if not _PYGAME_AVAILABLE:
            raise RuntimeError("pygame is not installed.")
        pygame.init()
        pygame.display.set_caption(f"Wandering in the Woods — Version {self._version}")
        self._screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self._clock = pygame.time.Clock()
        self._running = True

        # init audio AFTER pygame init (mixer)
        self._audio.initialize()

    def run(self, version: int = None) -> None:
        if version is not None:
            self._version = version
        self.initialize()

        try:
            if self._version == VERSION_K2:
                self.run_version1()
            elif self._version == VERSION_35:
                self.run_version2()
            else:
                self.run_version3()
        finally:
            if _PYGAME_AVAILABLE:
                pygame.quit()

    # ------------------------------------------------------------------
    # Version 1 (K–2)
    # ------------------------------------------------------------------

    def run_version1(self) -> None:
        """
        Version 1 (K–2):
        - Fixed square grid
        - Exactly 2 players start in opposite corners
        - Random wandering, counts moves per person
        - Music + audio prompts
        """
        from ui.renderer import Renderer
        from ui.controls import Controls

        grid = Grid(DEFAULT_GRID_SIZE, DEFAULT_GRID_SIZE)
        players = self._make_corner_players(grid)
        engine = SimulationEngine(grid, players)

        renderer = Renderer(self._screen, CELL_SIZE)
        controls = Controls()

        finished = False
        self._reset_per_player_steps(players)

        # Audio: kid-friendly loop music + intro prompt
        self._audio.play_music("k2_music")
        self._audio.speak_once("k2_intro", "Two friends are lost in the woods! Watch them wander until they meet!")

        while self._running:
            for event in pygame.event.get():
                action = controls.handle_event(event)
                if action["action"] == "quit":
                    self._running = False
                elif action["action"] == "restart":
                    engine.reset()
                    finished = False
                    self._reset_per_player_steps(players)
                    self._audio.speak_once("k2_restart", "Restarting! Let's see how fast they meet this time!")

            if not finished:
                before_positions = {p.get_id(): p.position for p in players}
                finished = engine.step()
                after_positions = {p.get_id(): p.position for p in players}
                # Count moves per-person (if position changed, count it)
                for pid, before in before_positions.items():
                    if after_positions.get(pid) != before:
                        self._per_player_steps = {p.get_id(): 0 for p in players}
                if finished:
                    self._stats.record_run(engine.get_step_count())
                    self._audio.play_sfx("meet")
                    # Announce stats audibly
                    p0 = self._per_player_steps.get(0, 0)
                    p1 = self._per_player_steps.get(1, 0)
                    self._audio.speak(
                        f"They met! Player one moved {p0} times. Player two moved {p1} times. "
                        f"Total steps: {engine.get_step_count()}."
                    )

            self._screen.fill(WHITE)
            renderer.draw_grid(grid)
            renderer.draw_players(players, grid)

            # Required: counter for each person
            self._blit_text(f"P1 moves: {self._per_player_steps.get(0, 0)}", 10, 10)
            self._blit_text(f"P2 moves: {self._per_player_steps.get(1, 0)}", 10, 36)
            self._blit_text(f"Total steps: {engine.get_step_count()}", 10, 62)

            if finished:
                renderer.draw_celebration(self._screen, engine.get_step_count())
                renderer.draw_button(
                    self._screen,
                    (WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT - 60, 120, 40),
                    "Restart (R)",
                    GREEN,
                )

            pygame.display.flip()
            self._clock.tick(FPS)

    # ------------------------------------------------------------------
    # Shared Setup Screen (Version 2 + 3)
    # ------------------------------------------------------------------

    def _run_setup_screen(self, title: str, allow_experiment: bool) -> Optional[SetupState]:
        """
        Setup screen:
        - width/height (rectangular)
        - num_players 2..4
        - click-to-place players on grid preview
        Returns SetupState or None if user quits.
        """
        from ui.renderer import Renderer
        from ui.controls import Controls

        controls = Controls()
        renderer = Renderer(self._screen, CELL_SIZE)

        st = SetupState(width=DEFAULT_GRID_SIZE, height=DEFAULT_GRID_SIZE, num_players=2)
        st.reset_placements()

        # UI elements
        btn_start = pygame.Rect(WINDOW_WIDTH - 220, WINDOW_HEIGHT - 80, 200, 44)
        btn_reset = pygame.Rect(20, WINDOW_HEIGHT - 80, 200, 44)
        btn_rand = pygame.Rect(240, WINDOW_HEIGHT - 80, 220, 44)

        # Increment/decrement controls
        btn_w_minus = pygame.Rect(20, 60, 40, 36)
        btn_w_plus  = pygame.Rect(140, 60, 40, 36)
        btn_h_minus = pygame.Rect(20, 110, 40, 36)
        btn_h_plus  = pygame.Rect(140, 110, 40, 36)
        btn_p_minus = pygame.Rect(20, 160, 40, 36)
        btn_p_plus  = pygame.Rect(140, 160, 40, 36)

        # Preview grid area (left side)
        preview_x = 20
        preview_y = 220
        max_cells_w = min(18, (WINDOW_WIDTH - 40) // CELL_SIZE)  # safe clamp
        max_cells_h = min(12, (WINDOW_HEIGHT - 280) // CELL_SIZE)

        self._audio.play_music("setup_music")
        self._audio.speak_once("setup_intro", "Set the grid size, choose players, then click on the grid to place them.")

        while self._running:
            # Build a preview grid that fits screen even if st.width/height large
            prev_w = min(st.width, max_cells_w)
            prev_h = min(st.height, max_cells_h)

            for event in pygame.event.get():
                action = controls.handle_event(event)
                a = action["action"]

                if a == "quit":
                    self._running = False
                    return None

                if a == "button":
                    mx, my = action["pos"]

                    # +/- buttons
                    if btn_w_minus.collidepoint((mx, my)):
                        st.width = max(2, st.width - 1)
                        st.reset_placements()
                    elif btn_w_plus.collidepoint((mx, my)):
                        st.width = min(60, st.width + 1)
                        st.reset_placements()
                    elif btn_h_minus.collidepoint((mx, my)):
                        st.height = max(2, st.height - 1)
                        st.reset_placements()
                    elif btn_h_plus.collidepoint((mx, my)):
                        st.height = min(60, st.height + 1)
                        st.reset_placements()
                    elif btn_p_minus.collidepoint((mx, my)):
                        st.num_players = max(2, st.num_players - 1)
                        st.reset_placements()
                    elif btn_p_plus.collidepoint((mx, my)):
                        st.num_players = min(4, st.num_players + 1)
                        st.reset_placements()

                    elif btn_reset.collidepoint((mx, my)):
                        st.reset_placements()
                        self._audio.play_sfx("click")

                    elif btn_rand.collidepoint((mx, my)):
                        st.reset_placements()
                        # simple random placement (no duplicates)
                        import random
                        used = set()
                        for _ in range(st.num_players):
                            while True:
                                x = random.randint(0, st.width - 1)
                                y = random.randint(0, st.height - 1)
                                if (x, y) not in used:
                                    used.add((x, y))
                                    st.placements.append((x, y))
                                    break
                        st.placing_index = st.num_players
                        self._audio.play_sfx("click")

                    elif btn_start.collidepoint((mx, my)):
                        if st.placements is None:
                            st.reset_placements()
                        if len(st.placements) != st.num_players:
                            st.error_msg = "Place all players first!"
                            self._audio.play_sfx("error")
                        else:
                            self._audio.play_sfx("start")
                            return st

                # Click-to-place on preview grid
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    # inside preview area?
                    if preview_x <= mx < preview_x + prev_w * CELL_SIZE and preview_y <= my < preview_y + prev_h * CELL_SIZE:
                        gx = (mx - preview_x) // CELL_SIZE
                        gy = (my - preview_y) // CELL_SIZE

                        # If grid larger than preview, this places within preview window only.
                        # That's OK for classroom use; clamp sizes to fit visually.
                        if st.placements is None:
                            st.reset_placements()
                        if st.placing_index < st.num_players:
                            if (gx, gy) in st.placements:
                                st.error_msg = "That spot is taken!"
                                self._audio.play_sfx("error")
                            else:
                                st.placements.append((gx, gy))
                                st.placing_index += 1
                                st.error_msg = ""
                                self._audio.play_sfx("place")
                                if st.placing_index == st.num_players:
                                    self._audio.speak("All set! Press Start.")

            # Draw
            self._screen.fill(WHITE)
            self._blit_text(title, WINDOW_WIDTH // 2, 15, center=True)

            # Controls labels
            self._blit_text(f"Width:  {st.width}", 70, 66)
            self._blit_text(f"Height: {st.height}", 70, 116)
            self._blit_text(f"Players: {st.num_players}", 70, 166)
            self._blit_text("Click the grid to place players:", 20, 200)

            # +/- buttons
            renderer.draw_button(self._screen, btn_w_minus, "-", GRAY)
            renderer.draw_button(self._screen, btn_w_plus, "+", GRAY)
            renderer.draw_button(self._screen, btn_h_minus, "-", GRAY)
            renderer.draw_button(self._screen, btn_h_plus, "+", GRAY)
            renderer.draw_button(self._screen, btn_p_minus, "-", GRAY)
            renderer.draw_button(self._screen, btn_p_plus, "+", GRAY)

            # Preview grid
            preview_grid = Grid(prev_w, prev_h)
            renderer.draw_grid(preview_grid, offset=(preview_x, preview_y))

            # Draw placed tokens
            if st.placements is None:
                st.reset_placements()
            for idx, (x, y) in enumerate(st.placements):
                # fake players for preview
                p = Player(idx, x, y)
                renderer.draw_players([p], preview_grid, offset=(preview_x, preview_y))

            # Status / next placement prompt
            if st.placing_index < st.num_players:
                self._blit_text(f"Place Player {st.placing_index + 1}", 20, preview_y + prev_h * CELL_SIZE + 10)
            else:
                self._blit_text("All players placed ✅", 20, preview_y + prev_h * CELL_SIZE + 10)

            if st.error_msg:
                self._blit_text(st.error_msg, 20, preview_y + prev_h * CELL_SIZE + 36)

            # Buttons
            renderer.draw_button(self._screen, btn_reset, "Reset Placements", ORANGE)
            renderer.draw_button(self._screen, btn_rand, "Random Placements", YELLOW)
            renderer.draw_button(self._screen, btn_start, "Start", GREEN)

            pygame.display.flip()
            self._clock.tick(FPS)

        return None

    # ------------------------------------------------------------------
    # Version 2 (3–5)
    # ------------------------------------------------------------------

    def run_version2(self) -> None:
        """
        Version 2 (3–5):
        - Students choose rectangular grid size
        - Choose 2–4 players
        - Click-to-place players anywhere
        - Run/Step + stats across multiple runs
        """
        from ui.renderer import Renderer
        from ui.controls import Controls

        setup = self._run_setup_screen("Version 2 (Grades 3–5) — Setup", allow_experiment=False)
        if setup is None:
            return

        controls = Controls()
        renderer = Renderer(self._screen, CELL_SIZE)

        grid = Grid(setup.width, setup.height)
        players = [Player(i, x, y) for i, (x, y) in enumerate(setup.placements or [])]
        engine = SimulationEngine(grid, players)

        finished = False
        auto_run = False

        btn_run = pygame.Rect(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 110, 160, 36)
        btn_step = pygame.Rect(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 60, 160, 36)
        btn_setup = pygame.Rect(20, WINDOW_HEIGHT - 60, 200, 36)

        self._audio.play_music("v2_music")
        self._audio.speak_once("v2_intro", "Choose step or run. Try different setups and compare the stats!")

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
                        self._audio.play_sfx("meet")

                elif a == "run":
                    auto_run = not auto_run
                    self._audio.play_sfx("click")

                elif a == "button":
                    if btn_run.collidepoint(action["pos"]):
                        auto_run = not auto_run
                        self._audio.play_sfx("click")
                    elif btn_step.collidepoint(action["pos"]) and not finished:
                        finished = engine.step()
                        if finished:
                            self._stats.record_run(engine.get_step_count())
                            self._audio.play_sfx("meet")
                    elif btn_setup.collidepoint(action["pos"]):
                        # Back to setup for replayable runs
                        setup2 = self._run_setup_screen("Version 2 (Grades 3–5) — Setup", allow_experiment=False)
                        if setup2 is None:
                            return
                        grid = Grid(setup2.width, setup2.height)
                        players = [Player(i, x, y) for i, (x, y) in enumerate(setup2.placements or [])]
                        engine = SimulationEngine(grid, players)
                        finished = False
                        auto_run = False

            if auto_run and not finished:
                finished = engine.step()
                if finished:
                    self._stats.record_run(engine.get_step_count())
                    self._audio.play_sfx("meet")

            self._screen.fill(WHITE)
            renderer.draw_grid(grid)
            renderer.draw_players(players, grid)

            self._blit_text(f"Steps: {engine.get_step_count()}", 10, 10)
            self._blit_text(f"Grid: {grid.get_dimensions()[0]}×{grid.get_dimensions()[1]}", 10, 36)
            self._blit_text(f"Players: {len(players)}", 10, 62)

            renderer.draw_stats(self._screen, self._stats.get_summary())
            renderer.draw_button(self._screen, btn_run, "Run (Enter)", YELLOW)
            renderer.draw_button(self._screen, btn_step, "Step (Space)", ORANGE)
            renderer.draw_button(self._screen, btn_setup, "Change Setup", GRAY)

            if finished:
                renderer.draw_celebration(self._screen, engine.get_step_count())

            pygame.display.flip()
            self._clock.tick(FPS)

    # ------------------------------------------------------------------
    # Version 3 (6–8) — Experiment Lab
    # ------------------------------------------------------------------

    def run_version3(self) -> None:
        """
        Version 3 (6–8):
        - Same setup controls as version 2
        - Experiment lab: run many simulations across multiple shapes
        - Graph distribution + compare averages
        """
        from ui.renderer import Renderer
        from ui.controls import Controls

        controls = Controls()
        renderer = Renderer(self._screen, CELL_SIZE)

        setup = self._run_setup_screen("Version 3 (Grades 6–8) — Setup", allow_experiment=True)
        if setup is None:
            return

        runner = ExperimentRunner(self._stats)
        grapher = GraphGenerator()

        # Build a short “shape set” for experiments (students can change by changing setup)
        # Keep it simple: vary shape while holding area somewhat comparable.
        shapes = [
            (setup.width, setup.height),
            (max(2, setup.width * 2), max(2, setup.height // 2)),
            (max(2, setup.width // 2), max(2, setup.height * 2)),
        ]
        num_sims = 100  # "big data-ish" without melting laptops
        players_n = setup.num_players

        # Manual play state
        grid = Grid(setup.width, setup.height)
        players = [Player(i, x, y) for i, (x, y) in enumerate(setup.placements or [])]
        engine = SimulationEngine(grid, players)
        finished = False
        auto_run = False

        # Buttons
        btn_run = pygame.Rect(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 110, 160, 36)
        btn_step = pygame.Rect(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 60, 160, 36)
        btn_setup = pygame.Rect(20, WINDOW_HEIGHT - 60, 200, 36)
        btn_experiment = pygame.Rect(20, WINDOW_HEIGHT - 110, 200, 36)
        btn_graph = pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT - 60, 280, 36)

        # Experiment results
        exp_rows: list[tuple[str, float]] = []
        last_runs: list[int] = []

        self._audio.play_music("v3_music")
        self._audio.speak_once(
            "v3_intro",
            "Welcome to the experiment lab! Try different grid shapes and see how the average meeting time changes."
        )

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
                        self._audio.play_sfx("meet")

                elif a == "run":
                    auto_run = not auto_run
                    self._audio.play_sfx("click")

                elif a == "button":
                    if btn_run.collidepoint(action["pos"]):
                        auto_run = not auto_run
                        self._audio.play_sfx("click")
                    elif btn_step.collidepoint(action["pos"]) and not finished:
                        finished = engine.step()
                        if finished:
                            self._stats.record_run(engine.get_step_count())
                            self._audio.play_sfx("meet")

                    elif btn_setup.collidepoint(action["pos"]):
                        setup2 = self._run_setup_screen("Version 3 (Grades 6–8) — Setup", allow_experiment=True)
                        if setup2 is None:
                            return
                        setup = setup2
                        shapes = [
                            (setup.width, setup.height),
                            (max(2, setup.width * 2), max(2, setup.height // 2)),
                            (max(2, setup.width // 2), max(2, setup.height * 2)),
                        ]
                        players_n = setup.num_players
                        grid = Grid(setup.width, setup.height)
                        players = [Player(i, x, y) for i, (x, y) in enumerate(setup.placements or [])]
                        engine = SimulationEngine(grid, players)
                        finished = False
                        auto_run = False
                        exp_rows = []
                        last_runs = []

                    elif btn_experiment.collidepoint(action["pos"]):
                        # Run multiple shapes, gather average for each
                        exp_rows = []
                        last_runs = []
                        self._audio.speak("Running experiments. This may take a moment.")
                        for (w, h) in shapes:
                            # Reset stats for each shape to compute per-shape average cleanly
                            local_stats = StatsEngine()
                            local_runner = ExperimentRunner(local_stats)
                            results = local_runner.run_experiment(w, h, players_n, num_sims)
                            summ = local_stats.get_summary()
                            exp_rows.append((f"{w}×{h}", float(summ["average"])))
                            if (w, h) == shapes[0]:
                                last_runs = results.get("runs", [])
                        self._audio.speak("Experiments complete! Compare the averages.")

                    elif btn_graph.collidepoint(action["pos"]):
                        if last_runs:
                            w, h = shapes[0]
                            grapher.plot_run_distribution(
                                last_runs,
                                title=f"Meeting Time Distribution ({w}×{h}, {players_n} players)",
                            )
                        else:
                            self._audio.play_sfx("error")

            if auto_run and not finished:
                finished = engine.step()
                if finished:
                    self._stats.record_run(engine.get_step_count())
                    self._audio.play_sfx("meet")

            # Draw manual play
            self._screen.fill(WHITE)
            renderer.draw_grid(grid)
            renderer.draw_players(players, grid)

            self._blit_text("Manual Play (Step/Run) + Experiment Lab", 10, 10)
            self._blit_text(f"Steps: {engine.get_step_count()}", 10, 36)
            self._blit_text(f"Grid: {grid.get_dimensions()[0]}×{grid.get_dimensions()[1]} | Players: {len(players)}", 10, 62)

            renderer.draw_stats(self._screen, self._stats.get_summary())
            renderer.draw_button(self._screen, btn_run, "Run (Enter)", YELLOW)
            renderer.draw_button(self._screen, btn_step, "Step (Space)", ORANGE)
            renderer.draw_button(self._screen, btn_setup, "Change Setup", GRAY)

            # Experiment panel (right-ish)
            renderer.draw_button(self._screen, btn_experiment, "Run Experiments", GREEN)
            renderer.draw_button(self._screen, btn_graph, "Graph Distribution (shape 1)", YELLOW)

            y = 120
            self._blit_text("Experiment Results (Average Steps)", WINDOW_WIDTH - 260, y)
            y += 28
            if exp_rows:
                for shape, avg in exp_rows:
                    self._blit_text(f"{shape}: {avg:.1f}", WINDOW_WIDTH - 260, y)
                    y += 24
            else:
                self._blit_text("Click 'Run Experiments' to compare shapes.", WINDOW_WIDTH - 260, y)

            if finished:
                renderer.draw_celebration(self._screen, engine.get_step_count())

            pygame.display.flip()
            self._clock.tick(FPS)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _reset_per_player_steps(self, players: list[Player]) -> None:
        self._per_player_steps = {p.player_id: 0 for p in players}

    def _blit_text(self, text: str, x: int, y: int, center: bool = False) -> None:
        if not _PYGAME_AVAILABLE or self._screen is None:
            return
        font = pygame.font.SysFont("Arial", 20)
        surf = font.render(text, True, BLACK)
        if center:
            x -= surf.get_width() // 2
        self._screen.blit(surf, (x, y))

    @staticmethod
    def _make_corner_players(grid: Grid) -> list[Player]:
        w, h = grid.get_dimensions()
        return [Player(0, 0, 0), Player(1, w - 1, h - 1)]