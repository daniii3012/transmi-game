import hashlib
import json
import sys
import unittest
from pathlib import Path
from shapely.geometry import LineString, Point, shape
from shapely.ops import transform
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_network_2d import build, SNAPSHOT, LOAD_CORRIDORS
from build_pilot import PROJECT
from vehicle_definition import digest

class Network2DTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=build()

    def test_all_reference_parts_and_ids_retained(self):
        d=self.data
        self.assertEqual(len(d['stations']),153)
        self.assertEqual(len(d['corridors']),22)
        self.assertEqual(sum(len(c['components']) for c in d['corridors']),48)
        self.assertEqual(len({s['id'] for s in d['stations']}),153)
        self.assertEqual(d['vehicle']['sha256'],digest())
        for name,sha in d['source_sha256'].items():
            self.assertEqual(sha,hashlib.sha256((ROOT/'data/raw'/SNAPSHOT/name).read_bytes()).hexdigest())

    def test_trial_paths_do_not_invent_connections_or_compress(self):
        source={f['properties']['id_trazado']:transform(PROJECT.transform,shape(f['geometry'])) for f in json.loads((ROOT/'data/raw'/SNAPSHOT/'corridors.geojson').read_text())['features']}
        stations={s['id']:s for s in self.data['stations']}
        for p in self.data['patterns']:
            line=LineString(p['points'])
            self.assertLess(abs(line.length-p['length_m']),.2)
            for xy in p['points']:
                self.assertLess(source[p['corridor_id']].distance(Point(xy)),.001)
            self.assertEqual(p['status'],'synthetic_not_commercial_service')
            for stop in p['stops']:
                s=stations[stop['station_id']]
                self.assertEqual(s['corridor_id'],p['corridor_id'])
                self.assertLessEqual(line.distance(Point(s['xy'])),35.001)
            if p['scenario']=='load':
                self.assertIn(p['corridor_id'],LOAD_CORRIDORS)
        pilot=[p for p in self.data['patterns'] if p['scenario']=='pilot']
        self.assertEqual(len(pilot),2)
        self.assertAlmostEqual(pilot[0]['length_m'],1602.465665,places=3)
        self.assertEqual([s['station_id'] for s in pilot[0]['stops']],['05101','05102','05103'])

    def test_generated_bundle_matches_source(self):
        on_disk=json.loads((ROOT/'web/transmi2d/dist/network.json').read_text())
        self.assertEqual(on_disk,json.loads(json.dumps(self.data)))

if __name__=='__main__':
    unittest.main()
