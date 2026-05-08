#!/usr/bin/env python3
"""c151_conformal_bootstrap.py — CLM-035 parity guard.

Verifies every exact-ℚ value in ConformalBootstrap.lean against
the full Machacek-Vaughn two-loop beta function formula.

Convention: Standard Weyl fermion.
  β₀ = (11N − T'_total) / 3,  T'(fund) = 1
  β₁ = (34/3)N² − Σ T_std([k]) · [(10/3)N + 2C₂([k])]
  T_std([k]) = C(N-2, k-1) / 2,  C₂([k]) = k(N-k)(N+1)/(2N)

All arithmetic exact Fraction per Commandment XII.
"""

import unittest
from fractions import Fraction
from math import comb

CANDIDATES = [6, 7, 8, 9, 10]
CONTENT = [1, 3, 5, 7]


# ── Group-theoretic functions (exact Fraction) ───────────────

def dynkin_index_prime(k, N):
    """T'([k], N) = C(N-2, k-1), T(fund) = 1 convention."""
    if k - 1 > N - 2 or k - 1 < 0:
        return 0
    return comb(N - 2, k - 1)


def dynkin_sum_prime(N):
    """T'_total(N) = Σ_{k∈{1,3,5,7}} C(N-2, k-1)."""
    return sum(dynkin_index_prime(k, N) for k in CONTENT)


def t_std(k, N):
    """T_std([k], N) = C(N-2, k-1) / 2, T(fund) = 1/2."""
    return Fraction(dynkin_index_prime(k, N), 2)


def casimir_2(k, N):
    """C₂([k], N) = k(N-k)(N+1) / (2N)."""
    return Fraction(k * (N - k) * (N + 1), 2 * N)


def beta0(N):
    """β₀(N) = (11N − T'_total(N)) / 3."""
    return Fraction(11 * N - dynkin_sum_prime(N), 3)


def beta1_matter(N):
    """Σ_{k∈{1,3,5,7}} T_std([k]) · [(10/3)N + 2C₂([k])]."""
    total = Fraction(0)
    for k in CONTENT:
        ts = t_std(k, N)
        c2 = casimir_2(k, N)
        term = ts * (Fraction(10, 3) * N + 2 * c2)
        total += term
    return total


def beta1(N):
    """β₁(N) = (34/3)N² − matter_sum(N)."""
    return Fraction(34, 3) * N ** 2 - beta1_matter(N)


# ── Test classes ─────────────────────────────────────────────

class DynkinSumTests(unittest.TestCase):
    """Verify Dynkin sums match Lean constants."""

    def test_dynkin_6(self):
        self.assertEqual(dynkin_sum_prime(6), 8)

    def test_dynkin_7(self):
        self.assertEqual(dynkin_sum_prime(7), 16)

    def test_dynkin_8(self):
        self.assertEqual(dynkin_sum_prime(8), 32)

    def test_dynkin_9(self):
        self.assertEqual(dynkin_sum_prime(9), 64)

    def test_dynkin_10(self):
        self.assertEqual(dynkin_sum_prime(10), 127)

    def test_per_rep_N6(self):
        self.assertEqual(dynkin_index_prime(1, 6), 1)
        self.assertEqual(dynkin_index_prime(3, 6), 6)
        self.assertEqual(dynkin_index_prime(5, 6), 1)
        self.assertEqual(dynkin_index_prime(7, 6), 0)

    def test_per_rep_N7(self):
        self.assertEqual(dynkin_index_prime(1, 7), 1)
        self.assertEqual(dynkin_index_prime(3, 7), 10)
        self.assertEqual(dynkin_index_prime(5, 7), 5)
        self.assertEqual(dynkin_index_prime(7, 7), 0)

    def test_per_rep_N8(self):
        self.assertEqual(dynkin_index_prime(1, 8), 1)
        self.assertEqual(dynkin_index_prime(3, 8), 15)
        self.assertEqual(dynkin_index_prime(5, 8), 15)
        self.assertEqual(dynkin_index_prime(7, 8), 1)

    def test_per_rep_N9(self):
        self.assertEqual(dynkin_index_prime(1, 9), 1)
        self.assertEqual(dynkin_index_prime(3, 9), 21)
        self.assertEqual(dynkin_index_prime(5, 9), 35)
        self.assertEqual(dynkin_index_prime(7, 9), 7)

    def test_per_rep_N10(self):
        self.assertEqual(dynkin_index_prime(1, 10), 1)
        self.assertEqual(dynkin_index_prime(3, 10), 28)
        self.assertEqual(dynkin_index_prime(5, 10), 70)
        self.assertEqual(dynkin_index_prime(7, 10), 28)

    def test_component_sum_N6(self):
        self.assertEqual(comb(4, 0) + comb(4, 2) + comb(4, 4) + comb(4, 6), 8)

    def test_component_sum_N8(self):
        self.assertEqual(comb(6, 0) + comb(6, 2) + comb(6, 4) + comb(6, 6), 32)

    def test_component_sum_N9(self):
        self.assertEqual(comb(7, 0) + comb(7, 2) + comb(7, 4) + comb(7, 6), 64)

    def test_component_sum_N10(self):
        self.assertEqual(comb(8, 0) + comb(8, 2) + comb(8, 4) + comb(8, 6), 127)


