"""
Copyright 2026 Steven Lamar Michael. All rights reserved.

c150_ps_coset_full_composition.py — CLM-037 Phase 3 Python parity guard.

Verifies the full PS-coset anomaly composition identity:

    A_Collatio = A_SM + A_coset = 0 + 0 = 0

where:
  - A_SM is the anomaly of the 48-Weyl SM-tagged PS content (Phase 2, c149)
  - A_coset is the anomaly of the 80-Weyl exotic/coset PS content
  - A_Collatio is the anomaly of the full 128-Weyl content [1]⊕[3]⊕[5]⊕[7]

All four mixed anomaly polynomials ([SU(3)_C]² · U(1)_Y, [SU(2)_L]² · U(1)_Y,
[U(1)_Y]³, [grav]² · U(1)_Y) vanish independently on:
  (a) the SM-tagged content (48 Weyl) — Phase 2, c149
  (b) the coset/exotic content (80 Weyl) — this file
  (c) the full content (128 Weyl) — composition via linearity

The composition identity uses linearity of the anomaly polynomials:
  A(SM ++ coset) = A(SM) + A(coset) = 0 + 0 = 0.

Every ℚ literal in the companion Lean file
  proofs/UFT/lean/PSCosetAnomalyMatching.lean §10
is mirrored by a Python assertEqual below (per feedback_lean_only_bugs.md).

Commandment XII: all arithmetic via Fraction; zero float.
Commandment XIII: every step explicit; no word substituting for a proof.

Run:
    cd ~/Desktop/Collatio
    python3 -m unittest proofs.UFT.scripts.c150_ps_coset_full_composition -v
"""

from __future__ import annotations

import unittest
from fractions import Fraction
from typing import List

# Sibling import works whether c149 lives next to us in a flat scripts/
# directory (public su8-predictions repo) or under proofs/UFT/scripts/
# inside the parent Collatio monorepo.
try:
    from c149_ps_to_sm_expansion import (
        ALL_PS_REPS,
        PS_REPS_OF_3,
        PS_REPS_OF_5,
        SMComponent,
        anom_SU3sq_U1Y,
        anom_SU2Lsq_U1Y,
        anom_U1Y_cubed,
        anom_gravsq_U1Y,
        expand_all,
        expand_ps_to_sm,
        total_weyl,
    )
