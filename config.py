"""Configuration constants for the Wandering in the Woods Simulation."""

# Grid settings
DEFAULT_GRID_SIZE = 10
MIN_GRID_SIZE = 5
MAX_GRID_SIZE = 50

# Movement directions as (delta_x, delta_y) / (column_delta, row_delta):
# (0, 1)  → y increases → one row down
# (0, -1) → y decreases → one row up
# (1, 0)  → x increases → one column right
# (-1, 0) → x decreases → one column left
DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

# Display settings
CELL_SIZE = 60
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
FPS = 10

# Colors (RGB tuples)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BLUE = (30, 100, 200)
RED = (200, 50, 50)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
PURPLE = (148, 0, 211)
GRAY = (180, 180, 180)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
CYAN = (0, 200, 200)

# Player color palette
PLAYER_COLORS = [BLUE, RED, ORANGE, PURPLE, CYAN, YELLOW]

# Version identifiers
VERSION_K2 = 1    # Kindergarten–Grade 2
VERSION_35 = 2    # Grades 3–5
VERSION_68 = 3    # Grades 6–8

# UI layout constants
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10
PANEL_WIDTH = 200
INFO_PANEL_X = WINDOW_WIDTH - PANEL_WIDTH

# Font sizes
FONT_LARGE = 36
FONT_MEDIUM = 24
FONT_SMALL = 18
