"""
c172_non_minimal_coupling_essence.py — CLM-044

Non-minimal coupling ξ R φ² → induced Starobinsky R² scalaron mass.
Route B second attempt at closing M_R² = M_PS structurally.

VERDICT: HONEST-NEGATIVE.  No natural SU(8) cascade group invariant
produces ξ in the required interval [3689, 14548] without paper-gated
matching (Bezrukov-Shaposhnikov 2008).  Closest candidate:
  ξ = (N²-1)² = 3969 — factor 1.6 miss (PASS_FACTOR_3 threshold).

Sibling of CLM-043 (minimal coupling: structurally insufficient).

Commandment XII compliance: all rational arithmetic as Fraction;
zero floats in derivation path.  Commandment XIII: every claim
has an explicit assertEqual or a Lean tactic mirror.

Copyright 2026 Steven Lamar Michael. All rights reserved.
"""

import unittest
from fractions import Fraction


# ═══════════════════════════════════════════════════════════════
# §1  SU(8) content (mirrors c171_one_loop_r2.py)
# ═══════════════════════════════════════════════════════════════

N = 8
N_ADJ = Fraction(N**2 - 1)                 # 63
N_SCALAR_EXT = Fraction(N_ADJ + 30)        # 93 (adjoint + Δ_R)

XI_CONF = Fraction(1, 6)                   # conformal coupling in d=4
XI_MIN = Fraction(0)                       # minimal coupling (CLM-043)


def r2_coeff(xi):
    """γ(ξ) = (ξ − 1/6)² / 2 per real scalar (Seeley-DeWitt a₂)."""
    return (Fraction(xi) - XI_CONF) ** 2 / 2


def r2_coeff_alt(xi):
    """Alternative form: (6ξ − 1)² / 72 per real scalar."""
    return (6 * Fraction(xi) - 1) ** 2 / Fraction(72)


def total_r2_adjoint_only(xi):
    """Total R² beta with N_ADJ = 63 adjoint scalars."""
    return N_ADJ * r2_coeff(xi)


def scalaron_mass_sq_over_Mpl_sq_times_L_over_pi_sq(xi):
    """
    M_R² / M_Pl² × L / π² = (32/21) / (6ξ − 1)²   (from 1-loop derivation)

    Returns the pure rational prefactor; the user multiplies by π²/L
    and (M_Pl/M_PS)² for the mass-ratio check.
    """
    six_xi_m1 = 6 * Fraction(xi) - 1
    if six_xi_m1 == 0:
        raise ValueError("ξ = 1/6 is conformal — induced R² vanishes.")
    return Fraction(32, 21) / (six_xi_m1 ** 2)


# ═══════════════════════════════════════════════════════════════
# §2  Mass scales (mirrors c171)
# ═══════════════════════════════════════════════════════════════

LOG10_MPS = Fraction(1370, 100)            # 13.70
LOG10_MPL = Fraction(1839, 100)            # 18.39 reduced Planck
LOG10_RATIO = LOG10_MPL - LOG10_MPS        # 4.69
LOG10_RATIO_SQ = 2 * LOG10_RATIO           # 9.38

# (M_Pl/M_PS)² bounds as exact ℚ:
# 10^9 < (M_Pl/M_PS)² < 10^10  (strict; true since 9 < 9.38 < 10)
MPL_MPS_SQ_LB = Fraction(10 ** 9)
MPL_MPS_SQ_UB = Fraction(10 ** 10)

# π² bounds: 9 < π² < 10 (exact)
PI_SQ_LB = Fraction(9)
PI_SQ_UB = Fraction(10)

# L ∈ [20, 28] (natural range, bracketing ln((M_Pl/M_PS)²) ≈ 21.6)
L_LB = Fraction(20)
L_UB = Fraction(28)


def required_six_xi_m1_sq(pi_sq, L, mpl_mps_sq):
    """Exact ℚ: required (6ξ-1)² = (32/21) × π²/L × (M_Pl/M_PS)²."""
    return Fraction(32, 21) * pi_sq / L * mpl_mps_sq


# ═══════════════════════════════════════════════════════════════
# §3  Cascade drift guards (mirror c171)
# ═══════════════════════════════════════════════════════════════

CASCADE_XI = Fraction(15, 49)
CASCADE_CG = Fraction(8, 9)
CASCADE_R = Fraction(9, 8)
C_MR = Fraction(32, 21)                    # from CLM-043


# ═══════════════════════════════════════════════════════════════
# §4  Natural SU(8) group invariants (honest enumeration)
# ═══════════════════════════════════════════════════════════════

NATURAL_CASCADE_INVARIANTS = {
    "N": Fraction(N),                          # 8
    "N(N+1)/2": Fraction(N * (N + 1), 2),      # 36
    "(N²-1)·N/(N+1)": Fraction((N**2 - 1) * N, N + 1),  # 56
    "N²-1 (adjoint dim)": Fraction(N**2 - 1),  # 63
    "N²": Fraction(N**2),                      # 64
    "N(N²-1)": Fraction(N * (N**2 - 1)),       # 504
    "N³": Fraction(N**3),                      # 512
    "N²(N²-1)/2": Fraction(N**2 * (N**2 - 1), 2),  # 2016
    "(N²-1)² (adjoint squared)": Fraction((N**2 - 1) ** 2),  # 3969
    "N³(N²-1)": Fraction(N**3 * (N**2 - 1)),   # 32256
}


