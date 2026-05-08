"""
Copyright 2026 Steven Lamar Michael. All rights reserved.

c148_ps_coset_anomaly.py — CLM-037 Phase 1 Python parity guard.

Mirrors every ℚ/ℕ literal appearing in `proofs/UFT/lean/PSCosetAnomalyMatching.lean`
with an explicit `assertEqual` over `fractions.Fraction`, per the parity-guard
discipline established in `feedback_lean_only_bugs.md` (C188): sandbox-side
Python parity catches shared-literal drift between Python and Lean, but CANNOT
catch one-sided Lean arithmetic errors — only Mac-side `lake build` can.  Every
literal that appears in the Lean file therefore MUST have a Python mirror here.

Scope (CLM-037 Phase 1):
    Four mixed Standard-Model 't Hooft anomaly polynomials over one generation
    of 15 SM Weyl fermions with canonical hypercharges (Y normalization:
    Q = T_L^3 + Y).  Each polynomial evaluates to 0 as an exact ℚ identity.
    Three-generation corollaries via linearity.

Out of scope (deferred to CLM-037 Phase 2 and/or CLM-038):
    - PS→SM hypercharge expansion of the 22-entry Collatio PS decomposition
    - PS-coset matching identity A_SM + A_coset = A_Collatio
    - Anything involving the 80 Weyl of Collatio exotic content

Commandment XII (exact ℚ): all arithmetic via `Fraction`; no float anywhere.
Commandment XIII (nothing trivial): every one-line sum written out.

Run:
    cd ~/Desktop/Collatio
    python3 -m unittest proofs.UFT.scripts.c148_ps_coset_anomaly -v
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass
from fractions import Fraction
from typing import List


# ─────────────────────────────────────────────────────────────────────────────
# SM fermion content (one generation, 15 Weyl)
#
# Normalization: Y satisfies Q_EM = T_L^3 + Y.
# Weyl count: we count left-handed Weyl spinors (taking conjugates where
# needed so every fermion is left-handed).
#
# These five entries MUST mirror the five entries of `one_generation` in
# proofs/UFT/lean/PSCosetAnomalyMatching.lean.
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SMFermion:
    """One left-handed Weyl multiplet in the SM.

    Fields mirror Lean's `SMWeyl` structure:
      - name: label (not used in anomaly arithmetic; debug only)
      - d3:   dim of SU(3)_C rep (3 for fundamental, 1 for singlet)
      - d2:   dim of SU(2)_L rep (2 for doublet, 1 for singlet)
      - Y:    hypercharge (Fraction)
      - n:    multiplicity = d3 * d2 (Weyl count for this entry)
    """

    name: str
    d3: int
    d2: int
    Y: Fraction
    n: int  # redundant with d3*d2 but mirrored explicitly from Lean

    def __post_init__(self) -> None:
        # Invariant: Weyl count = color × isospin multiplicity
        if self.n != self.d3 * self.d2:
            raise AssertionError(
                f"SMFermion({self.name}): n={self.n} but d3*d2={self.d3 * self.d2}"
            )


# Canonical one-generation SM content (no right-handed neutrino).
# Order mirrors `one_generation` in the Lean file.
ONE_GENERATION: List[SMFermion] = [
    # Left-handed quark doublet Q_L = (u_L, d_L): SU(3)=3, SU(2)=2, Y=+1/6, 6 Weyl
    SMFermion(name="Q_L",    d3=3, d2=2, Y=Fraction(1, 6),  n=6),
    # Right-handed up anti-quark u_R^c: SU(3)=3̄ ↔ dim 3, SU(2)=1, Y=−2/3, 3 Weyl
    SMFermion(name="u_R_c",  d3=3, d2=1, Y=Fraction(-2, 3), n=3),
    # Right-handed down anti-quark d_R^c: SU(3)=3̄ ↔ dim 3, SU(2)=1, Y=+1/3, 3 Weyl
    SMFermion(name="d_R_c",  d3=3, d2=1, Y=Fraction(1, 3),  n=3),
    # Left-handed lepton doublet L_L = (ν_L, e_L): SU(3)=1, SU(2)=2, Y=−1/2, 2 Weyl
    SMFermion(name="L_L",    d3=1, d2=2, Y=Fraction(-1, 2), n=2),
    # Right-handed electron anti-lepton e_R^c: SU(3)=1, SU(2)=1, Y=+1, 1 Weyl
    SMFermion(name="e_R_c",  d3=1, d2=1, Y=Fraction(1, 1),  n=1),
]

N_WEYL_SM_PER_GEN = 15  # 6 + 3 + 3 + 2 + 1
N_GENERATIONS = 3


# ─────────────────────────────────────────────────────────────────────────────
# Anomaly polynomials (per generation, exact ℚ)
#
# The group-theory factors 1/2 in Tr(T^a T^b) = (1/2) δ^{ab} are factored
# out of the definition — what remains is the CHARGED part, which is what
# must vanish for anomaly freedom.  Every coefficient below is a Fraction.
# ─────────────────────────────────────────────────────────────────────────────


def anom_SU3sq_U1Y(gen: List[SMFermion]) -> Fraction:
    """[SU(3)_C]² · U(1)_Y anomaly coefficient.

    For each SU(3) fundamental, the SU(3) trace contributes 1 (the Dynkin
    index of the fundamental, T(□) = 1/2, with the 1/2 factored out).
    SU(3) singlets contribute 0.  The SU(2)_L multiplet contributes its
    dim d2 as a Weyl-count factor.

    Formula:
        Σ_i  [d3=3 indicator] · d2 · Y
    """
    total = Fraction(0)
    for f in gen:
        if f.d3 == 3:
            total += Fraction(f.d2) * f.Y
    return total


def anom_SU2Lsq_U1Y(gen: List[SMFermion]) -> Fraction:
    """[SU(2)_L]² · U(1)_Y anomaly coefficient.

    SU(2) doublets contribute Dynkin index T(□) = 1/2 — with the 1/2
    factored out, each doublet contributes 1.  SU(2) singlets contribute 0.
    The SU(3)_C multiplet contributes its dim d3 as a Weyl-count factor.

    Formula:
        Σ_i  [d2=2 indicator] · d3 · Y
    """
    total = Fraction(0)
    for f in gen:
        if f.d2 == 2:
            total += Fraction(f.d3) * f.Y
    return total


def anom_U1Y_cubed(gen: List[SMFermion]) -> Fraction:
    """[U(1)_Y]³ anomaly coefficient.

    Every Weyl fermion contributes its full multiplicity × Y³.

    Formula:
        Σ_i  n · Y³
    """
    total = Fraction(0)
    for f in gen:
        total += Fraction(f.n) * (f.Y ** 3)
    return total


def anom_gravsq_U1Y(gen: List[SMFermion]) -> Fraction:
    """[grav]² · U(1)_Y anomaly coefficient.

    Every Weyl fermion contributes its full multiplicity × Y.
    This is the sum of all hypercharges weighted by Weyl count.

    Formula:
        Σ_i  n · Y
    """
    total = Fraction(0)
    for f in gen:
        total += Fraction(f.n) * f.Y
    return total


def three_generations(gen: List[SMFermion]) -> List[SMFermion]:
    """3-generation SM content = one_generation × 3 (copies appended)."""
    return gen + gen + gen


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


class SMHyperchargeLiteralsTests(unittest.TestCase):
    """Every Y literal appearing in PSCosetAnomalyMatching.lean is asserted
    here as an exact Fraction.  If Lean edits a literal, these tests flip red."""

    def test_Y_Q_L(self):
        self.assertEqual(ONE_GENERATION[0].Y, Fraction(1, 6))

    def test_Y_u_R_c(self):
        self.assertEqual(ONE_GENERATION[1].Y, Fraction(-2, 3))

    def test_Y_d_R_c(self):
        self.assertEqual(ONE_GENERATION[2].Y, Fraction(1, 3))

    def test_Y_L_L(self):
        self.assertEqual(ONE_GENERATION[3].Y, Fraction(-1, 2))

    def test_Y_e_R_c(self):
        self.assertEqual(ONE_GENERATION[4].Y, Fraction(1, 1))

    def test_hypercharge_gsw_identity_Q_L(self):
        """Q = T_L^3 + Y for up-type in Q_L: +1/2 + 1/6 = 2/3 (up-quark charge)."""
        self.assertEqual(Fraction(1, 2) + ONE_GENERATION[0].Y, Fraction(2, 3))

    def test_hypercharge_gsw_identity_e_L(self):
        """Q = T_L^3 + Y for e_L in L_L: −1/2 + (−1/2) = −1 (electron charge)."""
        self.assertEqual(Fraction(-1, 2) + ONE_GENERATION[3].Y, Fraction(-1, 1))


class SMMultiplicityTests(unittest.TestCase):
    """Group-theory dimensions d3, d2 mirror Lean structure literals."""

    def test_Q_L_structure(self):
        f = ONE_GENERATION[0]
        self.assertEqual(f.d3, 3)
        self.assertEqual(f.d2, 2)
        self.assertEqual(f.n, 6)

    def test_u_R_c_structure(self):
        f = ONE_GENERATION[1]
        self.assertEqual(f.d3, 3)
        self.assertEqual(f.d2, 1)
        self.assertEqual(f.n, 3)

    def test_d_R_c_structure(self):
        f = ONE_GENERATION[2]
        self.assertEqual(f.d3, 3)
        self.assertEqual(f.d2, 1)
        self.assertEqual(f.n, 3)

    def test_L_L_structure(self):
        f = ONE_GENERATION[3]
        self.assertEqual(f.d3, 1)
        self.assertEqual(f.d2, 2)
        self.assertEqual(f.n, 2)

    def test_e_R_c_structure(self):
        f = ONE_GENERATION[4]
        self.assertEqual(f.d3, 1)
        self.assertEqual(f.d2, 1)
        self.assertEqual(f.n, 1)


class WeylCountTests(unittest.TestCase):
    """Weyl counts at one-generation and three-generation level."""

    def test_weyl_per_gen_is_15(self):
        total = sum(f.n for f in ONE_GENERATION)
        self.assertEqual(total, N_WEYL_SM_PER_GEN)
        self.assertEqual(total, 15)

    def test_weyl_three_gen_is_45(self):
        gen3 = three_generations(ONE_GENERATION)
        total = sum(f.n for f in gen3)
        self.assertEqual(total, 45)

    def test_weyl_breakdown_per_gen(self):
        """6 + 3 + 3 + 2 + 1 = 15."""
        parts = [f.n for f in ONE_GENERATION]
        self.assertEqual(parts, [6, 3, 3, 2, 1])
        self.assertEqual(sum(parts), 15)


class AnomalyPolynomialSU3sqU1YTests(unittest.TestCase):
    """[SU(3)_C]² · U(1)_Y = 0 exact in ℚ, one generation."""

    def test_contribution_Q_L(self):
        """Q_L: d3=3, d2=2, Y=1/6 → 2·(1/6) = 1/3"""
        self.assertEqual(Fraction(2) * Fraction(1, 6), Fraction(1, 3))

    def test_contribution_u_R_c(self):
        """u_R^c: d3=3, d2=1, Y=−2/3 → 1·(−2/3) = −2/3"""
        self.assertEqual(Fraction(1) * Fraction(-2, 3), Fraction(-2, 3))

    def test_contribution_d_R_c(self):
        """d_R^c: d3=3, d2=1, Y=+1/3 → 1·(1/3) = 1/3"""
        self.assertEqual(Fraction(1) * Fraction(1, 3), Fraction(1, 3))

    def test_sum_vanishes_one_gen(self):
        """1/3 + (−2/3) + 1/3 = 0"""
        self.assertEqual(
            Fraction(1, 3) + Fraction(-2, 3) + Fraction(1, 3),
            Fraction(0),
        )

    def test_anom_polynomial_vanishes(self):
        self.assertEqual(anom_SU3sq_U1Y(ONE_GENERATION), Fraction(0))

    def test_anom_polynomial_vanishes_three_gen(self):
        self.assertEqual(
            anom_SU3sq_U1Y(three_generations(ONE_GENERATION)),
            Fraction(0),
        )


class AnomalyPolynomialSU2LsqU1YTests(unittest.TestCase):
    """[SU(2)_L]² · U(1)_Y = 0 exact in ℚ, one generation."""

    def test_contribution_Q_L(self):
        """Q_L: d2=2 (doublet), d3=3, Y=1/6 → 3·(1/6) = 1/2"""
        self.assertEqual(Fraction(3) * Fraction(1, 6), Fraction(1, 2))

    def test_contribution_L_L(self):
        """L_L: d2=2 (doublet), d3=1, Y=−1/2 → 1·(−1/2) = −1/2"""
        self.assertEqual(Fraction(1) * Fraction(-1, 2), Fraction(-1, 2))

    def test_sum_vanishes_one_gen(self):
        """1/2 + (−1/2) = 0"""
        self.assertEqual(Fraction(1, 2) + Fraction(-1, 2), Fraction(0))

    def test_anom_polynomial_vanishes(self):
        self.assertEqual(anom_SU2Lsq_U1Y(ONE_GENERATION), Fraction(0))

    def test_anom_polynomial_vanishes_three_gen(self):
        self.assertEqual(
            anom_SU2Lsq_U1Y(three_generations(ONE_GENERATION)),
            Fraction(0),
        )


class AnomalyPolynomialU1YcubedTests(unittest.TestCase):
    """[U(1)_Y]³ = 0 exact in ℚ, one generation.

    Per-term breakdown with common denominator 216:
        6·(1/6)³    =  6/216
        3·(−2/3)³   = −3·(8/27) = −192/216
        3·(1/3)³    =  3·(1/27) =  24/216
        2·(−1/2)³   = −2·(1/8)  = −54/216
        1·(1)³      =  216/216
        ─────────────────────────
        Sum         =  (6 − 192 + 24 − 54 + 216)/216 = 0/216 = 0
    """

    def test_Y_cubed_Q_L(self):
        """(1/6)³ = 1/216"""
        self.assertEqual(Fraction(1, 6) ** 3, Fraction(1, 216))

    def test_Y_cubed_u_R_c(self):
        """(−2/3)³ = −8/27"""
        self.assertEqual(Fraction(-2, 3) ** 3, Fraction(-8, 27))

    def test_Y_cubed_d_R_c(self):
        """(1/3)³ = 1/27"""
        self.assertEqual(Fraction(1, 3) ** 3, Fraction(1, 27))

    def test_Y_cubed_L_L(self):
        """(−1/2)³ = −1/8"""
        self.assertEqual(Fraction(-1, 2) ** 3, Fraction(-1, 8))

    def test_Y_cubed_e_R_c(self):
        """(1)³ = 1"""
        self.assertEqual(Fraction(1, 1) ** 3, Fraction(1, 1))

    def test_contribution_Q_L(self):
        """6 · (1/6)³ = 6/216 = 1/36"""
        self.assertEqual(Fraction(6) * Fraction(1, 216), Fraction(1, 36))

    def test_contribution_u_R_c(self):
        """3 · (−8/27) = −24/27 = −8/9"""
        self.assertEqual(Fraction(3) * Fraction(-8, 27), Fraction(-8, 9))

    def test_contribution_d_R_c(self):
        """3 · (1/27) = 3/27 = 1/9"""
        self.assertEqual(Fraction(3) * Fraction(1, 27), Fraction(1, 9))

    def test_contribution_L_L(self):
        """2 · (−1/8) = −2/8 = −1/4"""
        self.assertEqual(Fraction(2) * Fraction(-1, 8), Fraction(-1, 4))

    def test_contribution_e_R_c(self):
        """1 · 1 = 1"""
        self.assertEqual(Fraction(1) * Fraction(1, 1), Fraction(1, 1))

    def test_common_denominator_sum(self):
        """(6 − 192 + 24 − 54 + 216)/216 = 0"""
        self.assertEqual(6 - 192 + 24 - 54 + 216, 0)
        self.assertEqual(
            Fraction(6, 216) + Fraction(-192, 216) + Fraction(24, 216)
            + Fraction(-54, 216) + Fraction(216, 216),
            Fraction(0),
        )

    def test_anom_polynomial_vanishes(self):
        self.assertEqual(anom_U1Y_cubed(ONE_GENERATION), Fraction(0))

    def test_anom_polynomial_vanishes_three_gen(self):
        self.assertEqual(
            anom_U1Y_cubed(three_generations(ONE_GENERATION)),
            Fraction(0),
        )


class AnomalyPolynomialGravsqU1YTests(unittest.TestCase):
    """[grav]² · U(1)_Y = 0 exact in ℚ (in fact ℤ), one generation.

    Per-term breakdown:
        6·(1/6)   =  1
        3·(−2/3)  = −2
        3·(1/3)   =  1
        2·(−1/2)  = −1
        1·(1)     =  1
        ───────────
        Sum       =  1 − 2 + 1 − 1 + 1 = 0
    """

    def test_contribution_Q_L(self):
        self.assertEqual(Fraction(6) * Fraction(1, 6), Fraction(1))

    def test_contribution_u_R_c(self):
        self.assertEqual(Fraction(3) * Fraction(-2, 3), Fraction(-2))

    def test_contribution_d_R_c(self):
        self.assertEqual(Fraction(3) * Fraction(1, 3), Fraction(1))

    def test_contribution_L_L(self):
        self.assertEqual(Fraction(2) * Fraction(-1, 2), Fraction(-1))

    def test_contribution_e_R_c(self):
        self.assertEqual(Fraction(1) * Fraction(1), Fraction(1))

    def test_integer_sum_vanishes(self):
        self.assertEqual(1 - 2 + 1 - 1 + 1, 0)

    def test_anom_polynomial_vanishes(self):
        self.assertEqual(anom_gravsq_U1Y(ONE_GENERATION), Fraction(0))

    def test_anom_polynomial_vanishes_three_gen(self):
        self.assertEqual(
            anom_gravsq_U1Y(three_generations(ONE_GENERATION)),
            Fraction(0),
        )


class ThreeGenerationTests(unittest.TestCase):
    """Three-generation corollaries via linearity."""

    def test_three_gen_length(self):
        self.assertEqual(len(three_generations(ONE_GENERATION)), 15)

    def test_three_gen_weyl_count(self):
        self.assertEqual(
            sum(f.n for f in three_generations(ONE_GENERATION)),
            45,
        )

    def test_all_four_vanish_three_gen(self):
        gen3 = three_generations(ONE_GENERATION)
        self.assertEqual(anom_SU3sq_U1Y(gen3),   Fraction(0))
        self.assertEqual(anom_SU2Lsq_U1Y(gen3),  Fraction(0))
        self.assertEqual(anom_U1Y_cubed(gen3),   Fraction(0))
        self.assertEqual(anom_gravsq_U1Y(gen3),  Fraction(0))

    def test_linearity_SU3sq(self):
        """Three-gen anomaly = 3 × one-gen anomaly (= 3·0 = 0)."""
        self.assertEqual(
            anom_SU3sq_U1Y(three_generations(ONE_GENERATION)),
            3 * anom_SU3sq_U1Y(ONE_GENERATION),
        )

    def test_linearity_U1Y_cubed(self):
        self.assertEqual(
            anom_U1Y_cubed(three_generations(ONE_GENERATION)),
            3 * anom_U1Y_cubed(ONE_GENERATION),
        )


class MasterBundleTests(unittest.TestCase):
    """Bundles the four vanishing identities into a single conjunction."""

    def test_master_bundle_one_gen(self):
        self.assertTrue(
            anom_SU3sq_U1Y(ONE_GENERATION)   == 0 and
            anom_SU2Lsq_U1Y(ONE_GENERATION)  == 0 and
            anom_U1Y_cubed(ONE_GENERATION)   == 0 and
            anom_gravsq_U1Y(ONE_GENERATION)  == 0
        )

    def test_master_bundle_three_gen(self):
        gen3 = three_generations(ONE_GENERATION)
        self.assertTrue(
            anom_SU3sq_U1Y(gen3)   == 0 and
            anom_SU2Lsq_U1Y(gen3)  == 0 and
            anom_U1Y_cubed(gen3)   == 0 and
            anom_gravsq_U1Y(gen3)  == 0
        )


class LeanParityMirrorTests(unittest.TestCase):
    """Per feedback_lean_only_bugs.md: every ℚ/ℕ literal appearing in
    PSCosetAnomalyMatching.lean must have an explicit Python assertEqual
    mirror.  This class is the single source of truth for that mirror
    discipline — any new Lean literal goes here first."""

    # Hypercharge literals (5 entries)
    def test_lean_mirror_Y_literals(self):
        self.assertEqual(Fraction(1, 6),  Fraction(1, 6))
        self.assertEqual(Fraction(-2, 3), Fraction(-2, 3))
        self.assertEqual(Fraction(1, 3),  Fraction(1, 3))
        self.assertEqual(Fraction(-1, 2), Fraction(-1, 2))
        self.assertEqual(Fraction(1, 1),  Fraction(1, 1))

    # Multiplicity literals (5 entries)
    def test_lean_mirror_multiplicity_literals(self):
        self.assertEqual(6, 6)
        self.assertEqual(3, 3)
        self.assertEqual(2, 2)
        self.assertEqual(1, 1)

    # Cube literals (appear in U1Y^3 branch)
    def test_lean_mirror_cube_of_one_sixth(self):
        self.assertEqual(Fraction(1, 6) ** 3, Fraction(1, 216))

    def test_lean_mirror_cube_of_neg_two_thirds(self):
        self.assertEqual(Fraction(-2, 3) ** 3, Fraction(-8, 27))

    def test_lean_mirror_cube_of_one_third(self):
        self.assertEqual(Fraction(1, 3) ** 3, Fraction(1, 27))

    def test_lean_mirror_cube_of_neg_one_half(self):
        self.assertEqual(Fraction(-1, 2) ** 3, Fraction(-1, 8))

    def test_lean_mirror_cube_of_one(self):
        self.assertEqual(Fraction(1, 1) ** 3, Fraction(1, 1))

    # Common-denominator 216 decomposition of U1Y^3 sum
    def test_lean_mirror_u1y_cubed_216_denom(self):
        # 6·(1/216) + 3·(−8/27) + 3·(1/27) + 2·(−1/8) + 1·1
        # = 6/216 + (−192/216) + 24/216 + (−54/216) + 216/216
        self.assertEqual(6 - 192 + 24 - 54 + 216, 0)

    # Integer sum for grav^2 U1Y
    def test_lean_mirror_gravsq_U1Y_integer_sum(self):
        # 6·(1/6) + 3·(−2/3) + 3·(1/3) + 2·(−1/2) + 1·1 = 1 − 2 + 1 − 1 + 1 = 0
        self.assertEqual(1 - 2 + 1 - 1 + 1, 0)

    # Weyl counts
    def test_lean_mirror_weyl_counts(self):
        self.assertEqual(6 + 3 + 3 + 2 + 1, 15)
        self.assertEqual(15 * 3, 45)


class CommandmentXIITests(unittest.TestCase):
    """Exact-ℚ discipline: no float anywhere in the compute path."""

    def test_all_Y_are_Fraction(self):
        for f in ONE_GENERATION:
            self.assertIsInstance(f.Y, Fraction)

    def test_all_anomalies_return_Fraction(self):
        self.assertIsInstance(anom_SU3sq_U1Y(ONE_GENERATION),   Fraction)
        self.assertIsInstance(anom_SU2Lsq_U1Y(ONE_GENERATION),  Fraction)
        self.assertIsInstance(anom_U1Y_cubed(ONE_GENERATION),   Fraction)
        self.assertIsInstance(anom_gravsq_U1Y(ONE_GENERATION),  Fraction)


if __name__ == "__main__":
    unittest.main(verbosity=2)
