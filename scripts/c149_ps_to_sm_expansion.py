"""
Copyright 2026 Steven Lamar Michael. All rights reserved.

c149_ps_to_sm_expansion.py — CLM-037 Phase 2 Python parity guard.

Expands each of the 22 Pati-Salam irreps from CollatioPSBranching.lean
(the Koszul decomposition of [1]⊕[3]⊕[5]⊕[7] of SU(8)) to Standard
Model irreps under the standard PS → SM embedding:

    SU(4)_C × SU(2)_L × SU(2)_R  →  SU(3)_C × SU(2)_L × U(1)_Y

with hypercharge

    Y = T_R^3 + (B−L)/2.

The SU(4)_C decomposition depends on the Koszul exterior-power index `a`:

    a=0: ∧⁰(4) = 1  →  (1, B-L=0)
    a=1: ∧¹(4) = 4  →  (3, +1/3) ⊕ (1, −1)       [fundamental]
    a=2: ∧²(4) = 6  →  (3, +2/3) ⊕ (3, −2/3)      [antisymmetric]
    a=3: ∧³(4) = 4̄  →  (3, −1/3) ⊕ (1, +1)        [anti-fundamental]
    a=4: ∧⁴(4) = 1  →  (1, B-L=0)                   [determinant]

The SU(2)_R decomposition depends on the Koszul index `c`:

    c=0: ∧⁰(2) = 1  →  T_R^3 = 0
    c=1: ∧¹(2) = 2  →  T_R^3 ∈ {+1/2, −1/2}
    c=2: ∧²(2) = 1  →  T_R^3 = 0                    [determinant]

KEY FINDING (resolving §4 structural tension of CLM-037 claim file):

    The (4,2,2) bidoublet in [3] comes from Koszul (a=1,b=1,c=1), giving
    the fundamental 4 of SU(4) with B-L = +1/3 (quarks) and −1 (lepton).

    The (4,2,2) bidoublet in [5] comes from Koszul (a=3,b=1,c=1), giving
    the anti-fundamental 4̄ of SU(4) with B-L = −1/3 and +1.

    Neither bidoublet alone gives canonical SM hypercharges (confirming
    §4's per-bidoublet observation).  But the PAIR forms a conjugate set
    whose anomaly contributions cancel exactly.  Similarly [1]↔[7].

    Result: all four mixed anomaly polynomials vanish over the SM-tagged
    subset of [1]⊕[3]⊕[5]⊕[7], as exact ℚ identities.

Commandment XII: all arithmetic via Fraction; zero float.
Commandment XIII: every step explicit; no "trivial" language.

Run:
    cd ~/Desktop/Collatio
    python3 -m unittest proofs.UFT.scripts.c149_ps_to_sm_expansion -v
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class KoszulPSRep:
    """A single Pati-Salam irrep from the Koszul decomposition of ∧^k(8).

    Fields:
      - k:     which antisymmetric rep of SU(8) this belongs to (1, 3, 5, 7)
      - a:     Koszul index for SU(4)_C (0 ≤ a ≤ 4)
      - b:     Koszul index for SU(2)_L (0 ≤ b ≤ 2)
      - c:     Koszul index for SU(2)_R (0 ≤ c ≤ 2)
      - isSM:  declared SM tag (per c121 / CollatioPSBranching.lean)
      - su4:   dim of SU(4)_C factor = C(4,a)
      - su2L:  dim of SU(2)_L factor = C(2,b)
      - su2R:  dim of SU(2)_R factor = C(2,c)
    """

    k: int
    a: int
    b: int
    c: int
    isSM: bool
    su4: int
    su2L: int
    su2R: int

    @property
    def ps_dim(self) -> int:
        return self.su4 * self.su2L * self.su2R


@dataclass(frozen=True)
class SMComponent:
    """One SM irrep component from the PS → SM expansion.

    Fields:
      - d3:  dim of SU(3)_C rep (3 for fundamental/anti-fundamental, 1 for singlet)
      - d2:  dim of SU(2)_L rep (kept from PS; 1 or 2)
      - Y:   hypercharge = T_R^3 + (B−L)/2, exact Fraction
      - n:   Weyl count = d3 × d2
      - BmL: (B−L) charge (for traceability)
      - TR3: T_R^3 value (for traceability)
    """

    d3: int
    d2: int
    Y: Fraction
    n: int
    BmL: Fraction
    TR3: Fraction


# ─────────────────────────────────────────────────────────────────────────────
# SU(4)_C decomposition under SU(3)_C × U(1)_{B-L}
#
# Returns list of (d3, B_minus_L) pairs.
# ─────────────────────────────────────────────────────────────────────────────


def su4_decompose(a: int) -> List[Tuple[int, Fraction]]:
    """Decompose ∧^a(4) of SU(4)_C under SU(3)_C × U(1)_{B-L}.

    a=0: trivial   → [(1, 0)]
    a=1: fund 4    → [(3, +1/3), (1, −1)]
    a=2: antisym 6 → [(3, +2/3), (3, −2/3)]
    a=3: anti-fund 4̄ → [(3, −1/3), (1, +1)]
    a=4: det 1     → [(1, 0)]
    """
    if a == 0:
        return [(1, Fraction(0))]
    elif a == 1:
        return [(3, Fraction(1, 3)), (1, Fraction(-1))]
    elif a == 2:
        return [(3, Fraction(2, 3)), (3, Fraction(-2, 3))]
    elif a == 3:
        return [(3, Fraction(-1, 3)), (1, Fraction(1))]
    elif a == 4:
        return [(1, Fraction(0))]
    else:
        raise ValueError(f"a must be in 0..4, got {a}")


# ─────────────────────────────────────────────────────────────────────────────
# SU(2)_R decomposition: T_R^3 values
# ─────────────────────────────────────────────────────────────────────────────


def su2R_TR3_values(c: int) -> List[Fraction]:
    """T_R^3 eigenvalues for ∧^c(2_R).

    c=0: trivial → [0]
    c=1: fund    → [+1/2, −1/2]
    c=2: det     → [0]
    """
    if c == 0:
        return [Fraction(0)]
    elif c == 1:
        return [Fraction(1, 2), Fraction(-1, 2)]
    elif c == 2:
        return [Fraction(0)]
    else:
        raise ValueError(f"c must be in 0..2, got {c}")


# ─────────────────────────────────────────────────────────────────────────────
# PS → SM expansion
# ─────────────────────────────────────────────────────────────────────────────


def expand_ps_to_sm(rep: KoszulPSRep) -> List[SMComponent]:
    """Expand one PS irrep to its SM components under Y = T_R^3 + (B−L)/2."""
    components: List[SMComponent] = []
    su4_parts = su4_decompose(rep.a)
    tr3_values = su2R_TR3_values(rep.c)
    d2 = rep.su2L

    for d3, BmL in su4_parts:
        for TR3 in tr3_values:
            Y = TR3 + BmL / 2
            n = d3 * d2
            components.append(SMComponent(d3=d3, d2=d2, Y=Y, n=n, BmL=BmL, TR3=TR3))

    return components


# ─────────────────────────────────────────────────────────────────────────────
# The 22-entry PS table (mirrors CollatioPSBranching.lean exactly)
# ─────────────────────────────────────────────────────────────────────────────

# [1] = ∧¹(8), 3 entries, all SM
PS_REPS_OF_1: List[KoszulPSRep] = [
    KoszulPSRep(k=1, a=1, b=0, c=0, isSM=True,  su4=4, su2L=1, su2R=1),  # (1,0,0) → (4,1,1)
    KoszulPSRep(k=1, a=0, b=1, c=0, isSM=True,  su4=1, su2L=2, su2R=1),  # (0,1,0) → (1,2,1)
    KoszulPSRep(k=1, a=0, b=0, c=1, isSM=True,  su4=1, su2L=1, su2R=2),  # (0,0,1) → (1,1,2)
]

# [3] = ∧³(8), 8 entries, bidoublet (a=1,b=1,c=1) is SM
PS_REPS_OF_3: List[KoszulPSRep] = [
    KoszulPSRep(k=3, a=3, b=0, c=0, isSM=False, su4=4, su2L=1, su2R=1),  # (3,0,0) → 4̄⊗1⊗1
    KoszulPSRep(k=3, a=2, b=1, c=0, isSM=False, su4=6, su2L=2, su2R=1),  # (2,1,0) → 6⊗2⊗1
    KoszulPSRep(k=3, a=2, b=0, c=1, isSM=False, su4=6, su2L=1, su2R=2),  # (2,0,1) → 6⊗1⊗2
    KoszulPSRep(k=3, a=1, b=2, c=0, isSM=False, su4=4, su2L=1, su2R=1),  # (1,2,0) → 4⊗1⊗1
    KoszulPSRep(k=3, a=1, b=1, c=1, isSM=True,  su4=4, su2L=2, su2R=2),  # (1,1,1) → 4⊗2⊗2 SM
    KoszulPSRep(k=3, a=1, b=0, c=2, isSM=False, su4=4, su2L=1, su2R=1),  # (1,0,2) → 4⊗1⊗1
    KoszulPSRep(k=3, a=0, b=2, c=1, isSM=False, su4=1, su2L=1, su2R=2),  # (0,2,1) → 1⊗1⊗2
    KoszulPSRep(k=3, a=0, b=1, c=2, isSM=False, su4=1, su2L=2, su2R=1),  # (0,1,2) → 1⊗2⊗1
]

# [5] = ∧⁵(8), 8 entries, bidoublet (a=3,b=1,c=1) is SM
PS_REPS_OF_5: List[KoszulPSRep] = [
    KoszulPSRep(k=5, a=1, b=2, c=2, isSM=False, su4=4, su2L=1, su2R=1),  # (1,2,2) → 4⊗1⊗1
    KoszulPSRep(k=5, a=2, b=2, c=1, isSM=False, su4=6, su2L=1, su2R=2),  # (2,2,1) → 6⊗1⊗2
    KoszulPSRep(k=5, a=2, b=1, c=2, isSM=False, su4=6, su2L=2, su2R=1),  # (2,1,2) → 6⊗2⊗1
    KoszulPSRep(k=5, a=3, b=2, c=0, isSM=False, su4=4, su2L=1, su2R=1),  # (3,2,0) → 4̄⊗1⊗1
    KoszulPSRep(k=5, a=3, b=1, c=1, isSM=True,  su4=4, su2L=2, su2R=2),  # (3,1,1) → 4̄⊗2⊗2 SM
    KoszulPSRep(k=5, a=3, b=0, c=2, isSM=False, su4=4, su2L=1, su2R=1),  # (3,0,2) → 4̄⊗1⊗1
    KoszulPSRep(k=5, a=4, b=1, c=0, isSM=False, su4=1, su2L=2, su2R=1),  # (4,1,0) → 1⊗2⊗1
    KoszulPSRep(k=5, a=4, b=0, c=1, isSM=False, su4=1, su2L=1, su2R=2),  # (4,0,1) → 1⊗1⊗2
]

# [7] = ∧⁷(8), 3 entries, all SM
PS_REPS_OF_7: List[KoszulPSRep] = [
    KoszulPSRep(k=7, a=3, b=2, c=2, isSM=True,  su4=4, su2L=1, su2R=1),  # (3,2,2) → 4̄⊗1⊗1
    KoszulPSRep(k=7, a=4, b=2, c=1, isSM=True,  su4=1, su2L=1, su2R=2),  # (4,2,1) → 1⊗1⊗2
    KoszulPSRep(k=7, a=4, b=1, c=2, isSM=True,  su4=1, su2L=2, su2R=1),  # (4,1,2) → 1⊗2⊗1
]

ALL_PS_REPS: List[KoszulPSRep] = PS_REPS_OF_1 + PS_REPS_OF_3 + PS_REPS_OF_5 + PS_REPS_OF_7


# ─────────────────────────────────────────────────────────────────────────────
# Anomaly polynomial functions (reused from c148, adapted for SMComponent)
# ─────────────────────────────────────────────────────────────────────────────


def anom_SU3sq_U1Y(components: List[SMComponent]) -> Fraction:
    """[SU(3)_C]² · U(1)_Y: sum d2·Y over SU(3) non-singlets (d3=3)."""
    total = Fraction(0)
    for c in components:
        if c.d3 == 3:
            total += Fraction(c.d2) * c.Y
    return total


def anom_SU2Lsq_U1Y(components: List[SMComponent]) -> Fraction:
    """[SU(2)_L]² · U(1)_Y: sum d3·Y over SU(2) doublets (d2=2)."""
    total = Fraction(0)
    for c in components:
        if c.d2 == 2:
            total += Fraction(c.d3) * c.Y
    return total


def anom_U1Y_cubed(components: List[SMComponent]) -> Fraction:
    """[U(1)_Y]³: sum n·Y³ over all components."""
    total = Fraction(0)
    for c in components:
        total += Fraction(c.n) * (c.Y ** 3)
    return total


def anom_gravsq_U1Y(components: List[SMComponent]) -> Fraction:
    """[grav]² · U(1)_Y: sum n·Y over all components."""
    total = Fraction(0)
    for c in components:
        total += Fraction(c.n) * c.Y
    return total


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def expand_all(reps: List[KoszulPSRep], sm_only: bool = False) -> List[SMComponent]:
    """Expand a list of PS reps to SM components.

    If sm_only=True, only expand SM-tagged reps.
    """
    result: List[SMComponent] = []
    for rep in reps:
        if sm_only and not rep.isSM:
            continue
        result.extend(expand_ps_to_sm(rep))
    return result


def total_weyl(components: List[SMComponent]) -> int:
    return sum(c.n for c in components)


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestSU4Decomposition(unittest.TestCase):
    """Verify the SU(4) → SU(3) × U(1)_{B-L} decomposition rules."""

    def test_a0_trivial(self):
        parts = su4_decompose(0)
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0], (1, Fraction(0)))

    def test_a1_fundamental(self):
        parts = su4_decompose(1)
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0], (3, Fraction(1, 3)))
        self.assertEqual(parts[1], (1, Fraction(-1)))

    def test_a2_antisymmetric(self):
        parts = su4_decompose(2)
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0], (3, Fraction(2, 3)))
        self.assertEqual(parts[1], (3, Fraction(-2, 3)))

    def test_a3_antifundamental(self):
        parts = su4_decompose(3)
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0], (3, Fraction(-1, 3)))
        self.assertEqual(parts[1], (1, Fraction(1)))

    def test_a4_determinant(self):
        parts = su4_decompose(4)
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0], (1, Fraction(0)))

    def test_dim_sum_a1(self):
        """3 + 1 = 4 = C(4,1)."""
        self.assertEqual(sum(d3 for d3, _ in su4_decompose(1)), 4)

    def test_dim_sum_a2(self):
        """3 + 3 = 6 = C(4,2)."""
        self.assertEqual(sum(d3 for d3, _ in su4_decompose(2)), 6)

    def test_dim_sum_a3(self):
        """3 + 1 = 4 = C(4,3)."""
        self.assertEqual(sum(d3 for d3, _ in su4_decompose(3)), 4)

    def test_fund_antifund_conjugation(self):
        """4̄ B-L charges are negatives of 4's B-L charges."""
        fund = su4_decompose(1)
        anti = su4_decompose(3)
        for (d3_f, BmL_f), (d3_a, BmL_a) in zip(fund, anti):
            self.assertEqual(d3_f, d3_a)
            self.assertEqual(BmL_f, -BmL_a)

    def test_BmL_traceless_fund(self):
        """Tr(B-L) over fundamental = 3·(1/3) + 1·(-1) = 0."""
        parts = su4_decompose(1)
        self.assertEqual(
            sum(Fraction(d3) * BmL for d3, BmL in parts),
            Fraction(0),
        )

    def test_BmL_traceless_antisym(self):
        """Tr(B-L) over 6 = 3·(2/3) + 3·(-2/3) = 0."""
        parts = su4_decompose(2)
        self.assertEqual(
            sum(Fraction(d3) * BmL for d3, BmL in parts),
            Fraction(0),
        )


