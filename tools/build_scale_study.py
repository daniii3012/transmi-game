"""Reproducible, non-drivable comparison of official and condensed Américas axes.

Positions are derived from the official corridor, not lane-level geometry.
Protected spans and roadside modules are design assumptions, not surveys.
"""
import hashlib
import json
import math
from pathlib import Path

from shapely.geometry import LineString, Point, shape
from shapely.ops import substring, transform
from build_pilot import ORIGIN, PROJECT, LOCAL_CRS
from corridor_layout import CorridorLayout

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'data/design/americas_scale_study.json'


def read(path):
    return json.loads(path.read_text())


def build(config_path=CONFIG):
    config = read(config_path)
    folder = ROOT / 'data/raw' / config['source_snapshot']
    station_features = {f['properties']['num_est']: f for f in read(folder / 'stations.geojson')['features']}
    selected = [station_features[s] for s in config['station_ids']]
    station_points = [transform(PROJECT.transform, shape(f['geometry'])) for f in selected]
    corridor = next(f for f in read(folder / 'corridors.geojson')['features'] if f['properties']['id_trazado'] == config['corridor_id'])
    projected = transform(PROJECT.transform, shape(corridor['geometry']))
    lines = list(projected.geoms) if projected.geom_type == 'MultiLineString' else [projected]
    # Never bridge a missing component by drawing an invented straight connection.
    candidates = [line for line in lines if all(line.distance(p) < .5 for p in station_points)]
    if len(candidates) != 1:
        raise ValueError('Expected exactly one connected source component through all pilot stations.')
    line = candidates[0]
    if line.project(station_points[0]) > line.project(station_points[-1]):
        line = LineString(list(line.coords)[::-1])
    station_s = [line.project(p) for p in station_points]
    if station_s != sorted(station_s):
        raise ValueError('Station order does not match source geometry.')
    margin = config['end_margin_source_m']
    start, end = station_s[0] - margin, station_s[-1] + margin
    if start < 0 or end > line.length:
        raise ValueError('Source component does not cover requested margins.')
    clipped = substring(line, start, end)
    # X east, Z south. Source origin retained separately from layout coordinates.
    points = [(x, -north) for x, north in clipped.coords]
    origin = points[0]
    station_s = [s - start for s in station_s]
    protection = []
    for f, s in zip(selected, station_s):
        length = float(f['properties']['long_est'])
        if not 0 < length < 1000:
            raise ValueError('Station length needs manual review.')
        half = length / 2 + config['station_approach_allowance_m']
        protection.append({'id': 'station-' + f['properties']['num_est'], 'from_source_m': max(0, s - half),
                           'to_source_m': min(clipped.length, s + half), 'reason': 'Longitud publicada + reserva de aproximación de diseño; cotas pendientes.'})
    for node in config['protected_nodes']:
        s = station_s[config['station_ids'].index(node['station_id'])]
        protection.append({'id': 'node-' + node['station_id'], 'from_source_m': max(0, s - node['half_length_source_m']),
                           'to_source_m': min(clipped.length, s + node['half_length_source_m']), 'reason': node['reason']})
    protected = [(p['from_source_m'], p['to_source_m']) for p in protection]
    baseline = CorridorLayout(points, protected, factor=1)
    compact = CorridorLayout(points, protected, config['eligible_factor'])
    if not LineString(compact.positions).is_simple:
        raise ValueError('Condensed corridor intersects itself; manual layout required.')
    result = {
        'schema_version': 1, 'layout_revision': config['layout_revision'],
        'source_snapshot': folder.name, 'source_corridor_id': config['corridor_id'],
        'source_origin_lon_lat': ORIGIN, 'projection': LOCAL_CRS.to_string(),
        'layout_origin_source_xz': origin, 'unit_game_m': 1.0,
        'source_sha256': {name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in ['stations.geojson', 'corridors.geojson']},
        'config_sha256': hashlib.sha256(config_path.read_bytes()).hexdigest(),
        'status': 'layout_study_not_drivable', 'assumptions': config,
        'protection': protection,
        'stations': [{'id': f['properties']['num_est'], 'name': f['properties']['nom_est'],
                      'source_lon_lat': f['geometry']['coordinates'], 'source_m': s,
                      'published_length_m': f['properties']['long_est'],
                      'model_status': 'marker_and_design_envelope_only'} for f, s in zip(selected, station_s)],
        'variants': [],
    }
    for key, label, layout in [('reference', 'Referencia geográfica', baseline), ('condensed', 'Bogotá condensada · ensayo', compact)]:
        # Include every original vertex and protection boundary exactly in the export.
        samples = sorted({*layout.knots, *station_s, *[float(s) for s in range(0, math.ceil(layout.length), 8)]})
        variant = {'id': key, 'label': label, 'length_game_m': layout.game_s[-1],
                   'samples': [layout.pose(s) for s in samples],
                   'stations': [dict(station, **layout.pose(station['source_m'])) for station in result['stations']],
                   'protected_spans': [{'from_game_m': layout.to_game(a), 'to_game_m': layout.to_game(b)} for a, b in layout.protected],
                   'segments': [{'source_from_m': a, 'source_to_m': b, 'game_from_m': layout.game_s[i],
                                 'game_to_m': layout.game_s[i + 1], 'factor': layout.factors[i]} for i, (a, b) in enumerate(zip(layout.knots, layout.knots[1:]))],
                   'context': []}
        # Fixed-size illustrative modules: fewer slots, never squashed footprints.
        spacing = config['illustrative_context_spacing_game_m']
        for side in [-1, 1]:
            game_m = 24.0
            while game_m < layout.game_s[-1] - 24:
                source_m = layout.to_source(game_m)
                # Keep the Boyacá node visually clear; this is not its final geometry.
                node = next(p for p in protection if p['id'] == 'node-05102')
                if not node['from_source_m'] <= source_m <= node['to_source_m']:
                    pose = layout.pose(source_m)
                    pose['side'] = side
                    variant['context'].append(pose)
                game_m += spacing
        result['variants'].append(variant)
    length = baseline.game_s[-1]
    protected_m = sum(b - a for a, b in compact.protected)
    result['metrics'] = {'source_axis_m': length, 'condensed_axis_game_m': compact.game_s[-1],
                         'protected_source_m': protected_m, 'eligible_source_m': length - protected_m,
                         'eligible_factor': config['eligible_factor'],
                         'reduction_percent': (1 - compact.game_s[-1] / length) * 100,
                         'measurement_note': 'Longitud sobre eje oficial con 180 m de margen por extremo; no distancia de carril ni horario de servicio.',
                         'between_station_centers': []}
    for i in range(len(station_s) - 1):
        a, b = station_s[i:i + 2]
        result['metrics']['between_station_centers'].append({'from': result['stations'][i]['name'], 'to': result['stations'][i + 1]['name'],
            'source_axis_m': b - a, 'condensed_axis_game_m': compact.to_game(b) - compact.to_game(a)})
    return result


def main():
    payload = build()
    (ROOT / 'game/data/scale_study.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    report = {k: payload[k] for k in ['layout_revision', 'source_snapshot', 'source_sha256', 'config_sha256', 'metrics']}
    report['context_modules'] = {v['id']: len(v['context']) for v in payload['variants']}
    report['context_note'] = 'Módulos ilustrativos del estudio, no edificios reales ni estimación del ahorro total de modelado.'
    (ROOT / 'data/processed/scale_study_summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
