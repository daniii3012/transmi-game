"""Piecewise metric layout for a single corridor, independent from GIS rendering.

A protected interval retains all displacement vectors. Only eligible intervals
shorten. Never apply this mapping to a whole city's mesh or independent edges of
a loop: shared junction constraints require a separate network layout stage.
"""
import bisect
import math


class CorridorLayout:
    def __init__(self, points, protected=(), factor=0.5):
        if not math.isfinite(factor) or not 0 < factor <= 1:
            raise ValueError('Compression factor must be finite and in (0, 1].')
        if len(points) < 2 or any(len(p) != 2 or not all(math.isfinite(v) for v in p) for p in points):
            raise ValueError('At least two finite 2D points are required.')
        self.points = [tuple(points[0])]
        self.source_s = [0.0]
        for point in points[1:]:
            distance = math.dist(point, self.points[-1])
            if distance > 1e-8:
                self.source_s.append(self.source_s[-1] + distance)
                self.points.append(tuple(point))
        if len(self.points) < 2:
            raise ValueError('Corridor has zero length.')
        self.length = self.source_s[-1]
        self.protected = self._merge(protected)
        boundaries = {0.0, self.length, *self.source_s}
        for start, end in self.protected:
            boundaries.update((start, end))
        self.knots = sorted(boundaries)
        self.positions = [(0.0, 0.0)]
        self.game_s = [0.0]
        self.factors = []
        for start, end in zip(self.knots, self.knots[1:]):
            mid = (start + end) / 2
            scale = 1.0 if any(a <= mid <= b for a, b in self.protected) else factor
            self.factors.append(scale)
            a, b = self.source_position(start), self.source_position(end)
            prior = self.positions[-1]
            self.positions.append(tuple(prior[k] + (b[k] - a[k]) * scale for k in range(2)))
            self.game_s.append(self.game_s[-1] + (end - start) * scale)

    def _merge(self, intervals):
        clipped = []
        for a, b in intervals:
            if not math.isfinite(a) or not math.isfinite(b) or b < a:
                raise ValueError('Invalid protected interval.')
            a, b = max(0.0, a), min(self.length, b)
            if b > a:
                clipped.append((a, b))
        merged = []
        for a, b in sorted(clipped):
            if merged and a <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
            else:
                merged.append((a, b))
        return merged

    @staticmethod
    def _segment(knots, value):
        if not math.isfinite(value) or value < -1e-7 or value > knots[-1] + 1e-7:
            raise ValueError('Chainage outside corridor.')
        value = min(knots[-1], max(0.0, value))
        return min(len(knots) - 2, max(0, bisect.bisect_right(knots, value) - 1)), value

    def source_position(self, source_m):
        i, s = self._segment(self.source_s, source_m)
        t = (s - self.source_s[i]) / (self.source_s[i + 1] - self.source_s[i])
        return tuple(self.points[i][k] + (self.points[i + 1][k] - self.points[i][k]) * t for k in range(2))

    def to_game(self, source_m):
        i, s = self._segment(self.knots, source_m)
        return self.game_s[i] + (s - self.knots[i]) * self.factors[i]

    def to_source(self, game_m):
        i, s = self._segment(self.game_s, game_m)
        return self.knots[i] + (s - self.game_s[i]) / self.factors[i]

    def game_position(self, source_m):
        i, s = self._segment(self.knots, source_m)
        point, start = self.source_position(s), self.source_position(self.knots[i])
        return tuple(self.positions[i][k] + (point[k] - start[k]) * self.factors[i] for k in range(2))

    def tangent(self, source_m):
        i, _ = self._segment(self.source_s, source_m)
        length = self.source_s[i + 1] - self.source_s[i]
        return tuple((self.points[i + 1][k] - self.points[i][k]) / length for k in range(2))

    def pose(self, source_m):
        return {'source_m': source_m, 'game_m': self.to_game(source_m),
                'position': list(self.game_position(source_m)), 'tangent': list(self.tangent(source_m))}
