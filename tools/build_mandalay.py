"""Build the local Mandalay practice section from cached, attributed polygons.

Station footprints remain metric. Only connectors beyond the protected area
are shortened; buildings translate as intact footprints and overlapping ones
are omitted. Ground levels, roofs, facade decoration and stop anchors are design
estimates. No claim of construction accuracy or official commercial service.
"""
import hashlib
import json
import math
from pathlib import Path

from shapely import make_valid
from shapely.affinity import translate, scale
from shapely.geometry import Point, Polygon, LineString, box, shape
from shapely.ops import transform, unary_union

from build_pilot import PROJECT, ROOT, add_polygon, polygons


def build():
    cfg = json.loads((ROOT / 'data/design/mandalay.json').read_text())
    raw = ROOT / 'data/raw' / cfg['source_snapshot']
    scheme = ROOT / 'data/research' / cfg['scheme_snapshot']
    manifest = json.loads((scheme / 'manifest.json').read_text())
    for filename, digest in manifest['sha256'].items():
        if hashlib.sha256((scheme / filename).read_bytes()).hexdigest() != digest:
            raise ValueError('Station source hash mismatch: ' + filename)
    station = next(f for f in json.loads((raw/'stations.geojson').read_text())['features'] if f['properties']['num_est'] == cfg['station_id'])
    lon, lat = station['geometry']['coordinates'][:2]
    pe, pn = PROJECT.transform(lon, lat)
    study = json.loads((ROOT/'game/data/scale_study.json').read_text())
    marker = next(s for s in study['variants'][0]['stations'] if s['id'] == cfg['station_id'])
    tx, tz = marker['tangent']
    half, width, protect, factor = (cfg[k] for k in ['source_half_length_m', 'source_half_width_m', 'protected_half_length_m', 'connector_factor'])
    if not (0 < protect < half and 0 < factor <= 1):
        raise ValueError('Invalid protected area or compression factor')
    clip = box(-width, -half, width, half)

    def local(geom):
        projected = transform(PROJECT.transform, make_valid(geom))
        return transform(lambda x, n: (-tz*(x-pe)+tx*(-n+pn), -tx*(x-pe)-tz*(-n+pn)), projected)

    def game_z(z):
        return z if abs(z) <= protect else math.copysign(protect+(abs(z)-protect)*factor, z)

    def compressed(geom):
        # Split before the piecewise map so polygon edges cross each seam exactly.
        parts = []
        for start, end in [(-half, -protect), (-protect, protect), (protect, half)]:
            for p in polygons(geom.intersection(box(-width, start, width, end))):
                parts.append(transform(lambda x, z: (x, game_z(z)), p))
        return unary_union(parts)

    groups, modules, buildings, trees, source_hashes = [], [], [], [], {}
    colors = {'roads': '535c59', 'sidewalks': 'b1afa0', 'medians': '8b9c76', 'plaza': 'ad8370', 'platforms': 'b9baac', 'roof': '839491'}

    def mesh_group(name, geom, base, height, color, collision=False):
        group = {'name': name, 'color': color, 'vertices': [], 'normals': [], 'collision': collision}
        for p in polygons(geom):
            if p.area > .02:
                # Existing triangulation consumes x/north and emits x/up/south.
                add_polygon(group, scale(p, xfact=1, yfact=-1, origin=(0, 0)), base, height)
        if group['vertices']:
            groups.append(group)

    geo = {}
    for layer in ['roads', 'sidewalks', 'medians', 'buildings']:
        path = raw / (layer+'.geojson')
        source_hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        rows = []
        for f in json.loads(path.read_text())['features']:
            g = local(shape(f['geometry']))
            if g.intersects(clip):
                rows.append((g, f['properties']))
        geo[layer] = rows
    for layer, level in [('roads', .035), ('sidewalks', .10), ('medians', .14)]:
        mesh_group(layer, compressed(unary_union([g for g, _ in geo[layer]]).intersection(clip)), level, 0, colors[layer])
    roads_game = compressed(unary_union([g for g, _ in geo['roads']]).intersection(clip))
    schemes = json.loads((scheme/'scheme.geojson').read_text())['features']
    station_parts = []
    for f in schemes:
        p, g = f['properties'], local(shape(f['geometry']))
        if p['secciontipo'] == 'Externa':
            continue  # Its physical function overlaps a carriageway and is unverified.
        if max(abs(g.bounds[1]), abs(g.bounds[3])) > protect:
            raise ValueError('A station footprint would be compressed')
        station_parts.append(g)
        if p['secciontipo'] != 'Vagon':
            continue
        coords = list(g.exterior.coords)
        south = 'W-E' in p['tipo']
        edges = [(a, b) for a, b in zip(coords, coords[1:]) if math.dist(a, b) > 30]
        a, b = max(edges, key=lambda e: (e[0][0]+e[1][0])*(1 if south else -1))
        # Forward is east (-z) on the south side and west (+z) on the north.
        if (b[1]-a[1] < 0) != south:
            a, b = b, a
        length = math.dist(a, b)
        forward = [(b[0]-a[0])/length, (b[1]-a[1])/length]
        right = [-forward[1], forward[0]]
        edge_center = [(a[i]+b[i])/2 for i in (0, 1)]
        pos = [edge_center[i]+right[i]*(1.275+cfg['target_door_gap_m'])+forward[i]*1.35 for i in (0, 1)]
        # Door targets are authored for the prototype, not inferred real platform gates.
        doors = [[pos[i]-forward[i]*z-right[i]*(1.275+cfg['target_door_gap_m']) for i in (0, 1)] for z in [-4.6, -.9, 4.7, 8.6]]
        module = {'id': p['objectid'], 'source_tipo': p['tipo'], 'source_name_conflict': p['nombre'], 'outline': list(g.exterior.coords)[:-1], 'area_m2': g.area, 'edge': [a, b], 'position': pos, 'heading': math.atan2(forward[0], -forward[1]), 'forward': forward, 'right': right, 'doors': doors, 'length_m': length, 'direction': 'Hacia Av. Boyacá' if south else 'Hacia Banderas', 'status': 'practice_anchors_estimated'}
        modules.append(module)
        mesh_group('Cubierta_'+str(p['objectid']), g.buffer(.22, join_style=2), cfg['roof_base_m'], cfg['roof_thickness_m'], colors['roof'])
    station_union = unary_union(station_parts)
    mesh_group('Plataforma_Mandalay', station_union, .04, cfg['platform_height_m']-.04, colors['plaza'], True)
    vagon_union = unary_union([Polygon(m['outline']) for m in modules])
    mesh_group('Acabado_plataformas', vagon_union, cfg['platform_height_m']+.006, 0, colors['platforms'])
    stops = []
    for module_id in cfg['practice_module_ids']:
        m = next(m for m in modules if m['id'] == module_id)
        p, f = m['position'], m['forward']
        spawn = [p[i]-f[i]*cfg['spawn_behind_stop_m'] for i in (0, 1)]
        stops.append({**m, 'spawn': spawn, 'departure_m': cfg['departure_m']})
    # Small surface joins resolve disagreement between the station scheme and
    # cadastral carriageway edge. They remain explicit, estimated geometry.
    practice_envelopes = []
    for stop in stops:
        p, f = stop['position'], stop['forward']
        a = [p[i]-f[i]*(cfg['spawn_behind_stop_m']+11) for i in (0, 1)]
        b = [p[i]+f[i]*(cfg['departure_m']+8) for i in (0, 1)]
        practice_envelopes.append(LineString([a, b]).buffer(1.55, cap_style=2))
    joins = unary_union(practice_envelopes).difference(roads_game).difference(station_union)
    # Do not quietly bridge substantial missing cartography.
    if not roads_game.buffer(1.0).covers(joins):
        raise ValueError('Practice path needs more than a 1 m surface adjustment')
    mesh_group('Raccords_provisionales', joins, .036, 0, colors['roads'])
    road_surface = roads_game.union(joins)
    # Surface joins must also remove higher sidewalk/median faces; otherwise
    # the bus would visually drive through grass despite the road coverage test.
    groups[:] = [g for g in groups if g['name'] not in ['medians', 'sidewalks']]
    for layer, level in [('sidewalks', .10), ('medians', .14)]:
        ground = compressed(unary_union([g for g, _ in geo[layer]]).intersection(clip)).difference(joins)
        mesh_group(layer, ground, level, 0, colors[layer])
    # Centre dashes for two-lane BRT carriageways; marking positions are estimates.
    marking_parts = []
    for z in range(-175, 176, 10):
        transect = roads_game.intersection(LineString([(-30, z), (32, z)]))
        pieces = list(transect.geoms) if hasattr(transect, 'geoms') else [transect]
        for line in pieces:
            if line.geom_type == 'LineString' and 6 < line.length < 10:
                c = line.interpolate(.5, normalized=True)
                marking_parts.append(box(c.x-.055, z-2, c.x+.055, z+2).intersection(roads_game))
    mesh_group('Marcas_BRT_estimadas', unary_union(marking_parts), .052, 0, 'c3c3a8')
    # Preserve building dimensions. Reject collisions caused by bringing parcels closer.
    occupied = roads_game.buffer(.8)
    omitted = 0
    for g, props in sorted(geo['buildings'], key=lambda item: (abs(item[0].centroid.y), item[1].get('OBJECTID', 0))):
        if not clip.covers(g):
            omitted += 1
            continue
        relocated = translate(g, yoff=game_z(g.centroid.y)-g.centroid.y)
        if relocated.intersects(occupied):
            omitted += 1
            continue
        occupied = unary_union([occupied, relocated.buffer(.12)])
        floors = props.get('CONNPISOS')
        floors = floors if isinstance(floors, (int, float)) and 1 <= floors <= 80 else 2
        height = float(floors)*3
        object_id = props['OBJECTID']
        palette = ['b78b72', 'bca88a', 'b29a80', 'a9b0a1', 'c4b49b']
        mesh_group('Construccion_'+str(object_id), relocated, .12, height, palette[object_id % len(palette)])
        for poly in polygons(relocated):
            buildings.append({'source_id': object_id, 'outline': list(poly.exterior.coords)[:-1], 'holes': [list(r.coords)[:-1] for r in poly.interiors], 'height_m': height, 'height_estimated': True})
    # Deterministic stylized vegetation; source polygons constrain placement, not tree identity.
    green = compressed(unary_union([g for g, _ in geo['medians']]).intersection(clip)).difference(station_union.buffer(3)).difference(roads_game.buffer(1.8))
    for z in range(-180, 181, 22):
        for x in [-51, -23, -3, 24, 51]:
            if green.covers(Point(x, z).buffer(2)):
                trees.append([x, z])
    summary = {'layout_version': cfg['layout_version'], 'origin_lon_lat': [lon, lat], 'source_axis_tangent_godot_xz': [tx, tz], 'frame': 'X derecha/sur, Y arriba, Z atrás/oeste; estación sin compresión', 'source_length_m': half*2, 'game_length_m': game_z(half)*2, 'protected_length_m': protect*2, 'connector_factor': factor, 'modules': len(modules), 'practice_stops': len(stops), 'buildings': len(buildings), 'omitted_building_features': omitted, 'surface_join_area_m2': joins.area, 'surface_join_max_distance_m': 1.0, 'triangles': sum(len(g['vertices'])//9 for g in groups), 'source_hashes': source_hashes, 'scheme_sha256': manifest['sha256'], 'scheme_license_status': manifest['license_status'], 'estimates': cfg['estimate_note'], 'excluded_schema_ids': [287]}
    return {'summary': summary, 'config': cfg, 'groups': groups, 'modules': modules, 'stops': stops, 'buildings': buildings, 'trees': trees, 'driving_surface': [{'outline':list(p.exterior.coords), 'holes':[list(r.coords) for r in p.interiors]} for p in polygons(road_surface)]}


def main():
    payload = build()
    (ROOT/'game/data/mandalay.json').write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')))
    (ROOT/'data/processed/mandalay_summary.json').write_text(json.dumps(payload['summary'], ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(payload['summary'], ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
