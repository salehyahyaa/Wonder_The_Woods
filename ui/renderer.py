"""Renderer module — all pygame drawing logic lives here."""

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False

from config import (
    WHITE, BLACK, GREEN, YELLOW, DARK_GREEN, LIGHT_GREEN,
    CELL_SIZE, FONT_LARGE, FONT_MEDIUM, FONT_SMALL, GRAY,
)


class Renderer:
    """Handles all pygame rendering for the simulation."""

    def __init__(self, screen, cell_size: int = CELL_SIZE) -> None:
        """
        Initialize the renderer.

        Args:
            screen:    The pygame Surface to draw on.
            cell_size: Pixel size of each grid cell.
        """
        self._screen = screen
        self._cell_size = cell_size
        self._font_large = None
        self._font_medium = None
        self._font_small = None
        if _PYGAME_AVAILABLE:
            pygame.font.init()
            self._font_large = pygame.font.SysFont("Arial", FONT_LARGE, bold=True)
            self._font_medium = pygame.font.SysFont("Arial", FONT_MEDIUM)
            self._font_small = pygame.font.SysFont("Arial", FONT_SMALL)

    # ------------------------------------------------------------------
    # Public drawing methods
    # ------------------------------------------------------------------

    def draw_grid(self, grid) -> None:
        """Draw the background grid on *self._screen*."""
        if not _PYGAME_AVAILABLE:
            return
        w, h = grid.get_dimensions()
        cs = self._cell_size
        for row in range(h):
            for col in range(w):
                rect = pygame.Rect(col * cs, row * cs, cs, cs)
                color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
                pygame.draw.rect(self._screen, color, rect)
                pygame.draw.rect(self._screen, BLACK, rect, 1)

    def draw_players(self, players: list, grid) -> None:
        """Draw each player as a filled circle with an id label."""
        if not _PYGAME_AVAILABLE:
            return
        cs = self._cell_size
        for player in players:
            x, y = player.position
            cx = x * cs + cs // 2
            cy = y * cs + cs // 2
            radius = cs // 3
            pygame.draw.circle(self._screen, player.get_color(), (cx, cy), radius)
            pygame.draw.circle(self._screen, BLACK, (cx, cy), radius, 2)
            if self._font_small:
                label = self._font_small.render(str(player.get_id() + 1), True, WHITE)
                lx = cx - label.get_width() // 2
                ly = cy - label.get_height() // 2
                self._screen.blit(label, (lx, ly))

    def draw_celebration(self, screen, steps: int) -> None:
        """
        Overlay a semi-transparent celebration banner when players meet.

        Args:
            screen: The pygame Surface to overlay on.
            steps:  Step count to display in the message.
        """
        if not _PYGAME_AVAILABLE or self._font_large is None:
            return
        sw, sh = screen.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        lines = [
            "🎉  They Met!  🎉",
            f"Steps taken: {steps}",
            "Press R to restart",
        ]
        fonts = [self._font_large, self._font_medium, self._font_small]
        y_offset = sh // 3
        for text, font in zip(lines, fonts):
            surf = font.render(text, True, YELLOW)
            screen.blit(surf, (sw // 2 - surf.get_width() // 2, y_offset))
            y_offset += surf.get_height() + 10

    def draw_stats(self, screen, stats: dict) -> None:
        """
        Draw a stats panel on the right side of the screen.

        Args:
            screen: Target pygame Surface.
            stats:  Dict with keys: count, shortest, longest, average.
        """
        if not _PYGAME_AVAILABLE or self._font_small is None:
            return
        sw = screen.get_width()
        panel_x = sw - 190
        lines = [
            ("Statistics", self._font_medium),
            (f"Runs: {stats.get('count', 0)}", self._font_small),
            (f"Shortest: {stats.get('shortest', 0)}", self._font_small),
            (f"Longest:  {stats.get('longest', 0)}", self._font_small),
            (f"Average:  {stats.get('average', 0.0):.1f}", self._font_small),
        ]
        y = 10
        for text, font in lines:
            surf = font.render(text, True, BLACK)
            screen.blit(surf, (panel_x, y))
            y += surf.get_height() + 4

    def draw_button(self, screen, rect: tuple, text: str, color: tuple) -> None:
        """
        Draw a labelled rectangular button.

        Args:
            screen: Target pygame Surface.
            rect:   (x, y, width, height) tuple.
            text:   Button label.
            color:  Background colour RGB tuple.
        """
        if not _PYGAME_AVAILABLE or self._font_small is None:
            return
        r = pygame.Rect(*rect)
        pygame.draw.rect(screen, color, r, border_radius=6)
        pygame.draw.rect(screen, BLACK, r, 2, border_radius=6)
        label = self._font_small.render(text, True, BLACK)
        lx = r.centerx - label.get_width() // 2
        ly = r.centery - label.get_height() // 2
        screen.blit(label, (lx, ly))
