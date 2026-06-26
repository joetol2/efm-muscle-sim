# Validation plan

This document describes the steps needed to validate the behavioral model against
experimental data before using it for quantitative engineering decisions.

## Step 1: Download the public dataset

Run scripts/fetch_zenodo_dataset.py to download the Zenodo v2 dataset locally.
The dataset is approximately 461 MB and contains experimental measurements from
the original research.

Do not commit downloaded data files. The data/ directory is excluded from git.

## Step 2: Inspect the dataset structure

Use scripts/inspect_dataset_placeholder.py as a starting point. Document:

- available file formats
- what physical quantities are measured (force, displacement, time)
- what experimental conditions are covered (fiber count, pre-pressurization level,
  load conditions)
- units used in each file

## Step 3: Select a reference condition for fitting

Choose one experimental condition as the primary fitting target. A step input
at a specific bundle configuration is the simplest starting point. Document:

- which file and condition was selected
- the peak contraction strain observed
- the approximate time to reach 63% of peak (the time constant)
- the peak force at that condition

## Step 4: Fit the parameter set

Adjust ElectroFluidicMuscleParams to match the reference condition:

- response_time_s: fit from the rise time of the step response curve
- max_force_per_fiber_n: fit from the plateau force divided by bundle count
- max_contraction_strain: confirm or adjust based on measured peak strain
- passive_stiffness_n_per_m and damping_n_s_per_m: fit from the shape of
  the force-displacement curve if available

Use run_actuator_step_response.py to generate a simulated curve, then overlay
the experimental curve to assess fit quality.

## Step 5: Cross-validate on a second condition

After fitting on the reference condition, test the fitted parameters on a second
experimental condition (different bundle count or load). Record the error. If
the model does not generalize, additional parameters or nonlinear terms may be
needed.

## Step 6: Joint model validation

If joint-level data is available in the dataset, validate the antagonistic joint
model using the fitted actuator parameters. Check that the simulated angle
trajectory and torque are qualitatively consistent with reported results.

## Step 7: Document fitted values

Replace placeholder values in ElectroFluidicMuscleParams with fitted values.
Add a comment noting the source condition, date of fitting, and who performed
the fit. Update docs/data_sources.md if new dataset versions are used.

## Acceptance criteria

The model passes basic validation when:

- simulated step response rise time matches the reference experimental rise time
  within 20%
- simulated peak contraction strain matches the reference within 10%
- force values are within a factor of 2 of reported values for the reference
  condition

These thresholds are permissive because the abstraction is a behavioral
approximation, not a physics replica. They are intended to confirm that the
model is in the right regime, not that it is quantitatively precise.
