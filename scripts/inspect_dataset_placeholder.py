"""
Placeholder script for inspecting the downloaded Zenodo dataset.

Run fetch_zenodo_dataset.py first to download the dataset to data/zenodo_v2/.
Then extend this script to parse, summarize, and plot experimental curves.

Current status: stub only. No inspection logic is implemented.
"""

from __future__ import annotations

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "zenodo_v2"


def main() -> None:
    if not DATA_DIR.exists():
        print(f"Dataset directory not found: {DATA_DIR}")
        print("Run scripts/fetch_zenodo_dataset.py first.")
        return

    files = sorted(DATA_DIR.iterdir())
    if not files:
        print(f"No files found in {DATA_DIR}.")
        print("Run scripts/fetch_zenodo_dataset.py first.")
        return

    print(f"Files in {DATA_DIR}:")
    for f in files:
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name}  ({size_kb:.1f} kB)")

    print()
    print("This script is a placeholder.")
    print("Add parsing and plotting logic here after reviewing the dataset format.")


if __name__ == "__main__":
    main()
