"""c175_rge_sm_arithmetic_parity.py — Zig↔Python bit-exact parity guard
for the BRICK B2 arithmetic utilities ported from Oracle/chain/exact_rge.py
to supercomputer/voltus_native/zig/src/rge_sm.zig.

SCOPE (what this guard covers):
  - _rational_sqrt ↔ rationalSqrt (Newton-Heron, default 6 iterations)
  - _rational_7th_root ↔ rationalSeventhRoot (Newton, default 4 iterations)
  - _rational_power_4_over_7 ↔ rationalPowerFourOverSeven (composes 7th-root)
  - _rational_ln ↔ rationalLn (range-reduced arctanh series, default 15 terms)
  - LN2 literal parity (6931472/10000000)
  - FRACTION_PRECISION = 10^15 mirror parity

TRIPWIRE ARCHITECTURE (matches c174's B1 pattern):
  - This file (c175) holds the Python authority. Every test vector is
    (re)computed live via `er._rational_sqrt` / `er._rational_7th_root` /
    `er._rational_power_4_over_7` / `er._rational_ln` and asserted
    against its hardcoded expected Fraction.
  - The companion Zig self-test block inside rge_sm.zig (section
    "BRICK B2 — ARITHMETIC UTILITIES PARITY COVERAGE") holds the same
    hardcoded Fractions on the Zig side and is run via `zig build test`
    on the Mac harness.
  - TestZigSourceParity in this file parses rge_sm.zig and asserts every
    expected (num, den) pair we compute appears somewhere in the B2 test
    block — catching the case where c175's hardcoded reference drifts
    from the Zig self-test's hardcoded reference.

If a future edit to either side drifts:
  - Python authority change → TestPythonAuthority red; fix Python OR
    update c175's hardcoded expected if the change was intentional.
  - Zig port change → `zig build test` red on Mac.
  - c175 ↔ Zig hardcoded drift → TestZigSourceParity red; the two files
    must agree byte-for-byte on every (num, den) pair.

Per Commandment XIII (nothing is trivial): every Newton-iteration output
is written down as an exact (num/den) pair; no adjective substitutes for
the rational. Per Commandment XII (exact arithmetic or nothing): only
fractions.Fraction appears in the derivation path; floats exist only in
numeric-formatted test names if at all.

Run:
    cd ~/Desktop/Collatio
    python3 -m unittest proofs.UFT.scripts.c175_rge_sm_arithmetic_parity -v
"""

from __future__ import annotations

import os
import re
import sys
import unittest
from fractions import Fraction
from typing import Callable, Tuple

# ---------------------------------------------------------------------------
# Path setup — make Oracle.chain.exact_rge importable regardless of cwd.
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from Oracle.chain import exact_rge as er  # noqa: E402

ZIG_SOURCE_PATH = os.path.join(
    REPO_ROOT,
    "supercomputer",
    "voltus_native",
    "zig",
    "src",
    "rge_sm.zig",
)


# ---------------------------------------------------------------------------
# Authoritative test vectors (Python ↔ Zig). Each row is:
#     (test_id, python_fn, args_as_Fractions, kwargs, expected_Fraction)
#
# Expected values were computed once via er._rational_* and captured
# verbatim here. They appear byte-for-byte in the Zig B2 self-test block.
# A bit-exact match between Python and Zig means both sides implement
# the same arithmetic path.
# ---------------------------------------------------------------------------