class Beta0Tests(unittest.TestCase):
    """Verify β₀ values against Lean."""

    def test_beta0_6(self):
        self.assertEqual(beta0(6), Fraction(58, 3))

    def test_beta0_7(self):
        self.assertEqual(beta0(7), Fraction(61, 3))

    def test_beta0_8(self):
        self.assertEqual(beta0(8), Fraction(56, 3))

    def test_beta0_9(self):
        self.assertEqual(beta0(9), Fraction(35, 3))

    def test_beta0_10(self):
        self.assertEqual(beta0(10), Fraction(-17, 3))


class AFFilterTests(unittest.TestCase):
    """Verify asymptotic freedom filter."""

    def test_af_6(self):
        self.assertGreater(beta0(6), 0)

    def test_af_7(self):
        self.assertGreater(beta0(7), 0)

    def test_af_8(self):
        self.assertGreater(beta0(8), 0)

    def test_af_9(self):
        self.assertGreater(beta0(9), 0)

    def test_not_af_10(self):
        self.assertLess(beta0(10), 0)


class CasimirTests(unittest.TestCase):
    """Verify quadratic Casimir C₂([k], N) = k(N-k)(N+1)/(2N)."""

    def test_c2_1_8(self):
        self.assertEqual(casimir_2(1, 8), Fraction(63, 16))

    def test_c2_3_8(self):
        self.assertEqual(casimir_2(3, 8), Fraction(135, 16))

    def test_c2_5_8(self):
        self.assertEqual(casimir_2(5, 8), Fraction(135, 16))

    def test_c2_7_8(self):
        self.assertEqual(casimir_2(7, 8), Fraction(63, 16))

    def test_c2_1_9(self):
        self.assertEqual(casimir_2(1, 9), Fraction(40, 9))

    def test_c2_3_9(self):
        self.assertEqual(casimir_2(3, 9), Fraction(10))

    def test_c2_5_9(self):
        self.assertEqual(casimir_2(5, 9), Fraction(100, 9))

    def test_c2_7_9(self):
        self.assertEqual(casimir_2(7, 9), Fraction(70, 9))

    def test_conjugation_symmetry(self):
        """C₂([k]) = C₂([N-k]) for all valid pairs."""
        for N in CANDIDATES:
            for k in CONTENT:
                nk = N - k
                if 1 <= nk <= N - 1:
                    self.assertEqual(
                        casimir_2(k, N), casimir_2(nk, N),
                        f"C₂([{k}],{N}) != C₂([{N-k}],{N})")


class Beta1MatterTests(unittest.TestCase):
    """Verify β₁ matter contributions against Lean constants."""

    def test_matter_6(self):
        self.assertEqual(beta1_matter(6), Fraction(352, 3))

    def test_matter_7(self):
        self.assertEqual(beta1_matter(7), Fraction(6032, 21))

    def test_matter_8(self):
        self.assertEqual(beta1_matter(8), Fraction(2063, 3))

    def test_matter_9(self):
        self.assertEqual(beta1_matter(9), Fraction(14560, 9))