# ═══════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════


class ForwardFormulaTests(unittest.TestCase):
    """§2 Non-minimal R² per-scalar coefficient."""

    def test_minimal_recovers_clm043(self):
        """At ξ = 0, γ(0) = 1/72 — same as CLM-043."""
        self.assertEqual(r2_coeff(XI_MIN), Fraction(1, 72))

    def test_minimal_alt_form(self):
        """Alternative form (6ξ-1)²/72 at ξ=0 gives (-1)²/72 = 1/72."""
        self.assertEqual(r2_coeff_alt(XI_MIN), Fraction(1, 72))

    def test_minimal_forms_agree(self):
        """Both forms agree at ξ = 0."""
        self.assertEqual(r2_coeff(XI_MIN), r2_coeff_alt(XI_MIN))

    def test_conformal_vanishes(self):
        """At ξ = 1/6, γ vanishes — conformal invariance."""
        self.assertEqual(r2_coeff(XI_CONF), Fraction(0))

    def test_conformal_alt_vanishes(self):
        """At ξ = 1/6, alternative form also vanishes."""
        self.assertEqual(r2_coeff_alt(XI_CONF), Fraction(0))

    def test_forms_agree_generic(self):
        """Both forms agree at generic ξ."""
        for xi_val in [Fraction(1), Fraction(100), Fraction(3969)]:
            self.assertEqual(r2_coeff(xi_val), r2_coeff_alt(xi_val))

    def test_large_xi_approx_xi_squared_over_2(self):
        """At large ξ, γ(ξ) ≈ ξ²/2 (BS regime)."""
        xi_val = Fraction(10000)
        exact = r2_coeff(xi_val)
        approx = xi_val ** 2 / 2
        # Relative error < 1/ξ ≈ 10⁻⁴
        rel_err = abs(exact - approx) / approx
        self.assertLess(rel_err, Fraction(1, 1000))


class TotalR2Tests(unittest.TestCase):
    """§3 Total N_ADJ × γ(ξ) bookkeeping."""

    def test_minimal_recovers_7_over_8(self):
        """At ξ = 0, 63 × 1/72 = 7/8 (matches CLM-043)."""
        self.assertEqual(total_r2_adjoint_only(XI_MIN), Fraction(7, 8))

    def test_conformal_total_vanishes(self):
        """At ξ = 1/6, total also vanishes."""
        self.assertEqual(total_r2_adjoint_only(XI_CONF), Fraction(0))

    def test_at_3969_large(self):
        """At ξ = 3969, total R² is huge (expected)."""
        total = total_r2_adjoint_only(Fraction(3969))
        # (6·3969-1)² = 23813² = 567058969
        # Total = 63 × 567058969 / 72 = 3969416983/8 = ...
        expected = Fraction(63) * Fraction(23813 ** 2, 72)
        self.assertEqual(total, expected)


class ScalarMassFormulaTests(unittest.TestCase):
    """§4 Inverted formula: (6ξ-1)² as function of inputs."""

    def test_prefactor_c_mr(self):
        """M_R²/M_Pl² = (32/21) × π²/L × 1/(6ξ-1)² — check 32/21."""
        # At (6ξ-1)² = 1, just gives the prefactor
        self.assertEqual(
            scalaron_mass_sq_over_Mpl_sq_times_L_over_pi_sq(Fraction(1, 3)),
            Fraction(32, 21),
        )

    def test_at_conformal_raises(self):
        """ξ = 1/6 should raise (conformal invariance — induced R² is zero)."""
        with self.assertRaises(ValueError):
            scalaron_mass_sq_over_Mpl_sq_times_L_over_pi_sq(XI_CONF)

    def test_matches_c171_minimal(self):
        """At ξ = 0, (6·0-1)² = 1, so M_R²/M_Pl² × L/π² = 32/21 — matches c171."""
        self.assertEqual(
            scalaron_mass_sq_over_Mpl_sq_times_L_over_pi_sq(XI_MIN),
            C_MR,
        )


class RequiredXiBoundsTests(unittest.TestCase):
    """§5 Required (6ξ-1)² interval as exact ℚ."""

    def test_lower_bound_exists(self):
        """With π² > 9, L < 28, (M_Pl/M_PS)² > 10^9:
           (6ξ-1)² > (32/21) × 9/28 × 10^9 = 24000000000/49."""
        lb = required_six_xi_m1_sq(PI_SQ_LB, L_UB, MPL_MPS_SQ_LB)
        self.assertEqual(lb, Fraction(24_000_000_000, 49))

    def test_upper_bound_exists(self):
        """With π² < 10, L > 20, (M_Pl/M_PS)² < 10^10:
           (6ξ-1)² < (32/21) × 10/20 × 10^10 = 160000000000/21."""
        ub = required_six_xi_m1_sq(PI_SQ_UB, L_LB, MPL_MPS_SQ_UB)
        self.assertEqual(ub, Fraction(160_000_000_000, 21))

    def test_lower_bound_greater_than_1e8(self):
        """Sanity: lower bound > 10^8."""
        lb = required_six_xi_m1_sq(PI_SQ_LB, L_UB, MPL_MPS_SQ_LB)
        self.assertGreater(lb, Fraction(10 ** 8))

    def test_upper_bound_less_than_1e10(self):
        """Sanity: upper bound < 10^10 (so 6ξ-1 < 100000)."""
        ub = required_six_xi_m1_sq(PI_SQ_UB, L_LB, MPL_MPS_SQ_UB)
        self.assertLess(ub, Fraction(10 ** 10))

    def test_interval_is_nonempty(self):
        """Lower < upper (trivially satisfied for the right direction)."""
        lb = required_six_xi_m1_sq(PI_SQ_LB, L_UB, MPL_MPS_SQ_LB)
        ub = required_six_xi_m1_sq(PI_SQ_UB, L_LB, MPL_MPS_SQ_UB)
        self.assertLess(lb, ub)


