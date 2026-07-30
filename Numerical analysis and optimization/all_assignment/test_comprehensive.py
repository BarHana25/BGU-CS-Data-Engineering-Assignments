"""
Comprehensive stress tests for Assignments 1-5.
Uses the course test functions f1-f11 plus random polynomials.
Measures accuracy and runtime for each test.
"""

import numpy as np
import time
import unittest
import sys

# ============================================================
# Course test functions f1-f11
# ============================================================

def f1(x):
    """f1(x) = 5"""
    return 5.0

def f2(x):
    """f2(x) = x^2 - 3x + 5"""
    return x**2 - 3*x + 5

def f3(x):
    """f3(x) = sin(x^2)"""
    return np.sin(x**2)

def f4(x):
    """f4(x) = e^(-2x^2)"""
    return np.exp(-2*x**2)

def f5(x):
    """f5(x) = arctan(x)"""
    return np.arctan(x)

def f6(x):
    """f6(x) = sin(x)/x"""
    x = float(x)
    if abs(x) < 1e-15:
        return 1.0
    return np.sin(x) / x

def f7(x):
    """f7(x) = 1/ln(x)"""
    x = float(x)
    lnx = np.log(x)
    if abs(lnx) < 1e-15:
        return float('inf')
    return 1.0 / lnx

def f8(x):
    """f8(x) = e^(e^x)"""
    return np.exp(np.exp(x))

def f9(x):
    """f9(x) = ln(ln(x))"""
    return np.log(np.log(x))

def f10(x):
    """f10(x) = sin(ln(x))"""
    return np.sin(np.log(x))

def f11(x):
    """f11(x) = 2^(1/x^2) * sin(1/x)"""
    x = float(x)
    if abs(x) < 1e-15:
        return 0.0
    return (2.0 ** (1.0 / (x**2))) * np.sin(1.0 / x)


# ============================================================
# Helper: generate random polynomial with coefficients in [-1,1]
# ============================================================
def random_poly(degree, seed=None):
    """Generate a random polynomial of given degree with coefficients in [-1, 1]."""
    if seed is not None:
        rng = np.random.RandomState(seed)
    else:
        rng = np.random.RandomState()
    coeffs = rng.uniform(-1, 1, degree + 1)
    return np.poly1d(coeffs)


# ============================================================
# Test Results Collector
# ============================================================
class TestResults:
    def __init__(self):
        self.results = []

    def add(self, assignment, test_name, passed, error=None, runtime=None, details=""):
        self.results.append({
            'assignment': assignment,
            'test': test_name,
            'passed': passed,
            'error': error,
            'runtime': runtime,
            'details': details
        })

    def summary(self):
        by_assignment = {}
        for r in self.results:
            a = r['assignment']
            if a not in by_assignment:
                by_assignment[a] = {'passed': 0, 'failed': 0, 'errors': [], 'runtimes': []}
            if r['passed']:
                by_assignment[a]['passed'] += 1
            else:
                by_assignment[a]['failed'] += 1
                by_assignment[a]['errors'].append(f"  FAIL: {r['test']}: {r['details']}")
            if r['error'] is not None and np.isfinite(r['error']):
                by_assignment[a]['errors_vals'] = by_assignment[a].get('errors_vals', [])
                by_assignment[a]['errors_vals'].append(r['error'])
            if r['runtime'] is not None:
                by_assignment[a]['runtimes'].append(r['runtime'])
        return by_assignment


results = TestResults()