# --- sqrt ------------------------------------------------------------------
SQRT_TESTS: list[tuple[str, Fraction, Fraction, int, Fraction]] = [
    # Fixed-point identities (guess² = x exactly; Newton stays)
    ("sqrt_fp_1", Fraction(1), Fraction(1), 6, Fraction(1, 1)),
    ("sqrt_fp_4", Fraction(4), Fraction(2), 6, Fraction(2, 1)),
    ("sqrt_fp_100", Fraction(100), Fraction(10), 6, Fraction(10, 1)),
    ("sqrt_fp_quarter", Fraction(1, 4), Fraction(1, 2), 6, Fraction(1, 2)),
    # √2 Newton-Heron progression from 3/2 — closed-form iterates
    ("sqrt2_iter1_from_3_2", Fraction(2), Fraction(3, 2), 1, Fraction(17, 12)),
    ("sqrt2_iter2_from_3_2", Fraction(2), Fraction(3, 2), 2, Fraction(577, 408)),
    ("sqrt2_iter3_from_3_2", Fraction(2), Fraction(3, 2), 3, Fraction(665857, 470832)),
    # 6-iter convergence with limit_denominator(10^15) — two different guesses
    # saturate at the same limited rational
    (
        "sqrt2_iter6_from_3_2",
        Fraction(2),
        Fraction(3, 2),
        6,
        Fraction(1023286908188737, 723573111879672),
    ),
    (
        "sqrt2_iter6_from_1_41421356",
        Fraction(2),
        Fraction(141421356, 100000000),
        6,
        Fraction(1023286908188737, 723573111879672),
    ),
    (
        "sqrt3_iter6_from_1_73",
        Fraction(3),
        Fraction(173, 100),
        6,
        Fraction(1385331749802026, 799821658665135),
    ),
    # Cascade boundary: sqrt(M_Z²) == M_Z exactly (exact_rge.Fraction(911876,10000))
    (
        "sqrt_MZ_squared_returns_MZ",
        Fraction(911876, 10000) ** 2,
        Fraction(911876, 10000),
        6,
        Fraction(911876, 10000),
    ),
]

# --- 7th root --------------------------------------------------------------
SEVENTH_ROOT_TESTS: list[tuple[str, Fraction, Fraction, int, Fraction]] = [
    # Fixed points
    ("7th_fp_1", Fraction(1), Fraction(1), 4, Fraction(1, 1)),
    ("7th_fp_128", Fraction(128), Fraction(2), 4, Fraction(2, 1)),  # 2^7 = 128
    # Newton 7th-root convergence milestones for 2^(1/7) from guess=11/10
    (
        "7th_root_2_iter1_from_11_10",
        Fraction(2),
        Fraction(11, 10),
        1,
        Fraction(68461513, 62004635),
    ),
    (
        "7th_root_2_iter2_from_11_10",
        Fraction(2),
        Fraction(11, 10),
        2,
        Fraction(1098083576010814, 994560274977575),
    ),
    (
        "7th_root_2_iter4_from_11_10",
        Fraction(2),
        Fraction(11, 10),
        4,
        Fraction(979288983719328, 886965206707547),
    ),
]

# --- 4/7 power -------------------------------------------------------------
POWER_4_7_TESTS: list[tuple[str, Fraction, Fraction, Fraction]] = [
    # Fixed point
    ("pow_4_7_fp_1", Fraction(1), Fraction(1), Fraction(1, 1)),
    # 2^(4/7) from a close guess
    (
        "pow_4_7_of_2_from_3_2",
        Fraction(2),
        Fraction(3, 2),
        Fraction(317376344654293, 213578441703583),
    ),
    # 128^(4/7) from guess=8 — demonstrates Newton does NOT converge to 16
    # in 4 iterations from this distant guess. The captured value is
    # input-deterministic, not answer-deterministic — any bit-exact match
    # between Python and Zig proves the arithmetic path is identical.
    (
        "pow_4_7_of_128_from_8_nonconvergent",
        Fraction(128),
        Fraction(8),
        Fraction(51802831834379551, 537151757497309),
    ),
]