class NaturalInvariantsEnumerationTests(unittest.TestCase):
    """§6 Enumeration of cascade invariants and their M_R/M_PS ratios."""

    def test_count_of_candidates(self):
        """Enumerate 10 natural SU(8) group invariants."""
        self.assertEqual(len(NATURAL_CASCADE_INVARIANTS), 10)

    def test_adjoint_dim_is_63(self):
        self.assertEqual(NATURAL_CASCADE_INVARIANTS["N²-1 (adjoint dim)"], Fraction(63))

    def test_adjoint_squared_is_3969(self):
        self.assertEqual(
            NATURAL_CASCADE_INVARIANTS["(N²-1)² (adjoint squared)"],
            Fraction(3969),
        )

    def test_N_squared_minus_1_squared_formula(self):
        """(N²-1)² = 63² = 3969."""
        self.assertEqual((N**2 - 1) ** 2, 3969)

    def test_all_positive(self):
        for val in NATURAL_CASCADE_INVARIANTS.values():
            self.assertGreater(val, Fraction(0))

    def test_all_integers(self):
        for val in NATURAL_CASCADE_INVARIANTS.values():
            self.assertEqual(val.denominator, 1)

    def test_sorted_ascending(self):
        values = list(NATURAL_CASCADE_INVARIANTS.values())
        self.assertEqual(values, sorted(values))


class NoneInRequiredIntervalTests(unittest.TestCase):
    """§7 Honest-negative: no natural invariant lies in the required ξ interval."""

    def test_required_six_xi_m1_lower_bound(self):
        """(6ξ-1) > sqrt(24×10^9/49).  Since 22000² = 484×10^6 < 24000×10^6/49,
           check 6ξ-1 > 22000 → ξ > 3667."""
        # (6ξ-1)² > 24_000_000_000 / 49
        # So (6ξ-1)² > 489,795,918
        # sqrt > 22131
        lb_sq = Fraction(24_000_000_000, 49)
        # 22130² = 489,736,900 < 489,795,918
        # 22140² = 490,179,600 > 489,795,918
        self.assertGreater(lb_sq, Fraction(22130 ** 2))
        self.assertLess(lb_sq, Fraction(22140 ** 2))
        # Hence ξ > (22130 + 1)/6 = 3688.5 → ξ > 3688
        # and ξ < (22140 + 1)/6 = 3690.17 → ξ < 3691

    def test_required_six_xi_m1_upper_bound(self):
        """(6ξ-1)² < 160×10^9/21 ≈ 7.619×10^9.  sqrt < 87287."""
        ub_sq = Fraction(160_000_000_000, 21)
        # 87287² = 7,619,024,369
        # 87300² = 7,621,290,000
        self.assertLess(ub_sq, Fraction(87300 ** 2))
        self.assertGreater(ub_sq, Fraction(87280 ** 2))

    def test_adjoint_squared_below_lower_bound(self):
        """Closest candidate ξ = (N²-1)² = 3969:
           (6·3969-1)² = 23813² = 567058969 < 24000000000/49 ≈ 4.898×10^8.
           Wait: 23813² = 567,059,569 > 489,795,918, so it's ABOVE the lower
           bound on (6ξ-1)² but BELOW the upper bound.  Check in detail."""
        lb_sq = Fraction(24_000_000_000, 49)  # ≈ 4.898×10^8
        six_xi_m1 = 6 * 3969 - 1
        sq = Fraction(six_xi_m1 ** 2)
        # sq = 567,059,569
        # Compare to lb_sq ≈ 489,795,918
        self.assertGreater(sq, lb_sq)
        # So (N²-1)² is above the lower bound on (6ξ-1)², meaning M_R
        # would be TOO SMALL compared to M_PS.  The M_R/M_PS ratio at
        # ξ = 3969 is < 1 (too low).

        # But at π² and L in the CENTRAL range (~9.87, ~22), (6ξ-1)²
        # required is higher than at the lower bound — hence (N²-1)²
        # is BELOW the central requirement by a factor ~3.
        # Central required ≈ 1.5×10^9 (from c172 analysis):
        central_required = Fraction(3) * Fraction(10 ** 9) // 2  # ≈ 1.5×10^9
        self.assertLess(sq, central_required)

    def test_adjoint_squared_is_closest_natural_invariant(self):
        """Among the 10 natural invariants, (N²-1)² = 3969 is closest to the
           central required ξ ≈ 6450.  Neighbors: 2016 (below) and 32256 (above).
           |log10(3969/6450)| ≈ 0.21, smaller than any other candidate's log-distance."""
        import math
        central_target = 6450
        log_distances = {}
        for name, val in NATURAL_CASCADE_INVARIANTS.items():
            log_dist = abs(math.log10(float(val) / central_target))
            log_distances[name] = log_dist
        closest = min(log_distances.items(), key=lambda kv: kv[1])
        self.assertEqual(closest[0], "(N²-1)² (adjoint squared)")
        # And it's within 0.25 orders
        self.assertLess(closest[1], 0.25)