# ============================================================
# ASSIGNMENT 1 TESTS - Interpolation
# ============================================================
class TestAssignment1Comprehensive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from assignment1 import Assignment1
        cls.ass1 = Assignment1()

    def _test_interpolate(self, f, a, b, n, test_name, n_eval=200, tol=None):
        """Helper: interpolate f on [a,b] with n points, evaluate at n_eval random points."""
        t0 = time.time()
        g = self.ass1.interpolate(f, a, b, n)
        runtime = time.time() - t0

        # Evaluate at random interior points
        xs = np.linspace(a + 0.01*(b-a), b - 0.01*(b-a), n_eval)
        errs = []
        for x in xs:
            try:
                yy = g(float(x))
                y = f(float(x))
                if np.isfinite(y) and np.isfinite(yy):
                    errs.append(abs(y - yy))
            except:
                pass

        mean_err = np.mean(errs) if errs else float('inf')
        results.add('Assignment1', test_name, True, error=mean_err, runtime=runtime)
        return mean_err, runtime

    # --- Course functions ---
    def test_f1_constant(self):
        err, _ = self._test_interpolate(f1, -5, 5, 10, "f1_constant_n10")
        self.assertLess(err, 1e-6)

    def test_f2_quadratic_n10(self):
        err, _ = self._test_interpolate(f2, -2, 5, 10, "f2_quad_n10")
        self.assertLess(err, 0.01)

    def test_f2_quadratic_n50(self):
        err, _ = self._test_interpolate(f2, -2, 5, 50, "f2_quad_n50")
        self.assertLess(err, 1e-6)

    def test_f3_sin_xsq_n50(self):
        err, _ = self._test_interpolate(f3, -2, 2, 50, "f3_sinx2_n50")
        self.assertLess(err, 0.1)

    def test_f3_sin_xsq_n100(self):
        err, _ = self._test_interpolate(f3, -2, 2, 100, "f3_sinx2_n100")
        self.assertLess(err, 0.01)

    def test_f4_gaussian_n20(self):
        err, _ = self._test_interpolate(f4, -3, 3, 20, "f4_gauss_n20")
        self.assertLess(err, 0.01)

    def test_f4_gaussian_n50(self):
        err, _ = self._test_interpolate(f4, -3, 3, 50, "f4_gauss_n50")
        self.assertLess(err, 1e-6)

    def test_f5_arctan_n20(self):
        err, _ = self._test_interpolate(f5, -10, 10, 20, "f5_arctan_n20")
        self.assertLess(err, 0.1)

    def test_f5_arctan_n100(self):
        err, _ = self._test_interpolate(f5, -10, 10, 100, "f5_arctan_n100")
        self.assertLess(err, 0.001)

    def test_f6_sinc_n50(self):
        err, _ = self._test_interpolate(f6, 0.1, 10, 50, "f6_sinc_n50")
        self.assertLess(err, 0.01)

    def test_f8_exp_exp_n50(self):
        err, _ = self._test_interpolate(f8, 0, 3, 50, "f8_expexp_n50")
        # This is a very steep function, allow larger error
        self.assertLess(err / abs(f8(1.5)), 0.1)

    def test_f10_sin_ln_n50(self):
        err, _ = self._test_interpolate(f10, 1, 10, 50, "f10_sinln_n50")
        self.assertLess(err, 0.001)

    # --- Random polynomials (>50% of tests) ---
    def test_random_poly_deg3_n10(self):
        for seed in range(5):
            p = random_poly(3, seed=seed)
            err, _ = self._test_interpolate(p, -1, 1, 10, f"rand_poly3_s{seed}_n10")
            self.assertLess(err, 0.01)

    def test_random_poly_deg5_n20(self):
        for seed in range(5):
            p = random_poly(5, seed=seed+10)
            err, _ = self._test_interpolate(p, -1, 1, 20, f"rand_poly5_s{seed}_n20")
            self.assertLess(err, 1e-4)

    def test_random_poly_deg10_n20(self):
        for seed in range(5):
            p = random_poly(10, seed=seed+20)
            err, _ = self._test_interpolate(p, -1, 1, 20, f"rand_poly10_s{seed}_n20")
            self.assertLess(err, 1.0)

    def test_random_poly_deg10_n50(self):
        for seed in range(5):
            p = random_poly(10, seed=seed+30)
            err, _ = self._test_interpolate(p, -1, 1, 50, f"rand_poly10_s{seed}_n50")
            self.assertLess(err, 0.01)

    def test_random_poly_deg15_n50(self):
        for seed in range(5):
            p = random_poly(15, seed=seed+40)
            err, _ = self._test_interpolate(p, -2, 2, 50, f"rand_poly15_s{seed}_n50")
            self.assertLess(err, 1.0)

    def test_random_poly_deg20_n100(self):
        for seed in range(5):
            p = random_poly(20, seed=seed+50)
            err, _ = self._test_interpolate(p, -1, 1, 100, f"rand_poly20_s{seed}_n100")
            self.assertLess(err, 1.0)

    # --- Edge cases ---
    def test_n1_returns_constant(self):
        g = self.ass1.interpolate(f2, 0, 1, 1)
        val = g(0.5)
        self.assertTrue(np.isfinite(val))

    def test_n2_returns_linear(self):
        g = self.ass1.interpolate(f2, 0, 1, 2)
        val = g(0.5)
        self.assertTrue(np.isfinite(val))

    def test_wide_range(self):
        err, _ = self._test_interpolate(f2, -100, 100, 50, "f2_wide_n50")
        self.assertLess(err, 100)

    def test_narrow_range(self):
        err, _ = self._test_interpolate(np.sin, 0, 0.01, 10, "sin_narrow_n10")
        self.assertLess(err, 1e-6)