class TestSU2RDecomposition(unittest.TestCase):
    """Verify T_R^3 decomposition of SU(2)_R."""

    def test_c0_trivial(self):
        self.assertEqual(su2R_TR3_values(0), [Fraction(0)])

    def test_c1_fundamental(self):
        vals = su2R_TR3_values(1)
        self.assertEqual(len(vals), 2)
        self.assertEqual(vals[0], Fraction(1, 2))
        self.assertEqual(vals[1], Fraction(-1, 2))

    def test_c2_determinant(self):
        self.assertEqual(su2R_TR3_values(2), [Fraction(0)])

    def test_c1_traceless(self):
        """Tr(T_R^3) over doublet = +1/2 + (-1/2) = 0."""
        self.assertEqual(sum(su2R_TR3_values(1)), Fraction(0))


class TestPSTableStructure(unittest.TestCase):
    """Verify the PS table matches CollatioPSBranching.lean."""

    def test_total_entry_count(self):
        self.assertEqual(len(ALL_PS_REPS), 22)

    def test_per_k_counts(self):
        self.assertEqual(len(PS_REPS_OF_1), 3)
        self.assertEqual(len(PS_REPS_OF_3), 8)
        self.assertEqual(len(PS_REPS_OF_5), 8)
        self.assertEqual(len(PS_REPS_OF_7), 3)

    def test_ps_dim_sum_of_1(self):
        self.assertEqual(sum(r.ps_dim for r in PS_REPS_OF_1), 8)

    def test_ps_dim_sum_of_3(self):
        self.assertEqual(sum(r.ps_dim for r in PS_REPS_OF_3), 56)

    def test_ps_dim_sum_of_5(self):
        self.assertEqual(sum(r.ps_dim for r in PS_REPS_OF_5), 56)

    def test_ps_dim_sum_of_7(self):
        self.assertEqual(sum(r.ps_dim for r in PS_REPS_OF_7), 8)

    def test_total_dim_128(self):
        self.assertEqual(sum(r.ps_dim for r in ALL_PS_REPS), 128)

    def test_sm_dim_48(self):
        self.assertEqual(sum(r.ps_dim for r in ALL_PS_REPS if r.isSM), 48)

    def test_exotic_dim_80(self):
        self.assertEqual(sum(r.ps_dim for r in ALL_PS_REPS if not r.isSM), 80)

    def test_koszul_abc_sums(self):
        """a + b + c = k for every entry."""
        for rep in ALL_PS_REPS:
            self.assertEqual(rep.a + rep.b + rep.c, rep.k,
                             f"Koszul sum mismatch: ({rep.a},{rep.b},{rep.c}) != {rep.k}")

    def test_koszul_dim_consistency(self):
        """su4 = C(4,a), su2L = C(2,b), su2R = C(2,c)."""
        from math import comb
        for rep in ALL_PS_REPS:
            self.assertEqual(rep.su4, comb(4, rep.a),
                             f"su4 mismatch at ({rep.a},{rep.b},{rep.c})")
            self.assertEqual(rep.su2L, comb(2, rep.b),
                             f"su2L mismatch at ({rep.a},{rep.b},{rep.c})")
            self.assertEqual(rep.su2R, comb(2, rep.c),
                             f"su2R mismatch at ({rep.a},{rep.b},{rep.c})")

    def test_bidoublet_koszul_indices(self):
        """[3]'s bidoublet has a=1 (fund); [5]'s has a=3 (anti-fund)."""
        bd3 = [r for r in PS_REPS_OF_3 if r.isSM]
        bd5 = [r for r in PS_REPS_OF_5 if r.isSM]
        self.assertEqual(len(bd3), 1)
        self.assertEqual(len(bd5), 1)
        self.assertEqual(bd3[0].a, 1)
        self.assertEqual(bd5[0].a, 3)


