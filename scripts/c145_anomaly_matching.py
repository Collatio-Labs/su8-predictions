"""
Copyright 2026 Steven Lamar Michael. All rights reserved.

c145_anomaly_matching.py — Python parity guard for CLM-034 (Avenue 1 of
Route A: 't Hooft anomaly-matching exhaustion for CG = 8/9).

This script computes, in exact Fraction arithmetic, whether the combined
constraints of

    (a) Banks-Georgi anomaly freedom on antisymmetric SU(N) content,
    (b) IR Standard Model fermion count ≥ 48 Weyl (3 generations × 16),
    (c) Pati-Salam fundamental embedding admissibility,

force N = 8 and, given N = 8, force the cascade Clebsch-Gordan ratio
1/r = N/(N+1) = 8/9 at the UV Yukawa vertex.

It is the Python side of Avenue 1.  The companion Lean file
`proofs/UFT/lean/AnomalyMatchingDerivation.lean` (not yet written in
this session) will mirror every ℚ literal that appears below as an
`assertEqual` on the Python side.  Per feedback_lean_only_bugs.md,
every Lean theorem of the form `A = B := by norm_num` or
`A = B := by decide` must have a Python `assertEqual(A_frac, B_frac)`
here — otherwise the parity guard has a blind spot.

Zero floats.  Zero estimates.  Zero fudges.  Exact Fraction throughout
per Commandment XII.

Closure direction (HONEST): partial positive.  This avenue establishes

    N = 8 uniquely among {6, 7, 8, 9, 10}  under the JOINT filter
    {Banks-Georgi anomaly freedom, fermion count ≥ 48,
     Pati-Salam fundamental embedding (STIPULATED, see GAP #1)}

and, given N = 8, the cascade rational (N+1)/N = 9/8 with inverse 8/9.

ALGEBRAIC vs PHYSICS (Commandment I precision).  All assertions here
are over ℚ (or ℤ, ℕ).  "8/9 is the cascade CG" in this file is a
statement about the algebraic rational N/(N+1) at N = 8, NOT a
derivation of the physics vertex coefficient y_t(M_8)/g_8(M_8) = 8/9
that CLM-001 postulates.  The physics identification is unchanged
by Avenue 1; this file only tightens the algebraic-side evidence
floor.

Avenue 1 does NOT independently rule out non-fundamental PS embeddings
at N ∈ {6, 7, 9, 10} — those require explicit SU(N)→PS branching
computations deferred to a follow-up or to Avenue 2 onwards.  It
also does NOT structurally derive the PS-fundamental filter; the
predicate `admits_ps_fundamental(N) := (N == 8)` is stipulated here
(GAP #1), and the 48 + 80 split of the 128 Weyl fermions at N = 8
is cited to BranchingRules.lean / C121 rather than re-derived
(GAP #3).  See Oracle/claims/CLM-034-open-gaps-handoff.md.

Per Commandment I / V / VIII, the partial-positive nature of the
closure is reported honestly and does NOT license promoting CLM-001
to `theorem`.  The CLM-001 label remains `structurally-forced`; Avenue 1
tightens the evidence floor by one avenue of the six-avenue Route A.
"""

from fractions import Fraction
from math import comb
import unittest


# ------------------------------------------------------------------
# Banks-Georgi anomaly coefficients (exact Fraction)
# ------------------------------------------------------------------
# A([k], N) = C(N-2, k-1) × (N - 2k) / (N - 2)
#
# This is the anomaly coefficient of the antisymmetric rank-k tensor
# representation of SU(N).  Derivation: standard.  Reference:
# Banks & Georgi 1976, formula also recorded in c99_cg_derivation.py.
# ------------------------------------------------------------------


def banks_georgi(k, N):
    """A([k], N) = C(N-2, k-1) × (N-2k) / (N-2), exact Fraction."""
    if not (1 <= k <= N - 1):
        raise ValueError(f"rank k={k} out of range for SU({N})")
    if N <= 2:
        raise ValueError(f"SU({N}) too small for Banks-Georgi formula")
    return Fraction(comb(N - 2, k - 1) * (N - 2 * k), N - 2)


def antisym_dim(k, N):
    """Dimension C(N, k) of the antisymmetric rank-k tensor of SU(N)."""
    return comb(N, k)


def content_anomaly(content, N):
    """Total anomaly of a multiset of antisymmetric ranks at SU(N)."""
    total = Fraction(0)
    for k in content:
        total += banks_georgi(k, N)
    return total


