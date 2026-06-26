# Data sources

This document lists the public sources used to inform the behavioral model
in this repository.

## Primary research paper

Title: Electrofluidic fiber muscles
Journal: Science Robotics
DOI: 10.1126/scirobotics.ady6438

This is the primary public source for the performance values used as defaults
in ElectroFluidicMuscleParams. Public summary figures used:

- 20% contraction strain
- approximately 0.3 s response time
- 2 mm fiber diameter reference
- 50 W/kg power density reference

## MIT News release

URL: https://news.mit.edu/2026/new-type-electrically-driven-artificial-muscle-fiber-0409

A public-facing summary of the research with additional context. Consulted for
qualitative description of the actuation mechanism and intended applications.

Note: URLs in this document should be verified before public release. Link
availability may change over time.

## Zenodo v2 dataset

URL: https://zenodo.org/records/18678491
Record ID: 18678491
Approximate size: 461 MB

This is the public experimental dataset released by the original research authors.
It is not bundled with this repository. Use scripts/fetch_zenodo_dataset.py to
download it locally.

Important: do not commit downloaded dataset files to this repository.

The dataset should be used to fit the placeholder parameter values before drawing
quantitative conclusions from simulation outputs. See docs/validation_plan.md for
the fitting workflow.

## Notes on source reliability

All sources listed here are public at the time of writing. The model parameters
labeled as public references correspond to values stated in public summaries, not
to proprietary experimental details. No internal or unpublished data from the
original research group was used.

If additional dataset versions are released (v3 or later), update this document
and the scripts/ directory accordingly. Re-validate fitted parameters after any
dataset update.