class TestExpansionWeylCounts(unittest.TestCase):
    """Verify Weyl counts are preserved through expansion."""

    def test_expansion_preserves_weyl_per_rep(self):
        """Each PS irrep's expansion has the same total Weyl as ps_dim."""
        for rep in ALL_PS_REPS:
            components = expand_ps_to_sm(rep)
            self.assertEqual(
                total_weyl(components), rep.ps_dim,
                f"Weyl mismatch for k={rep.k} ({rep.a},{rep.b},{rep.c}): "
                f"expanded {total_weyl(components)} != ps_dim {rep.ps_dim}",
            )

    def test_sm_tagged_expansion_weyl_48(self):
        """SM-tagged subset expands to 48 Weyl."""
        sm_components = expand_all(ALL_PS_REPS, sm_only=True)
        self.assertEqual(total_weyl(sm_components), 48)

    def test_full_expansion_weyl_128(self):
        """Full expansion totals 128 Weyl."""
        all_components = expand_all(ALL_PS_REPS, sm_only=False)
        self.assertEqual(total_weyl(all_components), 128)

    def test_per_k_sm_weyl(self):
        """SM Weyl per [k]: 8 + 16 + 16 + 8 = 48."""
        sm1 = total_weyl(expand_all(PS_REPS_OF_1, sm_only=True))
        sm3 = total_weyl(expand_all(PS_REPS_OF_3, sm_only=True))
        sm5 = total_weyl(expand_all(PS_REPS_OF_5, sm_only=True))
        sm7 = total_weyl(expand_all(PS_REPS_OF_7, sm_only=True))
        self.assertEqual(sm1, 8)
        self.assertEqual(sm3, 16)
        self.assertEqual(sm5, 16)
        self.assertEqual(sm7, 8)
        self.assertEqual(sm1 + sm3 + sm5 + sm7, 48)


