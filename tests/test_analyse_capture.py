"""What the capture analysis claims to measure, on readings built by hand.

Standard library only, like the module it tests. No test here touches the network or the captured
files: the point is to pin the meaning of a stop-to-stop time, not to re-measure Bogotá.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from analyse_capture import cobertura, depurar, flota, intervalos, percentiles, tramos, transiciones


def reading(build, bus, trip, stop, sequence, route='R1'):
    return {'build': str(build), 'bus': bus, 'placa': '', 'viaje': trip, 'ruta': route,
            'lat': '4.6', 'lon': '-74.1', 'parada': stop, 'secuencia': str(sequence)}


class Transitions(unittest.TestCase):
    def test_only_changes_are_marked(self):
        """Repeating the same target stop is not an event: the bus is still on its way to it."""
        rows = [reading(100, '1', 'T', 'A', 1), reading(120, '1', 'T', 'A', 1),
                reading(140, '1', 'T', 'B', 2), reading(160, '1', 'T', 'B', 2),
                reading(180, '1', 'T', 'C', 3)]
        marks = transiciones(rows)[('1', 'T')]
        self.assertEqual([(m[0], m[1]) for m in marks], [(100, 'A'), (140, 'B'), (180, 'C')])

    def test_unordered_input_is_sorted_before_reading_it(self):
        """El detalle se escribe por lotes; nada garantiza que llegue ordenado al análisis."""
        rows = [reading(180, '1', 'T', 'C', 3), reading(100, '1', 'T', 'A', 1), reading(140, '1', 'T', 'B', 2)]
        marks = transiciones(rows)[('1', 'T')]
        self.assertEqual([m[1] for m in marks], ['A', 'B', 'C'])

    def test_each_vehicle_and_trip_is_followed_apart(self):
        """Un mismo bus encadena viajes; mezclarlos inventaría un tramo del final de uno al inicio del otro."""
        rows = [reading(100, '1', 'T1', 'A', 1), reading(140, '1', 'T1', 'B', 2),
                reading(160, '1', 'T2', 'A', 1), reading(200, '1', 'T2', 'B', 2),
                reading(100, '2', 'T1', 'A', 1), reading(150, '2', 'T1', 'B', 2)]
        self.assertEqual(sorted(transiciones(rows)), [('1', 'T1'), ('1', 'T2'), ('2', 'T1')])


class Stretches(unittest.TestCase):
    published = {('R1', 'A', 'B'): {'seconds': 40.0, 'metres': 500.0},
                 ('R1', 'B', 'C'): {'seconds': 300.0, 'metres': 3000.0}}

    def rows(self, times):
        out = []
        for i, (bus, marks) in enumerate(times.items()):
            for build, stop, seq in marks:
                out.append(reading(build, bus, 'T' + bus, stop, seq))
        return out

    def test_a_stretch_is_leaving_one_stop_until_leaving_the_next(self):
        rows = self.rows({'1': [(0, 'A', 1), (40, 'B', 2), (340, 'C', 3)]})
        got = tramos(rows, self.published, minimum=1)
        pairs = {(r['from_stop'], r['to_stop']): r for r in got['detail']}
        self.assertEqual(pairs[('A', 'B')]['observed']['p50'], 40)
        self.assertEqual(pairs[('B', 'C')]['observed']['p50'], 300)
        self.assertEqual(got['observations_unmatched'], 0)

    def test_a_stretch_with_no_published_equivalent_is_counted_apart_not_dropped(self):
        rows = self.rows({'1': [(0, 'A', 1), (40, 'B', 2), (100, 'Z', 9)]})
        got = tramos(rows, self.published, minimum=1)
        self.assertEqual(got['observations_matched'], 1)
        self.assertEqual(got['observations_unmatched'], 1)

    def test_the_ratio_is_split_by_published_duration(self):
        """Un tramo corto y uno largo no se miden igual de bien; promediarlos juntos lo esconde."""
        rows = self.rows({'1': [(0, 'A', 1), (40, 'B', 2), (340, 'C', 3)],
                          '2': [(0, 'A', 1), (40, 'B', 2), (340, 'C', 3)]})
        got = tramos(rows, self.published, minimum=2)
        self.assertEqual(got['ratio_by_published_duration']['<90 s']['p50'], 1.0)
        self.assertEqual(got['ratio_by_published_duration']['>240 s']['p50'], 1.0)
        self.assertNotIn('90-150 s', got['ratio_by_published_duration'])

    def test_stretches_under_the_minimum_stay_out_of_the_ratio(self):
        rows = self.rows({'1': [(0, 'A', 1), (40, 'B', 2)]})
        got = tramos(rows, self.published, minimum=5)
        self.assertEqual(got['stretches'], 1)
        self.assertIsNone(got['ratio_observed_over_published'])


class Headways(unittest.TestCase):
    def test_spacing_is_between_different_vehicles_of_the_same_route_and_stop(self):
        rows = [*self.trip('1', 0), *self.trip('2', 180), *self.trip('3', 600)]
        got = intervalos(rows, {'R1': 'Troncal'})
        self.assertEqual(got, {})  # menos de veinte observaciones: no se informa nada

    def test_enough_observations_report_minutes_and_bunching(self):
        rows = []
        for i in range(25):
            rows.extend(self.trip(str(i), i * 120))
        got = intervalos(rows, {'R1': 'Troncal'})['Troncal']
        self.assertEqual(got['p50'], 2.0)
        self.assertEqual(got['bunched_under_60s_pct'], 0)

    @staticmethod
    def trip(bus, offset):
        return [reading(offset, bus, 'T' + bus, 'A', 1), reading(offset + 60, bus, 'T' + bus, 'B', 2)]


class Coverage(unittest.TestCase):
    def test_gaps_are_reported_not_smoothed_over(self):
        summary = [{'build': 100, 'hour': 6.0, 'trunk': 10, 'by_agency': {'Troncal': 10}},
                   {'build': 130, 'hour': 6.0, 'trunk': 12, 'by_agency': {'Troncal': 12}},
                   {'build': 900, 'hour': 6.2, 'trunk': 14, 'by_agency': {'Troncal': 14}},
                   {'at': 'x', 'error': 'timeout'}]
        got = cobertura(summary)
        self.assertEqual(got['builds'], 3)
        self.assertEqual(got['failures'], 1)
        self.assertEqual(got['gaps_total'], 1)
        self.assertEqual(got['gaps_over_2min'][0]['seconds'], 770)

    def test_fleet_is_a_median_per_hour_not_a_last_reading(self):
        summary = [{'build': 1, 'hour': 6.1, 'trunk': 10, 'by_agency': {'Troncal': 10}},
                   {'build': 2, 'hour': 6.9, 'trunk': 30, 'by_agency': {'Troncal': 30}},
                   {'build': 3, 'hour': 6.5, 'trunk': 20, 'by_agency': {'Troncal': 20}}]
        self.assertEqual(flota(summary)['6']['Troncal'], 20)

    def test_a_resumed_capture_does_not_break_the_reading(self):
        """Recrear el archivo deja una cabecera en medio: se descarta, no revienta la lectura."""
        rows = [reading(100, '1', 'T', 'A', 1),
                {k: k for k in reading(0, '', '', '', 0)},
                reading(140, '1', 'T', 'B', 2)]
        clean, counted = depurar(rows)
        self.assertEqual(counted['cabeceras_intrusas'], 1)
        self.assertEqual([r['parada'] for r in clean], ['A', 'B'])
        self.assertEqual([m[1] for m in transiciones(clean)[('1', 'T')]], ['A', 'B'])

    def test_a_batch_written_twice_counts_once(self):
        """Dos capturas solapadas repiten un lote entero; contarlo doble inventaría un intervalo de 0 s."""
        rows = [reading(100, '1', 'T', 'A', 1), reading(100, '1', 'T', 'A', 1),
                reading(140, '1', 'T', 'B', 2)]
        clean, counted = depurar(rows)
        self.assertEqual(counted['filas_repetidas'], 1)
        self.assertEqual(len(clean), 2)

    def test_percentiles_never_index_past_the_end(self):
        self.assertEqual(percentiles([5])['p90'], 5)
        self.assertIsNone(percentiles([]))


if __name__ == '__main__':
    unittest.main()
