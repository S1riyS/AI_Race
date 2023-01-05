import typing as t

from local_typing import Point


class ConvexHull:
    def __init__(self, points: t.List[Point]):
        self.points = points

    def get_points(self) -> t.List[Point]:
        hull = []
        self.points.sort(key=lambda x: [x[0], x[1]])

        start = self.points.pop(0)
        hull.append(start)

        self.points.sort(key=lambda p: (self.__get_slope(p, start), -p[1], p[0]))
        for pt in self.points:
            hull.append(pt)
            while len(hull) > 2 and self.__get_cross_product(hull[-3], hull[-2], hull[-1]) < 0:
                hull.pop(-2)

        return hull

    @staticmethod
    def __get_slope(p1: Point, p2: Point) -> float:
        if p1[0] == p2[0]:
            return float('inf')
        else:
            return 1.0 * (p1[1] - p2[1]) / (p1[0] - p2[0])

    @staticmethod
    def __get_cross_product(p1: Point, p2: Point, p3: Point):
        return ((p2[0] - p1[0]) * (p3[1] - p1[1])) - ((p2[1] - p1[1]) * (p3[0] - p1[0]))
