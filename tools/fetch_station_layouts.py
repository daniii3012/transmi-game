#!/usr/bin/env python3
"""Fetch small, reproducible OSM vectors around selected TransMilenio stations.

The query is deliberately limited to station areas: platforms/stop positions,
station relations and busway/service ways.  It does not fetch map tiles.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone


OVERPASS_URL = "https://overpass-api.de/api/interpreter"
ROOT = pathlib.Path(__file__).resolve().parents[1]

# The twelve stations of the first two milestones. They are always included so an
# expansion can never quietly drop geometry that is already published.
BASELINE = ["2000", "4000", "7000", "3000", "5000", "5100", "6000", "7111", "8000", "90004", "9110", "10000"]


ACCENTS = {"a": "aá", "e": "eé", "i": "ií", "o": "oó", "u": "uúü", "n": "nñ"}


def name_pattern(name: str) -> str:
    """Overpass name filter for one station.

    The published name often carries a qualifier after a dash that OSM does not use
    ("Portal Norte - Unicervantes" is just "Portal Norte" there), so the qualifier is
    dropped. Accented letters become character classes because Overpass's `,i` flag is
    case-insensitive but not accent-insensitive.
    """
    head = re.split(r"[-–—,(/]", name)[0]
    words = [w for w in re.sub(r"[^0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+", " ", head).split() if w][:3]
    out = []
    for character in " ".join(words):
        lowered = character.lower()
        base = next((k for k, v in ACCENTS.items() if lowered in v), None)
        out.append(f"[{ACCENTS[base]}]" if base else character if character.isalnum() or character == " " else re.escape(character))
    return "".join(out)


def select_stations(count: int) -> dict:
    """Baseline stations plus the busiest trunk stations, by number of usable services."""
    services = json.loads((ROOT / "app/dist/services.json").read_text())
    by_id = {s["id"]: s for s in services["stations"] if s.get("kind") != "street"}
    visits: dict[str, int] = {}
    for route in services["routes"]:
        if not route.get("ready"):
            continue
        for stop in route["stops"]:
            if stop["station_id"] in by_id:
                visits[stop["station_id"]] = visits.get(stop["station_id"], 0) + 1
    ranked = sorted(by_id, key=lambda sid: (-visits.get(sid, 0), by_id[sid]["name"]))
    chosen = list(BASELINE) + [sid for sid in ranked if sid not in BASELINE]
    selected = {}
    for sid in chosen[: max(count, len(BASELINE))]:
        station = by_id[sid]
        selected[sid] = {"name": station["name"], "lon_lat": station["lon_lat"], "services": visits.get(sid, 0)}
    return selected


def batched(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def query(radius_m: int, stations: dict) -> str:
    clauses: list[str] = []
    for value in stations.values():
        lon, lat = value["lon_lat"]
        name = name_pattern(value["name"])
        clauses.extend(
            [
                f"nwr(around:{radius_m},{lat},{lon})[public_transport~\"^(platform|stop_position|station|stop_area)$\"];",
                f"way(around:{radius_m},{lat},{lon})[highway~\"^(busway|service)$\"];",
                f"way(around:{radius_m},{lat},{lon})[railway~\"^(platform|service)$\"];",
                # The name filter keeps Metro and unrelated station relations out of the
                # recursive member fetch. It is built from each station's own published
                # name so adding stations never needs the pattern edited by hand.
                f"rel(around:{radius_m},{lat},{lon})[public_transport=station][name~\"{name}\",i];",
                f"rel(around:{radius_m},{lat},{lon})[public_transport=stop_area][name~\"{name}\",i];",
            ]
        )
    return "[out:json][timeout:180];(" + "".join(clauses) + ");out body geom;"


def relation_query(radius_m: int, stations: dict) -> str:
    clauses: list[str] = []
    for value in stations.values():
        lon, lat = value["lon_lat"]
        name = name_pattern(value["name"])
        clauses.extend(
            [
                f"rel(around:{radius_m},{lat},{lon})[public_transport=station][name~\"{name}\",i];",
                f"rel(around:{radius_m},{lat},{lon})[public_transport=stop_area][name~\"{name}\",i];",
            ]
        )
    return "[out:json][timeout:180];(" + "".join(clauses) + ");out body;"


def member_query(way_ids: list[int]) -> str:
    ids = ",".join(str(value) for value in sorted(set(way_ids)))
    return f"[out:json][timeout:180];way(id:{ids});out body geom;"


def fetch(url: str, q: str, attempts: int = 5, pause: float = 20.0) -> bytes:
    """Overpass is a shared free service: pace the requests and back off on 429/504."""
    for attempt in range(1, attempts + 1):
        request = urllib.request.Request(
            url,
            data=q.encode("utf-8"),
            headers={"User-Agent": "Transmi2D station layout research/2026"},
        )
        try:
            with urllib.request.urlopen(request, timeout=240) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code not in (429, 502, 503, 504) or attempt == attempts:
                raise
            delay = pause * attempt
            print(f"    Overpass respondió {error.code}; reintento {attempt}/{attempts - 1} en {delay:.0f} s")
            time.sleep(delay)
    raise RuntimeError("unreachable")


def fetch_json(url: str, q: str) -> dict:
    return json.loads(fetch(url, q))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--radius-m", type=int, default=450)
    parser.add_argument("--output-root", default="data/raw/station_layouts")
    parser.add_argument("--snapshot", help="UTC folder name, e.g. 20260911T020000Z")
    parser.add_argument("--endpoint", default=OVERPASS_URL)
    parser.add_argument("--stations", type=int, default=12,
                        help="how many stations to cover: the twelve baseline ones plus the busiest")
    parser.add_argument("--batch", type=int, default=10, help="stations per Overpass request")
    parser.add_argument("--pause", type=float, default=8.0, help="seconds to wait between Overpass requests")
    args = parser.parse_args()
    stations = select_stations(args.stations)
    print(f"{len(stations)} estaciones seleccionadas, en lotes de {args.batch}")

    queried_at = datetime.now(timezone.utc)
    snapshot = args.snapshot or queried_at.strftime("%Y%m%dT%H%M%SZ")
    output = pathlib.Path(args.output_root) / snapshot
    output.mkdir(parents=True, exist_ok=True)
    # One request per batch: a single query over every station times out on Overpass.
    ids = list(stations)
    queries, relation_queries, elements_by_key, relation_way_ids = [], [], {}, []
    for group in batched(ids, max(1, args.batch)):
        subset = {sid: stations[sid] for sid in group}
        q = query(args.radius_m, subset)
        queries.append(q)
        payload = fetch_json(args.endpoint, q)
        for element in payload.get("elements", []):
            elements_by_key[(element["type"], element["id"])] = element
        relations_q = relation_query(args.radius_m, subset)
        relation_queries.append(relations_q)
        relations_payload = fetch_json(args.endpoint, relations_q)
        for relation in relations_payload.get("elements", []):
            elements_by_key[(relation["type"], relation["id"])] = relation
        print(f"  lote de {len(subset)}: {len(elements_by_key)} elementos acumulados")
        time.sleep(args.pause)
    # Members are taken from every relation actually retrieved, not only from the ones the
    # name filter matched: an untagged member way is reachable no other way, and a station
    # relation whose OSM spelling differs from the published name still arrives through the
    # unfiltered public_transport clause.
    relation_way_ids = [
        int(member["ref"])
        for key, element in elements_by_key.items()
        if key[0] == "relation"
        for member in element.get("members", [])
        if member.get("type") == "way"
    ]
    missing = [wid for wid in set(relation_way_ids) if ("way", wid) not in elements_by_key]
    print(f"  {len(set(relation_way_ids))} vías miembro, {len(missing)} sin geometría todavía")
    members_q = member_query(relation_way_ids) if relation_way_ids else None
    if members_q:
        for element in fetch_json(args.endpoint, members_q).get("elements", []):
            elements_by_key[(element["type"], element["id"])] = element
    q, relations_q = queries, relation_queries
    payload = {"osm3s": {}}
    document = {
        "schema_version": 1,
        "source_url": args.endpoint,
        "source_dataset": "OpenStreetMap Overpass API",
        "queried_at": queried_at.isoformat(),
        "snapshot": snapshot,
        "radius_m": args.radius_m,
        "station_coordinate_source": "app/dist/services.json (map_stations)",
        "stations": [{"station_id": sid, **value} for sid, value in stations.items()],
        "overpass_queries": q,
        "relation_queries": relations_q,
        "member_query": members_q,
        "elements": list(elements_by_key.values()),
        "osm3s": payload.get("osm3s", {}),
    }
    raw_path = output / "overpass.json"
    raw_path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
    raw_sha256 = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    manifest = {
        "schema_version": 1,
        "snapshot": snapshot,
        "source_url": args.endpoint,
        "queried_at": queried_at.isoformat(),
        "radius_m": args.radius_m,
        "raw_file": raw_path.name,
        "raw_sha256": raw_sha256,
        "element_count": len(document["elements"]),
        "license": "OpenStreetMap contributors, ODbL 1.0; retrieved through Overpass API",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"snapshot": snapshot, "raw": str(raw_path), **manifest}, ensure_ascii=False))


if __name__ == "__main__":
    main()