# ============================================================
# ASSIGNMENT 2 TESTS - Intersections
# ============================================================
class TestAssignment2Comprehensive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from assignment2 import Assignment2
        cls.ass2 = Assignment2()

    def _test_intersections(self, f1, f2, a, b, maxerr, test_name, expected_min=None):
        """Helper: find intersections and verify they satisfy |f1(x)-f2(x)| < maxerr."""
        t0 = time.time()
        X = self.ass2.intersections(f1, f2, a, b, maxerr=maxerr)
        runtime = time.time() - t0

        X = list(X) if X else []
        all_valid = True
        max_residual = 0.0
        for x in X:
            residual = abs(f1(x) - f2(x))
            max_residual = max(max_residual, residual)
            if residual > maxerr:
                all_valid = False

        passed = all_valid and (expected_min is None or len(X) >= expected_min)
        details = f"found={len(X)}, max_resid={max_residual:.2e}"
        if expected_min and len(X) < expected_min:
            details += f", expected>={expected_min}"
        results.add('Assignment2', test_name, passed, error=max_residual, runtime=runtime, details=details)
        return X, runtime

    # --- Known intersection cases ---
    def test_quadratics_known(self):
        # x^2-1 and 1-x^2 intersect at x = ±1/sqrt(2) ≈ ±0.707
        g1 = lambda x: x**2 - 1
        g2 = lambda x: 1 - x**2
        X, _ = self._test_intersections(g1, g2, -2, 2, 0.001, "quad_known", expected_min=2)
        self.assertGreaterEqual(len(X), 2)
        for x in X:
            self.assertLessEqual(abs(g1(x) - g2(x)), 0.001)

    def test_sin_cos(self):
        X, _ = self._test_intersections(np.sin, np.cos, 0, 2*np.pi, 0.001, "sin_cos", expected_min=2)
        self.assertGreaterEqual(len(X), 2)

    def test_poly_vs_constant(self):
        p = lambda x: x**3 - 3*x
        c = lambda x: 0.0
        X, _ = self._test_intersections(p, c, -3, 3, 0.001, "poly_vs_const", expected_min=3)
        self.assertGreaterEqual(len(X), 3)

    def test_f2_vs_f5(self):
        # f2 = x^2-3x+5, f5 = arctan(x) - should intersect in [-5, 5]
        X, _ = self._test_intersections(f2, f5, -5, 5, 0.001, "f2_vs_f5")
        for x in X:
            self.assertLessEqual(abs(f2(x) - f5(x)), 0.001)

    def test_f3_vs_f4(self):
        # sin(x^2) vs e^(-2x^2) on [-2, 2]
        X, _ = self._test_intersections(f3, f4, -2, 2, 0.001, "f3_vs_f4")
        for x in X:
            self.assertLessEqual(abs(f3(x) - f4(x)), 0.001)

    def test_tangent_case(self):
        # x^2 and 2x-1 are tangent at x=1
        g1 = lambda x: x**2
        g2 = lambda x: 2*x - 1
        X, _ = self._test_intersections(g1, g2, -2, 3, 0.01, "tangent")
        # Tangent intersections are hard; just verify no false positives
        for x in X:
            self.assertLessEqual(abs(g1(x) - g2(x)), 0.01)

    # --- Random polynomial pairs (>50% of tests) ---
    def test_random_poly_pairs(self):
        for seed in range(10):
            p1 = random_poly(4, seed=seed*2)
            p2 = random_poly(4, seed=seed*2+1)
            X, _ = self._test_intersections(p1, p2, -2, 2, 0.001, f"rand_poly4_s{seed}")
            for x in X:
                self.assertLessEqual(abs(p1(x) - p2(x)), 0.001)

    def test_random_poly_high_degree(self):
        for seed in range(5):
            p1 = random_poly(6, seed=seed+100)
            p2 = random_poly(6, seed=seed+200)
            X, _ = self._test_intersections(p1, p2, -1, 1, 0.001, f"rand_poly6_s{seed}")
            for x in X:
                self.assertLessEqual(abs(p1(x) - p2(x)), 0.001)

    # --- Edge cases ---
    def test_no_intersection(self):
        g1 = lambda x: x**2 + 10
        g2 = lambda x: -x**2 - 10
        X, _ = self._test_intersections(g1, g2, -5, 5, 0.001, "no_intersect")
        self.assertEqual(len(X), 0)

    def test_small_maxerr(self):
        g1 = lambda x: x**2
        g2 = lambda x: x
        X, _ = self._test_intersections(g1, g2, -2, 2, 0.0001, "small_maxerr", expected_min=2)
        for x in X:
            self.assertLessEqual(abs(g1(x) - g2(x)), 0.0001)

    def test_many_intersections(self):
        g1 = np.sin
        g2 = lambda x: 0.0
        X, _ = self._test_intersections(g1, g2, 0, 10, 0.001, "many_inter", expected_min=3)
        for x in X:
            self.assertLessEqual(abs(g1(x) - g2(x)), 0.001)