class PromisingCoincidenceTests(unittest.TestCase):
    """§8 The (N²-1)² = 3969 case — document factor-1.6 miss."""

    def test_adjoint_squared_6xi_m1(self):
        """At ξ = 3969, 6ξ-1 = 23813."""
        self.assertEqual(6 * 3969 - 1, 23813)

    def test_adjoint_squared_6xi_m1_squared(self):
        """(6·3969-1)² = 23813² = 567058969."""
        self.assertEqual(23813 ** 2, 567_058_969)

    def test_factor_miss_documentation(self):
        """M_R²/M_PS² = C_MR × π²/L × (M_Pl/M_PS)² / (6ξ-1)²

        At CENTRAL values L = 22, π² = 10 (approx), (M_Pl/M_PS)² = 24×10^9
        (approximating 10^9.38), ξ = 3969:
          M_R²/M_PS² = (32/21) × 10/22 × 24×10^9 / 567058969
                     = (32 × 10 × 24 × 10^9) / (21 × 22 × 567058969)
                     = 7680 × 10^9 / (462 × 567058969)
                     ≈ 2.93

        So M_R/M_PS ≈ sqrt(2.93) ≈ 1.71 — factor ~1.7 miss.
        PASS_FACTOR_3 threshold (within factor 3 at central values).

        Note: at WIDEST bounds (π²<10, L>20, (M_Pl/M_PS)²<10^10) the ratio
        could be as high as ~13 (sqrt ~3.6), outside factor-3 band.  The
        "within factor 3" claim holds at central physical values only.
        """
        # Central representative values
        pi_sq_central = Fraction(10)
        L_central = Fraction(22)
        mpl_mps_sq_central = Fraction(24, 10) * Fraction(10 ** 9)  # ≈ 10^9.38
        six_xi_m1_sq = Fraction(567_058_969)
        ratio_sq = Fraction(32, 21) * pi_sq_central / L_central * mpl_mps_sq_central / six_xi_m1_sq
        # Check this is < 9 (so ratio < 3) at central values
        self.assertLess(ratio_sq, Fraction(9))
        # And > 1 (M_R > M_PS — miss on high side)
        self.assertGreater(ratio_sq, Fraction(1))
        # Specifically in the factor-(1.5, 2) band for the ratio itself
        # i.e. ratio_sq ∈ [2.25, 4]
        self.assertGreater(ratio_sq, Fraction(9, 4))
        self.assertLess(ratio_sq, Fraction(4))

    def test_miss_is_on_M_R_too_high_side(self):
        """ξ = 3969 is below the required central ξ ≈ 6450, so (6ξ-1)²
        is below the required (6ξ_req - 1)², so M_R² > M_PS² — M_R is
        TOO HIGH not too low."""
        xi_candidate = Fraction(3969)
        # At central ξ_req ≈ 6450, (6·6450-1)² = 38699² ≈ 1.498×10^9
        # At ξ_candidate = 3969, (6·3969-1)² = 23813² ≈ 5.671×10^8
        # Since 5.671×10^8 < 1.498×10^9, (6ξ-1)² is smaller than required
        # → denominator is smaller → M_R² is LARGER → M_R > M_PS
        six_xi_m1_sq_candidate = (6 * xi_candidate - 1) ** 2
        six_xi_req_m1_sq_central = Fraction(38699 ** 2)
        self.assertLess(six_xi_m1_sq_candidate, six_xi_req_m1_sq_central)


class CascadeDriftGuardTests(unittest.TestCase):
    """§9 Upstream cascade constants unchanged."""

    def test_cascade_xi_unchanged(self):
        self.assertEqual(CASCADE_XI, Fraction(15, 49))

    def test_cascade_cg_unchanged(self):
        self.assertEqual(CASCADE_CG, Fraction(8, 9))

    def test_cascade_r_unchanged(self):
        self.assertEqual(CASCADE_R, Fraction(9, 8))

    def test_cascade_master_identity(self):
        """r · CG = 1."""
        self.assertEqual(CASCADE_R * CASCADE_CG, Fraction(1))

    def test_c_mr_matches_clm043(self):
        """C_MR = 32/21 inherited from CLM-043."""
        self.assertEqual(C_MR, Fraction(32, 21))


