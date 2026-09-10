"""Independent source/vehicle checks for the local practice section."""
import hashlib
import json
import math
import sys
import unittest
from pathlib import Path

from pyproj import Geod
from shapely.geometry import Polygon, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]


class MandalayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT/'game/data/mandalay.json').read_text())
        cls.scheme = json.loads((ROOT/'data/research/mandalay_scheme_20260909/scheme.geojson').read_text())

    def test_station_edges_preserve_geodesic_lengths(self):
        geod = Geod(ellps='WGS84')
        for module in self.data['modules']:
            feature = next(f for f in self.scheme['features'] if f['properties']['objectid'] == module['id'])
            source = feature['geometry']['coordinates'][0]
            source_lengths = sorted(geod.inv(*a[:2], *b[:2])[2] for a, b in zip(source, source[1:]))
            outline = module['outline']+[module['outline'][0]]
            game_lengths = sorted(math.dist(a, b) for a, b in zip(outline, outline[1:]))
            self.assertEqual(len(source_lengths), len(game_lengths))
            for real, game in zip(source_lengths, game_lengths):
                self.assertAlmostEqual(real, game, delta=.001)

    def test_whole_bus_fits_surface_in_both_practices(self):
        surface = unary_union([Polygon(p['outline'], p['holes']) for p in self.data['driving_surface']])
        for stop in self.data['stops']:
            p, f, r = stop['position'], stop['forward'], stop['right']
            for distance in range(-75, 26):
                # 18 m by 2.55 m enclosing both straight modules, independent of engine meshes.
                shell = Polygon([[p[i]+f[i]*(distance-z)+r[i]*x for i in (0, 1)] for x, z in [(-1.275,-7.4),(1.275,-7.4),(1.275,10.6),(-1.275,10.6)]])
                self.assertLess(shell.difference(surface.buffer(.003)).area, .001, (stop['id'],distance))

    def test_source_checksums_and_building_dimensions(self):
        for path, expected in self.data['summary']['source_hashes'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),expected)
        raw = json.loads((ROOT/'data/raw/20260909T035301Z/buildings.geojson').read_text())
        geod = Geod(ellps='WGS84')
        features = {f['properties']['OBJECTID']: f for f in raw['features']}
        grouped = {}
        for building in self.data['buildings']:
            grouped.setdefault(building['source_id'],[]).append(Polygon(building['outline'],building.get('holes',[])))
        for identifier, polygons in grouped.items():
            source = shape(features[identifier]['geometry'])
            source_area = abs(geod.geometry_area_perimeter(source)[0])
            self.assertAlmostEqual(source_area,sum(p.area for p in polygons),delta=.025)

if __name__ == '__main__':
    unittest.main()