# ============================================================
# ASSIGNMENT 3 TESTS - Integration
# ============================================================
class TestAssignment3Comprehensive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from assignment3 import Assignment3
        cls.ass3 = Assignment3()

    def _test_integrate(self, f, a, b, n, true_val, test_name, rel_tol=0.01):
        """Helper: integrate and compare to known value."""
        t0 = time.time()
        result = self.ass3.integrate(f, a, b, n)
        runtime = time.time() - t0

        result_f = float(result)
        if abs(true_val) > 1e-10:
            error = abs(result_f - true_val) / abs(true_val)
        else:
            error = abs(result_f - true_val)

        passed = error <= rel_tol
        details = f"result={result_f:.6e}, true={true_val:.6e}, rel_err={error:.4e}"
        results.add('Assignment3', test_name, passed, error=error, runtime=runtime, details=details)

        self.assertEqual(result.dtype, np.float32, f"{test_name}: dtype not float32")
        return result_f, error, runtime

    # --- Known integrals ---
    def test_f1_constant(self):
        # integral of 5 from 0 to 3 = 15
        _, err, _ = self._test_integrate(f1, 0, 3, 10, 15.0, "f1_const_n10")
        self.assertLess(err, 1e-6)

    def test_f2_quadratic_n10(self):
        # integral of x^2-3x+5 from 0 to 3 = [x^3/3 - 3x^2/2 + 5x]_0^3 = 9-13.5+15 = 10.5
        _, err, _ = self._test_integrate(f2, 0, 3, 10, 10.5, "f2_quad_n10")
        self.assertLess(err, 0.001)

    def test_f2_quadratic_n50(self):
        _, err, _ = self._test_integrate(f2, 0, 3, 50, 10.5, "f2_quad_n50")
        self.assertLess(err, 1e-8)

    def test_f4_gaussian_n20(self):
        # integral of e^(-2x^2) from -3 to 3 ≈ sqrt(pi/2) ≈ 1.2533
        true_val = np.sqrt(np.pi / 2)
        _, err, _ = self._test_integrate(f4, -3, 3, 20, true_val, "f4_gauss_n20", rel_tol=0.01)
        self.assertLess(err, 0.01)

    def test_f4_gaussian_n100(self):
        true_val = np.sqrt(np.pi / 2)
        _, err, _ = self._test_integrate(f4, -3, 3, 100, true_val, "f4_gauss_n100", rel_tol=0.001)
        self.assertLess(err, 0.001)

    def test_sin_n11(self):
        # integral of sin from 0 to pi = 2
        _, err, _ = self._test_integrate(np.sin, 0, np.pi, 11, 2.0, "sin_n11")
        self.assertLess(err, 0.001)

    def test_sin_n101(self):
        _, err, _ = self._test_integrate(np.sin, 0, np.pi, 101, 2.0, "sin_n101")
        self.assertLess(err, 1e-8)

    def test_f5_arctan_n50(self):
        # integral of arctan(x) from 0 to 1 = pi/4 - ln(2)/2 ≈ 0.4388
        true_val = np.pi/4 - np.log(2)/2
        _, err, _ = self._test_integrate(f5, 0, 1, 50, true_val, "f5_arctan_n50")
        self.assertLess(err, 0.001)

    def test_f11_hard(self):
        # The hard case from the original test
        _, err, _ = self._test_integrate(f11, 0.09, 10, 20, -7.78662e33, "f11_hard_n20", rel_tol=0.001)
        self.assertLess(err, 0.001)

    # --- Random polynomials (>50% of tests) ---
    def test_random_poly_exact_simpson(self):
        """Simpson's rule is exact for polynomials up to degree 3."""
        for seed in range(10):
            p = random_poly(3, seed=seed+60)
            # True integral via numpy
            p_int = np.polyint(p)
            true_val = float(p_int(1) - p_int(-1))
            _, err, _ = self._test_integrate(p, -1, 1, 5, true_val, f"rand_poly3_exact_s{seed}", rel_tol=1e-6)
            self.assertLess(err, 1e-5)

    def test_random_poly_deg5_n20(self):
        for seed in range(5):
            p = random_poly(5, seed=seed+70)
            p_int = np.polyint(p)
            true_val = float(p_int(2) - p_int(-2))
            _, err, _ = self._test_integrate(p, -2, 2, 20, true_val, f"rand_poly5_n20_s{seed}", rel_tol=0.01)
            self.assertLess(err, 0.01)

    def test_random_poly_deg8_n50(self):
        for seed in range(5):
            p = random_poly(8, seed=seed+80)
            p_int = np.polyint(p)
            true_val = float(p_int(1) - p_int(-1))
            _, err, _ = self._test_integrate(p, -1, 1, 50, true_val, f"rand_poly8_n50_s{seed}", rel_tol=0.001)
            self.assertLess(err, 0.001)

    # --- Edge cases ---
    def test_n1_midpoint(self):
        r = self.ass3.integrate(np.sin, 0, np.pi, 1)
        self.assertEqual(r.dtype, np.float32)
        self.assertTrue(np.isfinite(float(r)))

    def test_n2_trapezoidal(self):
        r = self.ass3.integrate(np.sin, 0, np.pi, 2)
        self.assertEqual(r.dtype, np.float32)
        # Trapezoidal on sin(0..pi) = 0 (endpoints are 0)
        self.assertLess(abs(float(r)), 0.01)

    def test_even_n(self):
        _, err, _ = self._test_integrate(np.sin, 0, np.pi, 10, 2.0, "sin_even_n10", rel_tol=0.01)
        self.assertLess(err, 0.01)

    def test_negative_integral(self):
        _, err, _ = self._test_integrate(np.sin, np.pi, 2*np.pi, 11, -2.0, "sin_neg_n11")
        self.assertLess(err, 0.001)


