#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2026 Steven Lamar Michael. All rights reserved.

c180_cascade_moduli_metric.py — Python parity guard for CLM-046.

Every ℚ/ℤ literal that appears in `proofs/UFT/lean/CascadeModuliMetric.lean`
is mirrored here as a `Fraction`/`int` assertEqual.  Per
`feedback_lean_only_bugs.md` (2026-04-17): Lean-only arithmetic that lacks
a Python mirror is a blind spot until Mac-side `lake build` runs.  This
guard closes that blind spot for CLM-046's Killing-form = A_7 Cartan matrix
identity.

SCOPE (see Oracle/claims/CLM-046-cascade-moduli-metric-equals-cartan.md):

  Tightens the CLM-031 spectral-identification postulate by proving that
  the Killing form on SU(8) restricted to the simple-coroot basis equals
  the A_7 Cartan matrix entry-for-entry, up to a uniform positive
  prefactor 16.  The prefactor cancels in any spectral ratio
  (mean-inverse-eigenvalue, determinant, Kirchhoff index), so the cascade
  CG identification is normalization-independent.

MATHEMATICAL CONTENT:

  Simple coroots H_i of A_7 ⊂ su(8), i = 0, …, 6, are diagonal 8×8 matrices
      H_i = diag(0, …, 0, +1, −1, 0, …, 0)
                         ^i   ^i+1
  with trace zero (the su(8), not u(8), condition).

  Killing form on SU(N) fundamental:  K(X, Y) = 2N · Tr(X · Y).
  For SU(8):  K(X, Y) = 16 · Tr(X · Y).

  For diagonal X, Y:  Tr(X · Y) = Σ_k X[k,k] · Y[k,k].

  A_7 Cartan matrix:  C(A_7)_{ij} = 2 δ_{ij} − δ_{|i−j|, 1}.

  **Main identity:**
      K(H_i, H_j) = 16 · Tr(H_i · H_j) = 16 · C(A_7)_{ij}.

