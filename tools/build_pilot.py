"""Convert the official geographic snapshot into a metric 3D blockout.

Heights are explicitly estimates (3 m per CONNPISOS). CONELEVACI is NOT a
height in metres. This is a data feasibility proof, not an as-built survey.
"""
import json
import math
from pathlib import Path

import mapbox_earcut
import numpy as np
from pyproj import CRS, Geod, Transformer
from shapely.geometry import Polygon, shape, box
from shapely.geometry.polygon import orient
from shapely.ops import transform
from shapely import make_valid

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = (-74.136, 4.63027)
LOCAL_CRS = CRS.from_proj4(f"+proj=aeqd +lat_0={ORIGIN[1]} +lon_0={ORIGIN[0]} +datum=WGS84 +units=m +no_defs")
PROJECT = Transformer.from_crs("EPSG:4326", LOCAL_CRS, always_xy=True)


def triangulate(poly):
    rings = [list(poly.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in poly.interiors]
    vertices = np.asarray([p for ring in rings for p in ring], dtype=np.float64)
    ends = np.cumsum([len(r) for r in rings], dtype=np.uint32)
    indices = mapbox_earcut.triangulate_float64(vertices, ends)
    return vertices, indices


def polygons(geom):
    if geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        return [geom]
    if hasattr(geom, "geoms"):
        return [p for g in geom.geoms for p in polygons(g)]
    return []


def add_polygon(group, poly, base, height):
    poly = orient(poly, sign=1.0)
    coords, indices = triangulate(poly)
    for index in indices:
        x, north = coords[index]
        group["vertices"].extend([round(x, 3), round(base + height, 3), round(-north, 3)])
        group["normals"].extend([0, 1, 0])
    if height > 0:
        for ring in [poly.exterior, *poly.interiors]:
            points = list(ring.coords)
            for (x1, n1), (x2, n2) in zip(points, points[1:]):
                length = math.hypot(x2 - x1, n2 - n1)
                if length < 1e-6:
                    continue
                normal = [round((n2 - n1) / length, 5), 0, round((x2 - x1) / length, 5)]
                for x, y, z in [(x1, base, -n1), (x2, base, -n2), (x2, base + height, -n2), (x1, base, -n1), (x2, base + height, -n2), (x1, base + height, -n1)]:
                    group["vertices"].extend([round(x, 3), round(y, 3), round(z, 3)])
                    group["normals"].extend(normal)


def main():
    folder = ROOT / "data/raw" / json.loads((ROOT / "data/raw/latest.json").read_text())["snapshot"]
    manifest = json.loads((folder / "manifest.json").read_text())
    bbox = manifest["bbox_wgs84"]
    clip = transform(PROJECT.transform, box(*bbox))
    colors = {"roads": "#4b5157", "sidewalks": "#b4b3a3", "medians": "#78957a", "buildings_0": "#c3b9a9", "buildings_1": "#b4b9b8", "buildings_2": "#ad9380"}
    groups = {k: {"name": k, "color": v, "vertices": [], "normals": []} for k, v in colors.items()}
    summary = {"source_snapshot": folder.name, "origin_lon_lat": ORIGIN, "projection": LOCAL_CRS.to_string(), "unit_meters": 1.0, "height_policy": "Estimated: CONNPISOS * 3 m; default 2 floors if absent/invalid. Flat ground. CONALTURA/CONELEVACI not interpreted as roof height.", "counts": {}, "invalid_geometries_repaired": 0, "buildings_height_estimated": 0, "floors_defaulted": 0}
    for layer in ["roads", "sidewalks", "medians", "buildings"]:
        features = json.loads((folder / f"{layer}.geojson").read_text())["features"]
        count = 0
        for feature in features:
            geom = shape(feature["geometry"])
            if not geom.is_valid:
                geom = make_valid(geom)
                summary["invalid_geometries_repaired"] += 1
            geom = transform(PROJECT.transform, geom).intersection(clip)
            props = feature["properties"]
            height = 0
            base = {"roads": 0.03, "sidewalks": 0.12, "medians": 0.15, "buildings": 0.15}[layer]
            key = layer
            if layer == "buildings":
                floors = props.get("CONNPISOS")
                if not isinstance(floors, (int, float)) or not 1 <= floors <= 80:
                    floors = 2
                    summary["floors_defaulted"] += 1
                height = float(floors) * 3.0
                key = "buildings_" + str(int(props.get("OBJECTID") or 0) % 3)
                summary["buildings_height_estimated"] += 1
            for poly in polygons(geom):
                if poly.area > 0.02:
                    add_polygon(groups[key], poly, base, height)
                    count += 1
        summary["counts"][layer] = {"source_features": len(features), "rendered_polygon_parts": count}
    stations = []
    for f in json.loads((folder / "stations.geojson").read_text())["features"]:
        p = shape(f["geometry"])
        if box(*bbox).contains(p):
            x, n = PROJECT.transform(p.x, p.y)
            props = f["properties"]
            stations.append({"id": props["num_est"], "name": props["nom_est"], "position": [x, 0, -n], "source_properties": props, "model_status": "point marker only; no station geometry inferred"})
    stations.sort(key=lambda s: s["position"][0])
    # A metric check independent of the projection formula, using geodesics.
    geod = Geod(ellps="WGS84")
    a, b = stations[0], stations[-1]
    inverse = Transformer.from_crs(LOCAL_CRS, "EPSG:4326", always_xy=True)
    alon, alat = inverse.transform(a["position"][0], -a["position"][2])
    blon, blat = inverse.transform(b["position"][0], -b["position"][2])
    distance = geod.inv(alon, alat, blon, blat)[2]
    metric = math.dist(a["position"], b["position"])
    summary["scale_check"] = {"from": a["name"], "to": b["name"], "geodesic_m": distance, "scene_m": metric, "difference_m": abs(distance - metric), "note": "Straight-line station-center distance, not driving distance"}
    summary["stations"] = [s["name"] for s in stations]
    summary["triangle_count"] = sum(len(g["vertices"]) // 9 for g in groups.values())
    payload = {"summary": summary, "groups": list(groups.values()), "stations": stations, "bbox_local": list(clip.bounds)}
    (ROOT / "game/data").mkdir(exist_ok=True)
    (ROOT / "game/data/pilot.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    (ROOT / "data/processed/summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
