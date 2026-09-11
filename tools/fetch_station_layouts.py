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
import urllib.request
from datetime import datetime, timezone


OVERPASS_URL = "https://overpass-api.de/api/interpreter"
STATIONS = {
    "7000": {"name": "Portal Sur - JFK Coop. Financiera", "lon_lat": [-74.169328801, 4.59735103]},
    "3000": {"name": "Portal Suba", "lon_lat": [-74.094252542, 4.746992733]},
    "5000": {"name": "Portal Américas", "lon_lat": [-74.173221244, 4.629568928]},
    "5100": {"name": "Banderas", "lon_lat": [-74.14566342, 4.631326219]},
    "7111": {"name": "Ricaurte", "lon_lat": [-74.090418561, 4.612931094]},
    "9110": {"name": "Avenida Jiménez", "lon_lat": [-74.079034263, 4.602964699]},
}


def query(radius_m: int) -> str:
    clauses: list[str] = []
    for value in STATIONS.values():
        lon, lat = value["lon_lat"]
        clauses.extend(
            [
                f"nwr(around:{radius_m},{lat},{lon})[public_transport~\"^(platform|stop_position|station|stop_area)$\"];",
                f"way(around:{radius_m},{lat},{lon})[highway~\"^(busway|service)$\"];",
                f"way(around:{radius_m},{lat},{lon})[railway~\"^(platform|service)$\"];",
                # Name narrowing keeps Metro and unrelated station relations out of
                # the recursive member fetch while retaining the TransMilenio
                # relations whose operator spelling varies in OSM.
                f"rel(around:{radius_m},{lat},{lon})[public_transport=station][name~\"(Portal Sur|Portal Suba|Portal Am[eé]ricas|Banderas|Ricaurte|Avenida Jim[eé]nez)\",i];",
                f"rel(around:{radius_m},{lat},{lon})[public_transport=stop_area][name~\"(Portal Sur|Portal Suba|Portal Am[eé]ricas|Banderas|Ricaurte|Avenida Jim[eé]nez)\",i];",
            ]
        )
    return "[out:json][timeout:180];\n(\n" + "".join(clauses) + "\n);\nout body geom;"


def relation_query(radius_m: int) -> str:
    clauses: list[str] = []
    name_filter = "(Portal Sur|Portal Suba|Portal Am[eé]ricas|Banderas|Ricaurte|Avenida Jim[eé]nez)"
    for value in STATIONS.values():
        lon, lat = value["lon_lat"]
        clauses.extend(
            [
                f"rel(around:{radius_m},{lat},{lon})[public_transport=station][name~\"{name_filter}\",i];",
                f"rel(around:{radius_m},{lat},{lon})[public_transport=stop_area][name~\"{name_filter}\",i];",
            ]
        )
    return "[out:json][timeout:180];(" + "".join(clauses) + ");out body;"


def member_query(way_ids: list[int]) -> str:
    ids = ",".join(str(value) for value in sorted(set(way_ids)))
    return f"[out:json][timeout:180];way(id:{ids});out body geom;"


def fetch(url: str, q: str) -> bytes:
    request = urllib.request.Request(
        url,
        data=q.encode("utf-8"),
        headers={"User-Agent": "Transmi2D station layout research/2026"},
    )
    with urllib.request.urlopen(request, timeout=240) as response:
        return response.read()


def fetch_json(url: str, q: str) -> dict:
    return json.loads(fetch(url, q))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--radius-m", type=int, default=450)
    parser.add_argument("--output-root", default="data/raw/station_layouts")
    parser.add_argument("--snapshot", help="UTC folder name, e.g. 20260911T020000Z")
    parser.add_argument("--endpoint", default=OVERPASS_URL)
    args = parser.parse_args()

    queried_at = datetime.now(timezone.utc)
    snapshot = args.snapshot or queried_at.strftime("%Y%m%dT%H%M%SZ")
    output = pathlib.Path(args.output_root) / snapshot
    output.mkdir(parents=True, exist_ok=True)
    q = query(args.radius_m)
    payload = fetch_json(args.endpoint, q)
    relations_q = relation_query(args.radius_m)
    relations_payload = fetch_json(args.endpoint, relations_q)
    relation_way_ids = [
        int(member["ref"])
        for relation in relations_payload.get("elements", [])
        for member in relation.get("members", [])
        if member.get("type") == "way"
    ]
    members_q = member_query(relation_way_ids) if relation_way_ids else None
    members_payload = fetch_json(args.endpoint, members_q) if members_q else {"elements": []}
    elements_by_key = {(e["type"], e["id"]): e for e in payload.get("elements", [])}
    for element in relations_payload.get("elements", []) + members_payload.get("elements", []):
        elements_by_key[(element["type"], element["id"])] = element
    document = {
        "schema_version": 1,
        "source_url": args.endpoint,
        "source_dataset": "OpenStreetMap Overpass API",
        "queried_at": queried_at.isoformat(),
        "snapshot": snapshot,
        "radius_m": args.radius_m,
        "station_coordinate_source": "app/dist/services.json (map_stations)",
        "stations": [{"station_id": sid, **value} for sid, value in STATIONS.items()],
        "overpass_query": q,
        "relation_query": relations_q,
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
