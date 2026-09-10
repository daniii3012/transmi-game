"""Download a bounded, reproducible sample from official public ArcGIS services.

Run from any directory. Existing snapshots are reused; --refresh creates a new
dated snapshot rather than overwriting the previous one. No credentials needed.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BBOX = [-74.144, 4.6265, -74.1275, 4.6335]
TM = "https://gis.transmilenio.gov.co/arcgis/rest/services/ConsultaSubgerenciaPlanificacionSITP/Consulta_Planificacion_SITP/FeatureServer/"
MR = "https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/Mapa_Referencia/Mapa_Referencia/MapServer/"
SOURCES = {
    "stations": (TM + "2", "estaciones-troncales-de-transmilenio1", "objectid,num_est,nom_est,id_trazado,long_est,ancho_est,num_vag,esta_oper,cap_art,cap_biart", False),
    "corridors": (TM + "5", "trazados-troncales-de-transmilenio", "objectid,id_trazado,nom_traz,nom_tronc,le_troncal,ori_traz,fin_traz,tipo_tra,esta_oper", False),
    "buildings": ("https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/catastro/construccion/MapServer/0", "construccion", "OBJECTID,CONNPISOS,CONALTURA,CONELEVACI", True),
    "roads": (MR + "15", "calzada-bogota-d-c", "*", True),
    "sidewalks": (MR + "16", "mapa-de-referencia", "*", True),
    "medians": (MR + "17", "mapa-de-referencia", "*", True),
}


def get_json(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "BogotaTransmiPersonalPrototype/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.load(response)
    if "error" in result:
        raise RuntimeError(f"Service error at {url}: {result['error']}")
    return result


def download_layer(endpoint, fields, bounded):
    spatial = {"geometry": ",".join(map(str, BBOX)), "geometryType": "esriGeometryEnvelope", "inSR": 4326, "spatialRel": "esriSpatialRelIntersects"} if bounded else {}
    # Query IDs first: avoids silently losing features to service record limits.
    ids = sorted(get_json(endpoint + "/query", {"f": "json", "where": "1=1", "returnIdsOnly": "true", **spatial}).get("objectIds") or [])
    features = []
    for start in range(0, len(ids), 150):
        batch = get_json(endpoint + "/query", {"f": "geojson", "objectIds": ",".join(map(str, ids[start:start + 150])), "outFields": fields, "outSR": 4326, "returnGeometry": "true"})
        if batch.get("exceededTransferLimit"):
            raise RuntimeError("Unexpected transfer limit; reduce batch size")
        features.extend(batch["features"])
    if len(features) != len(ids):
        raise RuntimeError(f"Incomplete snapshot: expected {len(ids)}, got {len(features)}")
    return {"type": "FeatureCollection", "features": features}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    pointer = ROOT / "data/raw/latest.json"
    if pointer.exists() and not args.refresh:
        print("Using existing snapshot:", pointer.read_text())
        return
    now = dt.datetime.now(dt.timezone.utc)
    folder = ROOT / "data/raw" / now.strftime("%Y%m%dT%H%M%SZ")
    folder.mkdir(parents=True)
    manifest = {"retrieved_at_utc": now.isoformat(), "target_scenario_date": "2026-09-08", "bbox_wgs84": BBOX, "purpose": "Marsella–Mandalay geographic proof; current works not yet verified", "layers": {}}
    for name, (endpoint, slug, fields, bounded) in SOURCES.items():
        catalog = get_json("https://datosabiertos.bogota.gov.co/api/3/action/package_show", {"id": slug})["result"]
        metadata = get_json(endpoint, {"f": "pjson"})
        data = download_layer(endpoint, fields, bounded)
        raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode()
        (folder / f"{name}.geojson").write_bytes(raw)
        (folder / f"{name}.metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
        (folder / f"{name}.catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
        manifest["layers"][name] = {"endpoint": endpoint, "catalog_url": "https://datosabiertos.bogota.gov.co/dataset/" + slug, "license_id": catalog.get("license_id"), "license_title": catalog.get("license_title"), "metadata_modified": catalog.get("metadata_modified"), "count": len(data["features"]), "sha256": hashlib.sha256(raw).hexdigest(), "bounded": bounded, "output_crs": "EPSG:4326, server transformed"}
        print(name, len(data["features"]), manifest["layers"][name]["license_title"], flush=True)
    (folder / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    pointer.write_text(json.dumps({"snapshot": folder.name}, indent=2))


if __name__ == "__main__":
    main()