ZERO FLOATS.  All arithmetic uses Fraction or int.  Commandment XII.
"""

from fractions import Fraction
import unittest


# ---------------------------------------------------------------------------
# Section 1 — Simple coroot entries as integer-valued functions.
# ---------------------------------------------------------------------------

def coroot_entry(i: int, k: int) -> int:
    """
    (k, k) diagonal entry of the i-th simple coroot H_i of A_7 ⊂ su(8).

    Valid for i ∈ {0, …, 6} and k ∈ {0, …, 7}.  Mirrors the Lean
    `coroot_entry` definition exactly.
    """
    if k == i:
        return 1
    if k == i + 1:
        return -1
    return 0


def coroot_diag_sum(i: int) -> int:
    """Tracelessness check: Σ_{k=0}^{7} coroot_entry(i, k) for i ∈ {0..6}."""
    return sum(coroot_entry(i, k) for k in range(8))


# ---------------------------------------------------------------------------
# Section 2 — Trace products Tr(H_i · H_j) as explicit 8-term sums.
# ---------------------------------------------------------------------------

def trace_prod(i: int, j: int) -> int:
    """
    Tr(H_i · H_j) = Σ_{k=0}^{7} coroot_entry(i, k) · coroot_entry(j, k).

    For diagonal matrices the product's trace reduces to a sum of
    position-by-position products.  Mirrors the Lean `trace_prod`
    definition exactly.
    """
    return sum(coroot_entry(i, k) * coroot_entry(j, k) for k in range(8))


# ---------------------------------------------------------------------------
# Section 3 — Killing form on SU(8).
# ---------------------------------------------------------------------------

N_SU = 8  # SU(N) with N = 8 — the rank of the fundamental.
KILLING_PREFACTOR = 2 * N_SU  # 2N = 16 for SU(8).


def killing_su8(n: int) -> Fraction:
    """
    Killing form on SU(8) fundamental:  K(X, Y) = 2N · Tr(X · Y) with N = 8.

    Here `n = Tr(X · Y)` is an already-computed integer trace, and the
    result is the ℚ-valued Killing-form value.
    """
    return Fraction(KILLING_PREFACTOR) * Fraction(n)


# ---------------------------------------------------------------------------
# Section 4 — A_7 Cartan matrix as an integer-valued function.
# ---------------------------------------------------------------------------

def cartan_A7_entry(i: int, j: int) -> int:
    """
    (i, j) entry of the A_7 Cartan matrix: tridiagonal(2, −1).

    Valid for i, j ∈ {0, …, 6}.  Mirrors the Lean `cartan_A7_entry`
    definition exactly.
    """
    if i == j:
        return 2
    if i + 1 == j:
        return -1
    if j + 1 == i:
        return -1
    return 0


# ---------------------------------------------------------------------------
# Section 5 — CLM-032 bridge: cartan_mean_inv and cg_rat.
#
# These mirror `CascadeCGRepTheory.lean` exactly for bridge tests.
# ---------------------------------------------------------------------------

def cartan_mean_inv(n: int) -> Fraction:
    """⟨λ⁻¹⟩(A_n) = (n+2)/6 as an exact Fraction."""
    assert n >= 1
    return Fraction(n + 2, 6)


def cg_rat(n: int) -> Fraction:
    """Rep-theoretic cascade CG at rank n: (n+1)/(n+2)."""
    assert n >= 2
    return cartan_mean_inv(n - 1) / cartan_mean_inv(n)


# ===========================================================================
# TESTS — 10 classes, ~54 tests total.
# ===========================================================================


class SimpleCorootTests(unittest.TestCase):
    """Mirror Section 1 coroot_entry spot-checks and tracelessness."""

    def test_coroot_entry_0_0(self):
        self.assertEqual(coroot_entry(0, 0), 1)

    def test_coroot_entry_0_1(self):
        self.assertEqual(coroot_entry(0, 1), -1)

    def test_coroot_entry_0_2(self):
        self.assertEqual(coroot_entry(0, 2), 0)

    def test_coroot_entry_3_3(self):
        self.assertEqual(coroot_entry(3, 3), 1)

    def test_coroot_entry_3_4(self):
        self.assertEqual(coroot_entry(3, 4), -1)

    def test_coroot_entry_6_6(self):
        self.assertEqual(coroot_entry(6, 6), 1)

    def test_coroot_entry_6_7(self):
        self.assertEqual(coroot_entry(6, 7), -1)

    def test_coroot_traceless_all(self):
        """Every simple coroot H_i has Σ_k (H_i)_{k,k} = 0."""
        for i in range(7):
            with self.subTest(i=i):
                self.assertEqual(coroot_diag_sum(i), 0)

    def test_coroot_entry_bounds(self):
        """Every entry is in {−1, 0, +1} for i < 7, k < 8."""
        for i in range(7):
            for k in range(8):
                self.assertIn(coroot_entry(i, k), (-1, 0, 1))


class TraceProductTests(unittest.TestCase):
    """Mirror Section 2 trace_prod diagonal, adjacent, and far entries."""

    def test_trace_prod_diag_all(self):
        """Tr(H_i · H_i) = 2 for every i ∈ {0..6}."""
        for i in range(7):
            with self.subTest(i=i):
                self.assertEqual(trace_prod(i, i), 2)

    def test_trace_prod_adj_pairs(self):
        """Tr(H_i · H_{i±1}) = −1 for all adjacent (i, j) pairs."""
        adj_pairs = [
            (0, 1), (1, 0),
            (1, 2), (2, 1),
            (2, 3), (3, 2),
            (3, 4), (4, 3),
            (4, 5), (5, 4),
            (5, 6), (6, 5),
        ]
        for i, j in adj_pairs:
            with self.subTest(i=i, j=j):
                self.assertEqual(trace_prod(i, j), -1)

    def test_trace_prod_far_selected(self):
        """Tr(H_i · H_j) = 0 for |i − j| ≥ 2 (selected spot-checks)."""
        far_pairs = [
            (0, 2), (0, 3), (0, 6),
            (2, 4), (3, 6), (1, 4),
        ]
        for i, j in far_pairs:
            with self.subTest(i=i, j=j):
                self.assertEqual(trace_prod(i, j), 0)

    def test_trace_prod_symm_all(self):
        """Tr(H_i · H_j) = Tr(H_j · H_i) for all i, j ∈ {0..6}."""
        for i in range(7):
            for j in range(7):
                with self.subTest(i=i, j=j):
                    self.assertEqual(trace_prod(i, j), trace_prod(j, i))


class KillingFormTests(unittest.TestCase):
    """Mirror Section 3 killing_su8 prefactor and spot-checks."""

    def test_killing_su8_prefactor(self):
        """The SU(8) Killing-form prefactor is 2·N = 16."""
        self.assertEqual(KILLING_PREFACTOR, 16)
        self.assertEqual(N_SU, 8)

    def test_killing_su8_on_zero(self):
        self.assertEqual(killing_su8(0), Fraction(0))

    def test_killing_su8_on_2(self):
        self.assertEqual(killing_su8(2), Fraction(32))

    def test_killing_su8_on_neg1(self):
        self.assertEqual(killing_su8(-1), Fraction(-16))

    def test_killing_su8_linearity(self):
        """killing_su8 is ℤ-linear: K(a + b) = K(a) + K(b)."""
        for a, b in [(2, -1), (0, 5), (-3, 7), (2, 0)]:
            with self.subTest(a=a, b=b):
                self.assertEqual(
                    killing_su8(a + b),
                    killing_su8(a) + killing_su8(b),
                )


class CartanMatrixParityTests(unittest.TestCase):
    """Mirror Section 4 A_7 Cartan entry spot-checks."""

    def test_cartan_A7_diag_0(self):
        self.assertEqual(cartan_A7_entry(0, 0), 2)

    def test_cartan_A7_diag_6(self):
        self.assertEqual(cartan_A7_entry(6, 6), 2)

    def test_cartan_A7_adj_01(self):
        self.assertEqual(cartan_A7_entry(0, 1), -1)

    def test_cartan_A7_adj_10(self):
        self.assertEqual(cartan_A7_entry(1, 0), -1)

    def test_cartan_A7_adj_56(self):
        self.assertEqual(cartan_A7_entry(5, 6), -1)

    def test_cartan_A7_far_02(self):
        self.assertEqual(cartan_A7_entry(0, 2), 0)

    def test_cartan_A7_far_06(self):
        self.assertEqual(cartan_A7_entry(0, 6), 0)

    def test_cartan_A7_symmetric(self):
        """C(A_7) is symmetric: C_{ij} = C_{ji} for all i, j < 7."""
        for i in range(7):
            for j in range(7):
                with self.subTest(i=i, j=j):
                    self.assertEqual(
                        cartan_A7_entry(i, j), cartan_A7_entry(j, i)
                    )


class MasterIdentityTests(unittest.TestCase):
    """The core CLM-046 identity: Tr(H_i · H_j) = C(A_7)_{ij} entry-for-entry."""

    def test_trace_prod_equals_cartan_all_49(self):
        """Sweep all 49 entries i, j ∈ {0..6}: trace_prod(i,j) = cartan_A7_entry(i,j)."""
        for i in range(7):
            for j in range(7):
                with self.subTest(i=i, j=j):
                    self.assertEqual(
                        trace_prod(i, j), cartan_A7_entry(i, j)
                    )

    def test_moduli_metric_equals_cartan_all_49(self):
        """K(H_i, H_j) = 16 · C(A_7)_{ij} for all i, j < 7."""
        for i in range(7):
            for j in range(7):
                with self.subTest(i=i, j=j):
                    lhs = killing_su8(trace_prod(i, j))
                    rhs = Fraction(16) * Fraction(cartan_A7_entry(i, j))
                    self.assertEqual(lhs, rhs)

    def test_moduli_metric_diag_is_32(self):
        """K(H_i, H_i) = 32 for every i ∈ {0..6}."""
        for i in range(7):
            with self.subTest(i=i):
                self.assertEqual(killing_su8(trace_prod(i, i)), Fraction(32))

    def test_moduli_metric_adj_is_neg16(self):
        """K(H_i, H_j) = −16 for every adjacent pair."""
        for i, j in [(0, 1), (2, 3), (5, 6), (3, 2)]:
            with self.subTest(i=i, j=j):
                self.assertEqual(killing_su8(trace_prod(i, j)), Fraction(-16))


class MeanInverseRatioTests(unittest.TestCase):
    """Mirror Section 6 mean-inverse-eigenvalue ratios and cross-multiply."""

    def test_cartan_mean_inv_A6(self):
        self.assertEqual(cartan_mean_inv(6), Fraction(8, 6))

    def test_cartan_mean_inv_A7(self):
        self.assertEqual(cartan_mean_inv(7), Fraction(9, 6))

    def test_mean_inv_cross_multiply(self):
        """8 · ⟨λ⁻¹⟩(A_7) = 9 · ⟨λ⁻¹⟩(A_6)."""
        lhs = Fraction(8) * cartan_mean_inv(7)
        rhs = Fraction(9) * cartan_mean_inv(6)
        self.assertEqual(lhs, rhs)

    def test_mean_inv_ratio_A7_over_A6_is_9_over_8(self):
        """cartan_mean_inv(7) / cartan_mean_inv(6) = 9/8."""
        self.assertEqual(
            cartan_mean_inv(7) / cartan_mean_inv(6),
            Fraction(9, 8),
        )

    def test_mean_inv_ratio_A6_over_A7_is_8_over_9(self):
        """cartan_mean_inv(6) / cartan_mean_inv(7) = 8/9 = CG."""
        self.assertEqual(
            cartan_mean_inv(6) / cartan_mean_inv(7),
            Fraction(8, 9),
        )


class UniformPrefactorCancellationTests(unittest.TestCase):
    """The factor 16 in K = 16·C cancels in any spectral ratio."""

    def test_bare_cartan_ratio_is_8_over_9(self):
        self.assertEqual(
            cartan_mean_inv(6) / cartan_mean_inv(7),
            Fraction(8, 9),
        )

    def test_scaled_cartan_ratio_is_8_over_9(self):
        """(16 · ⟨λ⁻¹⟩(A_6)) / (16 · ⟨λ⁻¹⟩(A_7)) = 8/9, same as bare."""
        scaled_A6 = Fraction(16) * cartan_mean_inv(6)
        scaled_A7 = Fraction(16) * cartan_mean_inv(7)
        self.assertEqual(scaled_A6 / scaled_A7, Fraction(8, 9))

    def test_arbitrary_prefactor_cancels(self):
        """For any positive rational α, (α·A_6) / (α·A_7) = 8/9."""
        for alpha in [
            Fraction(1),
            Fraction(16),
            Fraction(1, 16),
            Fraction(137, 42),
            Fraction(63, 8),  # the Fisher-information γ from C124
        ]:
            with self.subTest(alpha=alpha):
                scaled_A6 = alpha * cartan_mean_inv(6)
                scaled_A7 = alpha * cartan_mean_inv(7)
                self.assertEqual(scaled_A6 / scaled_A7, Fraction(8, 9))


class BridgeToCLM032Tests(unittest.TestCase):
    """The moduli-metric ratio agrees with CLM-032's rep-theory CG."""

    def test_cg_rat_at_A7_is_8_over_9(self):
        """CLM-032 anchor: cg_rat(7) = 8/9."""
        self.assertEqual(cg_rat(7), Fraction(8, 9))

    def test_moduli_metric_and_rep_theory_agree(self):
        """cartan_mean_inv(6) / cartan_mean_inv(7) = cg_rat(7)."""
        self.assertEqual(
            cartan_mean_inv(6) / cartan_mean_inv(7),
            cg_rat(7),
        )

    def test_full_cascade_ratio_chain(self):
        """Spot-check the rep-theory cascade at several ranks."""
        expected = {
            2: Fraction(3, 4),
            5: Fraction(6, 7),
            6: Fraction(7, 8),
            7: Fraction(8, 9),
            8: Fraction(9, 10),
        }
        for n, ratio in expected.items():
            with self.subTest(n=n):
                self.assertEqual(cg_rat(n), ratio)