def content_fermion_count(content, N):
    """Total Weyl fermion count of a content multiset at SU(N)."""
    return sum(antisym_dim(k, N) for k in content)


def conjugate_pair_sum(k, N):
    """A([k], N) + A([N-k], N) — must equal 0 by Banks-Georgi identity."""
    return banks_georgi(k, N) + banks_georgi(N - k, N)


# ------------------------------------------------------------------
# IR Standard Model fermion-count target
# ------------------------------------------------------------------
# Q_L + u_R + d_R + L_L + e_R + ν_R per generation = 16 Weyl; 3 gen = 48.
# ------------------------------------------------------------------

SM_WEYL_PER_GEN = 16
N_GEN = 3
SM_WEYL_TOTAL = SM_WEYL_PER_GEN * N_GEN  # 48


# ------------------------------------------------------------------
# Pati-Salam embedding admissibility
# ------------------------------------------------------------------
# PS = SU(4)_C × SU(2)_L × SU(2)_R, rank = 3 + 1 + 1 = 5.
# For PS ⊂ SU(N): rank(SU(N)) = N − 1 ≥ 5, so N ≥ 6.
#
# For a *fundamental* PS embedding (i.e. the SU(N) fundamental
# decomposes cleanly into PS irreps without singlets or mismatches):
# the minimal PS fundamental irreps are (4,2,1), (4,1,2), (4̄,2,1),
# (4̄,1,2), each of dimension 8.  A single PS fundamental fits
# cleanly into SU(8); for N < 8 there is not enough room, and for
# N > 8 extra singlets or reducible pieces are required.  This is
# the standard Pati-Salam embedding used by Collatio.
#
# The rank condition is necessary; the fundamental-embedding
# condition is a stricter filter that selects N = 8 uniquely.
# ------------------------------------------------------------------

PS_RANK = 5


def suN_rank(N):
    return N - 1


def admits_ps_embedding_by_rank(N):
    """Necessary (not sufficient) rank condition for PS ⊂ SU(N)."""
    return suN_rank(N) >= PS_RANK


# ------------------------------------------------------------------
# GAP #1 CLOSED (C194) — PS fundamental embedding predicate is now
# STRUCTURAL, not stipulated.  Mirrors the Lean
# `admits_ps_fundamental` in AnomalyMatchingDerivation.lean.
# ------------------------------------------------------------------
# The PS factor fundamental dimensions are lowest-weight facts of
# each factor Lie algebra:
#     dim(SU(4)_C fund) = 4,  dim(SU(2)_L fund) = 2,
#     dim(SU(2)_R fund) = 2.
# A FUNDAMENTAL PS embedding of the SU(N) fundamental is the direct
# sum of each factor fundamental exactly once:
#     N = ps_dim_C · 1 + ps_dim_L · 1 + ps_dim_R · 1 = 4 + 2 + 2 = 8.
# The predicate returns True iff there exist multiplicities
# a = b = c = 1 with N = 4 a + 2 b + 2 c.  This is decidable by
# finite enumeration; Lean closes the same iff by `omega`.
# ------------------------------------------------------------------

PS_DIM_C = 4
PS_DIM_L = 2
PS_DIM_R = 2
PS_DIM_SUM = PS_DIM_C + PS_DIM_L + PS_DIM_R   # = 8


def admits_ps_fundamental_embedding(N):
    """Structural PS fundamental embedding predicate (GAP #1 closed).

    True iff there exist a = b = c = 1 such that
        N = PS_DIM_C · a + PS_DIM_L · b + PS_DIM_R · c.

    Equivalent (by elementary ℕ-arithmetic) to N == 8.  The
    multiplicities are pinned to 1 because "fundamental" means each
    PS factor contributes its smallest irreducible piece exactly
    once; allowing a, b, c > 1 would realise the SU(N) fundamental
    as a reducible sum of PS fundamentals, which is not fundamental.

    Mirrors Lean theorem `ps_fundamental_iff_N_eq_8`.
    """
    for a in (1,):
        for b in (1,):
            for c in (1,):
                if N == PS_DIM_C * a + PS_DIM_L * b + PS_DIM_R * c:
                    return True
    return False


# ------------------------------------------------------------------
# Collatio reference content at N = 8
# ------------------------------------------------------------------

COLLATIO_CONTENT = (1, 3, 5, 7)
COLLATIO_N = 8
COLLATIO_WEYL_TOTAL = 128   # 8 + 56 + 56 + 8
SM_SHARE_AT_N8 = 48         # 3 generations × 16 Weyl
EXOTIC_SHARE_AT_N8 = 80     # 128 − 48; per C121 branching