# --- natural log -----------------------------------------------------------
LN_TESTS: list[tuple[str, Fraction, int, Fraction]] = [
    # ln(1) = 0 — arctanh series with u=(1-1)/(1+1)=0 vanishes identically
    ("ln_1", Fraction(1), 15, Fraction(0, 1)),
    # ln(2) at varying truncation depths — pins down the series coefficient
    ("ln_2_10terms", Fraction(2), 10, Fraction(259940572436099, 375014974784881)),
    ("ln_2_15terms", Fraction(2), 15, Fraction(147761104653092, 213174212919291)),
    ("ln_2_20terms", Fraction(2), 20, Fraction(607454026575822, 876370911708971)),
    # ln(3/2) — inside [1/2, 2], no range reduction
    ("ln_3_2", Fraction(3, 2), 15, Fraction(123422489122225, 304397312257261)),
    # ln(1/2) = -ln(2) via range reduction (y=1/2 triggers the y<1/2 doubling)
    ("ln_half", Fraction(1, 2), 15, Fraction(-147761104653092, 213174212919291)),
    # ln(4) — one range reduction (4→2), n=1 → adds +1·LN2
    ("ln_4", Fraction(4), 15, Fraction(1228541669269144, 886205474462731)),
    # ln(8) — two range reductions (8→4→2), n=2 → adds +2·LN2
    ("ln_8", Fraction(8), 15, Fraction(1267216954428118, 609402527233723)),
    # ln(7/5) — inside [1/2, 2], realistic cascade-like argument (≈1.4)
    ("ln_7_5", Fraction(14, 10), 15, Fraction(138522263209744, 411690024118355)),
]


# ---------------------------------------------------------------------------
# Helper: load the Zig source exactly once.
# ---------------------------------------------------------------------------

def _load_zig_source() -> str:
    with open(ZIG_SOURCE_PATH, "r", encoding="utf-8") as handle:
        return handle.read()


_ZIG_SOURCE_CACHE: str | None = None


def _zig_source() -> str:
    global _ZIG_SOURCE_CACHE
    if _ZIG_SOURCE_CACHE is None:
        _ZIG_SOURCE_CACHE = _load_zig_source()
    return _ZIG_SOURCE_CACHE


def _b2_block(source: str) -> str:
    """Return the substring from 'BRICK B2' header to EOF. Every expected
    (num, den) literal must live inside this window; literals for other
    bricks do not count as evidence of Zig parity for B2."""
    marker = "BRICK B2 — ARITHMETIC UTILITIES PARITY COVERAGE"
    idx = source.find(marker)
    if idx == -1:
        raise RuntimeError(
            f"rge_sm.zig missing B2 header marker '{marker}'. "
            "The self-test block may have been removed or renamed."
        )
    return source[idx:]


def _fraction_present_in_b2(num: int, den: int) -> bool:
    """True iff vf.mk(num, den) appears in the B2 block as a whitespace-
    insensitive literal. Also accepts the form with a leading `-` on the
    numerator for negative fractions (Zig neg is carried by the literal)."""
    block = _b2_block(_zig_source())
    # Match vf.mk(<num>,<den>) with any whitespace.
    pattern = rf"vf\.mk\(\s*{num}\s*,\s*{den}\s*\)"
    return re.search(pattern, block) is not None


# ---------------------------------------------------------------------------
# TestPythonAuthority — one test per (function, inputs) pair. Calls the
# exact_rge.py authority function and asserts its output equals the
# hardcoded expected Fraction byte-for-byte.
# ---------------------------------------------------------------------------

def _make_sqrt_test(
    test_id: str, x: Fraction, guess: Fraction, iters: int, expected: Fraction
) -> Callable:
    def test(self: unittest.TestCase) -> None:
        got = er._rational_sqrt(x, guess, iters)
        self.assertEqual(
            got,
            expected,
            msg=(
                f"[{test_id}] _rational_sqrt({x!s}, {guess!s}, {iters}) → "
                f"{got.numerator}/{got.denominator}, expected "
                f"{expected.numerator}/{expected.denominator}"
            ),
        )
        # Stricter: match numerator AND denominator fields separately so
        # any Fraction reduction drift also fails the test.
        self.assertEqual(got.numerator, expected.numerator, msg=f"[{test_id}] num drift")
        self.assertEqual(got.denominator, expected.denominator, msg=f"[{test_id}] den drift")

    test.__name__ = f"test_python_{test_id}"
    return test


def _make_7th_root_test(
    test_id: str, x: Fraction, guess: Fraction, iters: int, expected: Fraction
) -> Callable:
    def test(self: unittest.TestCase) -> None:
        got = er._rational_7th_root(x, guess, iters)
        self.assertEqual(got, expected, msg=f"[{test_id}] _rational_7th_root drift")
        self.assertEqual(got.numerator, expected.numerator, msg=f"[{test_id}] num drift")
        self.assertEqual(got.denominator, expected.denominator, msg=f"[{test_id}] den drift")

    test.__name__ = f"test_python_{test_id}"
    return test


