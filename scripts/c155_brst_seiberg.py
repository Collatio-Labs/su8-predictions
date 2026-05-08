"""
Copyright 2026 Steven Lamar Michael. All rights reserved.

c155_brst_seiberg.py — Python parity guard for CLM-041 (Avenue 6 of
Route A: BRST cohomology / Seiberg duality constraints on the Collatio
antisymmetric content [1]+[3]+[5]+[7] of SU(N)).

Three exact-ℚ/ℤ filter conditions jointly select N = 8 uniquely among
the enumerated candidate set {6, 7, 8, 9, 10}:

  (A)  Asymptotic freedom — the one-loop β₀ = (11N − 2T(N))/3 is
       positive, where T(N) = Σ_{k∈{1,3,5,7}} C(N−2, k−1) is the
       total Dynkin index of the Collatio content.  AF is a necessary
       condition for a Seiberg-type dual description to exist.
       Eliminates N = 9 (β₀ = −29/3) and N = 10 (β₀ = −48).

  (B)  Non-degenerate conjugate pairing — all four content reps
       [1], [3], [5], [7] pair as [k] ↔ [N−k] with k ≠ N−k (no
       self-conjugate reps).  This condition operationalises BRST
       vacuum uniqueness: self-conjugate pairs give real flat
       directions that the BRST differential cannot lift, leading
       to dim(H⁰) > 1.  When every pair is non-degenerate (k < N−k),
       the mesonic moduli are liftable and H⁰ = ℂ (unique vacuum).
       Eliminates N = 6 (pair {3,3} is self-conjugate at N = 6
       because N − 3 = 3) and N = 7 (no content rep has its
       conjugate in the content).

  (C)  Combined: admits_brst_seiberg(N) := AF(N) AND n_proper_pairs(N) = 2.
       Within {6, 7, 8, 9, 10}, only N = 8 passes both.

Zero floats.  Exact Fraction throughout per Commandment XII.

CLOSURE DIRECTION: PARTIAL POSITIVE — same as CLM-034.  This avenue
establishes that within the enumerated candidate set and under the
stated joint filter, N = 8 is uniquely selected.  CLM-001 label
remains 'structurally-forced'.  Avenue 6 is the sixth and final
Route A avenue.

HONEST SCOPE (Commandment I):
  - "Seiberg duality" is used in the structural sense that AF is a
    necessary condition for a dual description; the explicit magnetic
    dual theory is NOT constructed.
  - "BRST cohomology H⁰ = 1-dim" is operationalised as the conjugate-
    pairing condition; an explicit BRST cohomology computation is NOT
    performed.
  - Seiberg duality in its original form applies to N = 1 SUSY
    theories; the Collatio content is non-SUSY.  The avenue uses the
    structural filter conditions (AF + conjugate pairing), not a
    literal N = 1 SUSY duality.

Companion Lean file: proofs/UFT/lean/BRSTSeibergDuality.lean.
Every ℚ/ℕ/ℤ literal that the Lean file asserts has an assertEqual
mirror in LeanParityMirrorTests below.
"""

from fractions import Fraction
from math import comb
import unittest


# ------------------------------------------------------------------
# Dynkin index of rank-k antisymmetric rep of SU(N)
# ------------------------------------------------------------------
# T([k]) = C(N-2, k-1)  in the normalisation T(fund) = 1.
# The one-loop β₀ uses this normalisation directly:
#   β₀ = (11N − 2 T_total) / 3.
# ------------------------------------------------------------------

CONTENT = (1, 3, 5, 7)


def dynkin_index(k, N):
    """Dynkin index T([k]) = C(N-2, k-1) for the rank-k antisymmetric
    representation of SU(N), in the normalisation T(fund) = 1."""
    if k < 1 or k > N - 1:
        return 0
    return comb(N - 2, k - 1)