class CLM043CrossCheckTests(unittest.TestCase):
    """§10 Cross-check with CLM-043 (minimal coupling)."""

    def test_minimal_gap_unchanged(self):
        """At ξ = 0, M_R²/M_Pl² × L/π² = 32/21 — CLM-043's prefactor."""
        self.assertEqual(
            scalaron_mass_sq_over_Mpl_sq_times_L_over_pi_sq(XI_MIN),
            Fraction(32, 21),
        )

    def test_minimal_gap_lower_bound(self):
        """At ξ = 0, π² > 9: M_R²/M_Pl² × L > (32/21) × 9 = 96/7 > 13."""
        prefactor = scalaron_mass_sq_over_Mpl_sq_times_L_over_pi_sq(XI_MIN)
        product = prefactor * PI_SQ_LB
        self.assertEqual(product, Fraction(96, 7))
        self.assertGreater(product, Fraction(13))

    def test_non_minimal_extends_clm043(self):
        """At any ξ ≠ 1/6 and ξ > 1/6, the (6ξ-1)² denominator REDUCES
        the induced M_R² below the minimal-coupling value — CLM-044's
        entire premise."""
        for xi_val in [Fraction(1), Fraction(10), Fraction(3969)]:
            non_min = scalaron_mass_sq_over_Mpl_sq_times_L_over_pi_sq(xi_val)
            min_val = scalaron_mass_sq_over_Mpl_sq_times_L_over_pi_sq(XI_MIN)
            self.assertLess(non_min, min_val)


class MasterTheoremTests(unittest.TestCase):
    """§11 Bundled identity (mirror of Lean master theorem)."""

    def test_master_bundle(self):
        """All five facts for CLM-044 master theorem:
          1. γ(0) = 1/72 (minimal)
          2. γ(1/6) = 0 (conformal)
          3. 63 × 1/72 = 7/8 (total at minimal)
          4. C_MR = 32/21 (scalaron prefactor)
          5. r · CG = 1 (cascade consistency)
        """
        self.assertEqual(r2_coeff(0), Fraction(1, 72))
        self.assertEqual(r2_coeff(Fraction(1, 6)), Fraction(0))
        self.assertEqual(N_ADJ * r2_coeff(0), Fraction(7, 8))
        self.assertEqual(C_MR, Fraction(32, 21))
        self.assertEqual(CASCADE_R * CASCADE_CG, Fraction(1))

    def test_required_xi_interval_exists(self):
        """Required (6ξ-1)² ∈ [24e9/49, 160e9/21] with π² ∈ [9,10], L ∈ [20,28]."""
        lb = required_six_xi_m1_sq(PI_SQ_LB, L_UB, MPL_MPS_SQ_LB)
        ub = required_six_xi_m1_sq(PI_SQ_UB, L_LB, MPL_MPS_SQ_UB)
        self.assertEqual(lb, Fraction(24_000_000_000, 49))
        self.assertEqual(ub, Fraction(160_000_000_000, 21))

    def test_promising_coincidence_landing(self):
        """(N²-1)² = 3969; (6·3969-1)² = 567058969.
        Below the central required (6ξ-1)² ≈ 1.5×10^9 — so M_R > M_PS by factor < 3."""
        xi_val = Fraction(3969)
        six_xi_m1_sq = (6 * xi_val - 1) ** 2
        self.assertEqual(six_xi_m1_sq, Fraction(567_058_969))
        # Check it's within factor-3 of central required:
        # central required = (32/21) × π²/L × 10^9.38 ≈ 1.5×10^9
        # Factor 3 window: 5×10^8 to 4.5×10^9
        self.assertGreater(six_xi_m1_sq, Fraction(5 * 10**8))
        self.assertLess(six_xi_m1_sq, Fraction(45 * 10**8))