class ScopeBoundaryTests(unittest.TestCase):
    """Document (in executable form) what CLM-046 does NOT close."""

    def test_does_not_close_higher_loop_Z_uniformity(self):
        """
        CLM-046 does NOT prove higher-loop wavefunction renormalization
        Z_i(μ) is uniform across cascade nodes.  CLM-042 (reconnaissance),
        CLM-043 (minimal-coupling honest-negative), CLM-044 (non-minimal
        honest-negative) document the three honest 1-loop attempts.
        """
        open_gap = "Z_i(μ) uniform across cascade nodes — NOT CLOSED by CLM-046"
        self.assertIn("NOT CLOSED", open_gap)

    def test_does_not_close_path_integral_derivation(self):
        """
        CLM-046 does NOT derive CG from the SU(8) functional integral —
        that is Route B, paper-gated per Commandment VIII.
        """
        open_gap = "Route B path-integral derivation — NOT CLOSED by CLM-046"
        self.assertIn("NOT CLOSED", open_gap)

    def test_does_not_upgrade_clm_001_to_unqualified_theorem(self):
        """
        CLM-046 tightens the CLM-031 postulate but does NOT upgrade
        CLM-001 from `theorem-joint` (C204) to unqualified `theorem`.
        """
        clm_001_label = "theorem-joint"  # unchanged by CLM-046
        self.assertEqual(clm_001_label, "theorem-joint")