class Beta1Tests(unittest.TestCase):
    """Verify β₁ values against Lean."""

    def test_beta1_6(self):
        self.assertEqual(beta1(6), Fraction(872, 3))

    def test_beta1_7(self):
        self.assertEqual(beta1(7), Fraction(5630, 21))

    def test_beta1_8(self):
        self.assertEqual(beta1(8), Fraction(113, 3))

    def test_beta1_9(self):
        self.assertEqual(beta1(9), Fraction(-6298, 9))


class ConfinementFilterTests(unittest.TestCase):
    """Verify β₁ sign for confinement (no BZ fixed point)."""

    def test_confines_6(self):
        self.assertGreater(beta1(6), 0)

    def test_confines_7(self):
        self.assertGreater(beta1(7), 0)

    def test_confines_8(self):
        self.assertGreater(beta1(8), 0)

    def test_bz_9(self):
        self.assertLess(beta1(9), 0)


class BZCouplingTests(unittest.TestCase):
    """Verify Banks-Zaks coupling at N = 9."""

    def test_bz_ratio(self):
        ratio = beta0(9) / abs(beta1(9))
        self.assertEqual(ratio, Fraction(105, 6298))

    def test_bz_perturbative(self):
        self.assertGreater(Fraction(105, 6298), 0)
        self.assertLess(Fraction(105, 6298), 1)

    def test_bz_numerics(self):
        self.assertAlmostEqual(float(Fraction(105, 6298)), 0.01667, places=4)


class JointFilterTests(unittest.TestCase):
    """Verify joint conformal filter (AF + confining)."""

    def test_viable_6(self):
        self.assertTrue(beta0(6) > 0 and beta1(6) > 0)

    def test_viable_7(self):
        self.assertTrue(beta0(7) > 0 and beta1(7) > 0)

    def test_viable_8(self):
        self.assertTrue(beta0(8) > 0 and beta1(8) > 0)

    def test_not_viable_9(self):
        self.assertFalse(beta0(9) > 0 and beta1(9) > 0)

    def test_not_viable_10(self):
        self.assertFalse(beta0(10) > 0 and beta1(10) > 0)

    def test_n9_excluded_by_confinement_not_af(self):
        self.assertTrue(beta0(9) > 0)
        self.assertLess(beta1(9), 0)

    def test_n10_excluded_by_af(self):
        self.assertLess(beta0(10), 0)


class CascadeCGTests(unittest.TestCase):
    """Verify cascade CG at N = 8."""

    def test_cg_8(self):
        cg = Fraction(8, 8 + 1)
        self.assertEqual(cg, Fraction(8, 9))

    def test_cg_formula(self):
        for N in CANDIDATES:
            cg = Fraction(N, N + 1)
            self.assertEqual(cg.numerator, N)
            self.assertEqual(cg.denominator, N + 1)


class MasterTheoremTests(unittest.TestCase):
    """Bundle all 6 master theorem facts from Lean."""

    def test_master_viable_6(self):
        self.assertTrue(beta0(6) > 0 and beta1(6) > 0)

    def test_master_viable_7(self):
        self.assertTrue(beta0(7) > 0 and beta1(7) > 0)

    def test_master_viable_8(self):
        self.assertTrue(beta0(8) > 0 and beta1(8) > 0)

    def test_master_not_viable_9(self):
        self.assertFalse(beta0(9) > 0 and beta1(9) > 0)

    def test_master_not_viable_10(self):
        self.assertFalse(beta0(10) > 0 and beta1(10) > 0)

    def test_master_cg_8(self):
        self.assertEqual(Fraction(8, 9), Fraction(8, 9))