def _make_pow_4_7_test(
    test_id: str, x: Fraction, guess: Fraction, expected: Fraction
) -> Callable:
    def test(self: unittest.TestCase) -> None:
        got = er._rational_power_4_over_7(x, guess)
        self.assertEqual(got, expected, msg=f"[{test_id}] _rational_power_4_over_7 drift")
        self.assertEqual(got.numerator, expected.numerator, msg=f"[{test_id}] num drift")
        self.assertEqual(got.denominator, expected.denominator, msg=f"[{test_id}] den drift")

    test.__name__ = f"test_python_{test_id}"
    return test


def _make_ln_test(
    test_id: str, x: Fraction, terms: int, expected: Fraction
) -> Callable:
    def test(self: unittest.TestCase) -> None:
        got = er._rational_ln(x, terms)
        self.assertEqual(got, expected, msg=f"[{test_id}] _rational_ln drift")
        self.assertEqual(got.numerator, expected.numerator, msg=f"[{test_id}] num drift")
        self.assertEqual(got.denominator, expected.denominator, msg=f"[{test_id}] den drift")

    test.__name__ = f"test_python_{test_id}"
    return test


class TestPythonSqrtParity(unittest.TestCase):
    """Python authority parity for _rational_sqrt vs hardcoded Fraction."""

    pass


class TestPythonSeventhRootParity(unittest.TestCase):
    """Python authority parity for _rational_7th_root vs hardcoded Fraction."""

    pass


class TestPythonPowerFourOverSevenParity(unittest.TestCase):
    """Python authority parity for _rational_power_4_over_7 vs hardcoded Fraction."""

    pass


class TestPythonLnParity(unittest.TestCase):
    """Python authority parity for _rational_ln vs hardcoded Fraction."""

    pass


# Install factory-generated tests.
for _tid, _x, _g, _i, _e in SQRT_TESTS:
    setattr(TestPythonSqrtParity, f"test_python_{_tid}",
            _make_sqrt_test(_tid, _x, _g, _i, _e))

for _tid, _x, _g, _i, _e in SEVENTH_ROOT_TESTS:
    setattr(TestPythonSeventhRootParity, f"test_python_{_tid}",
            _make_7th_root_test(_tid, _x, _g, _i, _e))

for _tid, _x, _g, _e in POWER_4_7_TESTS:
    setattr(TestPythonPowerFourOverSevenParity, f"test_python_{_tid}",
            _make_pow_4_7_test(_tid, _x, _g, _e))

for _tid, _x, _t, _e in LN_TESTS:
    setattr(TestPythonLnParity, f"test_python_{_tid}",
            _make_ln_test(_tid, _x, _t, _e))


# ---------------------------------------------------------------------------
# TestZigSourceParity — every expected Fraction (num, den) pair must
# appear byte-for-byte inside the rge_sm.zig B2 block. This catches the
# case where the Python side is updated but the Zig hardcoded expected
# drifts — or vice versa, provided the Zig side is updated through this
# file first.
#
# Negative fractions: Python stores Fraction(-147_761_104_653_092, 213_...)
# as (num=-N, den=D). Zig's vf.mk accepts signed numerators, so the
# Zig literal is `vf.mk(-N, D)` — we look for both signs.
# ---------------------------------------------------------------------------