class TestBidoubletHypercharges(unittest.TestCase):
    """Detailed check of bidoublet hypercharge assignments.

    This is the crux of the §4 tension resolution: [3]'s bidoublet (a=1,
    fundamental) and [5]'s bidoublet (a=3, anti-fundamental) have conjugate
    B-L charges, producing conjugate hypercharges.
    """

    def setUp(self):
        self.bd3 = [r for r in PS_REPS_OF_3 if r.isSM][0]
        self.bd5 = [r for r in PS_REPS_OF_5 if r.isSM][0]
        self.comps3 = expand_ps_to_sm(self.bd3)
        self.comps5 = expand_ps_to_sm(self.bd5)

    def test_bd3_is_fundamental(self):
        self.assertEqual(self.bd3.a, 1)

    def test_bd5_is_antifundamental(self):
        self.assertEqual(self.bd5.a, 3)

    def test_bd3_hypercharges(self):
        """[3] bidoublet (a=1): Y ∈ {2/3, -1/3, 0, -1}."""
        ys = sorted(c.Y for c in self.comps3)
        expected = sorted([Fraction(2, 3), Fraction(-1, 3),
                           Fraction(0), Fraction(-1)])
        self.assertEqual(ys, expected)

    def test_bd5_hypercharges(self):
        """[5] bidoublet (a=3): Y ∈ {1/3, -2/3, 1, 0}."""
        ys = sorted(c.Y for c in self.comps5)
        expected = sorted([Fraction(1, 3), Fraction(-2, 3),
                           Fraction(1), Fraction(0)])
        self.assertEqual(ys, expected)

    def test_bd3_specific_components(self):
        """[3] bidoublet: (3,2,2/3), (3,2,-1/3), (1,2,0), (1,2,-1)."""
        comps = [(c.d3, c.d2, c.Y) for c in self.comps3]
        self.assertIn((3, 2, Fraction(2, 3)), comps)
        self.assertIn((3, 2, Fraction(-1, 3)), comps)
        self.assertIn((1, 2, Fraction(0)), comps)
        self.assertIn((1, 2, Fraction(-1)), comps)

    def test_bd5_specific_components(self):
        """[5] bidoublet: (3,2,1/3), (3,2,-2/3), (1,2,1), (1,2,0)."""
        comps = [(c.d3, c.d2, c.Y) for c in self.comps5]
        self.assertIn((3, 2, Fraction(1, 3)), comps)
        self.assertIn((3, 2, Fraction(-2, 3)), comps)
        self.assertIn((1, 2, Fraction(1)), comps)
        self.assertIn((1, 2, Fraction(0)), comps)

    def test_bd3_bd5_not_identical(self):
        """The two bidoublets do NOT have the same hypercharges."""
        ys3 = sorted(c.Y for c in self.comps3)
        ys5 = sorted(c.Y for c in self.comps5)
        self.assertNotEqual(ys3, ys5)

    def test_bd3_weyl(self):
        self.assertEqual(total_weyl(self.comps3), 16)

    def test_bd5_weyl(self):
        self.assertEqual(total_weyl(self.comps5), 16)