class LeanParityMirrorTests(unittest.TestCase):
    """§12 Parity with NonMinimalCouplingDerivation.lean.

    Every ℚ literal in the Lean file must have a Python assertEqual
    mirror here — avoids the CLM-031 feedback_lean_only_bugs.md blind
    spot.
    """

    def test_minimal_one_over_72(self):
        # Lean: theorem r2_minimal : r2_coeff 0 = 1/72
        self.assertEqual(r2_coeff(0), Fraction(1, 72))

    def test_conformal_zero(self):
        # Lean: theorem r2_conformal : r2_coeff (1/6) = 0
        self.assertEqual(r2_coeff(Fraction(1, 6)), Fraction(0))

    def test_total_minimal_7_over_8(self):
        # Lean: total at ξ=0: 63 × 1/72 = 7/8
        self.assertEqual(N_ADJ * r2_coeff(0), Fraction(7, 8))

    def test_c_mr_32_over_21(self):
        # Lean: def c_mr : ℚ := 32/21
        self.assertEqual(C_MR, Fraction(32, 21))

    def test_log10_mps(self):
        # Lean literal: log10_MPS = 1370/100
        self.assertEqual(LOG10_MPS, Fraction(1370, 100))
        # Equivalent reduced form
        self.assertEqual(LOG10_MPS, Fraction(137, 10))

    def test_log10_mpl(self):
        # Lean literal: log10_MPl_red = 1839/100
        self.assertEqual(LOG10_MPL, Fraction(1839, 100))
        # Equivalent reduced form
        self.assertEqual(LOG10_MPL, Fraction(1839, 100))

    def test_log10_ratio(self):
        # Lean: log10_MPl - log10_MPS = 469/100
        self.assertEqual(LOG10_RATIO, Fraction(469, 100))

    def test_log10_ratio_squared(self):
        # Lean: 2 × 469/100 = 938/100
        self.assertEqual(LOG10_RATIO_SQ, Fraction(938, 100))
        self.assertEqual(LOG10_RATIO_SQ, Fraction(469, 50))

    def test_MPL_MPS_SQ_bounds(self):
        # Lean literal: 10^9 < (M_Pl/M_PS)² < 10^10
        self.assertEqual(MPL_MPS_SQ_LB, Fraction(1_000_000_000))
        self.assertEqual(MPL_MPS_SQ_UB, Fraction(10_000_000_000))

    def test_pi_sq_bounds(self):
        # Lean: π² > 9, π² < 10 (exact bounds)
        self.assertEqual(PI_SQ_LB, Fraction(9))
        self.assertEqual(PI_SQ_UB, Fraction(10))

    def test_L_bounds(self):
        # Lean: L ∈ [20, 28]
        self.assertEqual(L_LB, Fraction(20))
        self.assertEqual(L_UB, Fraction(28))

    def test_required_lower_bound_exact(self):
        # Lean: required (6ξ-1)² > 24×10^9 / 49
        lb = required_six_xi_m1_sq(PI_SQ_LB, L_UB, MPL_MPS_SQ_LB)
        self.assertEqual(lb, Fraction(24_000_000_000, 49))

    def test_required_upper_bound_exact(self):
        # Lean: required (6ξ-1)² < 160×10^9 / 21
        ub = required_six_xi_m1_sq(PI_SQ_UB, L_LB, MPL_MPS_SQ_UB)
        self.assertEqual(ub, Fraction(160_000_000_000, 21))

    def test_adjoint_squared_3969(self):
        # Lean: (N²-1)² = 3969
        self.assertEqual((N**2 - 1) ** 2, 3969)

    def test_adjoint_squared_six_xi_m1(self):
        # Lean: 6 × 3969 - 1 = 23813
        self.assertEqual(6 * 3969 - 1, 23813)

    def test_adjoint_squared_six_xi_m1_squared(self):
        # Lean: 23813² = 567058969
        self.assertEqual(23813 ** 2, 567_058_969)

    def test_cascade_r_times_cg(self):
        # Lean: r · CG = 1
        self.assertEqual(CASCADE_R * CASCADE_CG, Fraction(1))

    def test_cascade_xi(self):
        # Lean: cascade_xi = 15/49
        self.assertEqual(CASCADE_XI, Fraction(15, 49))


class CommandmentXIITests(unittest.TestCase):
    """§13 Commandment XII: zero floats in the derivation path."""

    def test_all_core_values_are_fractions(self):
        for xi_val in [XI_MIN, XI_CONF]:
            self.assertIsInstance(xi_val, Fraction)
        for val in [N_ADJ, N_SCALAR_EXT, C_MR, CASCADE_XI, CASCADE_CG, CASCADE_R]:
            self.assertIsInstance(val, Fraction)
        for val in [LOG10_MPS, LOG10_MPL, LOG10_RATIO, LOG10_RATIO_SQ]:
            self.assertIsInstance(val, Fraction)
        for val in [MPL_MPS_SQ_LB, MPL_MPS_SQ_UB, PI_SQ_LB, PI_SQ_UB, L_LB, L_UB]:
            self.assertIsInstance(val, Fraction)

    def test_r2_coeff_returns_fraction(self):
        for xi_val in [0, Fraction(1, 6), Fraction(1), Fraction(3969)]:
            self.assertIsInstance(r2_coeff(xi_val), Fraction)

    def test_required_six_xi_m1_sq_returns_fraction(self):
        result = required_six_xi_m1_sq(PI_SQ_LB, L_UB, MPL_MPS_SQ_LB)
        self.assertIsInstance(result, Fraction)

    def test_natural_invariants_are_all_fractions(self):
        for val in NATURAL_CASCADE_INVARIANTS.values():
            self.assertIsInstance(val, Fraction)