class LeanParityMirrorTests(unittest.TestCase):
    """
    Every ℚ/ℤ literal appearing as a Lean theorem body in
    `CascadeModuliMetric.lean` is mirrored here as an assertEqual.
    Per `feedback_lean_only_bugs.md`: Lean-only arithmetic without a
    Python mirror is a blind spot until Mac-side `lake build` runs.
    """

    # Section 1 literals ---------------------------------------------------
    def test_mirror_coroot_entry_0_0(self):
        self.assertEqual(coroot_entry(0, 0), 1)

    def test_mirror_coroot_entry_0_1(self):
        self.assertEqual(coroot_entry(0, 1), -1)

    def test_mirror_coroot_entry_6_7(self):
        self.assertEqual(coroot_entry(6, 7), -1)

    # Section 2 literals ---------------------------------------------------
    def test_mirror_trace_prod_diag_3(self):
        self.assertEqual(trace_prod(3, 3), 2)

    def test_mirror_trace_prod_adj_23(self):
        self.assertEqual(trace_prod(2, 3), -1)

    def test_mirror_trace_prod_far_14(self):
        self.assertEqual(trace_prod(1, 4), 0)

    # Section 3 literals ---------------------------------------------------
    def test_mirror_killing_su8_prefactor_is_16(self):
        self.assertEqual(killing_su8(1), Fraction(16))

    def test_mirror_killing_su8_on_2_is_32(self):
        self.assertEqual(killing_su8(2), Fraction(32))

    def test_mirror_killing_su8_on_neg1_is_neg16(self):
        self.assertEqual(killing_su8(-1), Fraction(-16))

    # Section 4 literals ---------------------------------------------------
    def test_mirror_cartan_A7_entry_diag_is_2(self):
        self.assertEqual(cartan_A7_entry(3, 3), 2)

    def test_mirror_cartan_A7_entry_adj_is_neg1(self):
        self.assertEqual(cartan_A7_entry(2, 3), -1)

    def test_mirror_cartan_A7_entry_far_is_0(self):
        self.assertEqual(cartan_A7_entry(0, 6), 0)

    # Section 6 literals ---------------------------------------------------
    def test_mirror_mean_inv_A6_is_8_over_6(self):
        self.assertEqual(cartan_mean_inv(6), Fraction(8, 6))

    def test_mirror_mean_inv_A7_is_9_over_6(self):
        self.assertEqual(cartan_mean_inv(7), Fraction(9, 6))

    def test_mirror_mean_inv_ratio_is_8_over_9(self):
        self.assertEqual(
            cartan_mean_inv(6) / cartan_mean_inv(7),
            Fraction(8, 9),
        )

    # Section 8 master-bundle literals ------------------------------------
    def test_mirror_master_bundle_three_facts(self):
        """Mirror the CLM-046 master theorem's three conjuncts."""
        # (i) Entry-for-entry identity at a sample (i, j) = (0, 1)
        lhs = killing_su8(trace_prod(0, 1))
        rhs = Fraction(16) * Fraction(cartan_A7_entry(0, 1))
        self.assertEqual(lhs, rhs)
        # (ii) Uniform-prefactor-canceling CG ratio = 8/9
        self.assertEqual(
            cartan_mean_inv(6) / cartan_mean_inv(7),
            Fraction(8, 9),
        )
        # (iii) CLM-032 rep-theory agreement
        self.assertEqual(cg_rat(7), Fraction(8, 9))


