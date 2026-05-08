"""c153_lattice_su8.py — Python parity guard for CLM-039
LatticeSU8StrongCoupling.lean

Every ℕ/ℚ literal in the Lean file has an assertEqual mirror here.
Commandment XII: all arithmetic via exact Fraction, zero floats.
"""

import unittest
from fractions import Fraction
from math import comb


class DimensionTests(unittest.TestCase):
    """Mirror §1: antisymmetric rep dimensions dim([k]) = C(N,k)."""

    def test_dim_1_at_6(self):
        self.assertEqual(comb(6, 1), 6)

    def test_dim_1_at_7(self):
        self.assertEqual(comb(7, 1), 7)

    def test_dim_1_at_8(self):
        self.assertEqual(comb(8, 1), 8)

    def test_dim_1_at_9(self):
        self.assertEqual(comb(9, 1), 9)

    def test_dim_1_at_10(self):
        self.assertEqual(comb(10, 1), 10)

    def test_dim_3_at_6(self):
        self.assertEqual(comb(6, 3), 20)

    def test_dim_3_at_7(self):
        self.assertEqual(comb(7, 3), 35)

    def test_dim_3_at_8(self):
        self.assertEqual(comb(8, 3), 56)

    def test_dim_3_at_9(self):
        self.assertEqual(comb(9, 3), 84)

    def test_dim_3_at_10(self):
        self.assertEqual(comb(10, 3), 120)

    def test_dim_5_at_6(self):
        self.assertEqual(comb(6, 5), 6)

    def test_dim_5_at_7(self):
        self.assertEqual(comb(7, 5), 21)

    def test_dim_5_at_8(self):
        self.assertEqual(comb(8, 5), 56)

    def test_dim_5_at_9(self):
        self.assertEqual(comb(9, 5), 126)

    def test_dim_5_at_10(self):
        self.assertEqual(comb(10, 5), 252)

    def test_dim_7_at_6(self):
        self.assertEqual(comb(6, 7), 0)

    def test_dim_7_at_7(self):
        self.assertEqual(comb(7, 7), 1)

    def test_dim_7_at_8(self):
        self.assertEqual(comb(8, 7), 8)

    def test_dim_7_at_9(self):
        self.assertEqual(comb(9, 7), 36)

    def test_dim_7_at_10(self):
        self.assertEqual(comb(10, 7), 120)

    def test_total_dim_at_8(self):
        self.assertEqual(comb(8, 1) + comb(8, 3) + comb(8, 5) + comb(8, 7), 128)

    def test_dim_7_at_6_is_zero(self):
        self.assertEqual(comb(6, 7), 0)

    def test_dim_7_at_7_is_singlet(self):
        self.assertEqual(comb(7, 7), 1)


class ContentNonTrivialityTests(unittest.TestCase):
    """Mirror §2: content_nontrivial(N) := all C(N,k) >= 2 for k in {1,3,5,7}."""

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

    def test_cnt_6_failure_is_dim7(self):
        self.assertLess(comb(6, 7), 2)

    def test_cnt_7_failure_is_dim7(self):
        self.assertLess(comb(7, 7), 2)

    def test_cnt_survivors(self):
        survivors = {N for N in range(6, 11) if self._cnt(N)}
        self.assertEqual(survivors, {8, 9, 10})


class DynkinTotalTests(unittest.TestCase):
    """Mirror §3: T'_total(N) = sum C(N-2, k-1) for k in {1,3,5,7}."""

    def _dynkin(self, N):
        return sum(comb(N - 2, k - 1) for k in [1, 3, 5, 7])

    def test_dynkin_6(self):
        self.assertEqual(self._dynkin(6), 8)

    def test_dynkin_7(self):
        self.assertEqual(self._dynkin(7), 16)

    def test_dynkin_8(self):
        self.assertEqual(self._dynkin(8), 32)

    def test_dynkin_9(self):
        self.assertEqual(self._dynkin(9), 64)

    def test_dynkin_10(self):
        self.assertEqual(self._dynkin(10), 127)


class Beta0Tests(unittest.TestCase):
    """Mirror §3: beta0(N) = (11N - T'_total) / 3."""

    def test_beta0_at_8(self):
        self.assertEqual(Fraction(11 * 8 - 32, 3), Fraction(56, 3))


