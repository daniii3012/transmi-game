"""The live proxy: projection, parsing and the guards that keep it from calling out by mistake.

Standard library only, like the module it tests, so it runs under the same Python that serves
the simulator. No test here touches the network.
"""
import sys
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import live_buses
from live_buses import LiveBuses, aeqd, normalise, reported_age

ORIGIN = (-74.136, 4.63027)
# Valores de pyproj con la definición de geo.py, para que la reimplementación no se desvíe.
REFERENCE = [((-74.06853068345309, 4.628316797400941), (7486.32, -215.63)),
             ((-74.17304142522808, 4.627406393837563), (-4110.08, -316.55)),
             ((-74.09042483775724, 4.742075297866035), (5056.16, 12363.78)),
             ((-74.15183017732086, 4.634129410986035), (-1756.48, 426.80))]

class ProjectionTests(unittest.TestCase):
    def test_matches_the_pyproj_definition_of_the_simulator_frame(self):
        for (lon, lat), expected in REFERENCE:
            x, y = aeqd(lon, lat, ORIGIN)
            self.assertAlmostEqual(x, expected[0], places=1)
            self.assertAlmostEqual(y, expected[1], places=1)

    def test_the_origin_itself_is_the_centre_of_the_frame(self):
        self.assertEqual(aeqd(ORIGIN[0], ORIGIN[1], ORIGIN), (0.0, 0.0))

class ParsingTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 11, 21, 3, 30, tzinfo=ZoneInfo('America/Bogota'))
        self.entry = {'id': '41103', 'label': 'T10103', 'latitude': 4.628316797400941,
                      'longitude': -74.06853068345309, 'angulo': 189, 'destino_limpio': 'Portal Américas',
                      'ocupacion_bus': 'VACIO', 'lasttime': '09:03:00 PM', 'posicion': 3421, 'route_id': 13310}

    def test_a_bus_arrives_in_simulator_coordinates_with_its_own_number(self):
        bus = normalise(self.entry, ORIGIN, self.now)
        self.assertEqual(bus['label'], 'T10103')
        self.assertAlmostEqual(bus['xy'][0], 7486.32, places=1)
        self.assertAlmostEqual(bus['xy'][1], -215.63, places=1)
        self.assertEqual(bus['reported_age_s'], 30)

    def test_a_position_that_cannot_be_believed_is_dropped_instead_of_drawn(self):
        for broken in [{}, {'latitude': 4.6}, {'latitude': 'x', 'longitude': 'y'},
                       {'latitude': 0, 'longitude': 0}, {'latitude': 40.4, 'longitude': -3.7}]:
            self.assertIsNone(normalise(broken, ORIGIN, self.now))

    def test_a_reading_from_before_midnight_is_not_read_as_a_day_in_the_future(self):
        midnight = datetime(2026, 9, 12, 0, 0, 30, tzinfo=ZoneInfo('America/Bogota'))
        self.assertEqual(reported_age('11:59:30 PM', midnight), 60)
        self.assertEqual(reported_age('12:00:10 AM', midnight), 20)
        self.assertIsNone(reported_age('a las once', midnight))
        self.assertIsNone(reported_age(None, midnight))

class NetworkTests(unittest.TestCase):
    def test_the_quadrants_tile_the_box_without_gaps_or_overlap(self):
        box = {'llLat': 4.0, 'llLon': -74.0, 'urLat': 5.0, 'urLon': -73.0}
        pieces = live_buses.quadrants(box)
        self.assertEqual(len(pieces), 4)
        area = sum((p['urLat'] - p['llLat']) * (p['urLon'] - p['llLon']) for p in pieces)
        self.assertAlmostEqual(area, (box['urLat'] - box['llLat']) * (box['urLon'] - box['llLon']))
        for corner in [(4.0, -74.0), (5.0, -73.0), (4.5, -73.5), (4.9, -73.1)]:
            inside = [p for p in pieces if p['llLat'] <= corner[0] <= p['urLat'] and p['llLon'] <= corner[1] <= p['urLon']]
            self.assertTrue(inside, f'{corner} quedó fuera de todos los cuadrantes')

    def test_a_planner_vehicle_keeps_its_line_and_drops_its_timetable(self):
        live = LiveBuses()
        journey = {'lat': 4.628316797400941, 'lon': -74.06853068345309, 'line': '5', 'lineId': '12841',
                   'operator': 'Transmilenio-Troncal', 'journeyDetailRef': 'ref',
                   'stops': [{'name': 'Portal Américas T4'}, {'name': 'Av. Jiménez C - 2 ó 5-T'}]}
        vehicle = live.vehicle(journey, ORIGIN)
        self.assertEqual(vehicle['line'], '5')
        self.assertEqual(vehicle['destination'], 'Av. Jiménez C - 2 ó 5-T')
        self.assertNotIn('stops', vehicle)
        self.assertAlmostEqual(vehicle['xy'][0], 7486.32, places=1)
        self.assertIsNone(live.vehicle({'lat': 40.4, 'lon': -3.7}, ORIGIN))
        self.assertIsNone(live.vehicle({}, ORIGIN))

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.live = LiveBuses()
        # Sin credencial alcanzable: si algo intentara salir a la red, esta prueba lo delataría.
        self.previous, live_buses.CREDENTIAL = live_buses.CREDENTIAL, ROOT / 'tools/no-existe.json'
        self.addCleanup(setattr, live_buses, 'CREDENTIAL', self.previous)

    def test_a_route_outside_the_catalogue_is_never_asked_for(self):
        self.assertEqual(self.live.buses('ZZZ99')[0], 'unknown_route')
        self.assertEqual(self.live.buses('')[0], 'unknown_route')
        self.assertEqual(self.live.buses('5; DROP')[0], 'unknown_route')

    def test_without_local_configuration_the_service_is_not_called(self):
        self.assertEqual(self.live.buses('5')[0], 'not_configured')
        self.assertFalse(self.live.configured())

    def test_the_catalogue_comes_from_the_same_file_the_page_loads(self):
        codes, origin = self.live.catalogue()
        self.assertEqual(tuple(origin), ORIGIN)
        for code in ['1', '5', 'C19', 'F60', 'A60']:
            self.assertIn(code, codes)

if __name__ == '__main__':
    unittest.main()
