"""
Assignment 4 - Function Fitting Under Noise and Time Constraints

Goal:
- Fit a model g(x) to noisy samples y = f(x) on the interval [a, b].
- Minimize approximation error (least-squares style) while obeying a strict runtime limit.
- Do NOT use numpy optimization / linear algebra solvers.

Key ideas:
1) Chebyshev polynomial basis for numerical stability.
2) Custom Gaussian elimination solver (partial pivoting) for normal equations.
3) Parallel sampling with ThreadPoolExecutor for concurrent denoising.
4) Adaptive sampling based on time budget and function evaluation cost.
5) Multiple samples per point with trimmed mean for robust noise reduction.

Constraints:
- Must return within maxtime + 5 seconds.
- No forbidden functions (np.linalg.solve, polyfit, lstsq, etc.).
"""

import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class Assignment4:
    def __init__(self):
        pass

    # ============================================================
    # Custom Gaussian Elimination Solver (Partial Pivoting)
    # ============================================================
    def _gauss_solve(self, A: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Solve Ax = b using Gaussian elimination with partial pivoting.
        Returns zeros if system is singular or ill-conditioned.
        """
        A = np.asarray(A, dtype=float).copy()
        b = np.asarray(b, dtype=float).copy()
        n = A.shape[0]

        if n == 0:
            return np.array([], dtype=float)

        # Forward elimination
        for i in range(n):
            # Partial pivoting: find row with max absolute value in column i
            max_row = i + int(np.argmax(np.abs(A[i:, i])))

            # Check for singular/ill-conditioned matrix
            if not np.isfinite(A[max_row, i]) or abs(A[max_row, i]) < 1e-14:
                return np.zeros(n, dtype=float)

            # Swap rows if needed
            if max_row != i:
                A[[i, max_row]] = A[[max_row, i]]
                b[[i, max_row]] = b[[max_row, i]]

            # Eliminate below
            pivot = A[i, i]
            for j in range(i + 1, n):
                factor = A[j, i] / pivot
                if factor != 0.0:
                    A[j, i:] -= factor * A[i, i:]
                    b[j] -= factor * b[i]

        # Back substitution
        x = np.zeros(n, dtype=float)
        for i in range(n - 1, -1, -1):
            x[i] = (b[i] - np.dot(A[i, i + 1:], x[i + 1:])) / A[i, i]

        return x

    # ============================================================
    # Chebyshev Polynomial Utilities
    # ============================================================
    @staticmethod
    def _cheby_basis(t: np.ndarray, deg: int) -> np.ndarray:
        """
        Build Chebyshev basis matrix T where T[i,k] = T_k(t[i]).
        Uses recurrence: T_k(x) = 2x*T_{k-1}(x) - T_{k-2}(x)
        """
        t = np.asarray(t, dtype=float)
        n = len(t)
        T = np.zeros((n, deg + 1), dtype=float)
        T[:, 0] = 1.0
        if deg >= 1:
            T[:, 1] = t
        for k in range(2, deg + 1):
            T[:, k] = 2.0 * t * T[:, k - 1] - T[:, k - 2]
        return T

    @staticmethod
    def _cheby_eval(c: np.ndarray, t: float) -> float:
        """
        Evaluate polynomial in Chebyshev basis using Clenshaw recurrence.
        """
        c = np.asarray(c, dtype=float)
        n = len(c)
        if n == 0:
            return 0.0
        if n == 1:
            return float(c[0])

        t = float(t)
        b_prev, b_curr = 0.0, 0.0
        for k in range(n - 1, 0, -1):
            b_next = float(c[k]) + 2.0 * t * b_curr - b_prev
            b_prev = b_curr
            b_curr = b_next
        return float(c[0]) + t * b_curr - b_prev

    @staticmethod
    def _cheby_eval_batch(c: np.ndarray, t: np.ndarray) -> np.ndarray:
        """
        Vectorized Chebyshev evaluation at multiple points.
        """
        c = np.asarray(c, dtype=float)
        t = np.asarray(t, dtype=float)
        n = len(c)
        if n == 0:
            return np.zeros_like(t)
        if n == 1:
            return np.full_like(t, c[0])

        b_prev = np.zeros_like(t)
        b_curr = np.zeros_like(t)
        for k in range(n - 1, 0, -1):
            b_next = c[k] + 2.0 * t * b_curr - b_prev
            b_prev = b_curr
            b_curr = b_next
        return c[0] + t * b_curr - b_prev

    # ============================================================
    # Least Squares Fitting (Normal Equations)
    # ============================================================
    def _fit_cheby(self, t_nodes: np.ndarray, y: np.ndarray, deg: int) -> np.ndarray:
        """
        Fit polynomial of degree 'deg' in Chebyshev basis.
        Solves normal equations: (T^T T + λI) c = T^T y
        """
        m = deg + 1
        T = self._cheby_basis(t_nodes, deg)

        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            G = T.T @ T
            rhs = T.T @ y

        if not (np.isfinite(G).all() and np.isfinite(rhs).all()):
            return np.array([float(np.nanmean(y))], dtype=float)

        # Ridge regularization
        trace = float(np.trace(G))
        lam = 1e-10 * (trace / m if trace > 0 else 1.0)
        G += lam * np.eye(m)

        return self._gauss_solve(G, rhs)

    # ============================================================
    # Parallel Sampling with Denoising
    # ============================================================
    def _parallel_sample(self, f, x_nodes, hard_deadline, n_workers=300, target_samples_per_node=10):
        """
        Sample f at x_nodes using parallel threads for concurrent denoising.
        Uses trimmed mean (drop top/bottom 10%) for robust noise reduction.
        Continues sampling until deadline to maximize noise reduction.
        """
        N = len(x_nodes)
        if N == 0:
            return np.array([]), np.array([])

        # Storage for all samples
        all_samples = [[] for _ in range(N)]
        lock = threading.Lock()
        done_event = threading.Event()

        def sample_task(idx):
            if done_event.is_set() or time.time() >= hard_deadline:
                return
            try:
                val = float(f(float(x_nodes[idx])))
                if np.isfinite(val):
                    with lock:
                        all_samples[idx].append(val)
            except:
                pass

        # Use ThreadPoolExecutor with continuous submission until deadline
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = []
            sample_round = 0

            # Keep submitting samples until we approach deadline
            while time.time() < hard_deadline - 0.1:
                # Submit a batch of samples (one per node)
                batch_futures = []
                for idx in range(N):
                    if time.time() >= hard_deadline - 0.1:
                        break
                    batch_futures.append(executor.submit(sample_task, idx))
                futures.extend(batch_futures)
                sample_round += 1

                # Stop if we have enough samples
                if sample_round >= target_samples_per_node:
                    # Wait a bit for pending futures to complete
                    time.sleep(0.001)
                    # Check if we have time for more
                    if time.time() >= hard_deadline - 0.5:
                        break

            # Signal completion
            done_event.set()

            # Wait for all submitted futures with short timeout
            for fut in futures:
                if time.time() >= hard_deadline:
                    break
                try:
                    fut.result(timeout=max(0.001, hard_deadline - time.time()))
                except:
                    pass

        # Compute trimmed mean for each node
        y = np.zeros(N, dtype=float)
        y_cnt = np.zeros(N, dtype=int)

        for i in range(N):
            samples = all_samples[i]
            n_samp = len(samples)
            y_cnt[i] = n_samp

            if n_samp == 0:
                y[i] = np.nan
            elif n_samp <= 2:
                y[i] = float(np.mean(samples))
            else:
                sorted_samp = sorted(samples)
                # 10% trimmed mean for robust denoising
                trim = max(1, int(n_samp * 0.1))
                if 2 * trim >= n_samp:
                    y[i] = float(sorted_samp[n_samp // 2])  # median
                else:
                    y[i] = float(np.mean(sorted_samp[trim:-trim]))

        return y, y_cnt

    # ============================================================
    # Main Fitting Function
    # ============================================================
    def fit(self, f: callable, a: float, b: float, d: int, maxtime: float) -> callable:
        """
        Fit a function g(x) to noisy samples of f(x) over [a, b].

        Strategy:
        1) Estimate function call time to budget samples
        2) Sample at Chebyshev nodes with parallel denoising
        3) Fit polynomial using Chebyshev basis + custom solver
        4) Use degree selection based on validation error
        5) Use full time budget for maximum denoising
        """
        start = time.time()
        # Use most of maxtime for sampling, keep some buffer for fitting
        hard_deadline = start + float(maxtime) - 0.3

        a, b = float(a), float(b)
        d = max(0, min(int(d), 12))

        # Handle degenerate interval
        if not np.isfinite(a) or not np.isfinite(b) or abs(b - a) < 1e-14:
            try:
                y0 = float(f(a))
            except:
                y0 = 0.0
            return lambda x, y0=y0: y0

        # Map [a,b] to [-1,1]
        mid = 0.5 * (a + b)
        half = 0.5 * (b - a)

        # Probe function to estimate call time (multiple probes for accuracy)
        probe_times = []
        y_probe = 0.0
        for _ in range(3):
            t0 = time.time()
            try:
                y_probe = float(f(mid))
            except:
                y_probe = 0.0
            probe_times.append(time.time() - t0)
        call_time = max(1e-6, np.median(probe_times))

        # Calculate effective time budget
        # With parallel threads, we can achieve much higher throughput for slow (delayed) functions
        remaining_time = max(0.5, hard_deadline - time.time() - 0.3)

        # Number of parallel workers - more workers = better concurrency for delayed functions
        n_workers = 300

        # Estimate effective throughput with parallelism
        # For delayed functions, parallel throughput can be much higher
        parallel_factor = min(n_workers, max(1, int(call_time / 0.001))) if call_time > 0.001 else 1
        effective_call_time = call_time / parallel_factor

        # Determine sampling strategy based on time budget
        # Goal: maximize samples for better noise reduction
        if effective_call_time < 0.0001:
            # Very fast function: sample aggressively
            N = max(50, 5 * (d + 1))
            N = min(N, 200)
            # Target using ~80% of time budget
            total_samples_budget = int(0.8 * remaining_time / max(1e-6, call_time / parallel_factor))
            samples_per_node = max(10, min(50, total_samples_budget // N))
        elif call_time < 0.05:
            # Moderately fast function
            N = max(40, 4 * (d + 1))
            N = min(N, 150)
            total_samples_budget = int(0.8 * remaining_time / max(1e-6, call_time / parallel_factor))
            samples_per_node = max(8, min(30, total_samples_budget // N))
        else:
            # Slow/delayed function - rely heavily on parallelism
            N = max(30, 3 * (d + 1))
            N = min(N, 100)
            # For delayed functions, parallelism helps a lot
            total_samples_budget = int(0.7 * remaining_time / max(1e-6, call_time / parallel_factor))
            samples_per_node = max(5, min(25, total_samples_budget // N))

        # Build Chebyshev nodes in [-1, 1]
        k = np.arange(N, dtype=float)
        t_nodes = np.cos(np.pi * (2 * k + 1) / (2 * N))
        t_nodes = np.clip(t_nodes, -1.0, 1.0)
        x_nodes = mid + half * t_nodes

        # Parallel sampling with denoising - use remaining time for maximum samples
        y, y_cnt = self._parallel_sample(
            f, x_nodes, hard_deadline,
            n_workers=n_workers,
            target_samples_per_node=samples_per_node
        )

        # Filter valid samples
        valid = y_cnt > 0
        if np.sum(valid) < 2:
            return lambda x, y0=y_probe: y0

        t_valid = t_nodes[valid]
        y_valid = y[valid]

        # Handle non-finite values
        finite_mask = np.isfinite(y_valid)
        if np.sum(finite_mask) < d + 1:
            c0 = float(np.nanmean(y_valid))
            return lambda x, c0=c0: c0

        t_valid = t_valid[finite_mask]
        y_valid = y_valid[finite_mask]
        n_valid = len(y_valid)

        # For low degree polynomials (most common case: 65% are d<=3)
        # Just fit directly without validation overhead
        if d <= 3 and n_valid >= d + 1:
            c = self._fit_cheby(t_valid, y_valid, d)
        elif n_valid >= 2 * (d + 1) and time.time() < hard_deadline - 0.1:
            # Degree selection with validation for higher degrees
            idx = np.arange(n_valid)
            train_idx = idx[::2]
            val_idx = idx[1::2]

            if len(val_idx) < 3:
                train_idx = idx
                val_idx = idx

            t_train = t_valid[train_idx]
            y_train = y_valid[train_idx]
            t_val = t_valid[val_idx]
            y_val = y_valid[val_idx]

            best_deg = d
            best_err = float('inf')
            best_c = None

            for deg_try in range(min(d, n_valid - 1) + 1):
                if time.time() >= hard_deadline - 0.05:
                    break

                c_try = self._fit_cheby(t_train, y_train, deg_try)
                pred = self._cheby_eval_batch(c_try, t_val)
                err = float(np.mean((y_val - pred) ** 2))
                err += 1e-9 * deg_try  # Very small penalty for complexity

                if np.isfinite(err) and err < best_err:
                    best_err = err
                    best_deg = deg_try
                    best_c = c_try

            if best_c is not None:
                c = best_c
            else:
                c = self._fit_cheby(t_valid, y_valid, min(d, n_valid - 1))
        else:
            actual_deg = min(d, n_valid - 1)
            c = self._fit_cheby(t_valid, y_valid, actual_deg)

        # Return fitted function
        def g(x, c=c, mid=mid, half=half):
            t = (float(x) - mid) / half
            t = max(-1.0, min(1.0, t))
            return self._cheby_eval(c, t)

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
