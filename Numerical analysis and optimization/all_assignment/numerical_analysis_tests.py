#!/usr/bin/env python3
"""
Numerical Analysis & Optimization - Comprehensive Test Suite
=============================================================
Tests for Assignments 1-5 using course functions f1-f11 plus random polynomials.

Usage:
    python numerical_analysis_tests.py            # Run all tests
    python numerical_analysis_tests.py 1          # Run only Assignment 1
    python numerical_analysis_tests.py 1 3 5      # Run Assignments 1, 3, and 5

Each test reports: name, pass/fail, error, runtime.
Final summary shows per-assignment statistics.
"""

import numpy as np
import time
import sys
import traceback

# ============================================================
# Course Test Functions f1 - f11
# ============================================================

def f1(x):
    """f1(x) = 5 (constant)"""
    return 5.0

def f2(x):
    """f2(x) = x^2 - 3x + 5"""
    return float(x)**2 - 3*float(x) + 5

def f3(x):
    """f3(x) = sin(x^2)"""
    return float(np.sin(float(x)**2))

def f4(x):
    """f4(x) = e^(-2x^2)"""
    return float(np.exp(-2*float(x)**2))

def f5(x):
    """f5(x) = arctan(x)"""
    return float(np.arctan(float(x)))

def f6(x):
    """f6(x) = sin(x)/x"""
    x = float(x)
    if abs(x) < 1e-15:
        return 1.0
    return float(np.sin(x) / x)

def f7(x):
    """f7(x) = 1/ln(x)  (domain: x > 0, x != 1)"""
    x = float(x)
    lnx = np.log(x)
    if abs(lnx) < 1e-15:
        return float('inf')
    return float(1.0 / lnx)

def f8(x):
    """f8(x) = e^(e^x)"""
    return float(np.exp(np.exp(float(x))))

def f9(x):
    """f9(x) = ln(ln(x))  (domain: x > 1)"""
    return float(np.log(np.log(float(x))))

def f10(x):
    """f10(x) = sin(ln(x))  (domain: x > 0)"""
    return float(np.sin(np.log(float(x))))

def f11(x):
    """f11(x) = 2^(1/x^2) * sin(1/x)  (the hard oscillation function)"""
    x = float(x)
    if abs(x) < 1e-15:
        return 0.0
    return float((2.0 ** (1.0 / (x**2))) * np.sin(1.0 / x))


# ============================================================
# Helper: Random Polynomial Generator
# ============================================================
def random_poly(degree, seed):
    """Generate polynomial with random coefficients in [-1, 1]."""
    rng = np.random.RandomState(seed)
    coeffs = rng.uniform(-1, 1, degree + 1)
    return np.poly1d(coeffs)


# ============================================================
# Test Result Tracking
# ============================================================
class TestResult:
    def __init__(self, name, passed, error=None, runtime=None, details=""):
        self.name = name
        self.passed = passed
        self.error = error
        self.runtime = runtime
        self.details = details


