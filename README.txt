Electrofluidic Fiber Muscle Sim
===============================

Version: 0.1.0

Purpose
-------
This package is an independent behavioral simulation abstraction for electrofluidic
fiber muscle style actuation. It is inspired by the MIT / Politecnico di Bari
electrofluidic fiber muscle research described in Science Robotics.

It is not a validated physical model and is not affiliated with MIT, Politecnico di
Bari, Science Robotics, or the original research authors.

What this package models
------------------------
Each muscle bundle is treated as a compliant linear actuator with:

- first-order activation lag
- contraction strain bounded by a configurable maximum
- force scaling by bundle count
- passive spring stiffness and velocity damping

An antagonistic joint model drives a one-degree-of-freedom hinge with opposing
flexor and extensor muscles.

What this package does NOT model
---------------------------------
- electrohydrodynamic pump charge injection
- dielectric fluid pressure dynamics
- cavitation or pre-pressurization effects
- McKibben actuator wall mechanics and deformation
- thermal behavior or material fatigue
- the sealed fluid circuit described in the original research

Do not use this model for hardware design, safety analysis, or quantitative
performance claims without first fitting the placeholder parameters against
experimental data.

Source basis
------------
Model behavior is based on public information only:

Primary paper:
Science Robotics
Electrofluidic fiber muscles
DOI: 10.1126/scirobotics.ady6438

MIT News release, April 2026:
https://news.mit.edu/2026/new-type-electrically-driven-artificial-muscle-fiber-0409

Public Zenodo v2 dataset:
https://zenodo.org/records/18678491

Starting public performance values used in this package:

- 20 percent contraction strain
- 0.3 second response time
- 2 mm fiber thickness reference
- 50 W/kg power density reference

Force and damping values are placeholders. They should be fitted from the Zenodo
dataset or from lab measurements before drawing quantitative conclusions.

Package structure
-----------------

README.txt
This file.

README.md
Markdown version of the project overview.

LICENSE
MIT license text.

NOTICE.md
Non-affiliation statement, attribution notes, dataset guidance.

CITATION.cff
How to cite this software repository.

pyproject.toml
Python packaging configuration.

requirements.txt
Minimal Python requirements.

src/efm_muscle_sim/
Python package. Core classes:
- ElectroFluidicMuscleParams  -- parameter dataclass
- AntagonisticJointParams     -- joint parameter dataclass
- ElectroFluidicMuscle        -- single bundle actuator model
- AntagonisticJoint           -- antagonistic joint model
- run_simulation()            -- simulation loop utility
- save_csv()                  -- CSV output helper
- plot_actuator_response()    -- actuator plot
- plot_joint_response()       -- joint plot

examples/run_actuator_step_response.py
Step input for one muscle bundle. Writes CSV and PNG.

examples/run_antagonistic_joint_demo.py
Flex/extend cycle for a two-muscle joint. Writes CSV and PNG.

examples/run_parameter_sweep.py
Sweeps bundle_count and max_force_per_fiber_n. Writes summary CSV.

examples/run_mujoco_loader.py
Attempts to load the MuJoCo XML arm model. Requires mujoco installed separately.
Exits cleanly if mujoco is not available.

models/mujoco/efm_biceps_triceps_arm.xml
Optional MuJoCo arm approximation. Placeholder for further engineering review.

scripts/fetch_zenodo_dataset.py
Downloads the public Zenodo v2 dataset locally.

scripts/inspect_dataset_placeholder.py
Placeholder script for dataset inspection after download.

docs/
Engineering notes, model assumptions, validation plan, data sources, and handoff
notes for Fabian.

tests/
Pytest test suite covering actuator behavior, joint dynamics, parameter validation,
and simulation utilities.

outputs/
CSV files from demo runs. Not committed.

plots/
PNG files from demo runs. Not committed.

data/
Reserved for local dataset files. Not committed.

Install instructions
--------------------
Create a Python virtual environment from inside the project folder:

    python -m venv .venv

Activate it:

    On macOS/Linux:    source .venv/bin/activate
    On Windows:        .venv\Scripts\Activate.ps1

Install the package in editable mode:

    pip install -e .

For the optional MuJoCo example:

    pip install mujoco

Run the demos
-------------

    python examples/run_actuator_step_response.py
    python examples/run_antagonistic_joint_demo.py
    python examples/run_parameter_sweep.py

Run tests
---------

    pytest tests/ -v

Download the public dataset
---------------------------
To download the Zenodo v2 dataset for parameter fitting:

    python scripts/fetch_zenodo_dataset.py

The dataset is approximately 461 MB and is not bundled with this repository.
Do not commit downloaded dataset files.

Parameters to review first
--------------------------
The most important placeholder values to fit from experimental data:

- max_force_per_fiber_n
- passive_stiffness_n_per_m
- damping_n_s_per_m
- response_time_s (for specific fiber conditions)

Known limitations
-----------------
This package does not model electrohydrodynamic pump behavior, dielectric fluid
dynamics, pressure transfer inside the sealed circuit, cavitation, pre-pressurization
physics, McKibben wall deformation, material fatigue, thermal behavior, or
manufacturing constraints.

Use this as a concept and controls abstraction only.