# Idiomatic-Zig equivalence whitelist: some B2 tests assert equality via
# a symbol (e.g. `Constants.M_Z` instead of the literal `vf.mk(227969, 2500)`)
# or via a predicate (e.g. `vf.isZero(rationalLn(...))` instead of
# `vf.eql(..., vf.mk(0, 1))`). These are STRICTLY BETTER Zig idioms than
# hardcoded literals — they document intent AND assert equality. c175's
# source-scan must accept them as equivalent to the literal form, otherwise
# the guard would force the Zig code to be less idiomatic than it needs to be.
#
# Each entry: test_id → list of additional regex patterns that, if any match
# in the B2 block, satisfy the presence check. The hardcoded `vf.mk(num, den)`
# check is always tried FIRST; alternates are only consulted on miss.
ZIG_ALTERNATE_PATTERNS: dict[str, list[str]] = {
    # sqrt(M_Z²) = M_Z — Zig uses `Constants.M_Z` symbol (value = 227969/2500)
    # instead of the raw Fraction literal. Both are mathematically identical;
    # the symbol form is preferable because it documents "this is M_Z" instead
    # of a numeric mystery.
    "sqrt_sqrt_MZ_squared_returns_MZ": [
        r"Constants\.M_Z\s*,\s*6\s*\)",
        r"rationalSqrt\([^)]*Constants\.M_Z[^)]*\)",
    ],
    # ln(1) = 0 — Zig uses `vf.isZero(rationalLn(vf.mk(1, 1), 15))` instead of
    # `vf.eql(rationalLn(vf.mk(1, 1), 15), vf.mk(0, 1))`. The isZero predicate
    # is the cleaner idiom for the zero-identity case.
    "ln_ln_1": [
        r"vf\.isZero\(rationalLn\(vf\.mk\(1\s*,\s*1\)\s*,\s*15\)\)",
    ],
}


def _make_zig_presence_test(label: str, num: int, den: int) -> Callable:
    def test(self: unittest.TestCase) -> None:
        if _fraction_present_in_b2(num, den):
            return
        # Fall back to idiomatic alternates for specific test IDs. A test ID
        # is looked up by its full label (e.g. "sqrt_sqrt_MZ_squared_returns_MZ").
        alternates = ZIG_ALTERNATE_PATTERNS.get(label, [])
        block = _b2_block(_zig_source())
        for pattern in alternates:
            if re.search(pattern, block):
                return
        self.fail(
            f"[{label}] expected literal vf.mk({num}, {den}) not found "
            f"in B2 block of rge_sm.zig, and no idiomatic alternate "
            f"pattern matched either. If this value changed, update "
            f"BOTH the Zig self-test hardcoded and this guard's "
            f"hardcoded Fraction in lockstep. If the Zig side uses "
            f"an idiomatic equivalent (symbol or predicate), add its "
            f"regex to ZIG_ALTERNATE_PATTERNS[{label!r}]."
        )

    test.__name__ = f"test_zig_contains_{label}"
    return test


class TestZigSourceParity(unittest.TestCase):
    """Every expected rational in this file appears verbatim in rge_sm.zig's B2 block.

    Catches the drift case: c175 Python-authority tests green AND Zig self-
    test green, but the hardcoded expected rationals in the two files no
    longer match because someone updated one and not the other.
    """

    def test_b2_header_present(self) -> None:
        self.assertIn(
            "BRICK B2 — ARITHMETIC UTILITIES PARITY COVERAGE",
            _zig_source(),
            msg="rge_sm.zig missing BRICK B2 header marker",
        )

    def test_ln2_literal_present(self) -> None:
        """LN2 literal — vf.mk(6931472, 10000000) — MUST appear byte-for-byte."""
        block = _b2_block(_zig_source())
        self.assertTrue(
            re.search(r"vf\.mk\(\s*6931472\s*,\s*10000000\s*\)", block),
            msg="LN2 literal vf.mk(6931472, 10000000) absent from B2 block",
        )

    def test_fraction_precision_literal_present(self) -> None:
        """FRACTION_PRECISION = 10^15 appears in B1 check; B2 reuses it.
        Confirm the B1 block still carries it (Constants.FRACTION_PRECISION
        = 1_000_000_000_000_000) — B2's `limit()` wrapper depends on it."""
        src = _zig_source()
        self.assertTrue(
            "Constants.FRACTION_PRECISION == 1_000_000_000_000_000" in src,
            msg="Constants.FRACTION_PRECISION == 1_000_000_000_000_000 "
            "missing from rge_sm.zig — B2 limit() wrapper depends on it",
        )