class TestRunner:
    def __init__(self):
        self.results = {}  # assignment -> list of TestResult

    def add(self, assignment, result):
        if assignment not in self.results:
            self.results[assignment] = []
        self.results[assignment].append(result)

        # Print immediately
        status = "\033[92mPASS\033[0m" if result.passed else "\033[91mFAIL\033[0m"
        err_str = f"err={result.error:.4e}" if result.error is not None else ""
        rt_str = f"time={result.runtime*1000:.1f}ms" if result.runtime else ""
        info = f"  [{status}] {result.name:45s} {err_str:20s} {rt_str}"
        if not result.passed and result.details:
            info += f"  ({result.details})"
        print(info)

    def print_summary(self):
        print("\n" + "=" * 75)
        print("FINAL SUMMARY")
        print("=" * 75)
        total_pass = 0
        total_fail = 0
        for assign in sorted(self.results.keys()):
            res_list = self.results[assign]
            passed = sum(1 for r in res_list if r.passed)
            failed = sum(1 for r in res_list if not r.passed)
            total_pass += passed
            total_fail += failed
            errors = [r.error for r in res_list if r.error is not None and np.isfinite(r.error)]
            runtimes = [r.runtime for r in res_list if r.runtime is not None]
            avg_err = np.mean(errors) if errors else 0
            avg_rt = np.mean(runtimes) * 1000 if runtimes else 0
            max_rt = max(runtimes) * 1000 if runtimes else 0

            status = "\033[92mALL PASS\033[0m" if failed == 0 else f"\033[91m{failed} FAILED\033[0m"
            print(f"\n  {assign}:")
            print(f"    Tests:       {passed}/{passed+failed} passed  ({status})")
            print(f"    Avg error:   {avg_err:.4e}")
            print(f"    Avg runtime: {avg_rt:.2f}ms  (max: {max_rt:.2f}ms)")

            if failed > 0:
                print(f"    Failures:")
                for r in res_list:
                    if not r.passed:
                        print(f"      - {r.name}: {r.details}")

        print(f"\n  {'─'*50}")
        print(f"  TOTAL: {total_pass}/{total_pass+total_fail} passed", end="")
        if total_fail > 0:
            print(f"  (\033[91m{total_fail} failed\033[0m)")
        else:
            print(f"  (\033[92mall passed\033[0m)")
        print("=" * 75)


runner = TestRunner()


# ============================================================
# ASSIGNMENT 1 TESTS - Interpolation
# ============================================================
def run_assignment1_tests():
    from assignment1 import Assignment1
    ass1 = Assignment1()
    print("\n" + "─" * 75)
    print("ASSIGNMENT 1: Interpolation")
    print("─" * 75)

    def test_interp(f, a, b, n, name, tol, n_eval=200):
        t0 = time.time()
        g = ass1.interpolate(f, a, b, n)
        runtime = time.time() - t0
        xs = np.linspace(a + 0.01*(b-a), b - 0.01*(b-a), n_eval)
        errs = []
        for x in xs:
            try:
                yy = g(float(x))
                y = f(float(x))
                if np.isfinite(y) and np.isfinite(yy):
                    errs.append(abs(y - yy))
            except Exception:
                pass
        mean_err = float(np.mean(errs)) if errs else float('inf')
        passed = mean_err < tol
        runner.add("Assignment 1", TestResult(name, passed, mean_err, runtime,
                   f"err={mean_err:.2e} > tol={tol:.0e}" if not passed else ""))

    # Course functions
    test_interp(f1, -5, 5, 10, "f1 constant (n=10)", 1e-6)
    test_interp(f2, -2, 5, 10, "f2 quadratic (n=10)", 0.01)
    test_interp(f2, -2, 5, 50, "f2 quadratic (n=50)", 1e-5)
    test_interp(f3, -2, 2, 50, "f3 sin(x^2) (n=50)", 0.1)
    test_interp(f3, -2, 2, 100, "f3 sin(x^2) (n=100)", 0.01)
    test_interp(f4, -3, 3, 20, "f4 gaussian (n=20)", 0.01)
    test_interp(f4, -3, 3, 50, "f4 gaussian (n=50)", 1e-5)
    test_interp(f5, -10, 10, 20, "f5 arctan (n=20)", 0.1)
    test_interp(f5, -10, 10, 100, "f5 arctan (n=100)", 0.001)
    test_interp(f6, 0.1, 10, 50, "f6 sinc (n=50)", 0.01)
    test_interp(f10, 1, 10, 50, "f10 sin(ln(x)) (n=50)", 0.001)

    # f8 has huge dynamic range - test relative error
    t0 = time.time()
    g = ass1.interpolate(f8, 0, 3, 50)
    runtime = time.time() - t0
    xs = np.linspace(0.1, 2.9, 100)
    rel_errs = []
    for x in xs:
        y = f8(x)
        yy = g(float(x))
        if np.isfinite(y) and np.isfinite(yy) and abs(y) > 1e-10:
            rel_errs.append(abs(y - yy) / abs(y))
    mean_rel = float(np.mean(rel_errs)) if rel_errs else float('inf')
    runner.add("Assignment 1", TestResult("f8 exp(exp(x)) (n=50, relative)", mean_rel < 0.5, mean_rel, runtime))

    # Random polynomials (>50% of tests)
    for deg, n, tol_p in [(3, 10, 0.01), (5, 20, 0.01), (10, 50, 0.1), (15, 50, 1.0), (20, 100, 1.0)]:
        for seed in range(5):
            p = random_poly(deg, seed=seed + deg*10)
            test_interp(p, -1, 1, n, f"poly deg={deg} seed={seed} (n={n})", tol_p)

    # Edge cases
    test_interp(f2, 0, 0.001, 10, "narrow range [0, 0.001] (n=10)", 1e-6)

    t0 = time.time()
    g = ass1.interpolate(f2, 0, 1, 1)
    runtime = time.time() - t0
    val = g(0.5)
    runner.add("Assignment 1", TestResult("n=1 edge case", np.isfinite(val), None, runtime))

    t0 = time.time()
    g = ass1.interpolate(f2, 0, 1, 2)
    runtime = time.time() - t0
    val = g(0.5)
    runner.add("Assignment 1", TestResult("n=2 edge case", np.isfinite(val), None, runtime))


