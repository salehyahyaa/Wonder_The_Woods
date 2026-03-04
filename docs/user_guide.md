Wandering in the Woods — User Guide

1. Introduction

Wandering in the Woods is an educational simulation designed to help students explore randomness, probability, and computational thinking.

Players (wanderers) move randomly across a grid representing a forest.
The simulation ends when all players meet in the same location.

The program provides three versions, each designed for a different grade level.

2. System Requirements

Before running the program ensure the following are installed:

Python 3.9 or newer

pygame

matplotlib (Version 3 graphs)

Operating systems supported:

Windows

macOS

Linux

3. Installation

Clone the repository and install dependencies:

git clone https://github.com/salehyahyaa/Wonder_The_Woods.git
cd Wonder_The_Woods
pip install -r requirements.txt 4. Running the Simulation
Run the graphical program
python main.py
Launch specific versions
python main.py --version 1
python main.py --version 2
python main.py --version 3
Run without a graphical interface

Headless mode runs simulations from the command line.

python main.py --headless
python main.py --headless --version 2
python main.py --headless --version 3

This is useful for testing or environments without a display.

5. Version Descriptions

Version 1 — Kindergarten to Grade 2

Features:

Fixed 10×10 grid

Exactly 2 players

Players start in diagonally opposite corners

Players move automatically

Visual elements include:

animated movement

per-player move counters

celebration when players meet

Controls
Key Action
R Restart simulation
Q / Esc Quit
Version 2 — Grades 3–5

Version 2 allows students to explore different configurations.

Setup Screen

Students choose:

grid width

grid height

number of players (2–4)

starting positions (click on grid)

Simulation Controls
Key / Button Action
Space / Step button Advance one step
Enter / Run button Toggle automatic movement
R Restart run
Change Setup Return to configuration screen
Q / Esc Quit
Statistics Panel

Displayed on the right side:

total runs

shortest run

longest run

average run

These update after each completed simulation.

Version 3 — Grades 6–8

Version 3 introduces computational experiments.

Students can investigate how grid shape affects meeting time.

Features

configurable grid size

multiple automated simulation runs

experiment comparison across grid shapes

graph generation

Experiment Mode

Press Run Experiments to perform many simulations automatically.

The system will calculate:

average meeting time

comparisons between grid shapes

Graphs

Press Graph Distribution to generate a histogram of meeting times.

Graphs are displayed using matplotlib.

Controls
Key Action
Space Step simulation
Enter Toggle auto-run
Run Experiments Perform experiment batch
Graph Distribution Show results chart
Change Setup Modify experiment parameters
Q / Esc Quit 6. Running Tests

Automated tests verify core simulation logic.

Run tests with:

python -m pytest tests/ -v

Tests cover:

player movement

meeting detection

group merging

statistics calculations

7. Project Layout

   Wonder_The_Woods/
   │
   ├── main.py Entry point
   ├── config.py Global constants
   │
   ├── simulation/ Core simulation logic
   │ ├── grid.py
   │ ├── player.py
   │ ├── movement.py
   │ └── simulation_engine.py
   │
   ├── statistics/ Data processing
   │ ├── stats_engine.py
   │ ├── experiment_runner.py
   │ └── graph_generator.py
   │
   ├── ui/ Graphical interface
   │ ├── game_window.py
   │ ├── renderer.py
   │ └── controls.py
   │
   ├── assets/ Images and sounds
   ├── docs/ Documentation
   └── tests/ Automated tests

8. Troubleshooting

   Problem Solution
   ModuleNotFoundError: pygame Run pip install pygame>=2.0.0
   ModuleNotFoundError: matplotlib Run pip install matplotlib>=3.5.0
   Black screen on startup Ensure a display is available, or run --headless
   Graph window does not appear Check matplotlib installation
   Tests fail with import errors Run tests from the project root

9. Classroom Usage (Optional)

Teachers can use the simulation to demonstrate:

randomness and probability

repeated experiments

statistical averages

computational modeling

Suggested activities:

1. Predict whether a larger grid will increase meeting time.

2. Run multiple simulations to collect data.

3. Compare results across different grid shapes.