# ============================================================
# ASSIGNMENT 4 TESTS - Fitting
# ============================================================
class TestAssignment4Comprehensive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from assignment4 import Assignment4
        cls.ass4 = Assignment4()

    def _test_fit(self, f, a, b, d, noise, maxtime, test_name, n_eval=200, tol=None):
        """Helper: fit noisy f, evaluate fit quality on clean f."""
        from functionUtils import NOISY
        nf = NOISY(noise)(f)
        t0 = time.time()
        g = self.ass4.fit(f=nf, a=a, b=b, d=d, maxtime=maxtime)
        runtime = time.time() - t0

        # Evaluate MSE on clean function
        xs = np.linspace(a, b, n_eval)
        mse = 0.0
        for x in xs:
            mse += (f(x) - g(x))**2
        mse /= n_eval

        passed = runtime <= maxtime + 5
        details = f"MSE={mse:.4e}, runtime={runtime:.2f}s (limit={maxtime}s)"
        results.add('Assignment4', test_name, passed, error=mse, runtime=runtime, details=details)
        self.assertLessEqual(runtime, maxtime + 5, f"{test_name}: exceeded time limit")
        return mse, runtime

    # --- Course functions with noise ---
    def test_f1_constant_noise(self):
        mse, _ = self._test_fit(f1, 0, 5, 5, 0.5, 5, "f1_const_noise0.5")
        self.assertLess(mse, 1.0)

    def test_f2_quadratic_noise(self):
        mse, _ = self._test_fit(f2, -2, 5, 5, 0.5, 5, "f2_quad_noise0.5")
        self.assertLess(mse, 2.0)

    def test_f5_arctan_noise(self):
        mse, _ = self._test_fit(f5, -5, 5, 8, 0.1, 5, "f5_arctan_noise0.1")
        self.assertLess(mse, 0.5)

    def test_f4_gaussian_noise(self):
        mse, _ = self._test_fit(f4, -3, 3, 10, 0.05, 5, "f4_gauss_noise0.05")
        self.assertLess(mse, 0.1)

    # --- Random polynomials with noise (>50% of tests) ---
    def test_random_poly_deg2_noise01(self):
        for seed in range(5):
            p = random_poly(2, seed=seed+90)
            mse, _ = self._test_fit(p, -1, 1, 5, 0.1, 5, f"rand_poly2_noise01_s{seed}")
            self.assertLess(mse, 0.5)

    def test_random_poly_deg3_noise05(self):
        for seed in range(5):
            p = random_poly(3, seed=seed+100)
            mse, _ = self._test_fit(p, -1, 1, 5, 0.5, 5, f"rand_poly3_noise05_s{seed}")
            self.assertLess(mse, 2.0)

    def test_random_poly_deg5_noise01(self):
        for seed in range(3):
            p = random_poly(5, seed=seed+110)
            mse, _ = self._test_fit(p, -1, 1, 8, 0.1, 5, f"rand_poly5_noise01_s{seed}")
            self.assertLess(mse, 1.0)

    # --- Edge cases ---
    def test_maxtime_respected(self):
        """Fit should return within maxtime+5 even with slow function."""
        from functionUtils import DELAYED, NOISY
        slow_f = DELAYED(3)(NOISY(0.01)(f1))
        t0 = time.time()
        g = self.ass4.fit(f=slow_f, a=0, b=1, d=5, maxtime=5)
        T = time.time() - t0
        # Allow maxtime + 10 for slow functions (a call started before deadline finishes after)
        self.assertLessEqual(T, 15)
        results.add('Assignment4', 'maxtime_respected', T <= 15, runtime=T)

    def test_degree_1(self):
        p = np.poly1d([2, 1])  # 2x + 1
        mse, _ = self._test_fit(p, 0, 1, 1, 0.1, 5, "linear_d1")
        self.assertLess(mse, 0.5)


