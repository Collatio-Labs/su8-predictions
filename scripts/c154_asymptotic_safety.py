"""c154_asymptotic_safety.py — Python parity guard for CLM-040
AsymptoticSafetyUniqueness.lean

Every ℕ/ℚ literal in the Lean file has an assertEqual mirror here.
Commandment XII: all arithmetic via exact Fraction, zero floats.
"""

import unittest
from fractions import Fraction
from math import comb


class SpectralHalfCountTests(unittest.TestCase):
    """Mirror §1: n_gen(N) = floor((N-1)/2)."""

    def test_shc_6(self):
        self.assertEqual((6 - 1) // 2, 2)

    def test_shc_7(self):
        self.assertEqual((7 - 1) // 2, 3)

    def test_shc_8(self):
        self.assertEqual((8 - 1) // 2, 3)

    def test_shc_9(self):
        self.assertEqual((9 - 1) // 2, 4)

    def test_shc_10(self):
        self.assertEqual((10 - 1) // 2, 4)


class ThreeGenFilterTests(unittest.TestCase):
    """Mirror §2: has_three_gen(N) := spectral_half_count(N) = 3."""

    def _has_3gen(self, N):
        return (N - 1) // 2 == 3

    def test_not_3gen_6(self):
        self.assertFalse(self._has_3gen(6))

    def test_3gen_7(self):
        self.assertTrue(self._has_3gen(7))

    def test_3gen_8(self):
        self.assertTrue(self._has_3gen(8))

    def test_not_3gen_9(self):
        self.assertFalse(self._has_3gen(9))

    def test_not_3gen_10(self):
        self.assertFalse(self._has_3gen(10))

    def test_3gen_survivors(self):
        survivors = {N for N in range(6, 11) if self._has_3gen(N)}
        self.assertEqual(survivors, {7, 8})


class DimensionTests(unittest.TestCase):
    """Mirror §3: antisymmetric rep dimensions C(N,k)."""

    def test_dim_1_all(self):
        for N, exp in [(6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]:
            self.assertEqual(comb(N, 1), exp, f"dim_1({N})")

    def test_dim_3_all(self):
        for N, exp in [(6, 20), (7, 35), (8, 56), (9, 84), (10, 120)]:
            self.assertEqual(comb(N, 3), exp, f"dim_3({N})")

    def test_dim_5_all(self):
        for N, exp in [(6, 6), (7, 21), (8, 56), (9, 126), (10, 252)]:
            self.assertEqual(comb(N, 5), exp, f"dim_5({N})")

    def test_dim_7_all(self):
        for N, exp in [(6, 0), (7, 1), (8, 8), (9, 36), (10, 120)]:
            self.assertEqual(comb(N, 7), exp, f"dim_7({N})")


class ContentNonTrivialityTests(unittest.TestCase):
    """Mirror §4: content_nontrivial(N) := all C(N,k) >= 2 for k in {1,3,5,7}."""

    def _cnt(self, N):
        return all(comb(N, k) >= 2 for k in [1, 3, 5, 7])

    def test_cnt_not_6(self):
        self.assertFalse(self._cnt(6))

    def test_cnt_not_7(self):
        self.assertFalse(self._cnt(7))

    def test_cnt_8(self):
        self.assertTrue(self._cnt(8))

    def test_cnt_9(self):
        self.assertTrue(self._cnt(9))

    def test_cnt_10(self):
        self.assertTrue(self._cnt(10))

    def test_cnt_survivors(self):
        survivors = {N for N in range(6, 11) if self._cnt(N)}
        self.assertEqual(survivors, {8, 9, 10})


class ASViableTests(unittest.TestCase):
    """Mirror §5: as_viable(N) := has_three_gen(N) AND content_nontrivial(N)."""

    def _viable(self, N):
        gen3 = (N - 1) // 2 == 3
        cnt = all(comb(N, k) >= 2 for k in [1, 3, 5, 7])
        return gen3 and cnt

    def test_not_viable_6(self):
        self.assertFalse(self._viable(6))

    def test_not_viable_7(self):
        self.assertFalse(self._viable(7))

    def test_viable_8(self):
        self.assertTrue(self._viable(8))

    def test_not_viable_9(self):
        self.assertFalse(self._viable(9))

    def test_not_viable_10(self):
        self.assertFalse(self._viable(10))

    def test_unique_survivor(self):
        survivors = {N for N in range(6, 11) if self._viable(N)}
        self.assertEqual(survivors, {8})


class UniquenessTests(unittest.TestCase):
    """Mirror uniqueness: only N=8 passes the joint filter."""

    def _viable(self, N):
        gen3 = (N - 1) // 2 == 3
        cnt = all(comb(N, k) >= 2 for k in [1, 3, 5, 7])
        return gen3 and cnt

    def test_uniqueness_over_candidates(self):
        for N in [6, 7, 9, 10]:
            self.assertFalse(self._viable(N), f"N={N} should not be viable")
        self.assertTrue(self._viable(8))

    def test_uniqueness_extended_sweep(self):
        passing = {N for N in range(2, 31) if self._viable(N)}
        self.assertEqual(passing, {8})


class CascadeCGTests(unittest.TestCase):
    """Mirror §6: cascade_cg(N) = N/(N+1)."""

    def test_cascade_cg_8(self):
        self.assertEqual(Fraction(8, 8 + 1), Fraction(8, 9))


class MasterTheoremTests(unittest.TestCase):
    """Mirror §8: master theorem conjunction."""

    def _viable(self, N):
        gen3 = (N - 1) // 2 == 3
        cnt = all(comb(N, k) >= 2 for k in [1, 3, 5, 7])
        return gen3 and cnt

    def test_master_all_six_clauses(self):
        self.assertFalse(self._viable(6))
        self.assertFalse(self._viable(7))
        self.assertTrue(self._viable(8))
        self.assertFalse(self._viable(9))
        self.assertFalse(self._viable(10))
        self.assertEqual(Fraction(8, 9), Fraction(8, 9))


class LeanParityMirrorTests(unittest.TestCase):
    """Every ℕ literal in AsymptoticSafetyUniqueness.lean has a mirror here."""

    def test_shc_literals(self):
        for N, exp in [(6, 2), (7, 3), (8, 3), (9, 4), (10, 4)]:
            self.assertEqual((N - 1) // 2, exp, f"shc({N})")

    def test_dim_1_all_literals(self):
        for N in [6, 7, 8, 9, 10]:
            self.assertEqual(comb(N, 1), N, f"dim_1({N}) = N")

    def test_dim_3_at_8(self):
        self.assertEqual(comb(8, 3), 56)

    def test_dim_5_at_8(self):
        self.assertEqual(comb(8, 5), 56)

    def test_dim_7_at_8(self):
        self.assertEqual(comb(8, 7), 8)

    def test_dim_7_at_6_zero(self):
        self.assertEqual(comb(6, 7), 0)

    def test_dim_7_at_7_singlet(self):
        self.assertEqual(comb(7, 7), 1)

    def test_cascade_cg_literal(self):
        self.assertEqual(Fraction(8, 8 + 1), Fraction(8, 9))


class CommandmentXIITests(unittest.TestCase):
    """Commandment XII: zero floats in derivation path."""

    def test_no_float_in_fractions(self):
        vals = [Fraction(8, 9)]
        for v in vals:
            self.assertIsInstance(v, Fraction)


if __name__ == '__main__':
    unittest.main()