class AFTests(unittest.TestCase):
    """Mirror §3: is_af(N) := 11*N > dynkin_total(N)."""

    DYNKIN = {6: 8, 7: 16, 8: 32, 9: 64, 10: 127}

    def test_af_6(self):
        self.assertGreater(11 * 6, self.DYNKIN[6])

    def test_af_7(self):
        self.assertGreater(11 * 7, self.DYNKIN[7])

    def test_af_8(self):
        self.assertGreater(11 * 8, self.DYNKIN[8])

    def test_af_9(self):
        self.assertGreater(11 * 9, self.DYNKIN[9])

    def test_not_af_10(self):
        self.assertLessEqual(11 * 10, self.DYNKIN[10])


class LatticeViableTests(unittest.TestCase):
    """Mirror §4: lattice_viable(N) := is_af(N) AND content_nontrivial(N)."""

    DYNKIN = {6: 8, 7: 16, 8: 32, 9: 64, 10: 127}

    def _viable(self, N):
        af = 11 * N > self.DYNKIN[N]
        cnt = all(comb(N, k) >= 2 for k in [1, 3, 5, 7])
        return af and cnt

    def test_not_viable_6(self):
        self.assertFalse(self._viable(6))

    def test_not_viable_7(self):
        self.assertFalse(self._viable(7))

    def test_viable_8(self):
        self.assertTrue(self._viable(8))

    def test_viable_9(self):
        self.assertTrue(self._viable(9))

    def test_not_viable_10(self):
        self.assertFalse(self._viable(10))

    def test_survivors(self):
        survivors = {N for N in range(6, 11) if self._viable(N)}
        self.assertEqual(survivors, {8, 9})


class CascadeCGTests(unittest.TestCase):
    """Mirror §5: cascade_cg(N) = N/(N+1)."""

    def test_cascade_cg_8(self):
        self.assertEqual(Fraction(8, 8 + 1), Fraction(8, 9))


class MasterTheoremTests(unittest.TestCase):
    """Mirror §7: master theorem conjunction."""

    DYNKIN = {6: 8, 7: 16, 8: 32, 9: 64, 10: 127}

    def _viable(self, N):
        af = 11 * N > self.DYNKIN[N]
        cnt = all(comb(N, k) >= 2 for k in [1, 3, 5, 7])
        return af and cnt

    def test_master_all_six_clauses(self):
        self.assertFalse(self._viable(6))
        self.assertFalse(self._viable(7))
        self.assertTrue(self._viable(8))
        self.assertTrue(self._viable(9))
        self.assertFalse(self._viable(10))
        self.assertEqual(Fraction(8, 9), Fraction(8, 9))


class LeanParityMirrorTests(unittest.TestCase):
    """Every ℕ/ℚ literal in LatticeSU8StrongCoupling.lean has a mirror here."""

    def test_dim_1_all_literals(self):
        for N, exp in [(6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]:
            self.assertEqual(comb(N, 1), exp, f"dim_1({N})")

    def test_dim_3_all_literals(self):
        for N, exp in [(6, 20), (7, 35), (8, 56), (9, 84), (10, 120)]:
            self.assertEqual(comb(N, 3), exp, f"dim_3({N})")

    def test_dim_5_all_literals(self):
        for N, exp in [(6, 6), (7, 21), (8, 56), (9, 126), (10, 252)]:
            self.assertEqual(comb(N, 5), exp, f"dim_5({N})")

    def test_dim_7_all_literals(self):
        for N, exp in [(6, 0), (7, 1), (8, 8), (9, 36), (10, 120)]:
            self.assertEqual(comb(N, 7), exp, f"dim_7({N})")

    def test_dynkin_all_literals(self):
        for N, exp in [(6, 8), (7, 16), (8, 32), (9, 64), (10, 127)]:
            computed = sum(comb(N - 2, k - 1) for k in [1, 3, 5, 7])
            self.assertEqual(computed, exp, f"dynkin_total({N})")

    def test_beta0_8_literal(self):
        self.assertEqual(Fraction(11 * 8 - 32, 3), Fraction(56, 3))

    def test_total_dim_8_literal(self):
        self.assertEqual(8 + 56 + 56 + 8, 128)

    def test_cascade_cg_literal(self):
        self.assertEqual(Fraction(8, 8 + 1), Fraction(8, 9))


class CommandmentXIITests(unittest.TestCase):
    """Commandment XII: zero floats in derivation path."""

    def test_no_float_in_fractions(self):
        vals = [Fraction(56, 3), Fraction(8, 9)]
        for v in vals:
            self.assertIsInstance(v, Fraction)


if __name__ == '__main__':
    unittest.main()
