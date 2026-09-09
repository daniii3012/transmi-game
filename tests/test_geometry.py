import sys
from pathlib import Path
import unittest
import numpy as np
from pyproj import Geod
from shapely.geometry import Polygon

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_pilot import PROJECT, ORIGIN, triangulate


class GeometryTests(unittest.TestCase):
    def test_geographic_origin_and_meter_scale(self):
        x, y = PROJECT.transform(*ORIGIN)
        self.assertAlmostEqual(x, 0, places=5)
        self.assertAlmostEqual(y, 0, places=5)
        for azimuth in [0, 90, 180, 270]:
            lon, lat, _ = Geod(ellps="WGS84").fwd(*ORIGIN, azimuth, 1000)
            x, y = PROJECT.transform(lon, lat)
            self.assertAlmostEqual((x*x + y*y)**0.5, 1000, places=4)

    def test_roofs_preserve_courtyards(self):
        p = Polygon([(0,0), (30,0), (30,30), (20,30), (20,20), (0,20)], holes=[[(5,5),(5,15),(15,15),(15,5)]])
        vertices, indices = triangulate(p)
        area = 0
        for tri in indices.reshape((-1, 3)):
            triangle = Polygon(vertices[tri])
            self.assertTrue(p.covers(triangle))
            area += triangle.area
        self.assertAlmostEqual(area, p.area, places=5)


if __name__ == "__main__":
    unittest.main()
