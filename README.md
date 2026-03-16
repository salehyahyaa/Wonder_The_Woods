# Wonder_The_Woods (Wandering in the Woods)

A school project that simulates “wanderers” moving randomly on a grid (the “woods”) until they meet.  
It includes:
- A **pygame** graphical version with multiple difficulty/grade-level “versions”
- A **headless (terminal)** mode for quick runs and automated experiments
- A **statistics + graphing** module to analyze meeting time (steps) across different setups

## Features

- **Grid-based random-walk simulation**
  - Players move one step at a time on a rectangular grid.
  - Includes a bounded random movement strategy that keeps players in-bounds.
- **Meeting + grouping behavior**
  - When players meet, they can merge into groups (depending on the simulation version).
- **Multiple “versions”**
  - Version 1: geared toward K–2 (simple setup, 2 players, opposite corners).
  - Version 2/3: supports more statistical/experiment-style runs and comparisons.
- **Experiments + plots**
  - Run repeated simulations, collect min/max/average steps-to-meet.
  - Generate charts with matplotlib (grid size vs meeting time, player count vs meeting time, etc.).
- **Tests**
  - `pytest` test suite included under `tests/`.

## Project Structure

- `main.py` — entry point (supports GUI and `--headless`)
- `config.py` — constants (grid limits, colors, UI sizes, version IDs)
- `simulation/` — core simulation logic (grid, player, movement strategies, engine)
- `statistics/` — stats collection + experiment runner + graph generator
- `ui/` — pygame UI (rendering, controls, audio manager, main window)
- `assets/` — project assets (audio, etc.)
- `tests/` — pytest tests

## Requirements

Python 3.x recommended.

Dependencies (see `requirements.txt`):
- `pygame`
- `matplotlib`
- `numpy`
- `pytest`

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Run (GUI)

Run the graphical pygame simulation (defaults to version 1):

```bash
python main.py
```

Select a specific version:

```bash
python main.py --version 1
python main.py --version 2
python main.py --version 3
```

> Note: If `pygame` isn’t installed/available, use headless mode instead.

## Run (Headless / Terminal)

Run without any graphics:

```bash
python main.py --headless
```

Headless with a specific version:

```bash
python main.py --headless --version 2
python main.py --headless --version 3
```

## Run Tests

```bash
pytest
```

## Notes

- The bounded random movement includes a “stay in place” option to avoid parity issues on grid graphs (helps ensure players can eventually meet from any starting positions).
- If you add or change assets (especially audio), ensure paths under `assets/` stay consistent with `ui/audio.py`.
