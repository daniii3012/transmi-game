#!/usr/bin/env python3
"""Fetch the OSM carriageways that TransMilenio buses run on, with their lane counts.

The map draws two lanes per direction as a declared abstraction. This downloads the
actual carriageway geometry so it can be drawn as context: `highway=busway`, and roads
that OSM identifies as TransMilenio or as bus-only. Lane counts come from the `lanes`
tag where OSM supplies one; they are never guessed.

Nothing here changes how buses move. The simulation keeps following the published route
polyline, which can differ from the OSM carriageway by a few metres.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
ROOT = pathlib.Path(__file__).resolve().parents[1]


def query(bbox: str) -> str:
    return f"""[out:json][timeout:300];
(
  way["highway"="busway"]({bbox});
  way["highway"]["name"~"TransMilenio|Transmilenio|TRANSMILENIO",i]({bbox});
  way["highway"="service"]["bus"="yes"]["access"~"^(no|private)$"]({bbox});
  way["highway"]["psv"="bus"]({bbox});
);
out body geom;"""


def fetch(url: str, q: str, attempts: int = 5, pause: float = 25.0) -> bytes:
    for attempt in range(1, attempts + 1):
        request = urllib.request.Request(url, data=q.encode("utf-8"),
                                         headers={"User-Agent": "Transmi2D busway lane research/2026"})
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code not in (429, 502, 503, 504) or attempt == attempts:
                raise
            delay = pause * attempt
            print(f"  Overpass respondió {error.code}; reintento {attempt}/{attempts - 1} en {delay:.0f} s")
            time.sleep(delay)
    raise RuntimeError("unreachable")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bbox", default="4.5118,-74.2260,4.7890,-74.0235",
                        help="south,west,north,east covering the trunk and dual network")
    parser.add_argument("--output-root", default="data/raw/busway_lanes")
    parser.add_argument("--snapshot", help="UTC folder name")
    parser.add_argument("--endpoint", default=OVERPASS_URL)
    args = parser.parse_args()

    queried_at = datetime.now(timezone.utc)
    snapshot = args.snapshot or queried_at.strftime("%Y%m%dT%H%M%SZ")
    output = ROOT / args.output_root / snapshot
    output.mkdir(parents=True, exist_ok=False)

    q = query(args.bbox)
    payload = json.loads(fetch(args.endpoint, q))
    elements = [e for e in payload.get("elements", []) if e.get("type") == "way" and e.get("geometry")]
    with_lanes = sum(1 for e in elements if (e.get("tags") or {}).get("lanes"))
    document = {
        "schema_version": 1,
        "source_dataset": "OpenStreetMap Overpass API",
        "source_url": args.endpoint,
        "queried_at": queried_at.isoformat(),
        "snapshot": snapshot,
        "bbox": args.bbox,
        "overpass_query": q,
        "way_count": len(elements),
        "ways_with_lane_tag": with_lanes,
        "elements": elements,
        "osm3s": payload.get("osm3s", {}),
        "license": "OpenStreetMap contributors, ODbL 1.0; retrieved through Overpass API",
    }
    raw_path = output / "overpass.json"
    raw_path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
    digest = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    (output / "manifest.json").write_text(json.dumps({
        "schema_version": 1, "snapshot": snapshot, "source_url": args.endpoint,
        "queried_at": queried_at.isoformat(), "bbox": args.bbox,
        "raw_file": raw_path.name, "raw_sha256": digest,
        "way_count": len(elements), "ways_with_lane_tag": with_lanes,
        "license": document["license"],
    }, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"snapshot": snapshot, "ways": len(elements), "with_lanes": with_lanes,
                      "raw_sha256": digest, "bytes": raw_path.stat().st_size}, ensure_ascii=False))


if __name__ == "__main__":
    main()
