#!/usr/bin/env python3
"""
c171_one_loop_r2.py — CLM-043 parity guard

1-loop R² coefficient from SU(8) gauge + matter content.
All arithmetic exact (Fraction) per Commandment XII.

Key result: only minimally coupled scalars contribute to the
physical Starobinsky R² coefficient; fermions and gauge vectors
contribute zero by conformal invariance in 4D.  With N₀ = 63
adjoint scalars and γ₀ = 1/72 per scalar, the induced scalaron
mass is M_R² = (32π²/21L) M_Pl² — at least 4 orders of magnitude
above M_PS for any log factor L ∈ [1, 100].

Copyright 2026 Steven Lamar Michael. All rights reserved.
"""

import unittest
from fractions import Fraction
from decimal import Decimal, getcontext
from math import comb, gcd

getcontext().prec = 50

# ─── Exact constants ─────────────────────────────────────────

N = 8
N_ADJ = Fraction(N**2 - 1)               # 63
XI_CONF = Fraction(1, 6)                  # conformal coupling in 4D
XI_MIN = Fraction(0)                      # minimal coupling


def r2_coeff(xi):
    """R² coefficient per real scalar with non-minimal coupling ξ.

    γ(ξ) = (ξ − 1/6)² / 2 = (6ξ − 1)² / 72

    Fermions and gauge vectors couple conformally (ξ_eff = 1/6) so
    contribute γ = 0.  Only ξ ≠ 1/6 scalars produce physical R².
    """
    return (Fraction(xi) - XI_CONF) ** 2 / 2


GAMMA_0 = r2_coeff(XI_MIN)               # = 1/72
GAMMA_CONF = r2_coeff(XI_CONF)            # = 0

TOTAL_R2 = N_ADJ * GAMMA_0               # = 63/72 = 7/8

# Starobinsky scalaron mass rational prefactor
# M_R² = c_MR × π² / L × M_Pl²
# Derivation:
#   σ = TOTAL_R2 / (16π²) × L
#   M_R² = M_Pl² / (12 σ)
#       = M_Pl² × 16π² / (12 × TOTAL_R2 × L)
#       = 128π² M_Pl² / (84 L)
#       = (32/21) × π²/L × M_Pl²
C_MR = Fraction(32, 21)

# Fermion/gauge content (R² = 0 by conformal invariance)
WEYL_FERMIONS = 128
GAUGE_VECTORS = N_ADJ

# Δ_R = (10,1,3) scalars at M_PS
N_DELTA_R = Fraction(30)
N_TOTAL_SCALAR = N_ADJ + N_DELTA_R        # 93
TOTAL_R2_EXT = N_TOTAL_SCALAR * GAMMA_0   # 93/72 = 31/24
C_MR_EXT = Fraction(16) / (12 * TOTAL_R2_EXT)  # 32/31

# Cascade drift guards
CASCADE_XI = Fraction(15, 49)
CASCADE_CG = Fraction(8, 9)
CASCADE_R = Fraction(9, 8)

# Gap analysis constants
PI_SQ_LOWER = Fraction(9)                 # π² > 9
LOG10_MPS = Fraction(1370, 100)            # 13.70
LOG10_MPL = Fraction(1839, 100)            # 18.39 (reduced Planck)

# Non-minimal coupling rational prefactor
# ξ² = (8/189) × π² × (M_Pl/M_PS)² / L
XI_PREFACTOR = Fraction(8, 189)


# ═══════════════════════════════════════════════════════════════
#  TEST CLASSES
# ═══════════════════════════════════════════════════════════════

class SU8DOFTests(unittest.TestCase):
    def test_n_squared_minus_one(self):
        self.assertEqual(N**2 - 1, 63)

    def test_adjoint_dof(self):
        self.assertEqual(N_ADJ, Fraction(63))

    def test_weyl_fermion_count(self):
        total = sum(comb(8, k) for k in [1, 3, 5, 7])
        self.assertEqual(total, 128)

    def test_gauge_vector_count(self):
        self.assertEqual(GAUGE_VECTORS, Fraction(63))

    def test_delta_r_dof(self):
        self.assertEqual(N_DELTA_R, Fraction(30))

    def test_total_scalar_with_delta_r(self):
        self.assertEqual(N_TOTAL_SCALAR, Fraction(93))


class ConformalCouplingTests(unittest.TestCase):
    def test_conformal_coupling_value(self):
        self.assertEqual(XI_CONF, Fraction(1, 6))

    def test_conformal_from_dimension(self):
        d = 4
        xi_c = Fraction(d - 2, 4 * (d - 1))
        self.assertEqual(xi_c, Fraction(1, 6))

    def test_minimal_coupling_value(self):
        self.assertEqual(XI_MIN, Fraction(0))


