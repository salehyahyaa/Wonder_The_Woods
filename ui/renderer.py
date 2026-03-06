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

    def __init__(self, screen, cell_size=CELL_SIZE):
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

    def draw_grid(self, grid, offset=(0, 0)):
        """Draw the background grid on *self._screen*."""
        if not _PYGAME_AVAILABLE:
            return
        ox, oy = offset
        w, h = grid.get_dimensions()
        cs = self._cell_size
        for row in range(h):
            for col in range(w):
                rect = pygame.Rect(ox + col * cs, oy + row * cs, cs, cs)
                color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
                pygame.draw.rect(self._screen, color, rect)
                pygame.draw.rect(self._screen, BLACK, rect, 1)

    def draw_players(self, players, grid, offset=(0, 0)):
        """Draw each player as a filled circle with an id label."""
        if not _PYGAME_AVAILABLE:
            return
        ox, oy = offset
        cs = self._cell_size
        for player in players:
            x, y = player.position
            cx = ox + x * cs + cs // 2
            cy = oy + y * cs + cs // 2
            radius = cs // 3
            pygame.draw.circle(self._screen, player.get_color(), (cx, cy), radius)
            pygame.draw.circle(self._screen, BLACK, (cx, cy), radius, 2)
            if self._font_small:
                label = self._font_small.render(str(player.get_id() + 1), True, WHITE)
                lx = cx - label.get_width() // 2
                ly = cy - label.get_height() // 2
                self._screen.blit(label, (lx, ly))

    def draw_celebration(self, screen, steps):
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

    def draw_stats(self, screen, stats):
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

    def draw_button(self, screen, rect, text, color):
        if not _PYGAME_AVAILABLE or self._font_small is None:
            return

        r = rect if hasattr(rect, "x") else pygame.Rect(*rect)

        pygame.draw.rect(screen, color, r, border_radius=6)
        pygame.draw.rect(screen, BLACK, r, 2, border_radius=6)
        label = self._font_small.render(text, True, BLACK)
        lx = r.centerx - label.get_width() // 2
        ly = r.centery - label.get_height() // 2
        screen.blit(label, (lx, ly))
