import typing as t

from utils.types import Point, Curve


class QuadraticBezierCurve:
    def __init__(self, points: Curve):
        self.points = points
        self.n = len(points)

    def get_points(self):
        curve_points = []

        for index in range(0, self.n - 2, 2):
            p1 = self.points[index]
            p2 = self.points[index + 1]
            p3 = self.points[index + 2]
            segment_points = self.__get_segment_points(p1, p2, p3)
            for point in segment_points:
                curve_points.append(point)

        return curve_points

    @staticmethod
    def __get_segment_points(p1: Point, p2: Point, p3: Point) -> Curve:
        curve = []
        for i in map(lambda x: x / 100.0, range(0, 105, 5)):
            a = (1.0 - i) ** 2
            b = 2 * (1.0 - i) * i
            c = i ** 2

            x = a * p1[0] + b * p2[0] + c * p3[0]
            y = a * p1[1] + b * p2[1] + c * p3[1]
            curve.append((x, y))

        return curve