class TestBidoubletAnomalyCancellation(unittest.TestCase):
    """The two bidoublets' anomaly contributions cancel pairwise."""

    def setUp(self):
        self.bd3 = [r for r in PS_REPS_OF_3 if r.isSM][0]
        self.bd5 = [r for r in PS_REPS_OF_5 if r.isSM][0]
        self.c3 = expand_ps_to_sm(self.bd3)
        self.c5 = expand_ps_to_sm(self.bd5)

    def test_SU3sq_bd3(self):
        """[3] bidoublet: 2·(2/3) + 2·(-1/3) = 4/3 - 2/3 = 2/3."""
        self.assertEqual(anom_SU3sq_U1Y(self.c3), Fraction(2, 3))

    def test_SU3sq_bd5(self):
        """[5] bidoublet: 2·(1/3) + 2·(-2/3) = 2/3 - 4/3 = -2/3."""
        self.assertEqual(anom_SU3sq_U1Y(self.c5), Fraction(-2, 3))

    def test_SU3sq_bd3_plus_bd5(self):
        """2/3 + (-2/3) = 0."""
        self.assertEqual(
            anom_SU3sq_U1Y(self.c3) + anom_SU3sq_U1Y(self.c5),
            Fraction(0),
        )

    def test_SU2Lsq_bd3(self):
        """[3] bidoublet [SU(2)]²: 3·(2/3) + 3·(-1/3) + 1·0 + 1·(-1) = 0."""
        self.assertEqual(anom_SU2Lsq_U1Y(self.c3), Fraction(0))

    def test_SU2Lsq_bd5(self):
        """[5] bidoublet [SU(2)]²: 3·(1/3) + 3·(-2/3) + 1·1 + 1·0 = 0."""
        self.assertEqual(anom_SU2Lsq_U1Y(self.c5), Fraction(0))

    def test_U1Y3_bd3(self):
        """[3] bidoublet: 6·(2/3)³ + 6·(-1/3)³ + 2·0³ + 2·(-1)³ = -4/9."""
        self.assertEqual(anom_U1Y_cubed(self.c3), Fraction(-4, 9))

    def test_U1Y3_bd5(self):
        """[5] bidoublet: 6·(1/3)³ + 6·(-2/3)³ + 2·1³ + 2·0³ = +4/9."""
        self.assertEqual(anom_U1Y_cubed(self.c5), Fraction(4, 9))

    def test_U1Y3_bd3_plus_bd5(self):
        """-4/9 + 4/9 = 0."""
        self.assertEqual(
            anom_U1Y_cubed(self.c3) + anom_U1Y_cubed(self.c5),
            Fraction(0),
        )

    def test_gravsq_bd3(self):
        """[3] bidoublet [grav]²: 6·(2/3) + 6·(-1/3) + 2·0 + 2·(-1) = 0."""
        self.assertEqual(anom_gravsq_U1Y(self.c3), Fraction(0))

    def test_gravsq_bd5(self):
        """[5] bidoublet [grav]²: 6·(1/3) + 6·(-2/3) + 2·1 + 2·0 = 0."""
        self.assertEqual(anom_gravsq_U1Y(self.c5), Fraction(0))