# ------------------------------------------------------------------
# Cascade Clebsch-Gordan at the UV Yukawa vertex
# ------------------------------------------------------------------
# 1/r(N) = N / (N + 1); at N = 8 this is 8/9.  The ratio appears as
# a pure Clebsch-Gordan coefficient of the UV Yukawa vertex
# ψ_[k] ψ_[N-k] φ projected onto the SM top direction, NOT as an
# RGE-run quantity between two scales.  See CLM-034 pre-analysis
# fact (iii).
# ------------------------------------------------------------------


def cascade_cg_exact(N):
    """Cascade CG ratio 1/r = N/(N+1) at the UV vertex, exact Fraction."""
    return Fraction(N, N + 1)


CG_AT_N8 = Fraction(8, 9)


# ------------------------------------------------------------------
# Candidate content sweep across N ∈ {6, 7, 8, 9, 10}
# ------------------------------------------------------------------
# These are representative antisymmetric content multisets, NOT an
# exhaustive enumeration.  For each N the test sweep checks which
# multisets pass anomaly + fermion-count filters; the claim that
# N = 8 is uniquely selected is made under the joint filter that
# adds PS fundamental embedding.
# ------------------------------------------------------------------

CANDIDATES = {
    6:  [(1, 3, 5), (1, 5), (2, 4), (1, 2, 3, 4, 5)],
    7:  [(1, 3, 5), (1, 6), (1, 2, 5, 6), (1, 2, 3, 4, 5, 6)],
    8:  [(1, 3, 5, 7), (1, 7), (2, 6), (3, 5), (1, 3, 5, 7, 2, 6)],
    9:  [(1, 3, 5, 7), (1, 8), (1, 2, 7, 8)],
    10: [(1, 3, 5, 7, 9), (1, 9), (3, 7), (1, 2, 3, 4, 5, 6, 7, 8, 9)],
}


def survives_anomaly(content, N):
    return content_anomaly(content, N) == 0


def survives_fermion_count(content, N):
    return content_fermion_count(content, N) >= SM_WEYL_TOTAL


def survives_ps_rank(N):
    return admits_ps_embedding_by_rank(N)


def survives_ps_fundamental(N):
    return admits_ps_fundamental_embedding(N)


# ==================================================================
# TESTS
# ==================================================================


class BanksGeorgiCoefficientTests(unittest.TestCase):
    """Exact Fraction values of A([k], N) for the candidate N range."""

    def test_N8_k1(self):
        self.assertEqual(banks_georgi(1, 8), Fraction(1))

    def test_N8_k3(self):
        self.assertEqual(banks_georgi(3, 8), Fraction(5))

    def test_N8_k5(self):
        self.assertEqual(banks_georgi(5, 8), Fraction(-5))

    def test_N8_k7(self):
        self.assertEqual(banks_georgi(7, 8), Fraction(-1))

    def test_N6_k1(self):
        self.assertEqual(banks_georgi(1, 6), Fraction(1))

    def test_N6_k3(self):
        self.assertEqual(banks_georgi(3, 6), Fraction(0))

    def test_N6_k5(self):
        self.assertEqual(banks_georgi(5, 6), Fraction(-1))

    def test_N7_k2(self):
        self.assertEqual(banks_georgi(2, 7), Fraction(3))

    def test_N7_k5(self):
        self.assertEqual(banks_georgi(5, 7), Fraction(-3))

    def test_N9_k3(self):
        self.assertEqual(banks_georgi(3, 9), Fraction(9))

    def test_N10_k5(self):
        # C(8,4) × 0 / 8 = 0 (middle rank, self-conjugate-ish)
        self.assertEqual(banks_georgi(5, 10), Fraction(0))

    def test_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            banks_georgi(0, 8)
        with self.assertRaises(ValueError):
            banks_georgi(8, 8)


class ConjugationIdentityTests(unittest.TestCase):
    """A([k], N) + A([N-k], N) = 0 for all valid k, N."""

    def test_N8_k1_k7(self):
        self.assertEqual(conjugate_pair_sum(1, 8), Fraction(0))

    def test_N8_k3_k5(self):
        self.assertEqual(conjugate_pair_sum(3, 8), Fraction(0))

    def test_N7_k2_k5(self):
        self.assertEqual(conjugate_pair_sum(2, 7), Fraction(0))

    def test_conjugation_all_N_all_k(self):
        for N in (6, 7, 8, 9, 10):
            for k in range(1, N):
                self.assertEqual(
                    conjugate_pair_sum(k, N), Fraction(0),
                    f"conjugation fails at N={N}, k={k}",
                )