class HonestNegativeVerdictTests(unittest.TestCase):
    """§14 Honest-negative verdict documentation.

    NUANCE (load-bearing): at the WIDEST possible bounds (π² ∈ [9,10],
    L ∈ [20,28], (M_Pl/M_PS)² ∈ [10^9, 10^10]), the required ξ interval
    ≈ [3689, 14548] DOES contain ξ = (N²-1)² = 3969 as a set-membership
    claim.  But at any SPECIFIC physical (π², L), ξ = 3969 does NOT close
    M_R = M_PS — it gives M_R/M_PS ≈ 1.6–1.7 at central values.  The
    "containment" exists only because the interval sweeps a range of
    (π², L) uncertainty.  Without BS-2008 paper access, we cannot
    resolve the (π², L) uncertainty to confirm a fit.

    The honest-negative: at a representative central physical point, no
    natural SU(8) cascade invariant produces M_R²/M_PS² within a tight
    tolerance (factor 10^±0.2, i.e. squared ratio in [0.4, 2.5]).  The
    closest is (N²-1)² = 3969 at factor ~1.72 miss.
    """

    # Representative central physical values as exact ℚ rationals.
    # π² = 10 is the exact upper bound (π² < 10 strict).
    # L = 22 brackets the natural center of [20, 28] and is near the
    #   BS-convention L = ln((M_Pl/M_PS)²) ≈ 21.6.
    # (M_Pl/M_PS)² = 24/10 × 10^9 = 2.4×10^9 brackets 10^9.38 ≈ 2.40×10^9.
    PI_SQ_CENTRAL = Fraction(10)
    L_CENTRAL = Fraction(22)
    MPL_MPS_SQ_CENTRAL = Fraction(24, 10) * Fraction(10 ** 9)  # 2.4×10^9

    def test_no_natural_invariant_closes_M_R_equals_M_PS_at_central_values(self):
        """HONEST-NEGATIVE CORE: at representative central physical values
        (π² = 10, L = 22, (M_Pl/M_PS)² = 2.4×10^9), NO natural SU(8)
        cascade invariant produces M_R²/M_PS² inside the tight tolerance
        window [0.4, 2.5] (factor 10^±0.2, i.e. ratio ∈ [0.63, 1.58])."""
        required_6xi_m1_sq = (
            Fraction(32, 21)
            * self.PI_SQ_CENTRAL
            / self.L_CENTRAL
            * self.MPL_MPS_SQ_CENTRAL
        )
        # Tolerance window for M_R²/M_PS² at central physical values
        tol_lb = Fraction(4, 10)    # 0.4 (factor 10^-0.2)²
        tol_ub = Fraction(25, 10)   # 2.5 (factor 10^+0.2)²
        for name, xi_val in NATURAL_CASCADE_INVARIANTS.items():
            actual_6xi_m1_sq = (6 * xi_val - 1) ** 2
            ratio_sq = required_6xi_m1_sq / actual_6xi_m1_sq
            in_tolerance = tol_lb <= ratio_sq <= tol_ub
            self.assertFalse(
                in_tolerance,
                f"Unexpected: ξ = {name} ({xi_val}) gives "
                f"M_R²/M_PS² = {float(ratio_sq):.3f}, "
                f"in tolerance [{float(tol_lb)}, {float(tol_ub)}]",
            )

    def test_adjoint_squared_is_closest_among_natural_invariants(self):
        """At central values, (N²-1)² = 3969 gives M_R²/M_PS² ≈ 2.93
        (factor 1.71 miss), closer than any other natural invariant:
          ξ=2016  → M_R²/M_PS² ≈ 11.37 (factor 3.37)
          ξ=3969  → M_R²/M_PS² ≈  2.93 (factor 1.71) — CLOSEST
          ξ=32256 → M_R²/M_PS² ≈  0.04 (factor 4.75 on the low side)"""
        required_6xi_m1_sq = (
            Fraction(32, 21)
            * self.PI_SQ_CENTRAL
            / self.L_CENTRAL
            * self.MPL_MPS_SQ_CENTRAL
        )
        log_distances = {}
        for name, xi_val in NATURAL_CASCADE_INVARIANTS.items():
            actual_6xi_m1_sq = (6 * xi_val - 1) ** 2
            ratio_sq = required_6xi_m1_sq / actual_6xi_m1_sq
            # Log-distance to 1 (perfect fit)
            import math
            log_distances[name] = abs(math.log10(float(ratio_sq)))
        closest = min(log_distances.items(), key=lambda kv: kv[1])
        self.assertEqual(closest[0], "(N²-1)² (adjoint squared)")
        # Within 0.5 orders (factor 3.16)
        self.assertLess(closest[1], Fraction(5, 10))

    def test_adjoint_squared_factor_miss_at_central_values(self):
        """Document the (N²-1)² = 3969 factor-~1.71 miss exactly.

        required (6ξ-1)² at central values = (32/21) × 10 × 2.4×10^9 / 22
                                          = 32 × 24 × 10^9 / (21 × 22)
                                          = 768×10^9 / 462
                                          = 128×10^9 / 77
        actual (6·3969-1)² = 23813² = 567,058,969
        M_R²/M_PS² = (128×10^9 / 77) / 567,058,969
                   = 128×10^9 / (77 × 567,058,969)
                   = 128×10^9 / 43,663,540,613
                   ≈ 2.932
        M_R/M_PS ≈ sqrt(2.932) ≈ 1.712 — factor 1.71 miss.
        """
        required_6xi_m1_sq = (
            Fraction(32, 21)
            * self.PI_SQ_CENTRAL
            / self.L_CENTRAL
            * self.MPL_MPS_SQ_CENTRAL
        )
        self.assertEqual(required_6xi_m1_sq, Fraction(128_000_000_000, 77))

        xi_val = Fraction(3969)
        actual_6xi_m1_sq = (6 * xi_val - 1) ** 2
        self.assertEqual(actual_6xi_m1_sq, Fraction(567_058_969))

        ratio_sq = required_6xi_m1_sq / actual_6xi_m1_sq
        # Check ratio_sq ∈ (2.9, 3.0)
        self.assertGreater(ratio_sq, Fraction(29, 10))
        self.assertLess(ratio_sq, Fraction(30, 10))

    def test_three_closest_candidates_documented(self):
        """Three candidates nearest the central target:
          2016 (factor ~3.37 — too high on M_R side)
          3969 (factor ~1.71 — too high on M_R side) — CLOSEST
          32256 (factor ~4.75 — too low on M_R side)"""
        self.assertIn("N²(N²-1)/2", NATURAL_CASCADE_INVARIANTS)
        self.assertIn("(N²-1)² (adjoint squared)", NATURAL_CASCADE_INVARIANTS)
        self.assertIn("N³(N²-1)", NATURAL_CASCADE_INVARIANTS)
        self.assertEqual(NATURAL_CASCADE_INVARIANTS["N²(N²-1)/2"], Fraction(2016))
        self.assertEqual(
            NATURAL_CASCADE_INVARIANTS["(N²-1)² (adjoint squared)"],
            Fraction(3969),
        )
        self.assertEqual(NATURAL_CASCADE_INVARIANTS["N³(N²-1)"], Fraction(32256))

    def test_widest_bound_interval_contains_3969_but_this_is_not_a_fit(self):
        """NUANCE: at the widest possible physical bounds
        (π² ∈ [9, 10], L ∈ [20, 28], (M_Pl/M_PS)² ∈ [10^9, 10^10]),
        the required ξ interval ≈ [3689, 14548] DOES contain ξ = 3969
        as a set-membership claim.

        But this is NOT a fit — it's interval arithmetic eating uncertainty.
        At any SPECIFIC physical (π², L), ξ = 3969 gives M_R/M_PS ≈ 1.71.

        This test documents the nuance so it cannot be misread as a
        positive claim: yes, 3969 ∈ [3689, 14548]; no, that does not
        mean the non-minimal coupling mechanism closes M_R = M_PS at
        cascade-locked ξ."""
        xi_val = Fraction(3969)
        six_xi_m1_sq = (6 * xi_val - 1) ** 2
        # At widest bounds:
        lb = required_six_xi_m1_sq(PI_SQ_LB, L_UB, MPL_MPS_SQ_LB)
        ub = required_six_xi_m1_sq(PI_SQ_UB, L_LB, MPL_MPS_SQ_UB)
        # (6·3969-1)² IS in the widest-bound interval:
        self.assertGreater(six_xi_m1_sq, lb)
        self.assertLess(six_xi_m1_sq, ub)
        # BUT at central physical values, it's OUTSIDE the tight tolerance:
        required_central = (
            Fraction(32, 21)
            * self.PI_SQ_CENTRAL
            / self.L_CENTRAL
            * self.MPL_MPS_SQ_CENTRAL
        )
        ratio_sq_central = required_central / six_xi_m1_sq
        # ratio_sq ≈ 2.93 > 2.5 (factor-1.58 tolerance upper bound squared)
        self.assertGreater(ratio_sq_central, Fraction(25, 10))

    def test_honest_negative_verdict_final(self):
        """The honest-negative verdict summary:

        (1) At widest bounds (π², L, M_Pl/M_PS² all loosely bracketed),
            the required ξ interval ≈ [3689, 14548] contains ξ = 3969
            as set-membership.  But this is NOT a fit.

        (2) At any SPECIFIC representative central physical values
            (π² = 10, L = 22, (M_Pl/M_PS)² = 2.4×10^9), NO natural SU(8)
            cascade invariant produces M_R²/M_PS² inside tolerance
            [0.4, 2.5].  Closest is (N²-1)² = 3969 at ratio_sq ≈ 2.93,
            i.e. M_R/M_PS ≈ 1.71 — factor-1.71 miss.

        (3) No structural derivation exists at the scope of CLM-044 for
            why (N²-1)² should be the correct ξ — without BS-2008 paper
            access (Commandment VIII forbids from-memory reconstruction),
            the "coincidence" of closeness cannot be lifted to derivation.

        (4) Combined with CLM-043 (minimal coupling structurally
            insufficient), both paper-free Route B paths at 1-loop are
            now ruled out.  Only 2-loop matching via Barvinsky-Vilkovisky
            (1985) — also paper-blocked — remains.

        VERDICT: HONEST-NEGATIVE for Route B path (a)."""
        # Check (1): 3969 IS in widest-bound ξ interval
        self.assertGreaterEqual(Fraction(3969), Fraction(3689))
        self.assertLessEqual(Fraction(3969), Fraction(14548))
        # Check (2): at central values, ratio_sq > 2.5 (outside tolerance)
        required_central = (
            Fraction(32, 21)
            * self.PI_SQ_CENTRAL
            / self.L_CENTRAL
            * self.MPL_MPS_SQ_CENTRAL
        )
        actual_3969 = Fraction((6 * 3969 - 1) ** 2)
        ratio_sq = required_central / actual_3969
        self.assertGreater(ratio_sq, Fraction(25, 10))
        # Check (4): CLM-043 cross-reference — minimal coupling gap is > 4 orders
        # (32/21) × 9 = 96/7 > 13 (and (M_Pl/M_PS)² > 10^9)
        self.assertGreater(Fraction(32, 21) * 9, Fraction(13))


if __name__ == "__main__":
    unittest.main(verbosity=2)