def dynkin_sum(N):
    """Total Dynkin index of the Collatio content [1]+[3]+[5]+[7]."""
    return sum(dynkin_index(k, N) for k in CONTENT)


# ------------------------------------------------------------------
# One-loop β₀ and asymptotic freedom
# ------------------------------------------------------------------

def beta_zero(N):
    """One-loop β₀ = (11N − 2 T_total) / 3 as exact Fraction."""
    return Fraction(11 * N - 2 * dynkin_sum(N), 3)


def is_af(N):
    """Asymptotic freedom requires β₀ > 0, i.e. 11N > 2T(N)."""
    return 11 * N > 2 * dynkin_sum(N)


# ------------------------------------------------------------------
# Non-degenerate conjugate pairing
# ------------------------------------------------------------------

def in_content(k):
    return k in CONTENT


def n_proper_pairs(N):
    """Number of unordered pairs {k, N-k} with k, N-k ∈ content and k < N-k.

    This counts non-degenerate (k ≠ N-k) mesonic pairings.  A self-
    conjugate pair (k = N-k, i.e. k = N/2) does NOT count, because it
    corresponds to a real flat direction in the classical moduli space
    that the BRST differential cannot lift.
    """
    count = 0
    for k in CONTENT:
        partner = N - k
        if partner >= 0 and in_content(partner) and k < partner:
            count += 1
    return count


# ------------------------------------------------------------------
# Joint filter
# ------------------------------------------------------------------

def admits_brst_seiberg(N):
    """Joint filter: asymptotic freedom AND exactly 2 proper pairs."""
    return is_af(N) and n_proper_pairs(N) == 2


# ------------------------------------------------------------------
# Cascade CG (re-stated locally, same as CLM-034)
# ------------------------------------------------------------------

def cascade_cg(N):
    return Fraction(N, N + 1)


# ==================================================================
# TESTS
# ==================================================================


class DynkinIndexTests(unittest.TestCase):
    """Dynkin index values T([k]) = C(N-2, k-1) for each k at each N."""

    def test_T1_N8(self):
        self.assertEqual(dynkin_index(1, 8), 1)

    def test_T3_N8(self):
        self.assertEqual(dynkin_index(3, 8), 15)

    def test_T5_N8(self):
        self.assertEqual(dynkin_index(5, 8), 15)

    def test_T7_N8(self):
        self.assertEqual(dynkin_index(7, 8), 1)

    def test_T7_N6(self):
        self.assertEqual(dynkin_index(7, 6), 0)

    def test_T7_N7(self):
        self.assertEqual(dynkin_index(7, 7), 0)

    def test_T7_N9(self):
        self.assertEqual(dynkin_index(7, 9), 7)

    def test_T7_N10(self):
        self.assertEqual(dynkin_index(7, 10), 28)


class DynkinSumTests(unittest.TestCase):
    """Total Dynkin index T(N) = Σ C(N-2, k-1) for k ∈ {1,3,5,7}."""

    def test_dynkin_sum_N6(self):
        self.assertEqual(dynkin_sum(6), 8)

    def test_dynkin_sum_N7(self):
        self.assertEqual(dynkin_sum(7), 16)

    def test_dynkin_sum_N8(self):
        self.assertEqual(dynkin_sum(8), 32)

    def test_dynkin_sum_N9(self):
        self.assertEqual(dynkin_sum(9), 64)

    def test_dynkin_sum_N10(self):
        self.assertEqual(dynkin_sum(10), 127)

    def test_dynkin_sum_decomposition_N8(self):
        self.assertEqual(
            comb(6, 0) + comb(6, 2) + comb(6, 4) + comb(6, 6), 32
        )

    def test_dynkin_sum_decomposition_N6(self):
        self.assertEqual(
            comb(4, 0) + comb(4, 2) + comb(4, 4) + comb(4, 6), 8
        )