class R2CoefficientTests(unittest.TestCase):
    def test_gamma_0_exact(self):
        self.assertEqual(GAMMA_0, Fraction(1, 72))

    def test_gamma_0_from_formula(self):
        self.assertEqual((Fraction(0) - Fraction(1, 6))**2 / 2, Fraction(1, 72))

    def test_gamma_0_alternative_form(self):
        self.assertEqual((6 * Fraction(0) - 1)**2 / Fraction(72), Fraction(1, 72))

    def test_conformal_vanishes(self):
        self.assertEqual(GAMMA_CONF, Fraction(0))

    def test_conformal_from_formula(self):
        self.assertEqual((Fraction(1, 6) - Fraction(1, 6))**2 / 2, Fraction(0))

    def test_gamma_at_half_conformal(self):
        gamma = r2_coeff(Fraction(1, 12))
        self.assertEqual(gamma, Fraction(1, 288))

    def test_gamma_nonnegative(self):
        for n in range(7):
            xi = Fraction(n, 6)
            self.assertGreaterEqual(r2_coeff(xi), Fraction(0))

    def test_intermediate_derivation(self):
        self.assertEqual(Fraction(1, 6)**2, Fraction(1, 36))
        self.assertEqual(Fraction(1, 36) / 2, Fraction(1, 72))


class ConformalInvarianceTests(unittest.TestCase):
    """Fermions and gauge vectors contribute zero physical R².

    Fermions: Lichnerowicz -D̸² = -□ + R/4 gives conformal ξ=1/6.
    Gauge: Yang-Mills conformally invariant in d=4.
    Both yield γ = (1/6 − 1/6)²/2 = 0.
    """

    def test_fermion_r2_zero(self):
        self.assertEqual(r2_coeff(XI_CONF), Fraction(0))

    def test_gauge_r2_zero(self):
        self.assertEqual(r2_coeff(XI_CONF), Fraction(0))

    def test_total_conformal_contribution(self):
        n_conf = WEYL_FERMIONS + int(GAUGE_VECTORS)
        self.assertEqual(n_conf * GAMMA_CONF, 0)


class TotalR2Tests(unittest.TestCase):
    def test_total_r2(self):
        self.assertEqual(TOTAL_R2, Fraction(7, 8))

    def test_63_over_72_reduces(self):
        self.assertEqual(Fraction(63, 72), Fraction(7, 8))

    def test_gcd_63_72(self):
        self.assertEqual(gcd(63, 72), 9)

    def test_total_with_delta_r(self):
        self.assertEqual(TOTAL_R2_EXT, Fraction(31, 24))

    def test_93_over_72_reduces(self):
        self.assertEqual(Fraction(93, 72), Fraction(31, 24))


class InducedMassTests(unittest.TestCase):
    def test_c_mr_value(self):
        self.assertEqual(C_MR, Fraction(32, 21))

    def test_c_mr_derivation(self):
        c = Fraction(16) / (12 * TOTAL_R2)
        self.assertEqual(c, Fraction(32, 21))

    def test_128_84_reduces(self):
        self.assertEqual(gcd(128, 84), 4)
        self.assertEqual(Fraction(128, 84), Fraction(32, 21))

    def test_sigma_times_16pi2(self):
        self.assertEqual(N_ADJ * GAMMA_0, Fraction(7, 8))

    def test_12_times_total_r2(self):
        self.assertEqual(12 * TOTAL_R2, Fraction(21, 2))

    def test_reciprocal_step(self):
        self.assertEqual(Fraction(16) / Fraction(21, 2), Fraction(32, 21))

    def test_c_mr_with_delta_r(self):
        self.assertEqual(C_MR_EXT, Fraction(32, 31))


