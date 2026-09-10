import math
import sys
import unittest
from pathlib import Path

from shapely.geometry import LineString

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from corridor_layout import CorridorLayout
from build_scale_study import build


class CorridorLayoutTests(unittest.TestCase):
    def test_known_distance_and_inverse_at_boundaries(self):
        layout = CorridorLayout([(0, 0), (1000, 0)], [(100, 200), (700, 900)], .5)
        self.assertAlmostEqual(layout.game_s[-1], 650)
        for s in [0, .0001, 100, 150, 200, 699.99, 700, 900, 999.9, 1000]:
            self.assertAlmostEqual(layout.to_source(layout.to_game(s)), s, places=7)
        self.assertEqual(layout.game_position(1000), (650, 0))

    def test_overlapping_protections_count_once(self):
        layout = CorridorLayout([(0, 0), (1000, 0)], [(-50, 100), (50, 200), (100, 150), (900, 1100)], .5)
        self.assertEqual(layout.protected, [(0, 200), (900, 1000)])
        self.assertAlmostEqual(layout.game_s[-1], 650)

    def test_protected_bend_retains_vectors(self):
        layout = CorridorLayout([(0, 0), (100, 0), (100, 100)], [(80, 120)], .5)
        self.assertEqual(layout.game_position(100), (60, 0))
        self.assertEqual(layout.game_position(120), (60, 20))
        for a, b in [(85, 95), (90, 110), (102, 118)]:
            self.assertAlmostEqual(math.dist(layout.game_position(a), layout.game_position(b)),
                                   math.dist(layout.source_position(a), layout.source_position(b)))

    def test_baseline_is_translation_only(self):
        layout = CorridorLayout([(40, 50), (140, 50), (140, 170)], [(90, 140)], 1)
        for s in [0, 33, 100, 130, 220]:
            p = layout.source_position(s)
            self.assertAlmostEqual(layout.to_game(s), s)
            self.assertEqual(layout.game_position(s), (p[0] - 40, p[1] - 50))

    def test_rejects_collapsed_and_invalid_inputs(self):
        for factor in [0, -1, 2, float('nan')]:
            with self.assertRaises(ValueError):
                CorridorLayout([(0, 0), (100, 0)], factor=factor)
        with self.assertRaises(ValueError):
            CorridorLayout([(0, 0), (0, 0)])
        layout = CorridorLayout([(0, 0), (100, 0)])
        for s in [-1, 101, float('nan')]:
            with self.assertRaises(ValueError):
                layout.to_game(s)

    def test_actual_pilot_keeps_ids_order_and_protected_lengths(self):
        data = build()
        reference, compact = data['variants']
        self.assertEqual([s['id'] for s in compact['stations']], ['05101', '05102', '05103'])
        station_distances = [s['game_m'] for s in compact['stations']]
        self.assertEqual(station_distances, sorted(station_distances))
        self.assertTrue(LineString([p['position'] for p in compact['samples']]).is_simple)
        self.assertLess(compact['length_game_m'], reference['length_game_m'])
        self.assertEqual(len(reference['protected_spans']), len(compact['protected_spans']))
        for a, b in zip(reference['protected_spans'], compact['protected_spans']):
            self.assertAlmostEqual(a['to_game_m'] - a['from_game_m'], b['to_game_m'] - b['from_game_m'], places=6)
        self.assertAlmostEqual(data['metrics']['source_axis_m'], 1602.4656653818452, places=5)
        expected = data['metrics']['protected_source_m'] + data['metrics']['eligible_source_m'] * .5
        self.assertAlmostEqual(compact['length_game_m'], expected, places=6)
        self.assertLess(len(compact['context']), len(reference['context']))


if __name__ == '__main__':
    unittest.main()