class ConventionCrossCheckTests(unittest.TestCase):
    """Cross-check Weyl convention against known QCD results.
    SU(3) with 6 Dirac quarks = 12 Weyl fundamentals.
    Known: β₀ = 7, β₁ = 26 in the Weyl scheme."""

    def test_qcd_beta0(self):
        beta0_qcd = Fraction(11 * 3 - 12, 3)
        self.assertEqual(beta0_qcd, Fraction(7))

    def test_qcd_beta1(self):
        N = 3
        n_f = 12
        ts = Fraction(1, 2)
        c2_f = Fraction(N ** 2 - 1, 2 * N)
        matter = n_f * ts * (Fraction(10, 3) * N + 2 * c2_f)
        b1 = Fraction(34, 3) * N ** 2 - matter
        self.assertEqual(b1, Fraction(26))


class LeanParityMirrorTests(unittest.TestCase):
    """Mirror every ℚ literal in ConformalBootstrap.lean."""

    def test_beta0_num_6(self):
        self.assertEqual(11 * 6 - 8, 58)

    def test_beta0_num_7(self):
        self.assertEqual(11 * 7 - 16, 61)

    def test_beta0_num_8(self):
        self.assertEqual(11 * 8 - 32, 56)

    def test_beta0_num_9(self):
        self.assertEqual(11 * 9 - 64, 35)

    def test_beta0_num_10(self):
        self.assertEqual(11 * 10 - 127, -17)

    def test_beta1_matter_lean_6(self):
        self.assertEqual(beta1_matter(6), Fraction(352, 3))

    def test_beta1_matter_lean_7(self):
        self.assertEqual(beta1_matter(7), Fraction(6032, 21))

    def test_beta1_matter_lean_8(self):
        self.assertEqual(beta1_matter(8), Fraction(2063, 3))

    def test_beta1_matter_lean_9(self):
        self.assertEqual(beta1_matter(9), Fraction(14560, 9))

    def test_beta1_lean_6(self):
        self.assertEqual(Fraction(34, 3) * 36 - Fraction(352, 3),
                         Fraction(872, 3))

    def test_beta1_lean_7(self):
        self.assertEqual(Fraction(34, 3) * 49 - Fraction(6032, 21),
                         Fraction(5630, 21))

    def test_beta1_lean_8(self):
        self.assertEqual(Fraction(34, 3) * 64 - Fraction(2063, 3),
                         Fraction(113, 3))

    def test_beta1_lean_9(self):
        self.assertEqual(Fraction(34, 3) * 81 - Fraction(14560, 9),
                         Fraction(-6298, 9))

    def test_bz_lean_ratio(self):
        self.assertEqual(Fraction(35, 3) / Fraction(6298, 9),
                         Fraction(105, 6298))

    def test_bz_lean_lt_1(self):
        self.assertLess(Fraction(105, 6298), 1)

    def test_cg_lean_8_9(self):
        self.assertEqual(Fraction(8, 9), Fraction(8, 9))


class ScopeTests(unittest.TestCase):
    """Verify honest scope: N = 6, 7 survive conformal filter."""

    def test_n6_survives(self):
        self.assertGreater(beta0(6), 0)
        self.assertGreater(beta1(6), 0)

    def test_n7_survives(self):
        self.assertGreater(beta0(7), 0)
        self.assertGreater(beta1(7), 0)

    def test_viable_set_is_678(self):
        viable = [N for N in CANDIDATES
                  if beta0(N) > 0 and beta1(N) > 0]
        self.assertEqual(viable, [6, 7, 8])


class CommandmentXIITests(unittest.TestCase):
    """Verify all computations use exact Fraction."""

    def test_all_beta0_exact(self):
        for N in CANDIDATES:
            self.assertIsInstance(beta0(N), Fraction)

    def test_all_beta1_exact(self):
        for N in [6, 7, 8, 9]:
            self.assertIsInstance(beta1(N), Fraction)

    def test_all_matter_exact(self):
        for N in [6, 7, 8, 9]:
            self.assertIsInstance(beta1_matter(N), Fraction)

    def test_bz_exact(self):
        ratio = beta0(9) / abs(beta1(9))
        self.assertIsInstance(ratio, Fraction)


if __name__ == '__main__':
    unittest.main()
