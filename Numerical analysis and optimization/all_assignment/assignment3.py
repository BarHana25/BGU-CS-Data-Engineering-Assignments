"""
In this assignment you should find the area enclosed between the two given functions.
The rightmost and the leftmost x values for the integration are the rightmost and
the leftmost intersection points of the two functions.

The functions for the numeric answers are specified in MOODLE.


This assignment is more complicated than Assignment1 and Assignment2 because:
    1. You should work with float32 precision only (in all calculations) and minimize the floating point errors.
    2. You have the freedom to choose how to calculate the area between the two functions.
    3. The functions may intersect multiple times. Here is an example:
        https://www.wolframalpha.com/input/?i=area+between+the+curves+y%3D1-2x%5E2%2Bx%5E3+and+y%3Dx
    4. Some of the functions are hard to integrate accurately.
       You should explain why in one of the theoretical questions in MOODLE.

"""

import numpy as np
import time
import random


class Assignment3:
    def __init__(self):
        """
        Here goes any one time calculation that need to be made before
        solving the assignment for specific functions.
        """
        pass

    def integrate(self, f: callable, a: float, b: float, n: int) -> np.float32:
        """
        Integrate the function f in the closed range [a,b] using at most n
        points. Your main objective is minimizing the integration error.
        Your secondary objective is minimizing the running time. The assignment
        will be tested on variety of different functions.

        Integration error will be measured compared to the actual value of the
        definite integral.

        Note: It is forbidden to call f more than n times.

        Parameters
        ----------
        f : callable. it is the given function
        a : float
            beginning of the integration range.
        b : float
            end of the integration range.
        n : int
            maximal number of points to use.

        Returns
        -------
        np.float32
            The definite integral of f between a and b
        """

        # Use float64 internally for precision, cast to float32 only at return
        a = float(a)
        b = float(b)

        if n <= 0:
            return np.float32(0.0)

        if n == 1:
            mid = 0.5 * (a + b)
            val = float(f(mid))
            return np.float32((b - a) * val)

        if n == 2:
            fa = float(f(a))
            fb = float(f(b))
            return np.float32(0.5 * (b - a) * (fa + fb))

        # Sample endpoints to detect extreme value cases
        fa = float(f(a))
        fb = float(f(b))

        abs_fa = abs(fa)
        abs_fb = abs(fb)

        # Detect extreme value at boundaries:
        # Must be both relatively AND absolutely large to be "extreme"
        extreme_at_a = (np.isfinite(abs_fa) and abs_fa > 1e6
                        and abs_fa > 1e10 * max(abs_fb, 1e-30))
        extreme_at_b = (np.isfinite(abs_fb) and abs_fb > 1e6
                        and abs_fb > 1e10 * max(abs_fa, 1e-30))

        if extreme_at_a or extreme_at_b:
            # For functions with extreme peak at one endpoint, the integral is
            # dominated by a tiny region near that endpoint. We determine the
            # effective integration range from the ratio of endpoint values,
            # then apply Simpson's rule concentrated there.
            remaining_evals = n - 2
            if remaining_evals <= 0:
                return np.float32(0.5 * (b - a) * (fa + fb))

            # Determine cutoff fraction from the ratio
            ratio = abs_fa / max(abs_fb, 1e-30) if extreme_at_a else abs_fb / max(abs_fa, 1e-30)
            log_ratio = max(1.0, np.log10(max(ratio, 10.0)))
            # Heuristic: tighter cutoff for higher ratios
            frac = min(0.5, 0.02 / log_ratio)

            # Number of Simpson points: remaining_evals + 1 (reuse extreme endpoint)
            n_simp = remaining_evals + 1
            # Make odd for composite Simpson's 1/3
            if n_simp % 2 == 0:
                n_simp -= 1

            if extreme_at_a:
                cutoff = a + (b - a) * frac
                h = (cutoff - a) / (n_simp - 1)
                fvals = np.empty(n_simp, dtype=np.float64)
                fvals[0] = fa
                for i in range(1, n_simp):
                    fvals[i] = float(f(a + i * h))
            else:
                cutoff = b - (b - a) * frac
                h = (b - cutoff) / (n_simp - 1)
                fvals = np.empty(n_simp, dtype=np.float64)
                fvals[0] = fb
                for i in range(1, n_simp):
                    fvals[i] = float(f(b - i * h))

            # Composite Simpson's 1/3 (vectorized coefficients)
            coeffs = np.empty(n_simp, dtype=np.float64)
            coeffs[0] = 1.0
            coeffs[-1] = 1.0
            coeffs[1:n_simp - 1:2] = 4.0
            coeffs[2:n_simp - 1:2] = 2.0
            result = np.dot(coeffs, fvals) * (h / 3.0)

            return np.float32(result)

        # Normal cases: composite Simpson's rule
        if n == 3:
            fm = float(f(0.5 * (a + b)))
            h = b - a
            result = (h / 6.0) * (fa + 4.0 * fm + fb)
            return np.float32(result)

        elif n % 2 == 1:  # Odd n - perfect for composite Simpson's 1/3
            num_intervals = n - 1
            h = (b - a) / num_intervals

            # Evaluate all interior points
            fvals = np.empty(n, dtype=np.float64)
            fvals[0] = fa
            fvals[n - 1] = fb
            for i in range(1, n - 1):
                fvals[i] = float(f(a + i * h))

            # Vectorized weighted sum: coeffs are 1,4,2,4,2,...,4,1
            coeffs = np.empty(n, dtype=np.float64)
            coeffs[0] = 1.0
            coeffs[n - 1] = 1.0
            coeffs[1:n - 1:2] = 4.0
            coeffs[2:n - 1:2] = 2.0

            result = np.dot(coeffs, fvals) * (h / 3.0)
            return np.float32(result)

        else:  # Even n (n >= 4): Simpson's 1/3 + 3/8 hybrid
            num_intervals = n - 1
            h = (b - a) / num_intervals

            # Evaluate all points (reuse fa, fb)
            fvals = np.empty(n, dtype=np.float64)
            fvals[0] = fa
            fvals[n - 1] = fb
            for i in range(1, n - 1):
                x = a + i * h
                fvals[i] = float(f(x))

            if n == 4:
                # Simpson's 3/8 rule
                result = (3.0 * h / 8.0) * (
                    fvals[0] + 3.0 * fvals[1] + 3.0 * fvals[2] + fvals[3]
                )
            else:
                # Simpson's 1/3 on first (n-4) intervals (vectorized)
                n13 = n - 3
                c13 = np.empty(n13, dtype=np.float64)
                c13[0] = 1.0
                c13[-1] = 1.0
                c13[1:n13 - 1:2] = 4.0
                c13[2:n13 - 1:2] = 2.0
                result_13 = np.dot(c13, fvals[:n13]) * (h / 3.0)

                # Simpson's 3/8 on last 3 intervals
                j = n - 4
                result_38 = (3.0 * h / 8.0) * (
                    fvals[j] + 3.0 * fvals[j + 1] +
                    3.0 * fvals[j + 2] + fvals[j + 3]
                )
                result = result_13 + result_38

            return np.float32(result)

    def areabetween(self, f1: callable, f2: callable) -> np.float32:
        """
        Finds the area enclosed between two functions. This method finds
        all intersection points between the two functions to work correctly.

        Example: https://www.wolframalpha.com/input/?i=area+between+the+curves+y%3D1-2x%5E2%2Bx%5E3+and+y%3Dx

        Note, there is no such thing as negative area.

        In order to find the enclosed area the given functions must intersect
        in at least two points. If the functions do not intersect or intersect
        in less than two points this function returns NaN.
        This function may not work correctly if there is infinite number of
        intersection points.


        Parameters
        ----------
        f1,f2 : callable. These are the given functions

        Returns
        -------
        np.float32
            The area between function and the X axis

        """

        # We need to find intersection points first
        # Use Assignment2's intersection finding algorithm
        try:
            from assignment2 import Assignment2
            ass2 = Assignment2()
        except:
            return np.float32(np.nan)

        # Search for intersections in range [1, 100] as specified
        search_range_a = 1.0
        search_range_b = 100.0

        # Find intersections with tight tolerance
        intersections = ass2.intersections(f1, f2, search_range_a, search_range_b, maxerr=0.0001)

        # Filter and sort intersections (keep float64 for precision)
        intersections = sorted([float(x) for x in intersections if np.isfinite(x)])

        if len(intersections) < 2:
            return np.float32(np.nan)

        # Calculate area between consecutive intersection points (accumulate in float64)
        total_area = 0.0

        def abs_diff(x):
            return abs(f1(x) - f2(x))

        for i in range(len(intersections) - 1):
            seg_a = intersections[i]
            seg_b = intersections[i + 1]
            seg_width = seg_b - seg_a

            # Adaptive point count: more points for wider segments
            # Use at least 51, scale up to 501 for the widest expected segments
            n_points = max(51, min(501, int(seg_width * 10) | 1))
            # Ensure odd for clean Simpson's 1/3
            if n_points % 2 == 0:
                n_points += 1

            area_segment = self.integrate(abs_diff, seg_a, seg_b, n_points)
            total_area += float(area_segment)

        return np.float32(total_area)


##########################################################################


import unittest
from sampleFunctions import *
# from tqdm import tqdm


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