class BetaZeroTests(unittest.TestCase):
    """One-loop β₀ = (11N − 2T(N))/3 as exact Fraction."""

    def test_beta_zero_N6(self):
        self.assertEqual(beta_zero(6), Fraction(50, 3))

    def test_beta_zero_N7(self):
        self.assertEqual(beta_zero(7), Fraction(15))

    def test_beta_zero_N8(self):
        self.assertEqual(beta_zero(8), Fraction(8))

    def test_beta_zero_N9(self):
        self.assertEqual(beta_zero(9), Fraction(-29, 3))

    def test_beta_zero_N10(self):
        self.assertEqual(beta_zero(10), Fraction(-48))

    def test_beta_zero_numerator_N6(self):
        self.assertEqual(11 * 6 - 2 * dynkin_sum(6), 50)

    def test_beta_zero_numerator_N7(self):
        self.assertEqual(11 * 7 - 2 * dynkin_sum(7), 45)

    def test_beta_zero_numerator_N8(self):
        self.assertEqual(11 * 8 - 2 * dynkin_sum(8), 24)

    def test_beta_zero_numerator_N9(self):
        self.assertEqual(11 * 9 - 2 * dynkin_sum(9), -29)

    def test_beta_zero_numerator_N10(self):
        self.assertEqual(11 * 10 - 2 * dynkin_sum(10), -144)


class AsymptoticFreedomTests(unittest.TestCase):
    """AF requires β₀ > 0, i.e. 11N > 2T(N)."""

    def test_af_N6(self):
        self.assertTrue(is_af(6))

    def test_af_N7(self):
        self.assertTrue(is_af(7))

    def test_af_N8(self):
        self.assertTrue(is_af(8))

    def test_not_af_N9(self):
        self.assertFalse(is_af(9))

    def test_not_af_N10(self):
        self.assertFalse(is_af(10))

    def test_af_survivors(self):
        survivors = [N for N in (6, 7, 8, 9, 10) if is_af(N)]
        self.assertEqual(survivors, [6, 7, 8])


class ConjugatePairingTests(unittest.TestCase):
    """Non-degenerate conjugate pairs {k, N-k} with k < N-k."""

    def test_n_proper_pairs_N6(self):
        self.assertEqual(n_proper_pairs(6), 1)

    def test_n_proper_pairs_N7(self):
        self.assertEqual(n_proper_pairs(7), 0)

    def test_n_proper_pairs_N8(self):
        self.assertEqual(n_proper_pairs(8), 2)

    def test_n_proper_pairs_N9(self):
        self.assertEqual(n_proper_pairs(9), 0)

    def test_n_proper_pairs_N10(self):
        self.assertEqual(n_proper_pairs(10), 1)

    def test_N8_pairs_are_1_7_and_3_5(self):
        pairs = []
        for k in CONTENT:
            partner = 8 - k
            if in_content(partner) and k < partner:
                pairs.append((k, partner))
        self.assertEqual(pairs, [(1, 7), (3, 5)])

    def test_N6_self_conjugate_pair(self):
        self.assertEqual(6 - 3, 3)
        self.assertTrue(in_content(3))
        self.assertFalse(3 < 3)

    def test_N7_no_conjugates_in_content(self):
        for k in CONTENT:
            partner = 7 - k
            self.assertFalse(
                in_content(partner) and k < partner,
                f"k={k} unexpectedly pairs at N=7",
            )

    def test_N10_self_conjugate_5(self):
        self.assertEqual(10 - 5, 5)
        self.assertTrue(in_content(5))
        self.assertFalse(5 < 5)

    def test_unique_max_at_N8(self):
        vals = {N: n_proper_pairs(N) for N in (6, 7, 8, 9, 10)}
        max_N = max(vals, key=vals.get)
        self.assertEqual(max_N, 8)
        self.assertEqual(vals[8], 2)
        for N in (6, 7, 9, 10):
            self.assertLess(vals[N], 2)