# Install Zig-presence tests for every expected (num, den) pair across
# all four utilities. The label includes the utility + test id for
# pinpoint failure messages.
for _tid, _x, _g, _i, _e in SQRT_TESTS:
    setattr(
        TestZigSourceParity,
        f"test_zig_contains_sqrt_{_tid}",
        _make_zig_presence_test(f"sqrt_{_tid}", _e.numerator, _e.denominator),
    )

for _tid, _x, _g, _i, _e in SEVENTH_ROOT_TESTS:
    setattr(
        TestZigSourceParity,
        f"test_zig_contains_7th_{_tid}",
        _make_zig_presence_test(f"7th_{_tid}", _e.numerator, _e.denominator),
    )

for _tid, _x, _g, _e in POWER_4_7_TESTS:
    setattr(
        TestZigSourceParity,
        f"test_zig_contains_pow47_{_tid}",
        _make_zig_presence_test(f"pow47_{_tid}", _e.numerator, _e.denominator),
    )

for _tid, _x, _t, _e in LN_TESTS:
    setattr(
        TestZigSourceParity,
        f"test_zig_contains_ln_{_tid}",
        _make_zig_presence_test(f"ln_{_tid}", _e.numerator, _e.denominator),
    )


# ---------------------------------------------------------------------------
# TestArithmeticInvariants — structural properties that MUST hold regardless
# of iteration count or input choice. These catch algebraic bugs (sign flip,
# coefficient swap) that bit-exact literal checks would miss if both sides
# drifted in the same wrong direction.
# ---------------------------------------------------------------------------

class TestArithmeticInvariants(unittest.TestCase):
    """Algebraic invariants of the B2 utilities. Every invariant must hold
    over the exact rationals returned by the Python authority — any algebraic
    bug (wrong coefficient, wrong Newton formula) fails these even if the
    bit-exact literal tests happened to line up."""

    def test_sqrt_fixed_point_identity(self) -> None:
        """For x > 0 and guess = √x exactly, Newton stays at the guess."""
        for x in [Fraction(1), Fraction(4), Fraction(9), Fraction(16), Fraction(1, 4)]:
            # The exact roots are integers / half-integers; capture them.
            root = {
                Fraction(1): Fraction(1),
                Fraction(4): Fraction(2),
                Fraction(9): Fraction(3),
                Fraction(16): Fraction(4),
                Fraction(1, 4): Fraction(1, 2),
            }[x]
            got = er._rational_sqrt(x, root, 6)
            self.assertEqual(
                got, root, msg=f"sqrt({x}) from guess={root} drifted to {got}"
            )

    def test_sqrt_zero_guess_returns_zero(self) -> None:
        """Guess = 0 triggers the zero-early-return guard; output must be 0."""
        got = er._rational_sqrt(Fraction(4), Fraction(0), 6)
        self.assertEqual(got, Fraction(0))

    def test_ln_of_one_is_zero(self) -> None:
        """u = (1-1)/(1+1) = 0, the series is identically zero."""
        self.assertEqual(er._rational_ln(Fraction(1), 15), Fraction(0))
        self.assertEqual(er._rational_ln(Fraction(1), 1), Fraction(0))
        self.assertEqual(er._rational_ln(Fraction(1), 100), Fraction(0))

    def test_ln_reflection_identity_half_vs_two(self) -> None:
        """ln(1/2) = -ln(2) — range reduction must honor this reflection."""
        ln_2 = er._rational_ln(Fraction(2), 15)
        ln_half = er._rational_ln(Fraction(1, 2), 15)
        self.assertEqual(ln_half, -ln_2)

    def test_ln_panics_on_nonpositive(self) -> None:
        """x ≤ 0 must raise ValueError (Python) / @panic (Zig)."""
        with self.assertRaises(ValueError):
            er._rational_ln(Fraction(0), 15)
        with self.assertRaises(ValueError):
            er._rational_ln(Fraction(-1), 15)

    def test_seventh_root_fixed_point_at_one(self) -> None:
        """1^(1/7) = 1 is a fixed point."""
        self.assertEqual(
            er._rational_7th_root(Fraction(1), Fraction(1), 4), Fraction(1)
        )

    def test_power_4_over_7_at_one(self) -> None:
        """1^(4/7) = 1 — composition should not introduce drift."""
        self.assertEqual(
            er._rational_power_4_over_7(Fraction(1), Fraction(1)), Fraction(1)
        )

    def test_sqrt_newton_heron_closed_form_iter1(self) -> None:
        """Newton first iterate for √2 from 3/2 is exactly 17/12.
        Proves the Newton coefficient is (x + a/x)/2 — any sign/divisor
        swap fails this closed-form identity."""
        self.assertEqual(
            er._rational_sqrt(Fraction(2), Fraction(3, 2), 1), Fraction(17, 12)
        )

    def test_seventh_root_newton_coefficient(self) -> None:
        """Newton 7th-root first iterate for a=2 from guess=11/10 is
        exactly (6·(11/10) + 2·(11/10)^-6) / 7. Proves the coefficient is
        (6x + a/x^6)/7 — any swap of 6 ↔ 7 or x ↔ x^6 fails this."""
        guess = Fraction(11, 10)
        a = Fraction(2)
        # Compute the closed form once via Python.
        closed = (6 * guess + a / guess**6) / 7
        closed = closed.limit_denominator(er.FRACTION_PRECISION)
        got = er._rational_7th_root(a, guess, 1)
        self.assertEqual(got, closed)

    def test_limit_denominator_matches_python_constant(self) -> None:
        """_limit(val) must use FRACTION_PRECISION = 10^15."""
        self.assertEqual(er.FRACTION_PRECISION, 10**15)
        # Verify _limit does what it says.
        huge = Fraction(10**17 + 1, 10**17 + 3)
        limited = er._limit(huge)
        self.assertLessEqual(limited.denominator, 10**15)