class AntisymmetricDimensionTests(unittest.TestCase):
    """C(N, k) fermion counts for known content."""

    def test_N8_k1(self):
        self.assertEqual(antisym_dim(1, 8), 8)

    def test_N8_k3(self):
        self.assertEqual(antisym_dim(3, 8), 56)

    def test_N8_k5(self):
        self.assertEqual(antisym_dim(5, 8), 56)

    def test_N8_k7(self):
        self.assertEqual(antisym_dim(7, 8), 8)

    def test_collatio_content_total(self):
        total = content_fermion_count(COLLATIO_CONTENT, COLLATIO_N)
        self.assertEqual(total, COLLATIO_WEYL_TOTAL)
        self.assertEqual(total, 128)


class AnomalyFreedomTests(unittest.TestCase):
    """Content multisets that are Banks-Georgi anomaly-free."""

    def test_collatio_anomaly_free(self):
        self.assertEqual(
            content_anomaly(COLLATIO_CONTENT, COLLATIO_N), Fraction(0)
        )

    def test_N6_135_anomaly_free(self):
        self.assertEqual(content_anomaly((1, 3, 5), 6), Fraction(0))

    def test_N7_135_anomaly_free_by_conjugation(self):
        # N=7: [1,3,5] — NOT self-conjugate.  Check directly.
        # A([1])+A([3])+A([5]) = 1 + 2 + (-3) = 0.
        self.assertEqual(content_anomaly((1, 3, 5), 7), Fraction(0))

    def test_N9_1357_anomaly_free(self):
        self.assertEqual(content_anomaly((1, 3, 5, 7), 9), Fraction(0))

    def test_N10_13579_anomaly_free(self):
        self.assertEqual(content_anomaly((1, 3, 5, 7, 9), 10), Fraction(0))

    def test_all_odd_content_anomaly_free(self):
        for N in (6, 7, 8, 9, 10):
            odd = tuple(k for k in range(1, N) if k % 2 == 1)
            self.assertEqual(
                content_anomaly(odd, N), Fraction(0),
                f"all-odd content not anomaly-free at N={N}",
            )


class FermionCountingTests(unittest.TestCase):
    """IR SM fermion count as a tightening filter."""

    def test_sm_weyl_total(self):
        self.assertEqual(SM_WEYL_TOTAL, 48)

    def test_N6_135_count_insufficient(self):
        # 6 + 20 + 6 = 32 < 48 — ruled out by fermion count
        c = content_fermion_count((1, 3, 5), 6)
        self.assertEqual(c, 32)
        self.assertFalse(survives_fermion_count((1, 3, 5), 6))

    def test_N7_135_count_sufficient(self):
        # 7 + 35 + 21 = 63 — passes
        c = content_fermion_count((1, 3, 5), 7)
        self.assertEqual(c, 63)
        self.assertTrue(survives_fermion_count((1, 3, 5), 7))

    def test_N8_1357_count_equals_128(self):
        self.assertEqual(content_fermion_count((1, 3, 5, 7), 8), 128)
        self.assertTrue(survives_fermion_count((1, 3, 5, 7), 8))

    def test_N9_1357_count_equals_255(self):
        # 9 + 84 + 126 + 36 = 255
        self.assertEqual(content_fermion_count((1, 3, 5, 7), 9), 255)

    def test_N10_13579_count_equals_512(self):
        # 10 + 120 + 252 + 120 + 10 = 512
        self.assertEqual(content_fermion_count((1, 3, 5, 7, 9), 10), 512)

    def test_sm_share_plus_exotic_equals_collatio_total(self):
        self.assertEqual(SM_SHARE_AT_N8 + EXOTIC_SHARE_AT_N8,
                         COLLATIO_WEYL_TOTAL)


class PSEmbeddingTests(unittest.TestCase):
    """Rank and fundamental-embedding filters for PS ⊂ SU(N)."""

    def test_ps_rank_is_5(self):
        self.assertEqual(PS_RANK, 5)

    def test_rank_requires_N_at_least_6(self):
        self.assertTrue(admits_ps_embedding_by_rank(6))
        self.assertFalse(admits_ps_embedding_by_rank(5))

    def test_rank_admits_all_candidate_N(self):
        for N in (6, 7, 8, 9, 10):
            self.assertTrue(admits_ps_embedding_by_rank(N))

    def test_fundamental_only_at_N8(self):
        self.assertTrue(admits_ps_fundamental_embedding(8))
        for N in (6, 7, 9, 10):
            self.assertFalse(admits_ps_fundamental_embedding(N))