# ============================================================
# ASSIGNMENT 2 TESTS - Intersections
# ============================================================
def run_assignment2_tests():
    from assignment2 import Assignment2
    ass2 = Assignment2()
    print("\n" + "─" * 75)
    print("ASSIGNMENT 2: Intersections")
    print("─" * 75)

    def test_inter(f1_f, f2_f, a, b, maxerr, name, min_expected=None):
        t0 = time.time()
        X = ass2.intersections(f1_f, f2_f, a, b, maxerr=maxerr)
        runtime = time.time() - t0
        X = list(X) if X else []
        max_resid = 0.0
        all_valid = True
        for x in X:
            resid = abs(f1_f(x) - f2_f(x))
            max_resid = max(max_resid, resid)
            if resid > maxerr:
                all_valid = False
        count_ok = min_expected is None or len(X) >= min_expected
        passed = all_valid and count_ok
        details = ""
        if not all_valid:
            details = f"max_resid={max_resid:.2e}>{maxerr}"
        if not count_ok:
            details += f" found={len(X)}<{min_expected}"
        runner.add("Assignment 2", TestResult(f"{name} (found {len(X)})", passed, max_resid, runtime, details))

    # Known cases
    test_inter(lambda x: x**2 - 1, lambda x: 1 - x**2, -2, 2, 0.001, "x^2-1 vs 1-x^2", 2)
    test_inter(np.sin, np.cos, 0, 2*np.pi, 0.001, "sin vs cos [0,2pi]", 2)
    test_inter(lambda x: x**3 - 3*x, lambda x: 0.0, -3, 3, 0.001, "x^3-3x vs 0", 3)
    test_inter(lambda x: x**2, lambda x: float(x), -2, 2, 0.001, "x^2 vs x", 2)
    test_inter(np.sin, lambda x: 0.0, 0, 10, 0.001, "sin vs 0 [0,10]", 3)

    # Course functions
    test_inter(f3, f4, -2, 2, 0.001, "f3 vs f4", 1)
    test_inter(f5, lambda x: 0.5, -5, 5, 0.001, "f5 vs 0.5", 1)

    # Tangent (hard case)
    test_inter(lambda x: x**2, lambda x: 2*x - 1, -2, 3, 0.01, "tangent x^2 vs 2x-1")

    # No intersection
    t0 = time.time()
    X = ass2.intersections(lambda x: x**2 + 10, lambda x: -x**2 - 10, -5, 5, maxerr=0.001)
    runtime = time.time() - t0
    X = list(X) if X else []
    runner.add("Assignment 2", TestResult(f"no intersection (found {len(X)})", len(X) == 0, 0, runtime))

    # Random polynomial pairs (>50%)
    for seed in range(15):
        p1 = random_poly(4, seed=seed*2)
        p2 = random_poly(4, seed=seed*2+1)
        test_inter(p1, p2, -2, 2, 0.001, f"rand poly4 pair seed={seed}")

    # Tight tolerance
    test_inter(lambda x: x**2, lambda x: float(x), -2, 2, 0.0001, "tight tol=1e-4", 2)


