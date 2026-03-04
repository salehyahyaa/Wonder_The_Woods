# Wandering in the Woods — Design Document

## Overview

**Wandering in the Woods** is an educational probability simulation where players
(wanderers) move randomly on a grid until they meet.  The project is structured in
three progressively complex versions aimed at different grade levels.

---

## Versions

| Version | Audience  | Key Features |
|---------|-----------|--------------|
| 1 (K–2) | Kindergarten–Grade 2 | Fixed 10×10 grid, 2 players, visual only |
| 2 (3–5) | Grades 3–5 | Configurable grid & players, step-by-step, basic stats |
| 3 (6–8) | Grades 6–8 | Experiment mode, multiple runs, graphs |

---

## Architecture

```
Wonder_The_Woods/
├── config.py               — Global constants (colours, sizes, FPS …)
├── main.py                 — CLI entry point
│
├── simulation/             — Pure-logic layer (no pygame dependency)
│   ├── grid.py             — Grid model
│   ├── player.py           — Player model
│   ├── movement.py         — Movement strategies (Strategy pattern)
│   └── simulation_engine.py— Orchestration; group-merge logic
│
├── statistics/             — Data-collection layer
│   ├── stats_engine.py     — Per-run recording & summary
│   ├── experiment_runner.py— Batch experiment helpers
│   └── graph_generator.py  — matplotlib chart helpers
│
├── ui/                     — Presentation layer (pygame)
│   ├── game_window.py      — Top-level window & version loops
│   ├── renderer.py         — All draw calls
│   └── controls.py         — Event → action mapping
│
├── tests/
│   └── test_simulation.py  — pytest test suite
│
└── assets/                 — Sprites, sounds, music (future)
```

---

## Core Concepts

### Random Walk
Each player independently chooses one of four cardinal directions each step.
`BoundedRandomMovement` restricts choices to valid in-bound cells.

### Group Movement (Version 2+)
When two or more players land on the same cell, they **merge** into a group
and subsequently move as a single unit.  The simulation ends when all players
belong to one group.

### Statistics
`StatsEngine` accumulates step counts across runs.  `ExperimentRunner` drives
repeated simulations and computes summaries suitable for charting.

---

## Data Flow

```
main.py ──► GameWindow.run_versionN()
               │
               ├─► SimulationEngine.step() ──► MovementStrategy.get_next_position()
               │         │
               │         └─► Player.move_to()
               │
               ├─► Renderer.draw_*()
               └─► StatsEngine.record_run()
```

---

## Extension Points

* **New movement strategies**: subclass `MovementStrategy` and override
  `get_next_position()`.
* **New grid shapes**: replace `Grid` with a subclass that overrides
  `is_valid_position()` to implement hexagonal or toroidal topologies.
* **Sound effects**: hook into `SimulationEngine` events and call pygame mixer
  from `GameWindow`.
