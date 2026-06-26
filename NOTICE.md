# Notice

## Non-affiliation

This repository is an independent software project. It is not affiliated with,
endorsed by, or produced by MIT, Politecnico di Bari, Science Robotics, or the
original research authors.

## Attribution

The behavioral model in this repository was designed as a system-level abstraction
inspired by publicly available descriptions of electrofluidic fiber muscle actuation.

The primary public source is:

Electrofluidic fiber muscles
Science Robotics
DOI: 10.1126/scirobotics.ady6438

Additional public sources consulted:

MIT News release, April 2026:
https://news.mit.edu/2026/new-type-electrically-driven-artificial-muscle-fiber-0409

Public Zenodo v2 dataset:
https://zenodo.org/records/18678491

No proprietary or unpublished data from the original research group was used
in constructing this model.

## Dataset note

The Zenodo dataset referenced above is a public release by the original authors.
It is not bundled with this repository due to its size (~461 MB).
Do not commit dataset files to this repository.
Use scripts/fetch_zenodo_dataset.py to download the dataset locally for
parameter fitting.

## Parameter fitting status

Default parameter values in this package are placeholders. They have not been
fitted against experimental data from the Zenodo dataset or from any physical
hardware. Do not use default values for hardware design, safety analysis, or
quantitative performance claims.