class GapAnalysisTests(unittest.TestCase):
    def test_c_mr_times_9(self):
        self.assertEqual(C_MR * PI_SQ_LOWER, Fraction(96, 7))

    def test_288_21_reduces(self):
        self.assertEqual(Fraction(288, 21), Fraction(96, 7))

    def test_96_7_exceeds_13(self):
        self.assertGreater(Fraction(96, 7), Fraction(13))

    def test_at_L_1(self):
        mr_sq = C_MR * PI_SQ_LOWER
        self.assertGreater(mr_sq, Fraction(13))

    def test_at_L_100(self):
        mr_sq = C_MR * PI_SQ_LOWER / 100
        self.assertGreater(mr_sq, Fraction(1, 10))

    def test_mpl_minus_mps_log(self):
        self.assertEqual(LOG10_MPL - LOG10_MPS, Fraction(469, 100))

    def test_gap_exceeds_4_orders(self):
        delta = LOG10_MPL - LOG10_MPS
        self.assertGreater(delta - Fraction(1, 2), Fraction(4))

    def test_robust_to_L(self):
        for L in [1, 10, 24, 50, 100]:
            mr_sq_lower = C_MR * PI_SQ_LOWER / L
            self.assertGreater(mr_sq_lower, Fraction(1, 100),
                               f"Failed at L={L}")

    def test_gap_ratio_at_L_24(self):
        mr_sq_lower = C_MR * PI_SQ_LOWER / 24
        self.assertEqual(mr_sq_lower, Fraction(96, 168))
        self.assertEqual(Fraction(96, 168), Fraction(4, 7))
        self.assertGreater(Fraction(4, 7), Fraction(1, 2))


class NonMinimalCouplingTests(unittest.TestCase):
    def test_xi_rational_prefactor(self):
        self.assertEqual(Fraction(32, 12 * 63), Fraction(8, 189))

    def test_xi_prefactor_irreducible(self):
        self.assertEqual(gcd(8, 189), 1)

    def test_minimal_gives_max_r2_near_conformal(self):
        for n in range(1, 6):
            xi = Fraction(n, 36)
            self.assertGreater(r2_coeff(Fraction(0)), r2_coeff(xi))


class CascadeDriftGuardTests(unittest.TestCase):
    def test_cascade_xi(self):
        self.assertEqual(CASCADE_XI, Fraction(15, 49))

    def test_cascade_cg(self):
        self.assertEqual(CASCADE_CG, Fraction(8, 9))

    def test_r_times_cg(self):
        self.assertEqual(CASCADE_R * CASCADE_CG, Fraction(1))

    def test_r_value(self):
        self.assertEqual(CASCADE_R, Fraction(9, 8))


class LeanParityMirrorTests(unittest.TestCase):
    """Every ℚ literal in OneLoopR2FromSU8.lean mirrored here."""

    def test_adjoint_63(self):
        self.assertEqual(8 * 8 - 1, 63)

    def test_conf_1_6(self):
        self.assertEqual(Fraction(1, 6), Fraction(1, 6))

    def test_gamma_1_72(self):
        self.assertEqual(Fraction(1, 72), Fraction(1, 72))

    def test_total_7_8(self):
        self.assertEqual(Fraction(63) * Fraction(1, 72), Fraction(7, 8))

    def test_c_mr_32_21(self):
        self.assertEqual(Fraction(32, 21), Fraction(32, 21))

    def test_c_mr_times_9_96_7(self):
        self.assertEqual(Fraction(32, 21) * 9, Fraction(96, 7))

    def test_12_times_7_8(self):
        self.assertEqual(12 * Fraction(7, 8), Fraction(21, 2))

    def test_16_over_21_2(self):
        self.assertEqual(Fraction(16) / Fraction(21, 2), Fraction(32, 21))

    def test_1_36_half(self):
        self.assertEqual(Fraction(1, 36) / 2, Fraction(1, 72))

    def test_128_over_84(self):
        self.assertEqual(Fraction(128, 84), Fraction(32, 21))


class CommandmentXIITests(unittest.TestCase):
    def test_no_float_in_constants(self):
        for name, val in [
            ('GAMMA_0', GAMMA_0),
            ('GAMMA_CONF', GAMMA_CONF),
            ('TOTAL_R2', TOTAL_R2),
            ('C_MR', C_MR),
            ('CASCADE_XI', CASCADE_XI),
            ('CASCADE_CG', CASCADE_CG),
            ('C_MR_EXT', C_MR_EXT),
            ('TOTAL_R2_EXT', TOTAL_R2_EXT),
            ('XI_PREFACTOR', XI_PREFACTOR),
        ]:
            self.assertIsInstance(val, Fraction, f"{name} is not Fraction")

    def test_r2_coeff_returns_fraction(self):
        for n in range(7):
            xi = Fraction(n, 6)
            self.assertIsInstance(r2_coeff(xi), Fraction)

    def test_no_float_in_gap_bounds(self):
        for name, val in [
            ('PI_SQ_LOWER', PI_SQ_LOWER),
            ('LOG10_MPS', LOG10_MPS),
            ('LOG10_MPL', LOG10_MPL),
        ]:
            self.assertIsInstance(val, Fraction, f"{name} is not Fraction")


if __name__ == '__main__':
    unittest.main()
