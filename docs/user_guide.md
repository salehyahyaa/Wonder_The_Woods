# Wandering in the Woods — User Guide

## Quick Start

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run headless (no display required)
```bash
python main.py --headless              # Version 1 — single run
python main.py --headless --version 2  # Version 2 — 20 runs with stats
python main.py --headless --version 3  # Version 3 — grid-size & player-count experiments
```

### Run the graphical simulation
```bash
python main.py                         # Version 1 — K–2
python main.py --version 2             # Version 2 — Grades 3–5
python main.py --version 3             # Version 3 — Grades 6–8
```

---

## Versions

### Version 1 — Kindergarten to Grade 2
* Two players start at opposite corners of a **10×10** grid.
* The simulation steps automatically.
* When players meet a celebration banner appears.
* Press **R** to restart.

### Version 2 — Grades 3–5
| Key / Button | Action |
|---|---|
| Space / Step button | Advance one step |
| Enter / Run button  | Toggle auto-run |
| R                   | Restart |
| Q / Esc             | Quit |

Statistics (shortest, longest, average) are shown in the right panel and
update after each completed run.

### Version 3 — Grades 6–8
* 50 simulations run automatically on startup.
* Summary statistics are displayed in the window.
* Click **Show Distribution Graph** to see a histogram of meeting times.
* Press **Q** or **Esc** to quit.

---

## Running Tests
```bash
python -m pytest tests/ -v
```

---

## Project Layout
```
main.py               Entry point
config.py             Global constants
simulation/           Core simulation logic (no GUI)
ui/                   pygame presentation layer
statistics/           Data collection and charting
assets/               Sprites, sounds, music (future)
docs/                 This guide + design document
tests/                pytest test suite
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: pygame` | Run `pip install pygame>=2.0.0` |
| `ModuleNotFoundError: matplotlib` | Run `pip install matplotlib>=3.5.0` |
| Black screen on startup | Ensure your display is accessible; try `--headless` |
| Tests fail with import errors | Run tests from the project root: `python -m pytest tests/` |
