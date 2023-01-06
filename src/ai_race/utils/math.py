import math

from local_typing import Point, Radians


def angle_between_three_points(p1: Point, p2: Point, p3: Point) -> Radians:
    """Calculates angle between three points via cosine theorem (middle point is vertex)"""
    a = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
    b = math.sqrt((p3[0] - p2[0]) ** 2 + (p3[1] - p2[1]) ** 2)
    c = math.sqrt((p1[0] - p3[0]) ** 2 + (p1[1] - p3[1]) ** 2)

    return math.acos((a ** 2 + b ** 2 - c ** 2) / (2 * a * b))