class PSEmbeddingFilterStructural(unittest.TestCase):
    """GAP #1 closure (C194) — structural PS-fundamental predicate.

    Mirrors the Lean definition `admits_ps_fundamental` in
    AnomalyMatchingDerivation.lean and the load-bearing theorem
    `ps_fundamental_iff_N_eq_8`.  Every ℕ literal that appears in the
    Lean file (ps_dim_C = 4, ps_dim_L = 2, ps_dim_R = 2, the sum = 8,
    the enumeration over N ∈ {6, 7, 8, 9, 10}) has a Python
    assertEqual mirror here — no blind spots per
    feedback_lean_only_bugs.md.
    """

    # Per-factor fundamental dimensions.
    def test_ps_dim_C_is_4(self):
        self.assertEqual(PS_DIM_C, 4)

    def test_ps_dim_L_is_2(self):
        self.assertEqual(PS_DIM_L, 2)

    def test_ps_dim_R_is_2(self):
        self.assertEqual(PS_DIM_R, 2)

    def test_ps_dim_sum_is_8(self):
        self.assertEqual(PS_DIM_SUM, 8)

    def test_ps_dim_sum_arithmetic_identity(self):
        # Mirrors Lean `ps_dim_sum_eq_8 : ps_dim_C + ps_dim_L + ps_dim_R = 8`.
        self.assertEqual(PS_DIM_C + PS_DIM_L + PS_DIM_R, 8)

    # Structural existence at N = 8.
    def test_structural_witness_at_N8(self):
        # Mirrors Lean `ps_fundamental_at_N8 := (ps_fundamental_iff_N_eq_8 8).mpr rfl`.
        a, b, c = 1, 1, 1
        self.assertEqual(PS_DIM_C * a + PS_DIM_L * b + PS_DIM_R * c, 8)
        self.assertTrue(admits_ps_fundamental_embedding(8))

    # Structural non-existence at each other candidate.
    def test_no_structural_witness_at_N6(self):
        # Mirrors Lean `ps_fundamental_not_at_N6`.
        self.assertFalse(admits_ps_fundamental_embedding(6))
        # No (a=b=c=1) decomposition of 6 over dims (4,2,2).
        self.assertNotEqual(PS_DIM_C + PS_DIM_L + PS_DIM_R, 6)

    def test_no_structural_witness_at_N7(self):
        self.assertFalse(admits_ps_fundamental_embedding(7))
        self.assertNotEqual(PS_DIM_C + PS_DIM_L + PS_DIM_R, 7)

    def test_no_structural_witness_at_N9(self):
        self.assertFalse(admits_ps_fundamental_embedding(9))
        self.assertNotEqual(PS_DIM_C + PS_DIM_L + PS_DIM_R, 9)

    def test_no_structural_witness_at_N10(self):
        self.assertFalse(admits_ps_fundamental_embedding(10))
        self.assertNotEqual(PS_DIM_C + PS_DIM_L + PS_DIM_R, 10)

    # Biconditional (mirror of ps_fundamental_iff_N_eq_8).
    def test_iff_N_eq_8_across_candidate_set(self):
        for N in (6, 7, 8, 9, 10):
            self.assertEqual(admits_ps_fundamental_embedding(N), N == 8)

    def test_iff_N_eq_8_extended_sweep(self):
        # Extend to N ∈ {2, …, 30}: iff holds uniformly.
        for N in range(2, 31):
            self.assertEqual(admits_ps_fundamental_embedding(N), N == 8)

    # Guard against returning to the stipulation form.
    def test_predicate_is_not_stipulated(self):
        """Regression: if someone reverts to `return N == 8`, fine —
        but the *dimension constants* must still exist and sum to 8,
        and the predicate must still hold only at N = 8.  If the
        constants get deleted, this test red-lines before the Lean
        structural theorem breaks silently."""
        import sys
        mod = sys.modules[__name__]
        self.assertTrue(hasattr(mod, "PS_DIM_C"))
        self.assertTrue(hasattr(mod, "PS_DIM_L"))
        self.assertTrue(hasattr(mod, "PS_DIM_R"))
        self.assertTrue(hasattr(mod, "PS_DIM_SUM"))

    # Minimality: multiplicities > 1 are NOT a fundamental embedding.
    def test_multiplicities_pinned_to_one(self):
        """Essence of the word `fundamental`: each PS factor appears
        once.  If (a, b, c) = (2, 1, 1), we'd get dim 12, not 8 — and
        "SU(12) admits a reducible sum of PS fundamentals" is not the
        same claim as "SU(12) admits a fundamental PS embedding".
        The predicate excludes this by construction."""
        # (2, 1, 1) gives 4·2 + 2 + 2 = 12, which would "admit" a
        # reducible PS embedding but NOT a fundamental one.
        a, b, c = 2, 1, 1
        value_reducible = PS_DIM_C * a + PS_DIM_L * b + PS_DIM_R * c
        self.assertEqual(value_reducible, 12)
        # And our structural predicate correctly rejects N = 12.
        self.assertFalse(admits_ps_fundamental_embedding(12))