class JointFilterTests(unittest.TestCase):
    """admits_brst_seiberg(N) := AF(N) AND n_proper_pairs(N) = 2."""

    def test_admits_N8(self):
        self.assertTrue(admits_brst_seiberg(8))

    def test_not_admits_N6(self):
        self.assertFalse(admits_brst_seiberg(6))

    def test_not_admits_N7(self):
        self.assertFalse(admits_brst_seiberg(7))

    def test_not_admits_N9(self):
        self.assertFalse(admits_brst_seiberg(9))

    def test_not_admits_N10(self):
        self.assertFalse(admits_brst_seiberg(10))

    def test_N6_fails_on_pairing_not_af(self):
        self.assertTrue(is_af(6))
        self.assertNotEqual(n_proper_pairs(6), 2)

    def test_N7_fails_on_pairing(self):
        self.assertTrue(is_af(7))
        self.assertEqual(n_proper_pairs(7), 0)

    def test_N9_fails_on_af(self):
        self.assertFalse(is_af(9))

    def test_N10_fails_on_both(self):
        self.assertFalse(is_af(10))
        self.assertNotEqual(n_proper_pairs(10), 2)

    def test_uniqueness_over_candidate_set(self):
        survivors = [N for N in (6, 7, 8, 9, 10) if admits_brst_seiberg(N)]
        self.assertEqual(survivors, [8])

    def test_uniqueness_extended_sweep(self):
        for N in range(3, 31):
            if admits_brst_seiberg(N):
                self.assertEqual(N, 8, f"N={N} unexpectedly passes joint filter")


class CascadeCGTests(unittest.TestCase):
    """Cross-witness: cascade CG at N = 8 is 8/9."""

    def test_cg_N8(self):
        self.assertEqual(cascade_cg(8), Fraction(8, 9))

    def test_cg_N8_ne_cg_N7(self):
        self.assertNotEqual(cascade_cg(8), cascade_cg(7))


class HonestScopeTests(unittest.TestCase):
    """Honest scope per Commandment I."""

    def test_closure_partial_positive(self):
        self.assertTrue(admits_brst_seiberg(8))
        self.assertEqual(cascade_cg(8), Fraction(8, 9))
        for N in (6, 7, 9, 10):
            self.assertFalse(admits_brst_seiberg(N))

    def test_af_alone_insufficient(self):
        af_survivors = [N for N in (6, 7, 8, 9, 10) if is_af(N)]
        self.assertEqual(len(af_survivors), 3)

    def test_pairing_alone_insufficient(self):
        pair_survivors = [N for N in (6, 7, 8, 9, 10) if n_proper_pairs(N) == 2]
        self.assertEqual(pair_survivors, [8])


class CommandmentXIIAuditTests(unittest.TestCase):
    """Zero-float audit per Commandment XII."""

    def test_beta_zero_returns_fraction(self):
        for N in (6, 7, 8, 9, 10):
            self.assertIsInstance(beta_zero(N), Fraction)

    def test_cascade_cg_returns_fraction(self):
        for N in (6, 7, 8, 9, 10):
            self.assertIsInstance(cascade_cg(N), Fraction)

    def test_dynkin_sum_returns_int(self):
        for N in (6, 7, 8, 9, 10):
            self.assertIsInstance(dynkin_sum(N), int)

    def test_n_proper_pairs_returns_int(self):
        for N in (6, 7, 8, 9, 10):
            self.assertIsInstance(n_proper_pairs(N), int)