# ============================================================
# ASSIGNMENT 5 TESTS - Shape Area
# ============================================================
class TestAssignment5Comprehensive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from assignment5 import Assignment5
        from sampleFunctions import Circle
        cls.ass5 = Assignment5()
        cls.Circle = Circle

    def _test_area(self, contour_func, true_area, test_name, maxerr=0.001):
        """Helper: test the area() method."""
        t0 = time.time()
        computed = self.ass5.area(contour_func, maxerr=maxerr)
        runtime = time.time() - t0

        if abs(true_area) > 1e-10:
            error = abs(float(computed) - true_area) / abs(true_area)
        else:
            error = abs(float(computed) - true_area)

        passed = error <= maxerr * 5  # Allow some slack
        details = f"computed={float(computed):.6f}, true={true_area:.6f}, rel_err={error:.4e}"
        results.add('Assignment5', test_name, passed, error=error, runtime=runtime, details=details)
        return float(computed), error, runtime

    def _test_fit_shape(self, sample_func, true_area, test_name, maxtime=5, tol=0.1):
        """Helper: test fit_shape() and area of fitted shape."""
        t0 = time.time()
        shape = self.ass5.fit_shape(sample=sample_func, maxtime=maxtime)
        runtime = time.time() - t0

        fitted_area = shape.area()
        if abs(true_area) > 1e-10:
            error = abs(fitted_area - true_area) / abs(true_area)
        else:
            error = abs(fitted_area - true_area)

        passed = (runtime <= maxtime + 2) and (error <= tol)
        details = f"area={fitted_area:.4f}, true={true_area:.4f}, rel_err={error:.4f}, time={runtime:.2f}s"
        results.add('Assignment5', test_name, passed, error=error, runtime=runtime, details=details)
        self.assertLessEqual(runtime, maxtime + 2, f"{test_name}: exceeded time")
        return fitted_area, error, runtime

    # --- Area tests with known contours ---
    def test_area_circle(self):
        circ = self.Circle(0, 0, 1, 0)
        _, err, _ = self._test_area(circ.contour, np.pi, "area_unit_circle")
        self.assertLess(err, 0.001)

    def test_area_circle_r5(self):
        circ = self.Circle(2, 3, 5, 0)
        _, err, _ = self._test_area(circ.contour, 25*np.pi, "area_circle_r5")
        self.assertLess(err, 0.001)

    def test_area_square(self):
        """Test with a square contour."""
        def square_contour(n):
            pts = []
            per_side = max(1, n // 4)
            for i in range(per_side):
                t = i / per_side
                pts.append([t, 0])
            for i in range(per_side):
                t = i / per_side
                pts.append([1, t])
            for i in range(per_side):
                t = i / per_side
                pts.append([1-t, 1])
            for i in range(per_side):
                t = i / per_side
                pts.append([0, 1-t])
            return np.array(pts[:n], dtype=np.float32)

        _, err, _ = self._test_area(square_contour, 1.0, "area_square")
        self.assertLess(err, 0.05)

    # --- Fit shape tests ---
    def test_fit_circle_small_noise(self):
        from sampleFunctions import noisy_circle
        sample = noisy_circle(cx=0, cy=0, radius=2, noise=0.05)
        _, err, _ = self._test_fit_shape(sample, 4*np.pi, "fit_circle_noise005", maxtime=5, tol=0.05)
        self.assertLess(err, 0.05)

    def test_fit_circle_medium_noise(self):
        from sampleFunctions import noisy_circle
        sample = noisy_circle(cx=1, cy=1, radius=1, noise=0.1)
        _, err, _ = self._test_fit_shape(sample, np.pi, "fit_circle_noise01", maxtime=5, tol=0.1)
        self.assertLess(err, 0.1)

    def test_fit_circle_large_radius(self):
        from sampleFunctions import noisy_circle
        sample = noisy_circle(cx=0, cy=0, radius=10, noise=0.5)
        _, err, _ = self._test_fit_shape(sample, 100*np.pi, "fit_circle_r10", maxtime=10, tol=0.05)
        self.assertLess(err, 0.05)

    def test_fit_circle_offset(self):
        from sampleFunctions import noisy_circle
        sample = noisy_circle(cx=5, cy=-3, radius=3, noise=0.2)
        _, err, _ = self._test_fit_shape(sample, 9*np.pi, "fit_circle_offset", maxtime=5, tol=0.1)
        self.assertLess(err, 0.1)

    # --- Edge cases ---
    def test_fit_shape_timing(self):
        """Shape fitting must return within maxtime."""
        from sampleFunctions import noisy_circle
        sample = noisy_circle(cx=0, cy=0, radius=1, noise=0.1)
        t0 = time.time()
        shape = self.ass5.fit_shape(sample=sample, maxtime=3)
        T = time.time() - t0
        self.assertLessEqual(T, 5)
        results.add('Assignment5', 'timing_check', T <= 5, runtime=T)


# ============================================================
# Main: run all tests and print summary
# ============================================================
if __name__ == "__main__":
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestAssignment1Comprehensive))
    suite.addTests(loader.loadTestsFromTestCase(TestAssignment2Comprehensive))
    suite.addTests(loader.loadTestsFromTestCase(TestAssignment3Comprehensive))
    suite.addTests(loader.loadTestsFromTestCase(TestAssignment4Comprehensive))
    suite.addTests(loader.loadTestsFromTestCase(TestAssignment5Comprehensive))

    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*70)

    summary = results.summary()
    for assign in sorted(summary.keys()):
        data = summary[assign]
        total = data['passed'] + data['failed']
        avg_runtime = np.mean(data['runtimes']) if data['runtimes'] else 0
        avg_error = np.mean(data.get('errors_vals', [0]))
        print(f"\n{assign}:")
        print(f"  Tests: {data['passed']}/{total} passed, {data['failed']} failed")
        print(f"  Avg runtime: {avg_runtime*1000:.2f}ms")
        print(f"  Avg error:   {avg_error:.4e}")
        if data['failed'] > 0:
            print(f"  Failures:")
            for e in data.get('errors', []):
                print(f"    {e}")

    print("\n" + "="*70)