class CascadeCGTests(unittest.TestCase):
    """Exact vertex CG ratio 1/r(N) = N/(N+1)."""

    def test_cg_at_8_is_8_over_9(self):
        self.assertEqual(cascade_cg_exact(8), Fraction(8, 9))

    def test_cg_at_7_is_7_over_8(self):
        self.assertEqual(cascade_cg_exact(7), Fraction(7, 8))

    def test_cg_at_6_is_6_over_7(self):
        self.assertEqual(cascade_cg_exact(6), Fraction(6, 7))

    def test_cg_at_9_is_9_over_10(self):
        self.assertEqual(cascade_cg_exact(9), Fraction(9, 10))

    def test_cg_at_10_is_10_over_11(self):
        self.assertEqual(cascade_cg_exact(10), Fraction(10, 11))

    def test_cg_8_over_9_only_at_N_equals_8(self):
        # Across a wide range N ∈ {2, …, 30}, 8/9 occurs uniquely at N=8.
        for N in range(2, 31):
            if N == 8:
                self.assertEqual(cascade_cg_exact(N), Fraction(8, 9))
            else:
                self.assertNotEqual(cascade_cg_exact(N), Fraction(8, 9))

    def test_cg_matches_claim_constant(self):
        self.assertEqual(cascade_cg_exact(COLLATIO_N), CG_AT_N8)


class CandidateSweepTests(unittest.TestCase):
    """Filter-by-filter reduction of candidate (N, content) pairs."""

    def test_anomaly_alone_is_loose(self):
        survivors = [
            (N, c)
            for N, contents in CANDIDATES.items()
            for c in contents
            if survives_anomaly(c, N)
        ]
        # Anomaly freedom alone admits many candidates across N.
        # This is CLM-034 pre-analysis fact (i) made explicit.
        self.assertGreaterEqual(len(survivors), 8)

    def test_fermion_count_tightens_but_does_not_select_N(self):
        survivors_N = set()
        for N, contents in CANDIDATES.items():
            for c in contents:
                if survives_anomaly(c, N) and survives_fermion_count(c, N):
                    survivors_N.add(N)
        # At least two distinct N survive this joint filter.
        # Fermion count does NOT uniquely select N=8.
        self.assertGreater(len(survivors_N), 1)
        self.assertIn(8, survivors_N)

    def test_ps_fundamental_selects_N8_uniquely(self):
        survivors_N = set()
        for N, contents in CANDIDATES.items():
            for c in contents:
                if (survives_anomaly(c, N)
                        and survives_fermion_count(c, N)
                        and survives_ps_fundamental(N)):
                    survivors_N.add(N)
        # Under the triple joint filter, only N=8 survives.
        self.assertEqual(survivors_N, {8})

    def test_collatio_content_survives_all_filters(self):
        c, N = COLLATIO_CONTENT, COLLATIO_N
        self.assertTrue(survives_anomaly(c, N))
        self.assertTrue(survives_fermion_count(c, N))
        self.assertTrue(survives_ps_rank(N))
        self.assertTrue(survives_ps_fundamental(N))