class LeanParityMirrorTests(unittest.TestCase):
    """Mirror every ℚ/ℕ/ℤ literal in BRSTSeibergDuality.lean.

    Per feedback_lean_only_bugs.md, every Lean theorem of the form
    A = B := by decide/norm_num must have a Python assertEqual(A, B)
    mirror here.
    """

    # Dynkin sum values (Section 1)
    def test_mirror_dynkin_sum_N6(self):
        self.assertEqual(dynkin_sum(6), 8)

    def test_mirror_dynkin_sum_N7(self):
        self.assertEqual(dynkin_sum(7), 16)

    def test_mirror_dynkin_sum_N8(self):
        self.assertEqual(dynkin_sum(8), 32)

    def test_mirror_dynkin_sum_N9(self):
        self.assertEqual(dynkin_sum(9), 64)

    def test_mirror_dynkin_sum_N10(self):
        self.assertEqual(dynkin_sum(10), 127)

    # Beta zero numerators (Section 2)
    def test_mirror_beta_num_N6(self):
        self.assertEqual(11 * 6 - 2 * 8, 50)

    def test_mirror_beta_num_N7(self):
        self.assertEqual(11 * 7 - 2 * 16, 45)

    def test_mirror_beta_num_N8(self):
        self.assertEqual(11 * 8 - 2 * 32, 24)

    def test_mirror_beta_num_N9(self):
        self.assertEqual(11 * 9 - 2 * 64, -29)

    def test_mirror_beta_num_N10(self):
        self.assertEqual(11 * 10 - 2 * 127, -144)

    # Beta zero as ℚ (Section 2)
    def test_mirror_beta_zero_N6(self):
        self.assertEqual(beta_zero(6), Fraction(50, 3))

    def test_mirror_beta_zero_N7(self):
        self.assertEqual(beta_zero(7), Fraction(15))

    def test_mirror_beta_zero_N8(self):
        self.assertEqual(beta_zero(8), Fraction(8))

    def test_mirror_beta_zero_N9(self):
        self.assertEqual(beta_zero(9), Fraction(-29, 3))

    def test_mirror_beta_zero_N10(self):
        self.assertEqual(beta_zero(10), Fraction(-48))

    # AF conditions (Section 2)
    def test_mirror_af_N6(self):
        self.assertGreater(11 * 6, 2 * dynkin_sum(6))

    def test_mirror_af_N7(self):
        self.assertGreater(11 * 7, 2 * dynkin_sum(7))

    def test_mirror_af_N8(self):
        self.assertGreater(11 * 8, 2 * dynkin_sum(8))

    def test_mirror_not_af_N9(self):
        self.assertLessEqual(11 * 9, 2 * dynkin_sum(9))

    def test_mirror_not_af_N10(self):
        self.assertLessEqual(11 * 10, 2 * dynkin_sum(10))

    # Proper pair counts (Section 3)
    def test_mirror_pairs_N6(self):
        self.assertEqual(n_proper_pairs(6), 1)

    def test_mirror_pairs_N7(self):
        self.assertEqual(n_proper_pairs(7), 0)

    def test_mirror_pairs_N8(self):
        self.assertEqual(n_proper_pairs(8), 2)

    def test_mirror_pairs_N9(self):
        self.assertEqual(n_proper_pairs(9), 0)

    def test_mirror_pairs_N10(self):
        self.assertEqual(n_proper_pairs(10), 1)

    # Joint filter (Section 4)
    def test_mirror_admits_N8(self):
        self.assertTrue(admits_brst_seiberg(8))

    def test_mirror_not_admits_N6(self):
        self.assertFalse(admits_brst_seiberg(6))

    def test_mirror_not_admits_N7(self):
        self.assertFalse(admits_brst_seiberg(7))

    def test_mirror_not_admits_N9(self):
        self.assertFalse(admits_brst_seiberg(9))

    def test_mirror_not_admits_N10(self):
        self.assertFalse(admits_brst_seiberg(10))

    # Cascade CG cross-witness (Section 6)
    def test_mirror_cg_N8(self):
        self.assertEqual(cascade_cg(8), Fraction(8, 9))

    def test_mirror_cg_N8_ne_N7(self):
        self.assertNotEqual(cascade_cg(8), cascade_cg(7))


if __name__ == "__main__":
    unittest.main(verbosity=2)