# ============================================================
# ASSIGNMENT 3 TESTS - Integration
# ============================================================
def run_assignment3_tests():
    from assignment3 import Assignment3
    ass3 = Assignment3()
    print("\n" + "─" * 75)
    print("ASSIGNMENT 3: Integration")
    print("─" * 75)

    def test_integ(f, a, b, n, true_val, name, rel_tol=0.01):
        t0 = time.time()
        result = ass3.integrate(f, a, b, n)
        runtime = time.time() - t0
        result_f = float(result)
        if abs(true_val) > 1e-10:
            error = abs(result_f - true_val) / abs(true_val)
        else:
            error = abs(result_f - true_val)
        dtype_ok = (result.dtype == np.float32)
        passed = error <= rel_tol and dtype_ok
        details = ""
        if not dtype_ok:
            details = f"dtype={result.dtype}"
        if error > rel_tol:
            details += f" rel_err={error:.2e}>{rel_tol:.0e}"
        runner.add("Assignment 3", TestResult(name, passed, error, runtime, details))

    # Known integrals
    test_integ(f1, 0, 3, 10, 15.0, "f1 const [0,3] n=10", 1e-8)
    test_integ(f2, 0, 3, 5, 10.5, "f2 quad [0,3] n=5 (exact Simpson)", 1e-6)
    test_integ(f2, 0, 3, 50, 10.5, "f2 quad [0,3] n=50", 1e-10)
    test_integ(np.sin, 0, np.pi, 11, 2.0, "sin [0,pi] n=11", 0.001)
    test_integ(np.sin, 0, np.pi, 10, 2.0, "sin [0,pi] n=10 (even)", 0.001)
    test_integ(np.sin, 0, np.pi, 101, 2.0, "sin [0,pi] n=101", 1e-8)
    test_integ(np.sin, np.pi, 2*np.pi, 11, -2.0, "sin [pi,2pi] n=11 (neg)", 0.001)

    # Gaussian integral
    true_gauss = float(np.sqrt(np.pi / 2))
    test_integ(f4, -3, 3, 20, true_gauss, "f4 gauss [-3,3] n=20", 0.01)
    test_integ(f4, -3, 3, 100, true_gauss, "f4 gauss [-3,3] n=100", 0.001)

    # Arctan integral: int arctan(x) dx from 0 to 1 = pi/4 - ln(2)/2
    true_atan = float(np.pi/4 - np.log(2)/2)
    test_integ(f5, 0, 1, 50, true_atan, "f5 arctan [0,1] n=50", 0.001)

    # Hard case: f11
    test_integ(f11, 0.09, 10, 20, -7.78662e33, "f11 hard oscillation n=20", 0.001)

    # Random polynomials - Simpson exact for deg <= 3 (>50% of tests)
    for seed in range(10):
        p = random_poly(3, seed=seed + 60)
        p_int = np.polyint(p)
        true_val = float(p_int(1) - p_int(-1))
        test_integ(p, -1, 1, 5, true_val, f"rand poly3 seed={seed} exact", 1e-5)

    for seed in range(5):
        p = random_poly(5, seed=seed + 70)
        p_int = np.polyint(p)
        true_val = float(p_int(2) - p_int(-2))
        test_integ(p, -2, 2, 20, true_val, f"rand poly5 seed={seed} n=20", 0.01)

    for seed in range(5):
        p = random_poly(8, seed=seed + 80)
        p_int = np.polyint(p)
        true_val = float(p_int(1) - p_int(-1))
        test_integ(p, -1, 1, 50, true_val, f"rand poly8 seed={seed} n=50", 0.001)

    # Edge cases
    r = ass3.integrate(np.sin, 0, np.pi, 1)
    runner.add("Assignment 3", TestResult("n=1 midpoint", r.dtype == np.float32 and np.isfinite(float(r)), None, None))

    r = ass3.integrate(np.sin, 0, np.pi, 2)
    runner.add("Assignment 3", TestResult("n=2 trapezoidal", r.dtype == np.float32 and np.isfinite(float(r)), None, None))

    # n=4 (Simpson 3/8)
    test_integ(np.sin, 0, np.pi, 4, 2.0, "sin n=4 (Simpson 3/8)", 0.05)


