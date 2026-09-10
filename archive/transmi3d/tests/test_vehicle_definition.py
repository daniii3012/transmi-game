import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
import vehicle_definition as vehicle


class VehicleDefinitionTests(unittest.TestCase):
    def test_default_preserves_verified_prototype(self):
        spec = vehicle.load()
        self.assertEqual(vehicle.nominal_bounds(spec),(-7.4,10.600000000000001))
        self.assertAlmostEqual(spec['width_m'],2.55)
        for actual, expected in zip(vehicle.straight_doors(spec),[-4.6,-.9,4.7,8.6]):
            self.assertAlmostEqual(actual['z_m'],expected)
        self.assertEqual(len(vehicle.straight_doors(spec)),4)

    def test_rejects_bad_body_topology_and_door_openings(self):
        spec = vehicle.load()
        def invalid(change):
            altered = copy.deepcopy(spec)
            change(altered)
            with self.assertRaises(ValueError): vehicle.validate(altered)
        invalid(lambda d: d['modules'].append(copy.deepcopy(d['modules'][1])))
        invalid(lambda d: d['modules'][0]['doors'][0].update(z_m=-7.4))
        invalid(lambda d: d['modules'][1]['doors'][0].update(id='front_1'))
        invalid(lambda d: d['modules'][0]['axles'][1].update(z_m=1))
        invalid(lambda d: d['wheels'].update(radius_m=0))

    def test_mandalay_gates_and_asset_have_current_definition(self):
        spec = vehicle.load()
        sha = vehicle.digest()
        manifest = json.loads((ROOT/'game/assets/vehicles/articulado_prototipo.manifest.json').read_text())
        self.assertEqual(manifest['vehicle_spec_sha256'],sha)
        self.assertEqual(manifest['model_sha256'],hashlib.sha256((ROOT/'game/assets/vehicles/articulado_prototipo.glb').read_bytes()).hexdigest())
        mandalay = json.loads((ROOT/'game/data/mandalay.json').read_text())
        for stop in mandalay['stops']:
            self.assertEqual(stop['vehicle_spec_sha256'],sha)
            self.assertEqual(stop['vehicle_door_ids'],[d['id'] for d in vehicle.straight_doors(spec)])
            for target, anchor in zip(stop['doors'],vehicle.straight_doors(spec)):
                offset = [stop['position'][i]-target[i] for i in (0,1)]
                longitudinal = sum(offset[i]*stop['forward'][i] for i in (0,1))
                self.assertAlmostEqual(longitudinal,anchor['z_m'])

if __name__ == '__main__': unittest.main()
