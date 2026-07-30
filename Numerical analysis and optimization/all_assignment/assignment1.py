"""
Assignment 1 - Function Interpolation

Goal:
- Interpolate a function f on the interval [a, b] using at most n function evaluations.
- Return a callable g(x) that approximates f(x) on the interval.

Approach:
1) Sample f at Chebyshev-Lobatto nodes (reduces Runge phenomenon).
2) Apply automatic y-transform (identity / log / loglog / asinh) to handle large dynamic ranges.
3) Build a natural cubic spline on the transformed values.
4) Evaluate by inverting the transform on the spline output.

Constraints:
- Must call f at most n times.
- No forbidden functions (np.linalg.solve, polyfit, interpolate, etc.).
"""

import numpy as np
import time
import random


class Assignment1:
    def __init__(self):
        pass

    def interpolate(self, f: callable, a: float, b: float, n: int) -> callable:
        """
        Interpolate f on [a,b] using at most n calls to f.
        Approach:
        - Sample at Chebyshev–Lobatto nodes (good accuracy, less oscillation).
        - Apply an automatic y-transform (identity / log / loglog / asinh) to stabilize huge dynamic ranges.
        - Build a natural cubic spline on the transformed values (O(n)).
        - Evaluate spline in transformed space and invert back.
        """

        # -------------------------
        # 1) Edge cases
        # -------------------------
        if n <= 0:
            return lambda x: float("nan")

        if n == 1:
            y0 = float(f(float(a)))
            return lambda x, y0=y0: y0

        if n == 2:
            x0, x1 = float(a), float(b)
            y0, y1 = float(f(x0)), float(f(x1))
            dx = x1 - x0 if x1 != x0 else 1.0
            m = (y1 - y0) / dx

            def g(x, x0=x0, x1=x1, y0=y0, y1=y1, m=m):
                x = float(x)
                if x <= x0:
                    return y0
                if x >= x1:
                    return y1
                return y0 + m * (x - x0)

            return g

        # -------------------------
        # 2) Chebyshev–Lobatto nodes (in increasing order)
        # -------------------------
        k = np.arange(n - 1, -1, -1, dtype=float)
        t = np.cos(np.pi * k / (n - 1))  # increasing from -1 to 1
        xs = (a + b) * 0.5 + (b - a) * 0.5 * t

        # Ensure strictly increasing (avoid zero-length intervals)
        for i in range(1, n):
            if xs[i] <= xs[i - 1]:
                xs[i] = np.nextafter(xs[i - 1], np.inf)

        # -------------------------
        # 3) Sample f exactly n times
        # -------------------------
        ys = np.empty(n, dtype=float)
        for i in range(n):
            ys[i] = float(f(float(xs[i])))

        # -------------------------
        # 4) Choose a stable transform for y-values
        # -------------------------
        def forward(y):
            return y

        def inverse(tval):
            return tval

        ys_finite = np.isfinite(ys)
        if np.all(ys_finite) and np.all(ys > 0):
            y_min = float(np.min(ys))
            y_max = float(np.max(ys))
            y_ratio = y_max / y_min if y_min > 0 else 1.0

            # Check if log values are all positive (needed for log-log)
            logy = np.log(ys)
            logy_finite = np.all(np.isfinite(logy))

            if logy_finite and np.all(logy > 0):
                # Can try log-log transform
                loglogy = np.log(logy)
                span_y = y_max - y_min
                span_log = float(np.max(logy) - np.min(logy))
                span_loglog = float(np.max(loglogy) - np.min(loglogy))

                # Use log-log if it significantly compresses the range
                # This is critical for functions like e^(e^x)
                if span_loglog < 0.5 * span_log and span_log > 1.0:
                    def forward(y):
                        return np.log(np.log(y))

                    def inverse(tval):
                        return np.exp(np.exp(tval))
                elif y_ratio > 10 or span_log > 2.0:
                    # Use single log for moderate dynamic range
                    def forward(y):
                        return np.log(y)

                    def inverse(tval):
                        return np.exp(tval)

            elif logy_finite and y_ratio > 10:
                # Use single log for positive values with moderate range
                def forward(y):
                    return np.log(y)

                def inverse(tval):
                    return np.exp(tval)

        elif np.all(ys_finite):
            # Handle mixed signs or zeros with asinh
            abs_max = float(np.max(np.abs(ys)))
            if abs_max > 1e6:
                s = float(np.median(np.abs(ys)))
                if (not np.isfinite(s)) or s <= 0:
                    s = 1.0

                def forward(y, s=s):
                    return np.arcsinh(y / s)

                def inverse(tval, s=s):
                    return s * np.sinh(tval)

        # Transform samples for spline construction
        ts = forward(ys)

        # Interval lengths
        h = np.diff(xs)

        # -------------------------
        # 5) Natural cubic spline in transformed space
        # -------------------------
        m = n - 2  # unknowns M[1..n-2]
        a_sub = np.empty(m - 1, dtype=float) if m > 1 else np.empty(0, dtype=float)
        b_main = np.empty(m, dtype=float)
        c_sup = np.empty(m - 1, dtype=float) if m > 1 else np.empty(0, dtype=float)
        d_rhs = np.empty(m, dtype=float)

        for i in range(1, n - 1):
            r = i - 1
            hi_1 = h[i - 1]
            hi = h[i]

            b_main[r] = 2.0 * (hi_1 + hi)
            if m > 1:
                if r - 1 >= 0:
                    a_sub[r - 1] = hi_1
                if r <= m - 2:
                    c_sup[r] = hi

            # IMPORTANT: RHS uses transformed values ts
            d_rhs[r] = 6.0 * ((ts[i + 1] - ts[i]) / hi - (ts[i] - ts[i - 1]) / hi_1)

        # -------------------------
        # 6) Solve tridiagonal system (Thomas) for M_inner
        # -------------------------
        if m == 0:
            # Shouldn't happen because n>=2, but keep safe
            def g(x):
                return float(inverse(ts[0]))
            return g

        if m == 1:
            # Single equation
            denom = b_main[0]
            if abs(denom) < 1e-30:
                # fallback to linear in ORIGINAL y
                x0, x1 = float(xs[0]), float(xs[-1])
                y0, y1 = float(ys[0]), float(ys[-1])
                dx = x1 - x0 if x1 != x0 else 1.0
                slope = (y1 - y0) / dx

                def lin(x, x0=x0, x1=x1, y0=y0, y1=y1, slope=slope):
                    x = float(x)
                    if x <= x0:
                        return y0
                    if x >= x1:
                        return y1
                    return y0 + slope * (x - x0)

                return lin

            M_inner = np.array([d_rhs[0] / denom], dtype=float)
        else:
            cp = np.empty_like(c_sup)
            dp = np.empty_like(d_rhs)

            inv0 = 1.0 / b_main[0]
            cp[0] = c_sup[0] * inv0
            dp[0] = d_rhs[0] * inv0

            for i in range(1, m):
                denom = b_main[i] - a_sub[i - 1] * cp[i - 1]
                if abs(denom) < 1e-30:
                    # fallback to linear in ORIGINAL y
                    x0, x1 = float(xs[0]), float(xs[-1])
                    y0, y1 = float(ys[0]), float(ys[-1])
                    dx = x1 - x0 if x1 != x0 else 1.0
                    slope = (y1 - y0) / dx

                    def lin(x, x0=x0, x1=x1, y0=y0, y1=y1, slope=slope):
                        x = float(x)
                        if x <= x0:
                            return y0
                        if x >= x1:
                            return y1
                        return y0 + slope * (x - x0)

                    return lin

                inv = 1.0 / denom
                if i < m - 1:
                    cp[i] = c_sup[i] * inv
                dp[i] = (d_rhs[i] - a_sub[i - 1] * dp[i - 1]) * inv

            M_inner = np.empty(m, dtype=float)
            M_inner[-1] = dp[-1]
            for i in range(m - 2, -1, -1):
                M_inner[i] = dp[i] - cp[i] * M_inner[i + 1]

        # Full second-derivatives array M with natural boundary conditions
        M = np.zeros(n, dtype=float)
        M[1:n - 1] = M_inner

        # -------------------------
        # 7) Precompute cubic coefficients on each interval in transformed space
        # -------------------------
        # S_i(x) = a_i + b_i*dx + c_i*dx^2 + d_i*dx^3  in "t-space"
        a_coef = ts[:-1].copy()
        b_coef = np.empty(n - 1, dtype=float)
        c_coef = 0.5 * M[:-1]
        d_coef = np.empty(n - 1, dtype=float)

        for i in range(n - 1):
            hi = h[i]
            Mi, Mi1 = M[i], M[i + 1]
            b_coef[i] = (ts[i + 1] - ts[i]) / hi - (hi / 6.0) * (2.0 * Mi + Mi1)
            d_coef[i] = (Mi1 - Mi) / (6.0 * hi)

        # -------------------------
        # 8) Evaluator: spline in t-space, then invert to y
        # -------------------------
        x_min = float(xs[0])
        x_max = float(xs[-1])
        last_dx = float(xs[-1] - xs[-2])

        def g(x, xs=xs, a=a_coef, b=b_coef, c=c_coef, d=d_coef,
              x_min=x_min, x_max=x_max, last_dx=last_dx, inverse=inverse):
            x = float(x)

            if x <= x_min:
                return float(inverse(a[0]))

            if x >= x_max:
                dx = last_dx
                s = a[-1] + b[-1] * dx + c[-1] * dx * dx + d[-1] * dx * dx * dx
                return float(inverse(s))

            i = int(np.searchsorted(xs, x) - 1)
            if i < 0:
                i = 0
            elif i >= len(a):
                i = len(a) - 1

            dx = x - xs[i]
            s = a[i] + b[i] * dx + c[i] * dx * dx + d[i] * dx * dx * dx
            return float(inverse(s))

        return g



##########################################################################


import unittest
from functionUtils import *
from tqdm import tqdm


class TestAssignment1(unittest.TestCase):

    def test_with_poly(self):
        T = time.time()

        ass1 = Assignment1()
        mean_err = 0

        d = 30
        for i in tqdm(range(100)):
            a = np.random.randn(d)

            f = np.poly1d(a)

            ff = ass1.interpolate(f, -10, 10, 100)

            xs = np.random.random(200)
            err = 0
            for x in xs:
                yy = ff(x)
                y = f(x)
                err += abs(y - yy)

            err = err / 200
            mean_err += err
        mean_err = mean_err / 100

        T = time.time() - T
        print(T)
        print(mean_err)

    def test_with_poly_restrict(self):
        ass1 = Assignment1()
        a = np.random.randn(5)
        f = RESTRICT_INVOCATIONS(10)(np.poly1d(a))
        ff = ass1.interpolate(f, -10, 10, 10)
        xs = np.random.random(20)
        for x in xs:
            yy = ff(x)

if __name__ == "__main__":
    unittest.main()
