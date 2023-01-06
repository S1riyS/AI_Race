"""
Source: https://github.com/thestarvanisher/bezier_curve_interpolation
"""

import typing as t

import numpy as np

from local_typing import Point, Curve


class BezierCurve:
    def __init__(self, points: t.List[Point], curve_points_number=30):
        """
        Parameters:
            points: The coordinate of the points around which it will be interpolated
            curve_points_number: The number of points on a Bezier curve between two points
        """
        self.points = points
        self.n = len(points)
        self.curve_points_number = curve_points_number

        self.curve_points = None
        self.A = None
        self.B = None
        self.C = None
        self.P = None

        self.__fix_variables()

    def __fix_variables(self) -> None:
        """Fixes the type of the variables"""
        if type(self.points) != np.ndarray:
            self.points = np.array(self.points)

    def __create_coefficient_matrix(self) -> None:
        """Creates the coefficient matrix for the Bezier curve interpolation"""
        C = np.zeros((self.n, self.n))

        for i in range(self.n):
            r = i + 1 if i + 1 < self.n else (i + 1) % self.n
            row = np.zeros(self.n)
            row[i], row[r] = 1, 2
            C[i] = row

        self.C = C

    def __create_endpoint_vector(self) -> None:
        """Creates the column vector which contains the end points of each curve connecting two points"""
        P = np.zeros((self.n, 2))

        for i in range(self.n):
            l = i + 1 if i + 1 < self.n else (i + 1) % self.n
            r = i + 2 if i + 2 < self.n else (i + 2) % self.n

            val = 2 * self.points[l] + self.points[r]
            P[i] = val

        self.P = P

    def __find_control_points(self) -> None:
        """Find the control points for the Bezier curve"""
        A = np.linalg.solve(self.C, self.P)
        B = np.zeros_like(A)

        for i in range(self.n):
            l = i + 1 if i + 1 < self.n else (i + 1) % self.n
            B[i] = 2 * self.points[l] - A[l]

        self.A = A
        self.B = B

    def find_points(self) -> None:
        """Finds the points on the smooth curve"""
        self.__create_coefficient_matrix()
        self.__create_endpoint_vector()
        self.__find_control_points()

        all_points = []

        for i in range(self.n):
            next_i = i + 1 if i + 1 < self.n else (i + 1) % self.n
            dpts = np.linspace(0, 1, self.curve_points_number)
            for j in dpts:
                pt = np.power(1 - j, 3) * self.points[i] + 3 * j * np.power(1 - j, 2) * self.A[i] + 3 * (
                        1 - j) * np.power(j, 2) * self.B[i] + np.power(j, 3) * self.points[next_i]
                all_points.append(pt.tolist())

        self.curve_points = np.array(all_points)

    def get_points(self) -> Curve:
        """Return the points on the curve. If they haven't been computed, compute them"""
        if self.curve_points is None:
            self.find_points()

        return self.curve_points