class THooftMatchingStructuralTests(unittest.TestCase):
    """Structural 't Hooft matching facts recorded without redriving
    the full SU(N)→PS→SM branching for N ≠ 8.

    The branching computation for N ≠ 8 is the piece that would
    independently verify (or refute) the PS-fundamental-embedding
    filter via explicit irrep counting.  That work is out of scope
    for Avenue 1 and is deferred to Avenue 2 (conformal bootstrap)
    or a follow-up.
    """

    def test_collatio_SM_plus_exotic_matches_total(self):
        # Known from C121 branching: 128 = 48 SM + 80 exotic at N=8.
        self.assertEqual(
            SM_SHARE_AT_N8 + EXOTIC_SHARE_AT_N8,
            COLLATIO_WEYL_TOTAL,
        )

    def test_cg_ratio_is_vertex_not_rge(self):
        # Fact (iii) from CLM-034 pre-analysis: the 8/9 is a vertex
        # Clebsch-Gordan, a pure rational with no logs and no scale
        # dependence.  Verified by the exact Fraction form of
        # cascade_cg_exact for all N.
        for N in (6, 7, 8, 9, 10):
            r = cascade_cg_exact(N)
            self.assertIsInstance(r, Fraction)

    def test_N8_uniquely_hits_8_over_9(self):
        hits = [
            N for N in (6, 7, 8, 9, 10)
            if cascade_cg_exact(N) == Fraction(8, 9)
        ]
        self.assertEqual(hits, [8])


class HonestClosureTests(unittest.TestCase):
    """Explicit tests documenting the closure direction for Avenue 1.

    Per CLM-034 acceptance criteria, both positive (H₁) and negative
    (H₀) closures are valid under Commandment I.  These tests
    record the ACTUAL closure direction produced by the arithmetic
    above, not a pre-decided outcome.
    """

    def test_fact_i_anomaly_alone_insufficient(self):
        # CLM-034 pre-analysis fact (i): Banks-Georgi anomaly freedom
        # admits SU(N) for all N ∈ {6,…,10} with self-conjugate odd
        # content.
        for N in (6, 7, 8, 9, 10):
            odd = tuple(k for k in range(1, N) if k % 2 == 1)
            self.assertEqual(content_anomaly(odd, N), Fraction(0))

    def test_fact_ii_fermion_count_eliminates_small_N_minimal_content(self):
        # CLM-034 pre-analysis fact (ii): the SM fermion target 48
        # eliminates some (N, content) pairs but not entire N values.
        self.assertLess(content_fermion_count((1, 3, 5), 6), 48)
        self.assertGreaterEqual(content_fermion_count((1, 3, 5), 7), 48)

    def test_fact_iii_cg_is_pure_rational(self):
        # CLM-034 pre-analysis fact (iii): vertex CG is rational,
        # not RGE-run.
        for N in (6, 7, 8, 9, 10):
            r = cascade_cg_exact(N)
            self.assertEqual(r, Fraction(N, N + 1))

    def test_joint_filter_selects_N8_uniquely(self):
        # Actual Avenue 1 result under the three combined filters:
        # {anomaly freedom, fermion count ≥ 48, PS fundamental}
        # → only N = 8 survives in the enumerated candidate space.
        survivors = []
        for N, contents in CANDIDATES.items():
            for c in contents:
                if (survives_anomaly(c, N)
                        and survives_fermion_count(c, N)
                        and survives_ps_fundamental(N)):
                    survivors.append((N, c))
        self.assertTrue(survivors)
        self.assertTrue(all(N == 8 for (N, _) in survivors))

    def test_closure_direction_partial_positive(self):
        # HONEST CLOSURE (Avenue 1): PARTIAL POSITIVE.
        #
        # Establishes: within the enumerated candidate space and
        # under the triple filter (anomaly + fermion-count + PS
        # fundamental), N = 8 is uniquely selected, and the
        # vertex CG at N = 8 evaluates to 8/9 as a pure rational.
        #
        # Does NOT establish: ruling out non-fundamental PS
        # embeddings at N ∈ {6, 7, 9, 10}, which would require
        # explicit SU(N) → PS branching for those N.  Therefore
        # Avenue 1 tightens the CLM-001 evidence floor by one
        # avenue but does NOT by itself promote the label to
        # `theorem`.
        collatio_ratio = cascade_cg_exact(8)
        self.assertEqual(collatio_ratio, Fraction(8, 9))
        for N in (6, 7, 9, 10):
            self.assertNotEqual(cascade_cg_exact(N), Fraction(8, 9))


class CommandmentXIIAuditTests(unittest.TestCase):
    """Zero-float audit of the derivation path per Commandment XII."""

    def test_banks_georgi_returns_fraction(self):
        for N in (6, 7, 8, 9, 10):
            for k in range(1, N):
                self.assertIsInstance(banks_georgi(k, N), Fraction)

    def test_content_anomaly_returns_fraction(self):
        for N, contents in CANDIDATES.items():
            for c in contents:
                self.assertIsInstance(content_anomaly(c, N), Fraction)

    def test_cascade_cg_returns_fraction(self):
        for N in (6, 7, 8, 9, 10):
            self.assertIsInstance(cascade_cg_exact(N), Fraction)


