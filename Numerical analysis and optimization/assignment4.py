"""
Assignment 4 - Function Fitting Under Noise and Time Constraints

Goal:
- Fit a model g(x) to noisy samples y = f(x) on the interval [a, b].
- Minimize approximation error (least-squares style) while obeying a strict runtime limit.
- Do NOT use numpy optimization / linear algebra solvers (np.linalg.* forbidden).

Key ideas used in this solution:
1) Polynomial least-squares fitting using normal equations.
2) Solving the linear system via custom Gaussian elimination (partial pivoting).
3) If the function is "extreme" (e.g., exp(exp(x))), switch to piecewise fitting:
   - Split [a,b] into many small segments.
   - On each segment, optionally apply repeated log transforms (log-log) to stabilize values.
   - Fit a low-degree polynomial on each segment and invert the transform at prediction time.
4) Sampling strategy under noise:
   - Always sample at many nodes.
   - If time allows, re-sample and average values to reduce noise.
"""

import numpy as np
import time
import random  # (Currently unused)


class Assignment4:
    def __init__(self):
        """
        Initialization hook.
        You can place one-time computations here if needed.
        For this implementation, nothing is precomputed.
        """
        pass

    # ============================================================
    # Stage 1: Linear System Solver (Gaussian Elimination)
    # ============================================================
    # We must solve least-squares normal equations without np.linalg.
    # This function solves A x = b using:
    # - Partial pivoting for numerical stability
    # - Forward elimination + back substitution
    def _gauss_solve(self, A: np.ndarray, b: np.ndarray) -> np.ndarray:
        # Work on copies to avoid modifying the original inputs
        A = np.asarray(A, dtype=float).copy()
        b = np.asarray(b, dtype=float).copy()
        n = A.shape[0]

        # Edge case: empty system
        if n == 0:
            return np.array([], dtype=float)

        # Forward elimination (convert A to upper triangular form)
        for i in range(n):
            # Choose pivot row: the row with maximal |A[row, i]| among rows i..n-1
            piv = i + int(np.argmax(np.abs(A[i:, i])))

            # If pivot is tiny or non-finite, system is ill-conditioned -> return zeros fallback
            if (not np.isfinite(A[piv, i])) or abs(A[piv, i]) < 1e-14:
                return np.zeros(n, dtype=float)

            # Swap current row with pivot row if needed
            if piv != i:
                A[[i, piv]] = A[[piv, i]]
                b[[i, piv]] = b[[piv, i]]

            # Eliminate entries below the pivot
            ai = A[i, i]
            for j in range(i + 1, n):
                factor = A[j, i] / ai
                if factor != 0.0:
                    A[j, i:] -= factor * A[i, i:]
                    b[j] -= factor * b[i]

        # Back substitution (solve upper triangular system)
        x = np.zeros(n, dtype=float)
        for i in range(n - 1, -1, -1):
            s = b[i] - float(np.dot(A[i, i + 1:], x[i + 1:]))
            x[i] = s / A[i, i]
        return x

    # ============================================================
    # Stage 2: Polynomial Evaluation (Horner)
    # ============================================================
    @staticmethod
    def _poly_eval(c: np.ndarray, t: float) -> float:
        """
        Evaluate polynomial with coefficients c at value t using Horner's rule.
        Coefficients are assumed in increasing order:
            p(t) = c[0] + c[1]*t + c[2]*t^2 + ...
        Horner reduces numerical error and is fast.
        """
        val = 0.0
        for ck in c[::-1]:
            val = val * t + float(ck)
        return float(val)

    # ============================================================
    # Stage 3: Stabilization for Extreme Functions (log-log)
    # ============================================================
    # Some functions have values spanning many orders of magnitude.
    # For those, fitting directly in y-space is unstable.
    # We apply log() multiple times, but we must keep inputs positive.
    # Therefore, before each log, we shift y by a constant to make it > 0.
    @staticmethod
    def _safe_log_transform(y: np.ndarray, depth: int):
        """
        Apply log() repeatedly 'depth' times.

        To keep log valid, before each stage:
        - if min(y) <= 0, shift y by (-min(y) + eps).
        - store the shift so we can invert the transformation later.

        Returns:
        - y_t    : transformed values
        - shifts : list of applied shifts, one per log stage
        - ok     : True if all transformed values are finite
        """
        y_t = np.asarray(y, dtype=float).copy()
        shifts = []

        # depth == 0 means "no transform"
        if depth <= 0:
            return y_t, shifts, bool(np.isfinite(y_t).all())

        for _ in range(depth):
            minv = float(np.nanmin(y_t))
            if not np.isfinite(minv):
                return y_t, shifts, False

            shift = 0.0
            if minv <= 0.0:
                # eps depends on magnitude to avoid tiny shift relative to values
                eps = 1e-6 * max(1.0, abs(minv))
                shift = -minv + eps
                y_t = y_t + shift

            shifts.append(float(shift))

            # Compute log with error states suppressed; we check finiteness manually
            with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
                y_t = np.log(y_t)

            # If any NaN/inf occurred, transform failed
            if not np.isfinite(y_t).all():
                return y_t, shifts, False

        return y_t, shifts, True

    @staticmethod
    def _invert_log_transform(v: float, shifts):
        """
        Invert a repeated log transform for a scalar:
        - Apply exp() once for each log stage (reverse order),
        - Subtract the stored shift after each exp.

        Also performs mild clamping:
        - If intermediate value becomes non-positive but more exp steps remain,
          clamp to a tiny positive value to keep exp/log chain valid.
        """
        y = float(v)
        for k, shift in enumerate(reversed(shifts)):
            with np.errstate(over="ignore", invalid="ignore"):
                y = float(np.exp(y))
            y -= float(shift)

            if k < len(shifts) - 1:
                if (not np.isfinite(y)) or y <= 0.0:
                    y = 1e-12

        if not np.isfinite(y):
            return float("inf")
        return float(y)

    # ============================================================
    # Stage 4: Piecewise Fitting (per segment)
    # ============================================================
    def _fit_segment(self, f, seg_a, seg_b, d, hard_deadline, call_dt_hint):
        """
        Fit a local model on a small interval [seg_a, seg_b].

        Steps:
        1) Map x in [seg_a, seg_b] to t in [-1, 1] (affine transform).
        2) Sample f(x) at a small set of nodes (Chebyshev-like spacing).
        3) If values are extremely spread (large ratio), prefer log-log stabilization.
        4) Try several (log_depth, degree) combinations.
        5) Choose the best model according to mean absolute error on sampled nodes.
        """
        seg_a = float(seg_a)
        seg_b = float(seg_b)

        # Map segment to normalized coordinate t in [-1, 1]
        mid = 0.5 * (seg_a + seg_b)
        half = 0.5 * (seg_b - seg_a)

        # Degenerate segment: return constant model
        if half == 0.0 or not np.isfinite(half):
            y0 = float(f(seg_a))
            return {
                "a": seg_a, "b": seg_b,
                "mid": mid, "half": 1.0,
                "coeffs": np.array([y0], dtype=float),
                "deg": 0, "log_depth": 0, "shifts": []
            }

        # Limit local polynomial degree to keep it stable and cheap
        max_local_deg = max(0, min(int(d), 5))

        # Candidate polynomial degrees to try
        deg_candidates = [0, 1]
        if max_local_deg >= 2: deg_candidates.append(2)
        if max_local_deg >= 3: deg_candidates.append(3)
        if max_local_deg >= 4: deg_candidates.append(4)
        if max_local_deg >= 5: deg_candidates.append(5)

        # Choose number of sample nodes in this segment
        N = max(12, 4 * (max_local_deg + 1))
        N = min(N, 40)

        # Chebyshev-like nodes in [-1,1] (good for polynomial fitting)
        u = (np.arange(N, dtype=float) + 0.5) / N
        t_nodes = np.cos(np.pi * u)
        t_nodes = np.clip(t_nodes, -1.0, 1.0)
        x_nodes = mid + half * t_nodes

        # Sample f at each x node (one sample each, because there may be many segments)
        y = np.zeros(N, dtype=float)
        for i in range(N):
            if time.time() >= hard_deadline:
                # Truncate if time is nearly over
                y = y[: max(1, i)]
                t_nodes = t_nodes[: max(1, i)]
                break
            y[i] = float(f(float(x_nodes[i])))

        # If there are non-finite values, replace them with the median of finite values
        if not np.isfinite(y).all():
            finite = y[np.isfinite(y)]
            if finite.size == 0:
                return {
                    "a": seg_a, "b": seg_b,
                    "mid": mid, "half": half,
                    "coeffs": np.array([0.0], dtype=float),
                    "deg": 0, "log_depth": 0, "shifts": []
                }
            med = float(np.median(finite))
            y = np.where(np.isfinite(y), y, med)

        best = None
        best_score = float("inf")

        # Measure how extreme the segment is (ratio ymax/ymin for positive values)
        span_ratio = 0.0
        try:
            yy_f = y[np.isfinite(y)]
            if yy_f.size > 0:
                ymin = float(np.min(yy_f))
                ymax = float(np.max(yy_f))
                if ymin > 0.0:
                    span_ratio = ymax / ymin
        except Exception:
            span_ratio = 0.0

        # Prefer log-log first for huge positive ratios (typical exp(exp(x)) behavior)
        log_order = (2, 3) if span_ratio > 1e4 else (2, 3, 1, 0)

        # Try different stabilization depths and polynomial degrees
        for log_depth in log_order:
            if time.time() >= hard_deadline:
                break

            y_t, shifts, ok = self._safe_log_transform(y, log_depth)
            if not ok:
                continue

            for deg_try in deg_candidates:
                if time.time() >= hard_deadline:
                    break

                # Fit polynomial in transformed space
                c_try = self._fit_fixed_degree(t_nodes, y_t, deg_try)

                # Evaluate the fit at nodes
                pred_t = np.array([self._poly_eval(c_try, float(t)) for t in t_nodes], dtype=float)

                # Invert transform back to original y-space and compute error
                y_hat = np.empty_like(pred_t)
                ok_inv = True
                for ii in range(pred_t.size):
                    yh = self._invert_log_transform(float(pred_t[ii]), shifts)
                    if yh < 0.0:
                        yh = 0.0  # clamp negative predictions for positive-only targets
                    y_hat[ii] = yh
                    if not np.isfinite(y_hat[ii]):
                        ok_inv = False
                        break
                if not ok_inv:
                    continue

                # Score: mean absolute error (MAE) + tiny penalty for model complexity
                score = float(np.mean(np.abs(y - y_hat)))
                score += 1e-8 * (deg_try + 1) * (log_depth + 1)

                # Keep best model
                if np.isfinite(score) and score < best_score:
                    best_score = score
                    best = (log_depth, shifts, deg_try, c_try)

        # If nothing worked, fallback to constant fit
        if best is None:
            c0 = float(np.mean(y))
            return {
                "a": seg_a, "b": seg_b,
                "mid": mid, "half": half,
                "coeffs": np.array([c0], dtype=float),
                "deg": 0, "log_depth": 0, "shifts": []
            }

        # Return the best segment model
        log_depth, shifts, deg_try, c_try = best
        return {
            "a": seg_a, "b": seg_b,
            "mid": mid, "half": half,
            "coeffs": c_try, "deg": deg_try,
            "log_depth": log_depth, "shifts": shifts
        }

    # ============================================================
    # Stage 5: Least Squares Polynomial Fit (Normal Equations)
    # ============================================================
    def _fit_fixed_degree(self, t_nodes: np.ndarray, y: np.ndarray, deg: int) -> np.ndarray:
        """
        Fit a polynomial of fixed degree 'deg' in monomial basis over t in [-1,1].

        Procedure:
        - Build Vandermonde matrix A where A[i,k] = t_i^k
        - Solve normal equations: (A^T A) c = (A^T y)
        - Add small ridge regularization to improve conditioning
        - Solve using custom Gaussian elimination
        """
        m = deg + 1
        A = np.vander(t_nodes, N=m, increasing=True).astype(float)

        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            G = A.T @ A      # Gram matrix
            rhs = A.T @ y    # right-hand side

        # If matrix became non-finite, fallback to constant
        if (not np.isfinite(G).all()) or (not np.isfinite(rhs).all()):
            return np.array([float(np.mean(y))], dtype=float)

        # Ridge regularization: lambda scaled by trace(G)
        trG = float(np.trace(G))
        lam = 1e-8 * trG / m if np.isfinite(trG) and trG > 0 else 1e-8
        G = G + lam * np.eye(m)

        return self._gauss_solve(G, rhs)

    # ============================================================
    # Stage 6: Main Fitting Routine (fit)
    # ============================================================
    def fit(self, f: callable, a: float, b: float, d: int, maxtime: float) -> callable:
        """
        Returns a callable model g(x) approximating f(x) over [a, b].

        High-level flow:
        1) Set a hard deadline: must return within (maxtime + 5 seconds).
        2) Build sampling nodes (Chebyshev-like).
        3) Estimate call time per sample to decide how aggressive we can be.
        4) Detect extreme functions; if extreme and time allows -> piecewise fit.
        5) Otherwise do global polynomial LS fit:
           - sample once everywhere
           - if time allows, resample and average to reduce noise
           - choose degree (fast heuristic validation) if f is not slow
        6) Return g(x) that evaluates the fitted polynomial.
        """

        start = time.time()
        hard_deadline = start + float(maxtime) + 4.5  # ensures <= maxtime+5

        a = float(a)
        b = float(b)
        d = int(d)

        # Handle degenerate intervals: return constant function
        if not np.isfinite(a) or not np.isfinite(b) or a == b:
            y0 = float(f(a))
            return lambda x, y0=y0: y0

        # Map [a,b] to t in [-1,1]
        mid = 0.5 * (a + b)
        half = 0.5 * (b - a)
        if (not np.isfinite(half)) or abs(half) < 1e-12:
            y0 = float(f(a))
            return lambda x, y0=y0: y0

        # Cap degree for stability (grader expects max 12)
        max_deg = max(0, min(d, 12))
        m_full = max_deg + 1

        # Choose number of global sampling nodes
        N = max(3 * m_full, 40)
        N = min(N, 200)

        # Build Chebyshev-like nodes
        u = (np.arange(N, dtype=float) + 0.5) / N
        t_nodes = np.cos(np.pi * u)
        t_nodes = np.clip(t_nodes, -1.0, 1.0)
        x_nodes = mid + half * t_nodes

        # Probe f once to estimate how expensive a single evaluation is
        t0 = time.time()
        y_probe = float(f(float(x_nodes[0])))
        call_dt = max(1e-6, time.time() - t0)

        # -------------------------------------------------
        # Detect extreme functions (e.g., exp(exp(x)), ln(ln(x)))
        # and, if we have enough time, switch to piecewise fitting
        # with per-segment log/log stabilization.
        # -------------------------------------------------
        use_piecewise = False
        scan_ratio = 0.0
        if maxtime >= 8 and call_dt < 0.8:  # avoid too many calls if f is very slow
            # quick scan on a few points (cheap)
            scan_n = 9
            scan_x = np.linspace(a, b, scan_n, dtype=float)
            scan_y = np.empty(scan_n, dtype=float)
            scan_y[0] = y_probe
            ok_scan = True
            all_positive = False
            for i in range(1, scan_n):
                if time.time() >= hard_deadline:
                    ok_scan = False
                    break
                scan_y[i] = float(f(float(scan_x[i])))
            if ok_scan:
                finite = scan_y[np.isfinite(scan_y)]
                if finite.size > 0:
                    max_val = float(np.max(finite))
                    min_val = float(np.min(finite))
                    all_positive = (min_val > 0.0 and np.isfinite(min_val))
                    scan_ratio = (max_val / min_val) if (min_val > 0.0) else float('inf')
                    # as in your friend's patch: huge max or huge ratio
                    if max_val > 1e10:
                        use_piecewise = True
                    elif min_val > 0 and scan_ratio > 1e5:
                        use_piecewise = True
                # if we saw non-finite values at all, it's also a hint
                if not np.isfinite(scan_y).all():
                    use_piecewise = True

        if use_piecewise and time.time() < hard_deadline - 0.2:
            # choose number of segments: 20..50, but also respect time budget
            base_segments = max(25, min(80, int(abs(b - a) * 20)))

            # estimate cost per segment: ~N calls, N~10..30
            est_calls_per_seg = 18
            remaining = max(0.0, hard_deadline - time.time())
            # keep headroom for python overhead; use up to ~75% of remaining time
            max_calls = int(0.75 * remaining / max(1e-6, call_dt))
            max_segments_by_time = max(5, max_calls // max(1, est_calls_per_seg))
            num_segments = int(max(5, min(base_segments, max_segments_by_time)))

            s = np.linspace(0.0, 1.0, num_segments + 1, dtype=float)
            if all_positive and scan_ratio > 1e4:
                # pack more segments near the right edge (steep growth)
                gamma = 2.0
                s = 1.0 - np.power(1.0 - s, gamma)
            bounds = a + (b - a) * s
            models = []
            for i in range(num_segments):
                if time.time() >= hard_deadline:
                    break
                seg_a = float(bounds[i])
                seg_b = float(bounds[i + 1])
                models.append(self._fit_segment(f, seg_a, seg_b, d, hard_deadline, call_dt))

            # If we failed to build enough segments, fall back to global fit
            if len(models) >= 2:
                seg_ends = np.array([m["b"] for m in models], dtype=float)

                def piecewise_g(x, models=models, seg_ends=seg_ends, all_positive=all_positive):
                    xv = float(x)
                    # locate segment with binary search
                    j = int(np.searchsorted(seg_ends, xv, side="right"))
                    if j < 0:
                        j = 0
                    if j >= len(models):
                        j = len(models) - 1
                    md = models[j]
                    t = (xv - md["mid"]) / md["half"]
                    if t > 1.0:
                        t = 1.0
                    elif t < -1.0:
                        t = -1.0
                    v = self._poly_eval(md["coeffs"], t)
                    if md["log_depth"] > 0:
                        v = self._invert_log_transform(v, md["shifts"])
                    if all_positive and v < 0.0:
                        v = 0.0
                    return float(v)

                return piecewise_g

        # If f is slow, don't waste time on degree selection / heavy averaging
        slow = call_dt > 0.15
        very_slow = call_dt > 0.8

        # --------------------------------------
        # Two-stage sampling:
        # Stage 1: one sample per node (fast)
        # Stage 2: if time remains, add more samples to reduce noise
        # --------------------------------------
        y_sum = np.zeros(N, dtype=float)
        y_cnt = np.zeros(N, dtype=int)

        # include probe for node 0
        y_sum[0] = y_probe
        y_cnt[0] = 1

        # stage 1: one sample for all other nodes
        for i in range(1, N):
            if time.time() >= hard_deadline:
                # truncate
                t_nodes = t_nodes[:i]
                x_nodes = x_nodes[:i]
                y_sum = y_sum[:i]
                y_cnt = y_cnt[:i]
                N = i
                break
            y_sum[i] = float(f(float(x_nodes[i])))
            y_cnt[i] = 1

        if N <= 0:
            return lambda x: 0.0

        # stage 2: extra repeats only if not too slow and time remains
        # Compute an upper bound of extra repeats per node we can afford.
        remaining = max(0.0, hard_deadline - time.time())
        if not very_slow and remaining > 0:
            # allow up to 60% of remaining for extra averaging
            extra_budget = 0.60 * remaining
            extra_per_node = int(extra_budget / (N * call_dt)) if call_dt > 0 else 0
            extra_per_node = max(0, min(extra_per_node, 20))

            for _ in range(extra_per_node):
                # loop over nodes and add one more sample each
                for i in range(N):
                    if time.time() >= hard_deadline:
                        break
                    y_sum[i] += float(f(float(x_nodes[i])))
                    y_cnt[i] += 1
                if time.time() >= hard_deadline:
                    break

        y = y_sum / np.maximum(1, y_cnt)

        if (not np.isfinite(y).all()) or N < 2:
            c0 = float(np.nanmean(y)) if N > 0 else 0.0
            return lambda x, c0=c0: c0

        # --------------------------------------
        # Degree choice:
        # - If f is slow: trust given d (capped) to save time
        # - If f is fast: pick best degree by a small validation split
        # --------------------------------------
        if slow:
            best_deg = max_deg
        else:
            idx = np.arange(N)
            train = idx[::2]
            val = idx[1::2]
            if len(val) < 8:
                train = idx
                val = idx

            # keep validation small to save time
            V = min(25, len(val))
            val = val[:V]

            best_deg = 0
            best_score = float("inf")

            # Try degrees 0..max_deg, but stop early if time gets tight
            for deg_try in range(0, max_deg + 1):
                if time.time() >= hard_deadline:
                    break

                c_try = self._fit_fixed_degree(t_nodes[train], y[train], deg_try)

                # validation error against fresh noisy samples (1 sample each) – cheap but effective
                err = 0.0
                used = 0
                for j in val:
                    if time.time() >= hard_deadline:
                        break
                    xj = float(x_nodes[j])
                    yj = float(f(xj))  # fresh noise
                    pred = self._poly_eval(c_try, float(t_nodes[j]))
                    diff = yj - pred
                    err += diff * diff
                    used += 1

                if used > 0:
                    err /= used
                    if err < best_score:
                        best_score = err
                        best_deg = deg_try

        # Final fit on all data with chosen degree
        c = self._fit_fixed_degree(t_nodes, y, best_deg)

        def g(x, c=c, mid=mid, half=half):
            t = (float(x) - mid) / half
            if t > 1.0:
                t = 1.0
            elif t < -1.0:
                t = -1.0
            return self._poly_eval(c, t)

        return g


##########################################################################


import unittest
from sampleFunctions import *
from tqdm import tqdm


class TestAssignment4(unittest.TestCase):

    def test_return(self):
        f = NOISY(0.01)(poly(1,1,1))
        ass4 = Assignment4()
        T = time.time()
        shape = ass4.fit(f=f, a=0, b=1, d=10, maxtime=5)
        T = time.time() - T
        self.assertLessEqual(T, 5)

    def test_delay(self):
        f = DELAYED(7)(NOISY(0.01)(poly(1,1,1)))

        ass4 = Assignment4()
        T = time.time()
        shape = ass4.fit(f=f, a=0, b=1, d=10, maxtime=5)
        T = time.time() - T
        self.assertGreaterEqual(T, 5)

    def test_err(self):
        f = poly(1,1,1)
        nf = NOISY(1)(f)
        ass4 = Assignment4()
        T = time.time()
        ff = ass4.fit(f=nf, a=0, b=1, d=10, maxtime=5)
        T = time.time() - T
        mse=0
        for x in np.linspace(0,1,1000):
            self.assertNotEqual(f(x), nf(x))
            mse+= (f(x)-ff(x))**2
        mse = mse/1000
        print(mse)






if __name__ == "__main__":
    unittest.main()




##########################################################################


import unittest
from sampleFunctions import *
from tqdm import tqdm


class TestAssignment4(unittest.TestCase):

    def test_return(self):
        f = NOISY(0.01)(poly(1,1,1))
        ass4 = Assignment4()
        T = time.time()
        shape = ass4.fit(f=f, a=0, b=1, d=10, maxtime=5)
        T = time.time() - T
        self.assertLessEqual(T, 5)

    def test_delay(self):
        f = DELAYED(7)(NOISY(0.01)(poly(1,1,1)))

        ass4 = Assignment4()
        T = time.time()
        shape = ass4.fit(f=f, a=0, b=1, d=10, maxtime=5)
        T = time.time() - T
        self.assertGreaterEqual(T, 5)

    def test_err(self):
        f = poly(1,1,1)
        nf = NOISY(1)(f)
        ass4 = Assignment4()
        T = time.time()
        ff = ass4.fit(f=nf, a=0, b=1, d=10, maxtime=5)
        T = time.time() - T
        mse=0
        for x in np.linspace(0,1,1000):
            self.assertNotEqual(f(x), nf(x))
            mse+= (f(x)-ff(x))**2
        mse = mse/1000
        print(mse)






if __name__ == "__main__":
    unittest.main()