# ============================================================
# ASSIGNMENT 4 TESTS - Fitting
# ============================================================
def run_assignment4_tests():
    from assignment4 import Assignment4
    from functionUtils import NOISY
    ass4 = Assignment4()
    print("\n" + "─" * 75)
    print("ASSIGNMENT 4: Fitting")
    print("─" * 75)

    def test_fit(f, a, b, d, noise, maxtime, name, mse_tol=2.0):
        nf = NOISY(noise)(f)
        t0 = time.time()
        g = ass4.fit(f=nf, a=a, b=b, d=d, maxtime=maxtime)
        runtime = time.time() - t0
        xs = np.linspace(a, b, 200)
        mse = float(np.mean([(f(x) - g(x))**2 for x in xs]))
        time_ok = runtime <= maxtime + 5
        passed = mse < mse_tol and time_ok
        details = ""
        if mse >= mse_tol:
            details = f"MSE={mse:.2e}>{mse_tol}"
        if not time_ok:
            details += f" time={runtime:.1f}s>limit"
        runner.add("Assignment 4", TestResult(name, passed, mse, runtime, details))

    # Course functions with noise
    test_fit(f1, 0, 5, 5, 0.5, 5, "f1 const noise=0.5", 1.0)
    test_fit(f2, -2, 5, 5, 0.5, 5, "f2 quad noise=0.5", 2.0)
    test_fit(f5, -5, 5, 8, 0.1, 5, "f5 arctan noise=0.1", 0.5)
    test_fit(f4, -3, 3, 10, 0.05, 5, "f4 gauss noise=0.05", 0.1)

    # Random polynomials with noise (>50%)
    for seed in range(5):
        p = random_poly(2, seed=seed + 90)
        test_fit(p, -1, 1, 5, 0.1, 5, f"rand poly2 seed={seed} noise=0.1", 0.5)

    for seed in range(5):
        p = random_poly(3, seed=seed + 100)
        test_fit(p, -1, 1, 5, 0.5, 5, f"rand poly3 seed={seed} noise=0.5", 2.0)

    for seed in range(3):
        p = random_poly(5, seed=seed + 110)
        test_fit(p, -1, 1, 8, 0.1, 5, f"rand poly5 seed={seed} noise=0.1", 1.0)

    # Linear fit
    test_fit(lambda x: 2*x + 1, 0, 1, 1, 0.1, 5, "linear d=1 noise=0.1", 0.5)

    # Timing test
    from functionUtils import DELAYED
    slow_f = DELAYED(3)(NOISY(0.01)(f1))
    t0 = time.time()
    g = ass4.fit(f=slow_f, a=0, b=1, d=5, maxtime=5)
    T = time.time() - t0
    runner.add("Assignment 4", TestResult(f"timing with DELAYED(3) ({T:.1f}s)", T <= 15, None, T,
               f"took {T:.1f}s" if T > 15 else ""))