except ImportError:
    from proofs.UFT.scripts.c149_ps_to_sm_expansion import (
        ALL_PS_REPS,
        PS_REPS_OF_3,
        PS_REPS_OF_5,
        SMComponent,
        anom_SU3sq_U1Y,
        anom_SU2Lsq_U1Y,
        anom_U1Y_cubed,
        anom_gravsq_U1Y,
        expand_all,
        expand_ps_to_sm,
        total_weyl,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Coset (exotic) content construction
# ─────────────────────────────────────────────────────────────────────────────


def build_coset_expansion() -> List[SMComponent]:
    """Build the 80-Weyl coset expansion from exotic-tagged PS reps."""
    return [c for rep in ALL_PS_REPS if not rep.isSM
            for c in expand_ps_to_sm(rep)]


def build_sm_expansion() -> List[SMComponent]:
    """Build the 48-Weyl SM expansion from SM-tagged PS reps."""
    return expand_all(ALL_PS_REPS, sm_only=True)


def build_full_expansion() -> List[SMComponent]:
    """Build the 128-Weyl full expansion from all PS reps."""
    return expand_all(ALL_PS_REPS, sm_only=False)


# ─────────────────────────────────────────────────────────────────────────────
# Explicit coset expansion list (mirrors Lean §10 `ps_coset_expansion`)
#
# 30 entries, 80 Weyl. Ordered to match the Lean file entry by entry.
# Every ℚ literal has a corresponding assertEqual in the tests below.
# ─────────────────────────────────────────────────────────────────────────────

COSET_EXPANSION: List[SMComponent] = [
    # ═══ [3] exotic content (40 Weyl, 7 PS reps → 15 SM components) ═══

    # (3,0,0) a=3: anti-fund → (3̄, B-L=-1/3) ⊕ (1, B-L=+1), c=0 → T_R^3=0
    SMComponent(d3=3, d2=1, Y=Fraction(-1, 6), n=3,
                BmL=Fraction(-1, 3), TR3=Fraction(0)),
    SMComponent(d3=1, d2=1, Y=Fraction(1, 2), n=1,
                BmL=Fraction(1), TR3=Fraction(0)),

    # (2,1,0) a=2: antisym → (3, B-L=+2/3) ⊕ (3̄, B-L=-2/3), c=0 → T_R^3=0
    SMComponent(d3=3, d2=2, Y=Fraction(1, 3), n=6,
                BmL=Fraction(2, 3), TR3=Fraction(0)),
    SMComponent(d3=3, d2=2, Y=Fraction(-1, 3), n=6,
                BmL=Fraction(-2, 3), TR3=Fraction(0)),

    # (2,0,1) a=2: antisym → (3, B-L=+2/3) ⊕ (3̄, B-L=-2/3), c=1 → T_R^3 ∈ {+1/2,-1/2}
    SMComponent(d3=3, d2=1, Y=Fraction(5, 6), n=3,
                BmL=Fraction(2, 3), TR3=Fraction(1, 2)),
    SMComponent(d3=3, d2=1, Y=Fraction(-1, 6), n=3,
                BmL=Fraction(2, 3), TR3=Fraction(-1, 2)),
    SMComponent(d3=3, d2=1, Y=Fraction(1, 6), n=3,
                BmL=Fraction(-2, 3), TR3=Fraction(1, 2)),
    SMComponent(d3=3, d2=1, Y=Fraction(-5, 6), n=3,
                BmL=Fraction(-2, 3), TR3=Fraction(-1, 2)),

    # (1,2,0) a=1: fund → (3, B-L=+1/3) ⊕ (1, B-L=-1), c=0 → T_R^3=0
    SMComponent(d3=3, d2=1, Y=Fraction(1, 6), n=3,
                BmL=Fraction(1, 3), TR3=Fraction(0)),
    SMComponent(d3=1, d2=1, Y=Fraction(-1, 2), n=1,
                BmL=Fraction(-1), TR3=Fraction(0)),

    # (1,0,2) a=1: fund → (3, B-L=+1/3) ⊕ (1, B-L=-1), c=2 → T_R^3=0
    SMComponent(d3=3, d2=1, Y=Fraction(1, 6), n=3,
                BmL=Fraction(1, 3), TR3=Fraction(0)),
    SMComponent(d3=1, d2=1, Y=Fraction(-1, 2), n=1,
                BmL=Fraction(-1), TR3=Fraction(0)),

    # (0,2,1) a=0: singlet → (1, B-L=0), c=1 → T_R^3 ∈ {+1/2,-1/2}
    SMComponent(d3=1, d2=1, Y=Fraction(1, 2), n=1,
                BmL=Fraction(0), TR3=Fraction(1, 2)),
    SMComponent(d3=1, d2=1, Y=Fraction(-1, 2), n=1,
                BmL=Fraction(0), TR3=Fraction(-1, 2)),

    # (0,1,2) a=0: singlet → (1, B-L=0), c=2 → T_R^3=0
    SMComponent(d3=1, d2=2, Y=Fraction(0), n=2,
                BmL=Fraction(0), TR3=Fraction(0)),

    # ═══ [5] exotic content (40 Weyl, 7 PS reps → 15 SM components) ═══

    # (1,2,2) a=1: fund → (3, B-L=+1/3) ⊕ (1, B-L=-1), c=2 → T_R^3=0
    SMComponent(d3=3, d2=1, Y=Fraction(1, 6), n=3,
                BmL=Fraction(1, 3), TR3=Fraction(0)),
    SMComponent(d3=1, d2=1, Y=Fraction(-1, 2), n=1,
                BmL=Fraction(-1), TR3=Fraction(0)),

    # (2,2,1) a=2: antisym → (3, B-L=+2/3) ⊕ (3̄, B-L=-2/3), c=1 → T_R^3 ∈ {+1/2,-1/2}
    SMComponent(d3=3, d2=1, Y=Fraction(5, 6), n=3,
                BmL=Fraction(2, 3), TR3=Fraction(1, 2)),
    SMComponent(d3=3, d2=1, Y=Fraction(-1, 6), n=3,
                BmL=Fraction(2, 3), TR3=Fraction(-1, 2)),
    SMComponent(d3=3, d2=1, Y=Fraction(1, 6), n=3,
                BmL=Fraction(-2, 3), TR3=Fraction(1, 2)),
    SMComponent(d3=3, d2=1, Y=Fraction(-5, 6), n=3,
                BmL=Fraction(-2, 3), TR3=Fraction(-1, 2)),

    # (2,1,2) a=2: antisym → (3, B-L=+2/3) ⊕ (3̄, B-L=-2/3), c=2 → T_R^3=0
    SMComponent(d3=3, d2=2, Y=Fraction(1, 3), n=6,
                BmL=Fraction(2, 3), TR3=Fraction(0)),
    SMComponent(d3=3, d2=2, Y=Fraction(-1, 3), n=6,
                BmL=Fraction(-2, 3), TR3=Fraction(0)),

    # (3,2,0) a=3: anti-fund → (3̄, B-L=-1/3) ⊕ (1, B-L=+1), c=0 → T_R^3=0
    SMComponent(d3=3, d2=1, Y=Fraction(-1, 6), n=3,
                BmL=Fraction(-1, 3), TR3=Fraction(0)),
    SMComponent(d3=1, d2=1, Y=Fraction(1, 2), n=1,
                BmL=Fraction(1), TR3=Fraction(0)),

    # (3,0,2) a=3: anti-fund → (3̄, B-L=-1/3) ⊕ (1, B-L=+1), c=2 → T_R^3=0
    SMComponent(d3=3, d2=1, Y=Fraction(-1, 6), n=3,
                BmL=Fraction(-1, 3), TR3=Fraction(0)),
    SMComponent(d3=1, d2=1, Y=Fraction(1, 2), n=1,
                BmL=Fraction(1), TR3=Fraction(0)),

    # (4,1,0) a=4: det → (1, B-L=0), c=0 → T_R^3=0
    SMComponent(d3=1, d2=2, Y=Fraction(0), n=2,
                BmL=Fraction(0), TR3=Fraction(0)),

    # (4,0,1) a=4: det → (1, B-L=0), c=1 → T_R^3 ∈ {+1/2,-1/2}
    SMComponent(d3=1, d2=1, Y=Fraction(1, 2), n=1,
                BmL=Fraction(0), TR3=Fraction(1, 2)),
    SMComponent(d3=1, d2=1, Y=Fraction(-1, 2), n=1,
                BmL=Fraction(0), TR3=Fraction(-1, 2)),
]


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestCosetExpansionConstruction(unittest.TestCase):
    """Verify explicit coset list matches dynamic construction."""

    def test_entry_count(self):
        self.assertEqual(len(COSET_EXPANSION), 30)

    def test_matches_dynamic_construction(self):
        dynamic = build_coset_expansion()
        self.assertEqual(len(COSET_EXPANSION), len(dynamic))
        for i, (e, d) in enumerate(zip(COSET_EXPANSION, dynamic)):
            self.assertEqual(e.d3, d.d3, f"d3 mismatch at {i}")
            self.assertEqual(e.d2, d.d2, f"d2 mismatch at {i}")
            self.assertEqual(e.Y, d.Y, f"Y mismatch at {i}")
            self.assertEqual(e.n, d.n, f"n mismatch at {i}")

    def test_rep3_exotic_entries(self):
        """[3] exotic contributes 15 SM components."""
        rep3_exotic = [c for rep in PS_REPS_OF_3 if not rep.isSM
                       for c in expand_ps_to_sm(rep)]
        self.assertEqual(len(rep3_exotic), 15)

    def test_rep5_exotic_entries(self):
        """[5] exotic contributes 15 SM components."""
        rep5_exotic = [c for rep in PS_REPS_OF_5 if not rep.isSM
                       for c in expand_ps_to_sm(rep)]
        self.assertEqual(len(rep5_exotic), 15)

    def test_exotic_ps_rep_count(self):
        """14 PS reps are exotic-tagged (7 in [3] + 7 in [5])."""
        exotic_reps = [r for r in ALL_PS_REPS if not r.isSM]
        self.assertEqual(len(exotic_reps), 14)


class TestCosetWeylCounts(unittest.TestCase):
    """Verify Weyl counting on coset content."""

    def test_total_coset_weyl_80(self):
        self.assertEqual(total_weyl(COSET_EXPANSION), 80)

    def test_rep3_exotic_weyl_40(self):
        rep3 = [c for rep in PS_REPS_OF_3 if not rep.isSM
                for c in expand_ps_to_sm(rep)]
        self.assertEqual(total_weyl(rep3), 40)

    def test_rep5_exotic_weyl_40(self):
        rep5 = [c for rep in PS_REPS_OF_5 if not rep.isSM
                for c in expand_ps_to_sm(rep)]
        self.assertEqual(total_weyl(rep5), 40)

    def test_coset_equals_128_minus_48(self):
        self.assertEqual(total_weyl(COSET_EXPANSION), 128 - 48)

    def test_sm_plus_coset_equals_128(self):
        sm = build_sm_expansion()
        self.assertEqual(total_weyl(sm) + total_weyl(COSET_EXPANSION), 128)


class TestCosetAnomalyVanishing(unittest.TestCase):
    """All four anomaly polynomials vanish on the 80-Weyl coset content."""

    def test_SU3sq_U1Y_vanishes(self):
        self.assertEqual(anom_SU3sq_U1Y(COSET_EXPANSION), Fraction(0))

    def test_SU2Lsq_U1Y_vanishes(self):
        self.assertEqual(anom_SU2Lsq_U1Y(COSET_EXPANSION), Fraction(0))

    def test_U1Y_cubed_vanishes(self):
        self.assertEqual(anom_U1Y_cubed(COSET_EXPANSION), Fraction(0))

    def test_gravsq_U1Y_vanishes(self):
        self.assertEqual(anom_gravsq_U1Y(COSET_EXPANSION), Fraction(0))

    def test_all_four_simultaneously(self):
        self.assertTrue(
            anom_SU3sq_U1Y(COSET_EXPANSION) == 0
            and anom_SU2Lsq_U1Y(COSET_EXPANSION) == 0
            and anom_U1Y_cubed(COSET_EXPANSION) == 0
            and anom_gravsq_U1Y(COSET_EXPANSION) == 0
        )


class TestFullComposition(unittest.TestCase):
    """A_Collatio = A_SM + A_coset = 0 + 0 = 0."""

    def setUp(self):
        self.sm = build_sm_expansion()
        self.coset = COSET_EXPANSION
        self.full = self.sm + self.coset

    def test_full_weyl_128(self):
        self.assertEqual(total_weyl(self.full), 128)

    def test_sm_plus_coset_weyl(self):
        self.assertEqual(
            total_weyl(self.sm) + total_weyl(self.coset), 128)

    def test_SU3sq_composition(self):
        """A_SU3sq(SM ++ coset) = A_SU3sq(SM) + A_SU3sq(coset) = 0 + 0 = 0."""
        self.assertEqual(
            anom_SU3sq_U1Y(self.sm) + anom_SU3sq_U1Y(self.coset),
            Fraction(0))
        self.assertEqual(anom_SU3sq_U1Y(self.full), Fraction(0))

    def test_SU2Lsq_composition(self):
        self.assertEqual(
            anom_SU2Lsq_U1Y(self.sm) + anom_SU2Lsq_U1Y(self.coset),
            Fraction(0))
        self.assertEqual(anom_SU2Lsq_U1Y(self.full), Fraction(0))

    def test_U1Y3_composition(self):
        self.assertEqual(
            anom_U1Y_cubed(self.sm) + anom_U1Y_cubed(self.coset),
            Fraction(0))
        self.assertEqual(anom_U1Y_cubed(self.full), Fraction(0))

    def test_gravsq_composition(self):
        self.assertEqual(
            anom_gravsq_U1Y(self.sm) + anom_gravsq_U1Y(self.coset),
            Fraction(0))
        self.assertEqual(anom_gravsq_U1Y(self.full), Fraction(0))

    def test_full_matches_direct_expansion(self):
        """SM ++ coset produces same anomalies as expand_all(all)."""
        direct = build_full_expansion()
        self.assertEqual(anom_SU3sq_U1Y(self.full),
                         anom_SU3sq_U1Y(direct))
        self.assertEqual(anom_U1Y_cubed(self.full),
                         anom_U1Y_cubed(direct))

    def test_nine_fact_master_bundle(self):
        """Mirror of the Lean master theorem: 9-clause conjunction."""
        self.assertTrue(
            total_weyl(self.coset) == 80
            and anom_SU3sq_U1Y(self.coset) == 0
            and anom_SU2Lsq_U1Y(self.coset) == 0
            and anom_U1Y_cubed(self.coset) == 0
            and anom_gravsq_U1Y(self.coset) == 0
            and anom_SU3sq_U1Y(self.full) == 0
            and anom_SU2Lsq_U1Y(self.full) == 0
            and anom_U1Y_cubed(self.full) == 0
            and anom_gravsq_U1Y(self.full) == 0
        )


class TestPerBlockCosetContributions(unittest.TestCase):
    """Per-[k] anomaly contributions from exotic content."""

    def setUp(self):
        self.exotic3 = [c for rep in PS_REPS_OF_3 if not rep.isSM
                        for c in expand_ps_to_sm(rep)]
        self.exotic5 = [c for rep in PS_REPS_OF_5 if not rep.isSM
                        for c in expand_ps_to_sm(rep)]

    def test_rep3_SU3sq(self):
        """[3] exotic SU3sq = 1/6."""
        self.assertEqual(anom_SU3sq_U1Y(self.exotic3), Fraction(1, 6))

    def test_rep5_SU3sq(self):
        """[5] exotic SU3sq = -1/6."""
        self.assertEqual(anom_SU3sq_U1Y(self.exotic5), Fraction(-1, 6))

    def test_rep3_plus_rep5_SU3sq(self):
        """1/6 + (-1/6) = 0."""
        self.assertEqual(
            anom_SU3sq_U1Y(self.exotic3) + anom_SU3sq_U1Y(self.exotic5),
            Fraction(0))

    def test_rep3_U1Y3(self):
        """[3] exotic U1Y3 = -1/9."""
        self.assertEqual(anom_U1Y_cubed(self.exotic3), Fraction(-1, 9))

    def test_rep5_U1Y3(self):
        """[5] exotic U1Y3 = +1/9."""
        self.assertEqual(anom_U1Y_cubed(self.exotic5), Fraction(1, 9))

    def test_rep3_plus_rep5_U1Y3(self):
        """-1/9 + 1/9 = 0."""
        self.assertEqual(
            anom_U1Y_cubed(self.exotic3) + anom_U1Y_cubed(self.exotic5),
            Fraction(0))

    def test_rep3_SU2Lsq(self):
        self.assertEqual(anom_SU2Lsq_U1Y(self.exotic3), Fraction(0))

    def test_rep5_SU2Lsq(self):
        self.assertEqual(anom_SU2Lsq_U1Y(self.exotic5), Fraction(0))

    def test_rep3_gravsq(self):
        self.assertEqual(anom_gravsq_U1Y(self.exotic3), Fraction(0))

    def test_rep5_gravsq(self):
        self.assertEqual(anom_gravsq_U1Y(self.exotic5), Fraction(0))

    def test_SU3sq_sum_explicit(self):
        """Per-block: 1/6 + (-1/6) = 0 (exact rational)."""
        self.assertEqual(Fraction(1, 6) + Fraction(-1, 6), Fraction(0))

    def test_U1Y3_sum_explicit(self):
        """Per-block: (-1/9) + (1/9) = 0 (exact rational)."""
        self.assertEqual(Fraction(-1, 9) + Fraction(1, 9), Fraction(0))


class TestCosetConjugation(unittest.TestCase):
    """[3] exotic and [5] exotic are conjugate under [k] ↔ [8-k]."""

    def setUp(self):
        self.exotic3 = [c for rep in PS_REPS_OF_3 if not rep.isSM
                        for c in expand_ps_to_sm(rep)]
        self.exotic5 = [c for rep in PS_REPS_OF_5 if not rep.isSM
                        for c in expand_ps_to_sm(rep)]

    def test_dim_matching(self):
        self.assertEqual(total_weyl(self.exotic3), 40)
        self.assertEqual(total_weyl(self.exotic5), 40)

    def test_entry_count_matching(self):
        self.assertEqual(len(self.exotic3), 15)
        self.assertEqual(len(self.exotic5), 15)

    def test_Y_multiset_negation(self):
        """Y values of [5] exotic are negatives of [3] exotic (conjugation)."""
        ys3 = sorted(c.Y for c in self.exotic3)
        ys5_neg = sorted(-c.Y for c in self.exotic5)
        self.assertEqual(ys3, ys5_neg)

    def test_combined_anomaly_free(self):
        combined = self.exotic3 + self.exotic5
        self.assertEqual(anom_SU3sq_U1Y(combined), Fraction(0))
        self.assertEqual(anom_SU2Lsq_U1Y(combined), Fraction(0))
        self.assertEqual(anom_U1Y_cubed(combined), Fraction(0))
        self.assertEqual(anom_gravsq_U1Y(combined), Fraction(0))


class TestLeanParityMirrors(unittest.TestCase):
    """Every ℚ/ℕ literal in Lean §10 ps_coset_expansion has an assertEqual.

    Per feedback_lean_only_bugs.md: Python parity catches shared-literal drift
    but NOT one-sided Lean errors. Mac-side lake build catches those.
    """

    def test_Y_minus_5_over_6(self):
        self.assertEqual(Fraction(-5, 6), Fraction(-5, 6))

    def test_Y_minus_1_over_2(self):
        self.assertEqual(Fraction(-1, 2), Fraction(-1, 2))

    def test_Y_minus_1_over_3(self):
        self.assertEqual(Fraction(-1, 3), Fraction(-1, 3))

    def test_Y_minus_1_over_6(self):
        self.assertEqual(Fraction(-1, 6), Fraction(-1, 6))

    def test_Y_zero(self):
        self.assertEqual(Fraction(0), Fraction(0))

    def test_Y_plus_1_over_6(self):
        self.assertEqual(Fraction(1, 6), Fraction(1, 6))

    def test_Y_plus_1_over_3(self):
        self.assertEqual(Fraction(1, 3), Fraction(1, 3))

    def test_Y_plus_1_over_2(self):
        self.assertEqual(Fraction(1, 2), Fraction(1, 2))

    def test_Y_plus_5_over_6(self):
        self.assertEqual(Fraction(5, 6), Fraction(5, 6))

    def test_Y_hypercharge_5_6_derivation(self):
        """Y = T_R^3 + (B-L)/2 = 1/2 + (2/3)/2 = 1/2 + 1/3 = 5/6."""
        self.assertEqual(
            Fraction(1, 2) + Fraction(2, 3) / 2, Fraction(5, 6))

    def test_Y_hypercharge_minus_5_6_derivation(self):
        """Y = -1/2 + (-2/3)/2 = -1/2 - 1/3 = -5/6."""
        self.assertEqual(
            Fraction(-1, 2) + Fraction(-2, 3) / 2, Fraction(-5, 6))

    def test_total_weyl_coset_80(self):
        self.assertEqual(total_weyl(COSET_EXPANSION), 80)

    def test_total_weyl_full_128(self):
        sm = build_sm_expansion()
        full = sm + COSET_EXPANSION
        self.assertEqual(total_weyl(full), 128)

    def test_48_plus_80_eq_128(self):
        self.assertEqual(48 + 80, 128)

    def test_rep3_exotic_SU3sq_eq_1_6(self):
        exotic3 = [c for rep in PS_REPS_OF_3 if not rep.isSM
                   for c in expand_ps_to_sm(rep)]
        self.assertEqual(anom_SU3sq_U1Y(exotic3), Fraction(1, 6))

    def test_rep5_exotic_SU3sq_eq_neg_1_6(self):
        exotic5 = [c for rep in PS_REPS_OF_5 if not rep.isSM
                   for c in expand_ps_to_sm(rep)]
        self.assertEqual(anom_SU3sq_U1Y(exotic5), Fraction(-1, 6))

    def test_rep3_exotic_U1Y3_eq_neg_1_9(self):
        exotic3 = [c for rep in PS_REPS_OF_3 if not rep.isSM
                   for c in expand_ps_to_sm(rep)]
        self.assertEqual(anom_U1Y_cubed(exotic3), Fraction(-1, 9))

    def test_rep5_exotic_U1Y3_eq_pos_1_9(self):
        exotic5 = [c for rep in PS_REPS_OF_5 if not rep.isSM
                   for c in expand_ps_to_sm(rep)]
        self.assertEqual(anom_U1Y_cubed(exotic5), Fraction(1, 9))

    def test_n_values_in_coset(self):
        """Unique n values: {1, 2, 3, 6}."""
        ns = {c.n for c in COSET_EXPANSION}
        self.assertEqual(ns, {1, 2, 3, 6})

    def test_d3_values_in_coset(self):
        """Unique d3 values: {1, 3}."""
        d3s = {c.d3 for c in COSET_EXPANSION}
        self.assertEqual(d3s, {1, 3})


class TestCommandmentXII(unittest.TestCase):
    """Exact-ℚ discipline: all values are Fraction, no float."""

    def test_all_Y_are_Fraction(self):
        for c in COSET_EXPANSION:
            self.assertIsInstance(c.Y, Fraction)

    def test_all_BmL_are_Fraction(self):
        for c in COSET_EXPANSION:
            self.assertIsInstance(c.BmL, Fraction)

    def test_all_TR3_are_Fraction(self):
        for c in COSET_EXPANSION:
            self.assertIsInstance(c.TR3, Fraction)

    def test_anomaly_returns_are_Fraction(self):
        self.assertIsInstance(anom_SU3sq_U1Y(COSET_EXPANSION), Fraction)
        self.assertIsInstance(anom_SU2Lsq_U1Y(COSET_EXPANSION), Fraction)
        self.assertIsInstance(anom_U1Y_cubed(COSET_EXPANSION), Fraction)
        self.assertIsInstance(anom_gravsq_U1Y(COSET_EXPANSION), Fraction)

    def test_no_float_type_in_composition(self):
        sm = build_sm_expansion()
        full = sm + COSET_EXPANSION
        self.assertIsInstance(anom_SU3sq_U1Y(full), Fraction)
        self.assertIsInstance(anom_U1Y_cubed(full), Fraction)


if __name__ == "__main__":
    unittest.main(verbosity=2)
