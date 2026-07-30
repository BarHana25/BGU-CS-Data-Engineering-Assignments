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
        """
        Find all intersection points of f1 and f2 in the interval [a, b].

        Approach:
        1) Define g(x) = f1(x) - f2(x), so intersections are roots of g.
        2) Adaptive grid search with increasing resolution.
        3) Detect sign changes (bracket roots) and local minima (tangent roots).
        4) Refine each candidate using bisection/Newton hybrid.
        5) Early stopping when no new roots found in consecutive passes.

        Parameters
        ----------
        f1, f2 : callable
            The two functions to intersect.
        a, b : float
            The interval endpoints.
        maxerr : float
            Maximum allowed error for root verification.

        Returns
        -------
        Iterable of float
            The x-coordinates of intersection points.
        """
        def g(x):
            return f1(x) - f2(x)

        if b < a:
            a, b = b, a

        roots = []

        def add_root_if_new(xr, tol=None):
            if tol is None:
                tol = 5 * maxerr  # Tolerance on x-axis to avoid duplicate roots
            for r in roots:
                if abs(r - xr) <= tol:
                    return
            roots.append(float(xr))

        # --- Adaptive parameters ---
        N = 200
        Nmax = 20000
        max_passes = 6

        prev_root_count = 0
        no_new_roots_passes = 0

        for pass_num in range(max_passes):
            xs = np.linspace(a, b, N + 1, dtype=np.float64)
            gs = np.array([g(float(x)) for x in xs], dtype=np.float64)

            # 1) Sign changes: safe bracketing
            # Vectorized sign change detection
            signs = np.sign(gs)
            sign_changes = np.where((signs[:-1] * signs[1:] < 0) | (gs[:-1] == 0) | (gs[1:] == 0))[0]

            for i in sign_changes:
                g0, g1 = gs[i], gs[i + 1]
                if g0 == 0.0:
                    add_root_if_new(xs[i])
                    continue
                if g0 * g1 < 0.0 or g1 == 0.0:
                    left, right = float(xs[i]), float(xs[i + 1])
                    r = self._refine_root(g, left, right, maxerr)
                    if r is not None and abs(g(r)) <= maxerr:
                        add_root_if_new(r)

            # 2) Tangent roots: local minima of |g| (no sign change)
            abs_g = np.abs(gs)
            # Vectorized local minima detection
            is_local_min = (abs_g[1:-1] <= abs_g[:-2]) & (abs_g[1:-1] <= abs_g[2:]) & (abs_g[1:-1] <= 5 * maxerr)
            local_min_indices = np.where(is_local_min)[0] + 1

            for i in local_min_indices:
                x0 = float(xs[i])
                # Try to find a bracket with sign change around x0
                br = self._bracket_around(g, x0, a, b, max_expand=30)
                if br is not None:
                    left, right = br
                    r = self._refine_root(g, left, right, maxerr)
                    if r is not None and abs(g(r)) <= maxerr:
                        add_root_if_new(r)
                else:
                    # No sign change around it: still accept if very close to zero
                    if abs(g(x0)) <= maxerr:
                        add_root_if_new(x0)

            # Early stopping: if no new roots found in 2 consecutive passes, stop
            if len(roots) == prev_root_count:
                no_new_roots_passes += 1
                if no_new_roots_passes >= 2 and pass_num >= 1:
                    break
            else:
                no_new_roots_passes = 0
            prev_root_count = len(roots)

            # Stop if we seem done: found many roots or N is large
            if N >= Nmax or len(roots) > 200:
                break

            # Increase resolution for next pass
            N *= 2

        roots.sort()
        return roots

    def _bracket_around(self, g, x0, a, b, max_expand=30):
        """
        Try to find [L, R] around x0 such that g(L)*g(R) <= 0.
        If not found (true tangent), returns None.
        """
        gx0 = g(x0)
        # Already a root
        if abs(gx0) == 0.0:
            return (x0, x0)

        span = (b - a)
        # Initial relative step size
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
        Refine a root within [left, right] using a hybrid approach:
        - Safe bisection (when bracket exists)
        - Secant method acceleration when stable
        """
        gl = g(left)
        gr = g(right)

        if abs(gl) <= delta:
            return left
        if abs(gr) <= delta:
            return right

        # No true bracket, no guarantee
        if gl * gr > 0.0:
            return None

        x0, x1 = left, right
        f0, f1 = gl, gr

        for _ in range(max_iter):
            # Try secant method if stable
            denom = (f1 - f0)
            if denom != 0.0:
                x2 = x1 - f1 * (x1 - x0) / denom
                if left <= x2 <= right:
                    f2 = g(x2)
                    if abs(f2) <= delta:
                        return x2
                    # Update bracket
                    if f0 * f2 < 0.0:
                        x1, f1 = x2, f2
                    else:
                        x0, f0 = x2, f2
                    continue

            # Fallback to bisection
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