# ============================================================
# ASSIGNMENT 5 TESTS - Shape Area
# ============================================================
def run_assignment5_tests():
    from assignment5 import Assignment5
    from sampleFunctions import Circle, noisy_circle
    ass5 = Assignment5()
    print("\n" + "─" * 75)
    print("ASSIGNMENT 5: Shape Area")
    print("─" * 75)

    # --- 5.1: area() tests ---
    def test_area(contour_func, true_area, name, maxerr=0.001):
        t0 = time.time()
        computed = ass5.area(contour_func, maxerr=maxerr)
        runtime = time.time() - t0
        error = abs(float(computed) - true_area) / max(abs(true_area), 1e-10)
        passed = error < maxerr * 10
        runner.add("Assignment 5", TestResult(f"area: {name}", passed, error, runtime,
                   f"computed={float(computed):.4f} true={true_area:.4f}" if not passed else ""))

    # Circle contours
    test_area(Circle(0, 0, 1, 0).contour, np.pi, "unit circle")
    test_area(Circle(2, 3, 5, 0).contour, 25*np.pi, "circle r=5")
    test_area(Circle(-1, -1, 0.5, 0).contour, 0.25*np.pi, "circle r=0.5")

    # Square contour
    def square_contour(n):
        pts = []
        per_side = max(1, n // 4)
        for side in range(4):
            for i in range(per_side):
                t = i / per_side
                if side == 0: pts.append([t, 0])
                elif side == 1: pts.append([1, t])
                elif side == 2: pts.append([1-t, 1])
                else: pts.append([0, 1-t])
        return np.array(pts[:n], dtype=np.float32)

    test_area(square_contour, 1.0, "unit square", maxerr=0.01)

    # --- 5.2: fit_shape() tests ---
    def test_fit(cx, cy, r, noise, maxtime, name, tol=0.1):
        sample = noisy_circle(cx=cx, cy=cy, radius=r, noise=noise)
        t0 = time.time()
        shape = ass5.fit_shape(sample=sample, maxtime=maxtime)
        runtime = time.time() - t0
        true_area = np.pi * r**2
        fitted_area = shape.area()
        error = abs(fitted_area - true_area) / true_area
        time_ok = runtime <= maxtime + 2
        passed = error < tol and time_ok
        details = ""
        if error >= tol:
            details = f"area={fitted_area:.3f} true={true_area:.3f}"
        if not time_ok:
            details += f" time={runtime:.1f}s"
        runner.add("Assignment 5", TestResult(f"fit: {name}", passed, error, runtime, details))

    test_fit(0, 0, 1, 0.05, 5, "circle r=1 noise=0.05", 0.05)
    test_fit(1, 1, 1, 0.1, 5, "circle r=1 noise=0.1", 0.1)
    test_fit(0, 0, 2, 0.1, 5, "circle r=2 noise=0.1", 0.05)
    test_fit(5, -3, 3, 0.2, 5, "circle r=3 offset noise=0.2", 0.1)
    test_fit(0, 0, 10, 0.5, 10, "circle r=10 noise=0.5", 0.05)

    # Timing test
    sample = noisy_circle(cx=0, cy=0, radius=1, noise=0.1)
    t0 = time.time()
    shape = ass5.fit_shape(sample=sample, maxtime=3)
    T = time.time() - t0
    runner.add("Assignment 5", TestResult(f"timing maxtime=3 ({T:.1f}s)", T <= 5, None, T))


# ============================================================
# Main Entry Point
# ============================================================
if __name__ == "__main__":
    print("=" * 75)
    print("  NUMERICAL ANALYSIS & OPTIMIZATION - COMPREHENSIVE TEST SUITE")
    print("=" * 75)

    # Parse which assignments to run
    if len(sys.argv) > 1:
        assignments_to_run = [int(a) for a in sys.argv[1:] if a.isdigit()]
    else:
        assignments_to_run = [1, 2, 3, 4, 5]

    test_functions = {
        1: run_assignment1_tests,
        2: run_assignment2_tests,
        3: run_assignment3_tests,
        4: run_assignment4_tests,
        5: run_assignment5_tests,
    }

    for a in assignments_to_run:
        if a in test_functions:
            try:
                test_functions[a]()
            except Exception as e:
                print(f"\n  \033[91mERROR in Assignment {a}: {e}\033[0m")
                traceback.print_exc()

    runner.print_summary()