class TestRep1Rep7Cancellation(unittest.TestCase):
    """[1] and [7] form a conjugate pair; their SM anomalies cancel."""

    def setUp(self):
        self.sm1 = expand_all(PS_REPS_OF_1, sm_only=True)
        self.sm7 = expand_all(PS_REPS_OF_7, sm_only=True)

    def test_rep1_SU3sq(self):
        """[1] SM: only (4,1,1) a=1 → (3,1,1/6,3). Contribution: 1·(1/6) = 1/6."""
        self.assertEqual(anom_SU3sq_U1Y(self.sm1), Fraction(1, 6))

    def test_rep7_SU3sq(self):
        """[7] SM: only (4,1,1) a=3 → (3,1,-1/6,3). Contribution: 1·(-1/6) = -1/6."""
        self.assertEqual(anom_SU3sq_U1Y(self.sm7), Fraction(-1, 6))

    def test_rep1_plus_rep7_SU3sq(self):
        self.assertEqual(
            anom_SU3sq_U1Y(self.sm1) + anom_SU3sq_U1Y(self.sm7),
            Fraction(0),
        )

    def test_rep1_U1Y3(self):
        self.assertEqual(anom_U1Y_cubed(self.sm1), Fraction(-1, 9))

    def test_rep7_U1Y3(self):
        self.assertEqual(anom_U1Y_cubed(self.sm7), Fraction(1, 9))

    def test_rep1_plus_rep7_U1Y3(self):
        self.assertEqual(
            anom_U1Y_cubed(self.sm1) + anom_U1Y_cubed(self.sm7),
            Fraction(0),
        )

    def test_rep1_gravsq(self):
        self.assertEqual(anom_gravsq_U1Y(self.sm1), Fraction(0))

    def test_rep7_gravsq(self):
        self.assertEqual(anom_gravsq_U1Y(self.sm7), Fraction(0))

    def test_rep1_SU2Lsq(self):
        self.assertEqual(anom_SU2Lsq_U1Y(self.sm1), Fraction(0))

    def test_rep7_SU2Lsq(self):
        self.assertEqual(anom_SU2Lsq_U1Y(self.sm7), Fraction(0))


