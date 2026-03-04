Wandering in the Woods — Design Document

1. Overview

Wandering in the Woods is an educational computer simulation designed to help K-8 students understand concepts from:

probability

computation

random processes

data analysis

computational thinking

Players (wanderers) move randomly through a forest represented by a rectangular grid.
The simulation runs until all players meet in the same location.

The system is implemented in Python using pygame for visualization.

2. Target Learning Goals

The application supports progressively deeper learning across three grade levels.

Version Audience Learning Focus
Version 1 K–2 Basic randomness, visual exploration
Version 2 3–5 Observing data patterns and repeated trials
Version 3 6–8 Running experiments and interpreting statistical results 3. Software Requirements Specification (SRS)
3.1 Functional Requirements
FR-1 Grid Representation

The system shall represent the forest as a rectangular grid.

FR-2 Player Representation

The system shall represent each wanderer as a player object with a position and movement counter.

FR-3 Random Movement

Players shall move randomly to an adjacent cell each step.

Valid movement directions:

up
down
left
right

Movement must remain within the grid boundaries.

FR-4 Meeting Detection

If two or more players occupy the same cell, they are considered to have met.

FR-5 Group Movement

Once players meet, they merge into a group and move together as a unit.

FR-6 Simulation Termination

The simulation shall end when all players belong to one group.

FR-7 Statistics Tracking

The system shall record:

number of steps per run

shortest run

longest run

average run

FR-8 Multiple Runs

Users shall be able to execute multiple simulation runs for statistical analysis.

FR-9 Graph Generation

Version 3 shall allow visualization of run distributions using graphs.

FR-10 Reset

The simulation shall allow restarting a run without restarting the program.

4. Version-Specific Requirements
   Version 1 (K–2)

Features:

fixed 10×10 grid

exactly 2 players

players start in diagonally opposite corners

movement occurs automatically

step counters shown for each player

visual celebration when players meet

Goal:
Introduce students to randomness and observation.

Version 2 (Grades 3–5)

Features:

configurable grid size

2–4 players

manual step-by-step execution

repeated runs

statistics panel displaying:

runs
shortest
longest
average

Goal:
Introduce students to repeated trials and patterns in data.

Version 3 (Grades 6–8)

Features:

experiment mode

multiple automated simulation runs

graph generation

ability to compare outcomes across runs

Goal:
Teach students to perform computational experiments and interpret results.

5. System Architecture

The application follows a layered architecture separating:

simulation logic

statistics processing

user interface

Wonder_The_Woods/
├── config.py
├── main.py
│
├── simulation/
│ ├── grid.py
│ ├── player.py
│ ├── movement.py
│ └── simulation_engine.py
│
├── statistics/
│ ├── stats_engine.py
│ ├── experiment_runner.py
│ └── graph_generator.py
│
├── ui/
│ ├── game_window.py
│ ├── renderer.py
│ └── controls.py
│
├── tests/
│ └── test_simulation.py
│
└── assets/ 6. Design Patterns Used
Strategy Pattern

Movement behavior is implemented using the Strategy pattern.

MovementStrategy
│
└── BoundedRandomMovement

This allows new movement behaviors to be added without modifying the engine.

7. Class Responsibilities
   Grid

Represents the environment.

Responsibilities:

grid dimensions

validating positions

clamping positions inside the grid

Player

Represents a wandering individual.

Stores:

id
position
starting position
step counter
color

Key methods:

move_to()
reset()
get_steps()
SimulationEngine

Central controller of the simulation.

Responsibilities:

advancing the simulation step

managing player groups

detecting meetings

tracking meeting positions

terminating when all players meet

StatsEngine

Collects run statistics.

Responsibilities:

record_run()
get_summary()
ExperimentRunner

Executes large numbers of simulations.

Used in Version 3 to run statistical experiments.

Renderer

Responsible for all visual drawing operations.

Responsibilities:

grid rendering

player rendering

UI elements

statistics display

Controls

Handles user input.

Responsibilities:

keyboard input

mouse input

mapping events to actions

8. Data Flow
   main.py
   │
   ▼
   GameWindow
   │
   ▼
   SimulationEngine.step()
   │
   ▼
   MovementStrategy.get_next_position()
   │
   ▼
   Player.move_to()
   │
   ▼
   Renderer.draw()
   │
   ▼
   StatsEngine.record_run()
   
9. Future Extensions

The system was designed for extensibility.

Possible future features:

Additional movement strategies

Example:

WallFollowerMovement
SpiralMovement
CenterBiasMovement
Alternative grid topologies

Examples:

hexagonal grid
toroidal grid
Multiplayer interaction

Players controlled by students instead of random movement.

10. Testing

The project includes automated tests using pytest.

Tests validate:

player movement

meeting detection

group merging

simulation termination

statistics calculations