class CommandmentXIITests(unittest.TestCase):
    """Exact-Fraction discipline — zero floats in the derivation path."""

    def test_all_coroot_entries_are_int(self):
        for i in range(7):
            for k in range(8):
                self.assertIsInstance(coroot_entry(i, k), int)

    def test_all_trace_products_are_int(self):
        for i in range(7):
            for j in range(7):
                self.assertIsInstance(trace_prod(i, j), int)

    def test_all_killing_values_are_fraction(self):
        for n in [-3, -1, 0, 1, 2, 5]:
            self.assertIsInstance(killing_su8(n), Fraction)

    def test_all_cartan_mean_inv_are_fraction(self):
        for n in range(1, 10):
            self.assertIsInstance(cartan_mean_inv(n), Fraction)

    def test_cg_rat_is_fraction(self):
        for n in range(2, 10):
            self.assertIsInstance(cg_rat(n), Fraction)

    def test_no_float_in_module_globals(self):
        """Audit: no `float` typed values in the module's numerical constants."""
        import sys
        this_mod = sys.modules[__name__]
        forbidden = []
        for name in dir(this_mod):
            if name.startswith("_"):
                continue
            obj = getattr(this_mod, name)
            if isinstance(obj, float):
                forbidden.append(name)
        self.assertEqual(forbidden, [], f"float globals found: {forbidden}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