class TestSMTaggedAnomalyVanishing(unittest.TestCase):
    """THE MAIN RESULT: all four anomaly polynomials vanish over the
    SM-tagged subset of [1]⊕[3]⊕[5]⊕[7] under Y = T_R^3 + (B-L)/2.

    The vanishing follows from the conjugation structure:
      [1] SM + [7] SM = conjugate pair → anomaly-free
      [3] bidoublet + [5] bidoublet = conjugate pair → anomaly-free
    Total SM anomaly = 0 + 0 = 0.
    """

    def setUp(self):
        self.sm_components = expand_all(ALL_PS_REPS, sm_only=True)

    def test_sm_weyl_count(self):
        self.assertEqual(total_weyl(self.sm_components), 48)

    def test_SU3sq_U1Y_vanishes(self):
        self.assertEqual(anom_SU3sq_U1Y(self.sm_components), Fraction(0))

    def test_SU2Lsq_U1Y_vanishes(self):
        self.assertEqual(anom_SU2Lsq_U1Y(self.sm_components), Fraction(0))

    def test_U1Y_cubed_vanishes(self):
        self.assertEqual(anom_U1Y_cubed(self.sm_components), Fraction(0))

    def test_gravsq_U1Y_vanishes(self):
        self.assertEqual(anom_gravsq_U1Y(self.sm_components), Fraction(0))

    def test_all_four_vanish_conjunction(self):
        """Master bundle: all four vanish simultaneously."""
        self.assertTrue(
            anom_SU3sq_U1Y(self.sm_components) == 0
            and anom_SU2Lsq_U1Y(self.sm_components) == 0
            and anom_U1Y_cubed(self.sm_components) == 0
            and anom_gravsq_U1Y(self.sm_components) == 0
        )


class TestFullContentAnomalyVanishing(unittest.TestCase):
    """Cross-check: the FULL 128-Weyl content is also anomaly-free.

    [1]⊕[3]⊕[5]⊕[7] is self-conjugate ([k]* = [8-k], and {1,3,5,7}
    maps to itself under k → 8-k).  The anomaly of a self-conjugate
    set vanishes.  This is a consistency check on the expansion machinery.
    """

    def setUp(self):
        self.all_components = expand_all(ALL_PS_REPS, sm_only=False)

    def test_full_weyl_128(self):
        self.assertEqual(total_weyl(self.all_components), 128)

    def test_full_SU3sq_U1Y_vanishes(self):
        self.assertEqual(anom_SU3sq_U1Y(self.all_components), Fraction(0))

    def test_full_SU2Lsq_U1Y_vanishes(self):
        self.assertEqual(anom_SU2Lsq_U1Y(self.all_components), Fraction(0))

    def test_full_U1Y_cubed_vanishes(self):
        self.assertEqual(anom_U1Y_cubed(self.all_components), Fraction(0))

    def test_full_gravsq_U1Y_vanishes(self):
        self.assertEqual(anom_gravsq_U1Y(self.all_components), Fraction(0))


class TestExoticContentAnomalyVanishing(unittest.TestCase):
    """Since full = SM + exotic and both full and SM vanish, exotic vanishes."""

    def setUp(self):
        self.exotic = [c for rep in ALL_PS_REPS if not rep.isSM
                       for c in expand_ps_to_sm(rep)]

    def test_exotic_weyl_80(self):
        self.assertEqual(total_weyl(self.exotic), 80)

    def test_exotic_SU3sq_vanishes(self):
        self.assertEqual(anom_SU3sq_U1Y(self.exotic), Fraction(0))

    def test_exotic_SU2Lsq_vanishes(self):
        self.assertEqual(anom_SU2Lsq_U1Y(self.exotic), Fraction(0))

    def test_exotic_U1Y3_vanishes(self):
        self.assertEqual(anom_U1Y_cubed(self.exotic), Fraction(0))

    def test_exotic_gravsq_vanishes(self):
        self.assertEqual(anom_gravsq_U1Y(self.exotic), Fraction(0))


class TestPerTermArithmetic(unittest.TestCase):
    """Explicit per-term arithmetic for the SM anomaly sums.

    Mirrors the style of c148's per-contribution tests.
    """

    # ── [SU(3)]² · U(1)_Y per-block contributions ──

    def test_SU3sq_from_rep1(self):
        """[1] SM: 1·(1/6) = 1/6."""
        sm1 = expand_all(PS_REPS_OF_1, sm_only=True)
        self.assertEqual(anom_SU3sq_U1Y(sm1), Fraction(1, 6))

    def test_SU3sq_from_bd3(self):
        """[3] bidoublet: 2·(2/3) + 2·(-1/3) = 2/3."""
        bd3 = expand_ps_to_sm([r for r in PS_REPS_OF_3 if r.isSM][0])
        self.assertEqual(anom_SU3sq_U1Y(bd3), Fraction(2, 3))

    def test_SU3sq_from_bd5(self):
        """[5] bidoublet: 2·(1/3) + 2·(-2/3) = -2/3."""
        bd5 = expand_ps_to_sm([r for r in PS_REPS_OF_5 if r.isSM][0])
        self.assertEqual(anom_SU3sq_U1Y(bd5), Fraction(-2, 3))

    def test_SU3sq_from_rep7(self):
        """[7] SM: 1·(-1/6) = -1/6."""
        sm7 = expand_all(PS_REPS_OF_7, sm_only=True)
        self.assertEqual(anom_SU3sq_U1Y(sm7), Fraction(-1, 6))

    def test_SU3sq_sum_explicit(self):
        """1/6 + 2/3 + (-2/3) + (-1/6) = 0."""
        self.assertEqual(
            Fraction(1, 6) + Fraction(2, 3) + Fraction(-2, 3) + Fraction(-1, 6),
            Fraction(0),
        )

    # ── [U(1)_Y]³ per-block contributions ──

    def test_U1Y3_from_rep1(self):
        sm1 = expand_all(PS_REPS_OF_1, sm_only=True)
        self.assertEqual(anom_U1Y_cubed(sm1), Fraction(-1, 9))

    def test_U1Y3_from_bd3(self):
        bd3 = expand_ps_to_sm([r for r in PS_REPS_OF_3 if r.isSM][0])
        self.assertEqual(anom_U1Y_cubed(bd3), Fraction(-4, 9))

    def test_U1Y3_from_bd5(self):
        bd5 = expand_ps_to_sm([r for r in PS_REPS_OF_5 if r.isSM][0])
        self.assertEqual(anom_U1Y_cubed(bd5), Fraction(4, 9))

    def test_U1Y3_from_rep7(self):
        sm7 = expand_all(PS_REPS_OF_7, sm_only=True)
        self.assertEqual(anom_U1Y_cubed(sm7), Fraction(1, 9))

    def test_U1Y3_sum_explicit(self):
        """(-1/9) + (-4/9) + (4/9) + (1/9) = 0."""
        self.assertEqual(
            Fraction(-1, 9) + Fraction(-4, 9) + Fraction(4, 9) + Fraction(1, 9),
            Fraction(0),
        )