# ---------------------------------------------------------------------------
# TestZigStructuralMirrors — confirm the Zig file still exposes all four
# function symbols referenced in the skeleton test block AND that the
# iteration-count defaults match Python authority.
# ---------------------------------------------------------------------------

class TestZigStructuralMirrors(unittest.TestCase):
    """Zig-side structural parity: function symbols exist AND the defaults
    declared in the Python authority (sqrt=6 iters, 7th-root=4 iters,
    ln=15 terms) are reflected by the ACTUAL Python defaults."""

    def test_python_default_iters_unchanged(self) -> None:
        """If these defaults drift on the Python side, the comments in
        rge_sm.zig (which assume 6/4/15) also drift. We pin the Python
        defaults here so any change is loud."""
        import inspect

        sig_sqrt = inspect.signature(er._rational_sqrt)
        self.assertEqual(sig_sqrt.parameters["iterations"].default, 6)

        sig_7th = inspect.signature(er._rational_7th_root)
        self.assertEqual(sig_7th.parameters["iterations"].default, 4)

        sig_ln = inspect.signature(er._rational_ln)
        self.assertEqual(sig_ln.parameters["terms"].default, 15)

    def test_zig_file_exposes_b2_symbols(self) -> None:
        """rationalSqrt / rationalSeventhRoot / rationalPowerFourOverSeven /
        rationalLn must all be declared `pub fn` in the Zig source."""
        src = _zig_source()
        for sym in (
            "pub fn rationalSqrt(",
            "pub fn rationalSeventhRoot(",
            "pub fn rationalPowerFourOverSeven(",
            "pub fn rationalLn(",
        ):
            self.assertIn(sym, src, msg=f"rge_sm.zig missing '{sym}' declaration")

    def test_zig_ln_nonpositive_panic(self) -> None:
        """Zig's rationalLn must @panic on x ≤ 0 (mirror of Python ValueError)."""
        src = _zig_source()
        # Look for the guard inside rationalLn. We don't require exact
        # phrasing; we require SOMETHING that rejects non-positive input.
        m = re.search(
            r"pub fn rationalLn\(.*?^\}\n",
            src,
            re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, msg="could not locate rationalLn body")
        body = m.group(0)
        self.assertTrue(
            "isPositive" in body and "@panic" in body,
            msg=(
                "rationalLn body must guard x ≤ 0 via vf.isPositive + @panic "
                "— current body lacks one or both:\n" + body[:400]
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