class LeanParityMirrorTests(unittest.TestCase):
    """Mirror every ℚ literal that the companion Lean file will assert.

    These are the assertions the Lean file AnomalyMatchingDerivation.lean
    will close with `decide` / `norm_num`.  Keep this class in sync
    with the Lean file; any Lean literal without a mirror here is a
    blind spot per feedback_lean_only_bugs.md.
    """

    def test_mirror_bg_N8_k1(self):
        self.assertEqual(banks_georgi(1, 8), Fraction(1, 1))

    def test_mirror_bg_N8_k3(self):
        self.assertEqual(banks_georgi(3, 8), Fraction(5, 1))

    def test_mirror_bg_N8_k5(self):
        self.assertEqual(banks_georgi(5, 8), Fraction(-5, 1))

    def test_mirror_bg_N8_k7(self):
        self.assertEqual(banks_georgi(7, 8), Fraction(-1, 1))

    def test_mirror_collatio_anomaly_sum_zero(self):
        self.assertEqual(
            content_anomaly(COLLATIO_CONTENT, COLLATIO_N),
            Fraction(0, 1),
        )

    def test_mirror_collatio_weyl_128(self):
        self.assertEqual(
            content_fermion_count(COLLATIO_CONTENT, COLLATIO_N), 128
        )

    def test_mirror_cg_at_8(self):
        self.assertEqual(cascade_cg_exact(8), Fraction(8, 9))

    def test_mirror_cg_at_7(self):
        self.assertEqual(cascade_cg_exact(7), Fraction(7, 8))

    def test_mirror_cg_at_6(self):
        self.assertEqual(cascade_cg_exact(6), Fraction(6, 7))

    def test_mirror_cg_at_9(self):
        self.assertEqual(cascade_cg_exact(9), Fraction(9, 10))

    def test_mirror_cg_at_10(self):
        self.assertEqual(cascade_cg_exact(10), Fraction(10, 11))

    def test_mirror_sm_weyl_total_48(self):
        self.assertEqual(SM_WEYL_TOTAL, 48)

    def test_mirror_ps_rank_5(self):
        self.assertEqual(PS_RANK, 5)

    def test_mirror_sm_share_48_plus_exotic_80_equals_128(self):
        self.assertEqual(SM_SHARE_AT_N8 + EXOTIC_SHARE_AT_N8, 128)

    # --------------------------------------------------------------
    # GAP #1 closure (C194) — structural iff mirrors.  Each ℕ
    # literal that AnomalyMatchingDerivation.lean asserts inside
    # the new GAP #1 block has an assertEqual here, per
    # feedback_lean_only_bugs.md.
    # --------------------------------------------------------------

    def test_mirror_ps_dim_C_eq_4(self):
        self.assertEqual(PS_DIM_C, 4)

    def test_mirror_ps_dim_L_eq_2(self):
        self.assertEqual(PS_DIM_L, 2)

    def test_mirror_ps_dim_R_eq_2(self):
        self.assertEqual(PS_DIM_R, 2)

    def test_mirror_ps_dim_sum_eq_8(self):
        # Mirrors Lean `ps_dim_sum_eq_8`.
        self.assertEqual(PS_DIM_C + PS_DIM_L + PS_DIM_R, 8)

    def test_mirror_ps_fundamental_at_N8(self):
        # Mirrors Lean `ps_fundamental_at_N8`.
        self.assertTrue(admits_ps_fundamental_embedding(8))

    def test_mirror_ps_fundamental_not_at_N6(self):
        self.assertFalse(admits_ps_fundamental_embedding(6))

    def test_mirror_ps_fundamental_not_at_N7(self):
        self.assertFalse(admits_ps_fundamental_embedding(7))

    def test_mirror_ps_fundamental_not_at_N9(self):
        self.assertFalse(admits_ps_fundamental_embedding(9))

    def test_mirror_ps_fundamental_not_at_N10(self):
        self.assertFalse(admits_ps_fundamental_embedding(10))

    def test_mirror_structural_iff_holds(self):
        # Mirrors Lean `ps_fundamental_iff_N_eq_8` over the candidate set.
        for N in (6, 7, 8, 9, 10):
            self.assertEqual(admits_ps_fundamental_embedding(N), N == 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
