"""
Download the public Zenodo v2 dataset for electrofluidic fiber muscles.

The dataset is approximately 461 MB as listed on Zenodo. This script does not
run as part of the demo suite. Use it locally only when you want to inspect
or fit parameters from the research data.

Downloaded files are written to data/zenodo_v2/ and are excluded from git.
Do not commit downloaded dataset files.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

RECORD_ID = "18678491"
API_URL = f"https://zenodo.org/api/records/{RECORD_ID}"
OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "zenodo_v2"


def download_file(url: str, path: Path) -> None:
    req = Request(url, headers={"User-Agent": "efm-muscle-sim-downloader/0.1"})
    with urlopen(req) as response, path.open("wb") as fh:
        total = int(response.headers.get("Content-Length", "0"))
        read = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            fh.write(chunk)
            read += len(chunk)
            if total:
                pct = 100 * read / total
                print(f"\r  {path.name}: {pct:5.1f}%", end="", flush=True)
        print()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Querying Zenodo record {RECORD_ID} ...")

    req = Request(API_URL, headers={"User-Agent": "efm-muscle-sim-downloader/0.1"})
    with urlopen(req) as response:
        record = json.load(response)

    files = record.get("files", [])
    if not files:
        raise SystemExit("No files found in Zenodo record.")

    print(f"Found {len(files)} file(s).")
    for item in files:
        key = item.get("key", "download.bin")
        links = item.get("links", {})
        url = links.get("self") or links.get("download")
        if not url:
            print(f"Skipping {key}: no download URL found.", file=sys.stderr)
            continue
        out_path = OUT_DIR / key
        if out_path.exists():
            print(f"Already exists: {out_path}")
            continue
        print(f"Downloading {key}")
        download_file(url, out_path)

    print(f"Done. Files saved to: {OUT_DIR}")


if __name__ == "__main__":
    main()
