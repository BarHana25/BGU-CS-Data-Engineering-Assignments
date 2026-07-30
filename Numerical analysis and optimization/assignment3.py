"""
Assignment 3 - Area Between Two Functions (float32 only)

Goal:
- Compute the area enclosed between two functions f1 and f2.
- The area is computed between consecutive intersection points.
- Must use float32 arithmetic throughout to reduce floating-point drift
  under the assignment constraints.

Main challenges addressed:
1) Functions may intersect multiple times -> need to find all intersections.
2) Integrals can be hard due to oscillations / singular behavior near 0.
3) Must not call f more than n times in integrate().
4) Need stable numeric integration in float32.

Key ideas used:
- Composite Simpson's rule for accuracy on smooth-ish regions.
- If interval is positive and near zero, apply the substitution u = 1/x
  to handle "strong oscillations" / rapid changes near x=0.
"""

import numpy as np
import time
import random  # (Currently unused)

from assignment2 import Assignment2


class Assignment3:
    def __init__(self):
        """
        Initialization hook.
        You can place one-time precomputations here if needed.
        This implementation uses no precomputation.
        """
        pass

    # ============================================================
    # Stage 1: Simpson Integration on a Uniform Parameter Grid
    # ============================================================
    @staticmethod
    def _simpson_on_param(y: np.ndarray) -> np.float32:
        """
        Apply composite Simpson's rule on a *uniform* parameter grid s in [0,1],
        given samples y = integrand(s_i) at equally spaced points.

        Important details:
        - Simpson requires an odd number of samples (even number of subintervals).
        - If n is even, we do Simpson on the first n-1 samples and a trapezoid
          rule on the last interval (common practical fallback).

        Parameters
        ----------
        y : np.ndarray (float32 recommended)
            Values of integrand sampled on uniform grid in s.

        Returns
        -------
        np.float32
            Approximation of integral over s in [0,1].
        """
        n = int(y.size)
        if n < 2:
            return np.float32(0.0)

        # step size in parameter s-domain
        h = np.float32(1.0) / np.float32(n - 1)

        # n == 2 -> single trapezoid
        if n == 2:
            return np.float32(h * np.float32(0.5) * (y[0] + y[1]))

        # Odd number of points -> pure Simpson
        if (n % 2) == 1:
            odd = y[1:-1:2]   # coefficients 4
            even = y[2:-1:2]  # coefficients 2
            return np.float32((h / np.float32(3.0)) * (
                y[0] + y[-1] +
                np.float32(4.0) * np.sum(odd, dtype=np.float32) +
                np.float32(2.0) * np.sum(even, dtype=np.float32)
            ))
        else:
            # Even n: Simpson on first n-1, trapezoid on last interval
            y1 = y[:-1]
            odd = y1[1:-1:2]
            even = y1[2:-1:2]

            simpson = (h / np.float32(3.0)) * (
                y1[0] + y1[-1] +
                np.float32(4.0) * np.sum(odd, dtype=np.float32) +
                np.float32(2.0) * np.sum(even, dtype=np.float32)
            )

            trap_last = h * np.float32(0.5) * (y[-2] + y[-1])
            return np.float32(simpson + trap_last)

    # ============================================================
    # Stage 2: integrate(f, a, b, n) - Numeric Integration (≤ n calls)
    # ============================================================
    def integrate(self, f: callable, a: float, b: float, n: int) -> np.float32:
        """
        Integrate f over [a,b] using at most n evaluations of f.

        Strategy:
        1) Handle edge cases (n too small, reversed bounds, etc.).
        2) Special-case "hard oscillations near 0" for positive intervals:
           Use substitution u = 1/x to cluster sampling near x ~ 0.
           This transforms the integral to a more numerically stable form.
        3) Otherwise, use standard composite Simpson on uniform x grid.

        Constraint:
        - It is forbidden to call f more than n times.
          This implementation calls f exactly n times in each branch.

        Returns:
        - np.float32 result
        """
        a = np.float32(a)
        b = np.float32(b)
        n = int(n)

        # trivial cases
        if n <= 0 or a == b:
            return np.float32(0.0)

        # if bounds reversed, flip and negate
        if b < a:
            return np.float32(-1.0) * self.integrate(f, float(b), float(a), n)

        # with one sample you cannot do meaningful integration -> 0
        if n == 1:
            return np.float32(0.0)

        # ------------------------------------------------------------
        # Stage 2A: Special Transform for "hard oscillations" cases
        # ------------------------------------------------------------
        # Heuristic trigger:
        # - interval is strictly positive
        # - a is near 0 (where oscillations / singularity is problematic)
        # - b/a is large enough (wide range)
        # - n is not tiny (need enough points to benefit)
        #
        # Substitution:
        #   u = 1/x  =>  x = 1/u,  dx = -1/u^2 du
        #
        # We integrate over u in [1/a, 1/b] but we want positive orientation,
        # so we build u(s) mapping from s in [0,1].
        if (a > np.float32(0.0)) and (b > np.float32(0.0)) and (a < np.float32(0.5)) \
           and (float(b / a) > 2.0) and (n >= 6):

            ua = np.float32(1.0) / a  # u at left endpoint (x=a)
            ub = np.float32(1.0) / b  # u at right endpoint (x=b)

            # We want to cluster points near ua (which corresponds to x near a),
            # because that's typically where the function is hardest.
            p = np.float32(6.0)  # clustering exponent

            # uniform parameter samples s in [0,1]
            s = np.linspace(np.float32(0.0), np.float32(1.0), n, dtype=np.float32)

            # define u(s) with clustering:
            # u(s) = ub + (ua-ub)*(1 - (1-s)^p)
            one_minus_s = np.float32(1.0) - s
            u = ub + (ua - ub) * (np.float32(1.0) - np.power(one_minus_s, p, dtype=np.float32))

            # derivative du/ds:
            # du/ds = (ua-ub)*p*(1-s)^(p-1)
            dud_s = (ua - ub) * p * np.power(one_minus_s, p - np.float32(1.0), dtype=np.float32)

            # Build transformed integrand in s:
            # Original: ∫ f(x) dx
            # With x=1/u and dx = (1/u^2) du (sign handled by limits/mapping)
            # So integrand(s) = f(1/u(s)) * (1/u(s)^2) * du/ds
            y = np.empty(n, dtype=np.float32)
            for i in range(n):
                ui = u[i]
                xi = np.float32(1.0) / ui
                fx = np.float32(f(float(xi)))  # EXACTLY n calls in this branch
                y[i] = fx * (np.float32(1.0) / (ui * ui)) * dud_s[i]

            # integrate over s in [0,1] using Simpson on uniform parameter grid
            return self._simpson_on_param(y)

        # ------------------------------------------------------------
        # Stage 2B: Default Integration - Composite Simpson on uniform x
        # ------------------------------------------------------------
        xs = np.linspace(a, b, n, dtype=np.float32)
        ys = np.empty(n, dtype=np.float32)

        # EXACTLY n calls in this branch
        for i in range(n):
            ys[i] = np.float32(f(float(xs[i])))

        h = (b - a) / np.float32(n - 1)

        # n == 2 -> trapezoid
        if n == 2:
            return np.float32(h * np.float32(0.5) * (ys[0] + ys[1]))

        # Odd n -> Simpson
        if (n % 2) == 1:
            odd = ys[1:-1:2]
            even = ys[2:-1:2]
            res = (h / np.float32(3.0)) * (
                ys[0] + ys[-1] +
                np.float32(4.0) * np.sum(odd, dtype=np.float32) +
                np.float32(2.0) * np.sum(even, dtype=np.float32)
            )
            return np.float32(res)
        else:
            # Even n: Simpson on first n-1 + trapezoid on last interval
            ys1 = ys[:-1]
            odd = ys1[1:-1:2]
            even = ys1[2:-1:2]

            simpson = (h / np.float32(3.0)) * (
                ys1[0] + ys1[-1] +
                np.float32(4.0) * np.sum(odd, dtype=np.float32) +
                np.float32(2.0) * np.sum(even, dtype=np.float32)
            )
            trap_last = h * np.float32(0.5) * (ys[-2] + ys[-1])
            return np.float32(simpson + trap_last)

    # ============================================================
    # Stage 3: areabetween(f1, f2) - Area Between Two Curves
    # ============================================================
    def areabetween(self, f1: callable, f2: callable) -> np.float32:
        """
        Compute the enclosed area between f1 and f2.

        High-level approach:
        1) Find intersection points of f1 and f2 using Assignment2.intersections().
        2) Sort intersection x-values and merge near-duplicates (numerical noise).
        3) For each consecutive pair [x_i, x_{i+1}], integrate |f1(x)-f2(x)|.
        4) Sum contributions. Area is always non-negative.

        If fewer than 2 intersections exist, return NaN (no closed area).
        """
        # Search interval for intersections (problem-specific heuristic)
        a0 = np.float32(1.0)
        b0 = np.float32(100.0)

        ass2 = np.float32(Assignment2())

        # Find all intersections in [a0,b0]
        xs = list(ass2.intersections(f1, f2, float(a0), float(b0), maxerr=0.001))

        # Need at least two intersection points for a bounded area
        if len(xs) < 2:
            return np.float32(np.nan)

        xs = np.array(sorted(xs), dtype=np.float32)

        # Merge near-duplicate intersections caused by numerical errors
        merged = [xs[0]]
        tol = np.float32(1e-4)
        for x in xs[1:]:
            if np.abs(x - merged[-1]) > tol:
                merged.append(x)
        xs = np.array(merged, dtype=np.float32)

        if xs.size < 2:
            return np.float32(np.nan)

        # Define integrand = |f1 - f2| (area between curves on each interval)
        def absdiff(x: float) -> float:
            xx = np.float32(x)
            return float(np.abs(np.float32(f1(float(xx)) - f2(float(xx)))))

        # Integrate |f1-f2| on each sub-interval between consecutive intersections
        area = np.float32(0.0)
        for i in range(xs.size - 1):
            left = float(xs[i])
            right = float(xs[i + 1])
            if right <= left:
                continue

            # Use fixed n=80 points per interval (tradeoff accuracy/time)
            area = np.float32(area + self.integrate(absdiff, left, right, 80))

        return np.float32(area)


##########################################################################
# Unit Tests (local testing only; usually not submitted to the grader)
##########################################################################

import unittest
from sampleFunctions import *
from tqdm import tqdm


class TestAssignment3(unittest.TestCase):

    def test_integrate_float32(self):
        ass3 = Assignment3()
        f1 = np.poly1d([-1, 0, 1])
        r = ass3.integrate(f1, -1, 1, 10)
        self.assertEqual(r.dtype, np.float32)

    def test_integrate_hard_case(self):
        ass3 = Assignment3()
        f1 = strong_oscilations()
        r = ass3.integrate(f1, 0.09, 10, 20)
        true_result = -7.78662 * 10 ** 33
        self.assertGreaterEqual(0.001, abs((r - true_result) / true_result))


if __name__ == "__main__":
    unittest.main()