class TestSection4TensionResolution(unittest.TestCase):
    """Document the resolution of §4 structural tension.

    §4 of CLM-037 claim file observed that the (4,2,2) bidoublet under
    Y = T_R^3 + (B-L)/2 does not produce canonical SM hypercharges.
    This was correct for EACH bidoublet individually.

    The resolution: §4 implicitly assumed both bidoublets ([3] and [5])
    have the SAME SU(4) embedding.  In fact, [3]'s bidoublet comes from
    Koszul a=1 (fundamental, B-L = +1/3 for quarks) while [5]'s comes
    from a=3 (anti-fundamental, B-L = -1/3).  The pair is conjugate and
    its combined anomaly vanishes.
    """

    def test_section4_confirms_noncanonical_hypercharges(self):
        """Neither bidoublet alone has canonical SM hypercharges."""
        canonical_Y = {Fraction(1, 6), Fraction(-2, 3), Fraction(1, 3),
                       Fraction(-1, 2), Fraction(1)}
        bd3 = expand_ps_to_sm([r for r in PS_REPS_OF_3 if r.isSM][0])
        bd5 = expand_ps_to_sm([r for r in PS_REPS_OF_5 if r.isSM][0])
        ys3 = {c.Y for c in bd3}
        ys5 = {c.Y for c in bd5}
        self.assertFalse(ys3.issubset(canonical_Y),
                         "[3] bidoublet hypercharges are non-canonical")
        self.assertFalse(ys5.issubset(canonical_Y),
                         "[5] bidoublet hypercharges are non-canonical")

    def test_conjugation_is_the_resolution(self):
        """The pair [3]+[5] bidoublets cancel each anomaly polynomial."""
        bd3 = expand_ps_to_sm([r for r in PS_REPS_OF_3 if r.isSM][0])
        bd5 = expand_ps_to_sm([r for r in PS_REPS_OF_5 if r.isSM][0])
        combined = bd3 + bd5
        self.assertEqual(anom_SU3sq_U1Y(combined), Fraction(0))
        self.assertEqual(anom_SU2Lsq_U1Y(combined), Fraction(0))
        self.assertEqual(anom_U1Y_cubed(combined), Fraction(0))
        self.assertEqual(anom_gravsq_U1Y(combined), Fraction(0))

    def test_rep1_rep7_also_cancel(self):
        """[1] and [7] SM content also forms a conjugate pair."""
        sm1 = expand_all(PS_REPS_OF_1, sm_only=True)
        sm7 = expand_all(PS_REPS_OF_7, sm_only=True)
        combined = sm1 + sm7
        self.assertEqual(anom_SU3sq_U1Y(combined), Fraction(0))
        self.assertEqual(anom_SU2Lsq_U1Y(combined), Fraction(0))
        self.assertEqual(anom_U1Y_cubed(combined), Fraction(0))
        self.assertEqual(anom_gravsq_U1Y(combined), Fraction(0))


class TestCommandmentXII(unittest.TestCase):
    """Exact-ℚ discipline: all Y values and anomaly results are Fraction."""

    def test_all_sm_Y_are_Fraction(self):
        for comp in expand_all(ALL_PS_REPS, sm_only=True):
            self.assertIsInstance(comp.Y, Fraction)

    def test_all_anomaly_returns_are_Fraction(self):
        sm = expand_all(ALL_PS_REPS, sm_only=True)
        self.assertIsInstance(anom_SU3sq_U1Y(sm), Fraction)
        self.assertIsInstance(anom_SU2Lsq_U1Y(sm), Fraction)
        self.assertIsInstance(anom_U1Y_cubed(sm), Fraction)
        self.assertIsInstance(anom_gravsq_U1Y(sm), Fraction)

    def test_no_float_in_BmL(self):
        for comp in expand_all(ALL_PS_REPS):
            self.assertIsInstance(comp.BmL, Fraction)

    def test_no_float_in_TR3(self):
        for comp in expand_all(ALL_PS_REPS):
            self.assertIsInstance(comp.TR3, Fraction)


if __name__ == "__main__":
    unittest.main(verbosity=2)
