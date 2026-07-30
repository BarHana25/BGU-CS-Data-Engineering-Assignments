"""
In this assignment you should find the intersection points for two functions.
"""

import numpy as np
import time
import random
from collections.abc import Iterable


class Assignment2:
    def __init__(self):
        """
        Here goes any one time calculation that need to be made before
        solving the assignment for specific functions.
        """

        pass

    def intersections(self, f1: callable, f2: callable, a: float, b: float, maxerr=0.001) -> Iterable:
        def g(x):
            return f1(x) - f2(x)

        if b < a:
            a, b = b, a

        roots = []

        def add_root_if_new(xr, tol=None):
            if tol is None:
                tol = 5 * maxerr  # טולרנס על ציר x כדי לא להכפיל שורשים
            for r in roots:
                if abs(r - xr) <= tol:
                    return
            roots.append(float(xr))

        # --- פרמטרים אדפטיביים ---
        N = 200
        Nmax = 20000
        max_passes = 6

        for _ in range(max_passes):
            xs = np.linspace(a, b, N + 1, dtype=np.float64)
            gs = np.array([g(float(x)) for x in xs], dtype=np.float64)

            # 1) שינויי סימן: ברקט בטוח
            for i in range(N):
                g0, g1 = gs[i], gs[i + 1]
                if g0 == 0.0:
                    add_root_if_new(xs[i])
                    continue
                if g0 * g1 < 0.0 or g1 == 0.0:
                    left, right = float(xs[i]), float(xs[i + 1])
                    r = self._refine_root(g, left, right, maxerr)
                    if r is not None and abs(g(r)) <= maxerr:
                        add_root_if_new(r)

            # 2) שורשים משיקים: מינימום מקומי של |g| (בלי שינוי סימן)
            abs_g = np.abs(gs)
            # אינדקסים שהם מינימום מקומי (i-1 > i < i+1)
            for i in range(1, N):
                if abs_g[i] <= abs_g[i - 1] and abs_g[i] <= abs_g[i + 1]:
                    if abs_g[i] <= 5 * maxerr:  # מועמד חזק
                        x0 = float(xs[i])
                        # ננסה למצוא ברקט עם שינוי סימן סביב x0
                        br = self._bracket_around(g, x0, a, b, max_expand=30)
                        if br is not None:
                            left, right = br
                            r = self._refine_root(g, left, right, maxerr)
                            if r is not None and abs(g(r)) <= maxerr:
                                add_root_if_new(r)
                        else:
                            # אין שינוי סימן סביבו: עדיין אפשר לקבל נקודת חיתוך אם ממש קרוב לאפס
                            if abs(g(x0)) <= maxerr:
                                add_root_if_new(x0)

            # עצירה אם נראה שמיצינו: אם כבר מצאנו הרבה או N גדול
            if N >= Nmax or len(roots) > 200:
                break

            # הגדלת רזולוציה לסיבוב הבא
            N *= 2

        roots.sort()
        return roots

    def _bracket_around(self, g, x0, a, b, max_expand=30):
        """
        מנסה למצוא [L,R] סביב x0 כך ש-g(L)*g(R) <= 0.
        אם לא נמצא (למשיק אמיתי), מחזיר None.
        """
        gx0 = g(x0)
        # אם כבר "שורש"
        if abs(gx0) == 0.0:
            return (x0, x0)

        span = (b - a)
        # צעד התחלתי יחסי
        step = span / 2000.0 if span > 0 else 1e-3
        step = max(step, 1e-6)

        left = x0
        right = x0
        gl = gx0
        gr = gx0

        for k in range(1, max_expand + 1):
            left = max(a, x0 - k * step)
            right = min(b, x0 + k * step)
            gl = g(left)
            gr = g(right)
            if gl == 0.0:
                return (left, left)
            if gr == 0.0:
                return (right, right)
            if gl * gr < 0.0:
                return (left, right)

        return None

    def _refine_root(self, g, left, right, delta, max_iter=60):
        """
        ליטוש שורש בתוך [left,right] ע"י שילוב:
        - חצייה בטוחה (אם יש bracket)
        - ניסיון סיקנט פנימי כשאפשר (מזרז)
        """
        gl = g(left)
        gr = g(right)

        if abs(gl) <= delta:
            return left
        if abs(gr) <= delta:
            return right

        # אם אין bracket אמיתי, אין הבטחה
        if gl * gr > 0.0:
            return None

        x0, x1 = left, right
        f0, f1 = gl, gr

        for _ in range(max_iter):
            # ניסיון סיקנט אם יציב
            denom = (f1 - f0)
            if denom != 0.0:
                x2 = x1 - f1 * (x1 - x0) / denom
                if left <= x2 <= right:
                    f2 = g(x2)
                    if abs(f2) <= delta:
                        return x2
                    # עדכון bracket
                    if f0 * f2 < 0.0:
                        x1, f1 = x2, f2
                    else:
                        x0, f0 = x2, f2
                    continue

            # fallback חצייה
            mid = 0.5 * (x0 + x1)
            fm = g(mid)
            if abs(fm) <= delta:
                return mid
            if f0 * fm < 0.0:
                x1, f1 = mid, fm
            else:
                x0, f0 = mid, fm

            if abs(x1 - x0) <= 2 * delta:
                return 0.5 * (x0 + x1)

        return 0.5 * (x0 + x1)



##########################################################################


import unittest
from sampleFunctions import *
from tqdm import tqdm


class TestAssignment2(unittest.TestCase):

    def test_sqr(self):

        ass2 = Assignment2()

        f1 = np.poly1d([-1, 0, 1])
        f2 = np.poly1d([1, 0, -1])

        X = ass2.intersections(f1, f2, -1, 1, maxerr=0.001)

        for x in X:
            self.assertGreaterEqual(0.001, abs(f1(x) - f2(x)))

    def test_poly(self):

        ass2 = Assignment2()

        f1, f2 = randomIntersectingPolynomials(10)

        X = ass2.intersections(f1, f2, -1, 1, maxerr=0.001)

        for x in X:
            self.assertGreaterEqual(0.001, abs(f1(x) - f2(x)))


if __name__ == "__main__":
    unittest.main()
