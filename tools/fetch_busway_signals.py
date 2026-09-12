#!/usr/bin/env python3
"""Fetch OSM traffic signals that can be evaluated against TransMilenio routes.

The OSM API map endpoint is used because it returns complete vector membership
for the small route-covering cells.  Filtering is deliberately deferred to the
curation script: only a ``highway=traffic_signals`` node that is a member of a
``highway=busway`` way, or of an explicitly bus-only/TransMilenio service way,
can become an input signal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

from busway_criteria import busway_reason, street_reason, street_segments

from geo import LOCAL_CRS

API = "https://api.openstreetmap.org/api/0.6/map"
NODE_API = "https://api.openstreetmap.org/api/0.6/node/{id}"
WAY_API = "https://api.openstreetmap.org/api/0.6/way/{id}/full"
CELL = 0.005
TRANSMI_RE = re.compile(r"transmi(?:lenio)?", re.I)


def fetch(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Transmi2D busway signal research/20260911"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def tag_map(element: ET.Element) -> dict[str, str]:
    return {t.attrib["k"]: t.attrib["v"] for t in element.findall("tag")}


def parse_map(payload: bytes) -> tuple[dict[int, dict], dict[int, dict]]:
    root = ET.fromstring(payload)
    nodes: dict[int, dict] = {}
    ways: dict[int, dict] = {}
    for e in root:
        if e.tag not in {"node", "way"} or "id" not in e.attrib:
            continue
        eid = int(e.attrib["id"])
        if e.tag == "node":
            nodes[eid] = {
                "id": eid,
                "lat": float(e.attrib["lat"]),
                "lon": float(e.attrib["lon"]),
                "tags": tag_map(e),
            }
        elif e.tag == "way":
            ways[eid] = {
                "id": eid,
                "nodes": [int(n.attrib["ref"]) for n in e.findall("nd")],
                "tags": tag_map(e),
            }
    return nodes, ways


def parse_full(payload: bytes) -> tuple[dict[int, dict], dict[int, dict]]:
    """Parse an OSM /way/<id>/full XML response, including normal geometry nodes."""
    return parse_map(payload)


def route_cells(services_path: pathlib.Path) -> tuple[set[tuple[int, int]], list[list[float]]]:
    services = json.loads(services_path.read_text())
    # Routes are already in the project's AEQD metres.  Their points define
    # the exact coverage; no rectangular city-wide search is made.
    inverse = Transformer.from_crs(LOCAL_CRS, "EPSG:4326", always_xy=True)
    cells: set[tuple[int, int]] = set()
    route_points: list[list[float]] = []
    for route in services["routes"]:
        for x, y in route.get("points", []):
            lon, lat = inverse.transform(x, y)
            cells.add((int(lon // CELL), int(lat // CELL)))
            route_points.append([float(x), float(y)])
    return cells, route_points


def cell_bbox(ix: int, iy: int) -> tuple[float, float, float, float]:
    west, east = ix * CELL, (ix + 1) * CELL
    south, north = iy * CELL, (iy + 1) * CELL
    return west, south, east, north


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--services", default="app/dist/services.json")
    parser.add_argument("--output-root", default="data/raw/busway_signals")
    parser.add_argument("--snapshot", help="UTC folder name, e.g. 20260911T120000Z")
    parser.add_argument("--max-cells", type=int, default=0, help="Optional deterministic cap for dry runs")
    parser.add_argument("--pause", type=float, default=0.15)
    parser.add_argument("--reuse-raw", action="store_true", help="Reuse existing osm_map.json in requested snapshot")
    args = parser.parse_args()

    queried_at = datetime.now(timezone.utc)
    snapshot = args.snapshot or queried_at.strftime("%Y%m%dT%H%M%SZ")
    output = pathlib.Path(args.output_root) / snapshot
    output.mkdir(parents=True, exist_ok=True)
    existing_raw = output / "osm_map.json"
    if args.reuse_raw and existing_raw.exists():
        existing = json.loads(existing_raw.read_text())
        all_nodes = {int(n["id"]): n for n in existing["nodes"]}
        all_ways = {int(w["id"]): w for w in existing["ways"]}
        route_points = [[0.0, 0.0]] * int(existing.get("route_point_count", 0))
        if not route_points:
            route_points = [[0.0, 0.0] for route in json.loads(pathlib.Path(args.services).read_text())["routes"] for _ in route.get("points", [])]
        ordered_cells = [tuple(c["cell"]) for c in existing.get("cells", [])]
        cell_records = existing.get("cells", [])
    else:
        cells, route_points = route_cells(pathlib.Path(args.services))
        ordered_cells = sorted(cells, key=lambda p: (p[1], p[0]))
        if args.max_cells:
            ordered_cells = ordered_cells[: args.max_cells]
        all_nodes, all_ways, cell_records = {}, {}, []
        for index, (ix, iy) in enumerate(ordered_cells, 1):
            west, south, east, north = cell_bbox(ix, iy)
            url = API + "?" + urllib.parse.urlencode({"bbox": f"{west:.6f},{south:.6f},{east:.6f},{north:.6f}"})
            payload = fetch(url)
            nodes, ways = parse_map(payload)
            all_nodes.update(nodes)
            all_ways.update(ways)
            cell_records.append({
                "cell": [ix, iy], "bbox": [west, south, east, north], "url": url,
                "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload),
                "node_count": len(nodes), "way_count": len(ways),
            })
            print(f"{index}/{len(ordered_cells)} {west:.3f},{south:.3f} nodes={len(nodes)} ways={len(ways)}", flush=True)
            if args.pause and index < len(ordered_cells):
                time.sleep(args.pause)

    signal_ids = sorted(nid for nid, node in all_nodes.items() if node["tags"].get("highway") == "traffic_signals")
    member_ways = {
        nid: sorted(wid for wid, way in all_ways.items() if nid in way["nodes"])
        for nid in signal_ids
    }

    # Select only direct qualifying memberships whose signal is on a current
    # service route.  The old cell capture contains signal nodes and way refs;
    # /way/full below fills in every ordinary node needed for exact tangents.
    services = json.loads(pathlib.Path(args.services).read_text())
    route_lines = [LineString(r["points"]) for r in services["routes"] if len(r.get("points", [])) >= 2]
    route_tree = STRtree(route_lines)
    project = Transformer.from_crs("EPSG:4326", LOCAL_CRS, always_xy=True)
    # Street sections of dual services are kept apart from the exclusive carriageway:
    # a signal on an ordinary road only qualifies where a service actually leaves the
    # busway, never beside it.
    street_lines = [LineString(span) for span in street_segments(services)]
    street_tree = STRtree(street_lines) if street_lines else None
    near_route, near_street = set(), set()
    for nid in signal_ids:
        node = all_nodes[nid]
        point = Point(*project.transform(node["lon"], node["lat"]))
        if point.distance(route_lines[int(route_tree.nearest(point))]) <= 12.0:
            near_route.add(nid)
        if street_tree is not None and point.distance(street_lines[int(street_tree.nearest(point))]) <= 12.0:
            near_street.add(nid)
    selected_pairs = []
    for nid in sorted(near_route | near_street):
        for wid in member_ways.get(nid, []):
            tags = all_ways.get(wid, {}).get("tags", {})
            if nid in near_route and busway_reason(tags):
                selected_pairs.append((nid, wid))
            elif nid in near_street and street_reason(tags):
                selected_pairs.append((nid, wid))
    near_signal_ids = near_route | near_street
    selected_way_ids = sorted({wid for _, wid in selected_pairs})
    detail_root = output / "details"
    way_root, node_root = detail_root / "ways", detail_root / "nodes"
    way_root.mkdir(parents=True, exist_ok=True)
    node_root.mkdir(parents=True, exist_ok=True)
    detail_records = []
    print(f"Detailed capture: {len(selected_way_ids)} ways, {len({nid for nid, _ in selected_pairs})} signals", flush=True)
    for wid in selected_way_ids:
        way_url = WAY_API.format(id=wid)
        way_file = way_root / f"{wid}.xml"
        way_payload = way_file.read_bytes() if args.reuse_raw and way_file.exists() else fetch(way_url, timeout=25)
        (way_root / f"{wid}.xml").write_bytes(way_payload)
        detail_nodes, detail_ways = parse_full(way_payload)
        all_nodes.update(detail_nodes)
        all_ways.update(detail_ways)
        print(f"way {wid}", flush=True)
        detail_records.append({
            "kind": "way_full", "id": wid, "url": way_url,
            "file": str(pathlib.Path("details") / "ways" / f"{wid}.xml"),
            "sha256": hashlib.sha256(way_payload).hexdigest(),
        })
    for nid in sorted({nid for nid, _ in selected_pairs}):
        node_url = NODE_API.format(id=nid)
        node_file = node_root / f"{nid}.xml"
        node_payload = node_file.read_bytes() if args.reuse_raw and node_file.exists() else fetch(node_url, timeout=25)
        (node_root / f"{nid}.xml").write_bytes(node_payload)
        detail_records.append({
            "kind": "node", "id": nid, "url": node_url,
            "file": str(pathlib.Path("details") / "nodes" / f"{nid}.xml"),
            "sha256": hashlib.sha256(node_payload).hexdigest(),
        })
    details_manifest = {
        "schema_version": 1,
        "source_dataset": "OpenStreetMap API 0.6 XML",
        "selection": "direct qualifying way membership and signal-to-route distance <= 12 m",
        "records": detail_records,
    }
    (detail_root / "manifest.json").write_text(json.dumps(details_manifest, ensure_ascii=False, indent=2) + "\n")
    signal_ids = sorted(nid for nid, node in all_nodes.items() if node["tags"].get("highway") == "traffic_signals")
    member_ways = {nid: sorted(wid for wid, way in all_ways.items() if nid in way["nodes"]) for nid in signal_ids}
    document = {
        "schema_version": 1,
        "source_dataset": "OpenStreetMap API 0.6 XML",
        "source_url_template": API,
        "queried_at": queried_at.isoformat(),
        "snapshot": snapshot,
        "cell_size_degrees": CELL,
        "services_source": str(pathlib.Path(args.services)),
        "coverage_note": "Cells are selected from route points in app/dist/services.json; curation additionally checks projected distance to route geometry.",
        "route_point_count": len(route_points),
        "route_cells": len(ordered_cells),
        "cells": cell_records,
        "nodes": [all_nodes[nid] for nid in sorted(all_nodes)],
        "ways": [all_ways[wid] for wid in sorted(all_ways)],
        "signal_member_way_ids": {str(nid): wids for nid, wids in member_ways.items()},
        "selected_signal_way_pairs": [[nid, wid] for nid, wid in selected_pairs],
        "detail_selection": {"signal_count": len({nid for nid, _ in selected_pairs}), "way_count": len(selected_way_ids), "details_manifest": "details/manifest.json"},
    }
    raw_path = output / "osm_map.json"
    raw_path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
    raw_sha = hashlib.sha256(raw_path.read_bytes()).hexdigest()

    # Hash the canonical vector records captured from the OSM API.  The URLs
    # remain independently reviewable; no hundreds of extra API requests are
    # needed just to duplicate records already present in the raw capture.
    candidates = selected_pairs
    evidence = []
    detail_by_key = {(r["kind"], r["id"]): r for r in detail_records}
    for nid, wid in candidates:
        node_url, way_url = NODE_API.format(id=nid), WAY_API.format(id=wid)
        node_payload = json.dumps(all_nodes[nid], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        way_payload = json.dumps(all_ways[wid], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        node_detail = detail_by_key.get(("node", nid), {})
        way_detail = detail_by_key.get(("way_full", wid), {})
        evidence.append({
            "node_id": nid, "way_id": wid,
            "node_url": node_url, "way_url": way_url,
            "node_sha256": node_detail.get("sha256"),
            "way_sha256": way_detail.get("sha256"),
            "hash_basis": "raw XML response files in details/",
            "node_xml_file": node_detail.get("file"),
            "way_xml_file": way_detail.get("file"),
            "record_source": raw_path.name,
        })
    evidence_path = output / "evidence.json"
    evidence_path.write_text(json.dumps({"schema_version": 1, "records": evidence}, ensure_ascii=False, indent=2) + "\n")
    manifest = {
        "schema_version": 1,
        "snapshot": snapshot,
        "queried_at": queried_at.isoformat(),
        "source_dataset": document["source_dataset"],
        "source_url_template": API,
        "raw_file": raw_path.name,
        "raw_sha256": raw_sha,
        "evidence_file": evidence_path.name,
        "evidence_sha256": hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
        "cell_count": len(ordered_cells),
        "signal_node_count": len(signal_ids),
        "direct_membership_pairs": len(candidates),
        "license": "OpenStreetMap contributors, ODbL 1.0; retrieved through api.openstreetmap.org",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
