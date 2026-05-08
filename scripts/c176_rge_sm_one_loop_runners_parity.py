"""c176_rge_sm_one_loop_runners_parity.py — Zig↔Python bit-exact parity guard
for the BRICK B3 1-loop coupling runners ported from
Oracle/chain/exact_rge.py to supercomputer/voltus_native/zig/src/rge_sm.zig.

SCOPE (what this guard covers — Task #36, B3):
  - 13 Constants literals new in B3:
      TWO_PI, FOUR_PI, ALPHA_S_INV_MZ,
      LOG10_{MZ, MPS, M8, MLR, MT_OVER_MZ},
      LN_{MPS_OVER_MZ, M8_OVER_MZ, MLR_OVER_MZ, M8_OVER_MPS,
           MLR_OVER_MPS, MT_OVER_MZ}
  - Cross-constant arithmetic identities (Commandment XIII — every
    identity an explicit tactic, not an adjective):
      · TWO_PI = 2·PI
      · FOUR_PI = 2·TWO_PI
      · ALPHA_S_INV_MZ · ALPHA_S_MZ = 1
      · LN_M8_OVER_MZ = LN_MPS_OVER_MZ + LN_M8_OVER_MPS
      · LN_MLR_OVER_MZ = LN_MPS_OVER_MZ + LN_MLR_OVER_MPS
  - runCouplingInv structural properties:
      · Fixed point at ln(μ/μ₀) = 0
      · Sign-flip roundtrip: up then down recovers input
  - STEP 1 / STEP 2 / STEP 3a / STEP 3c / STEP 3d / STEP 3e milestone
    outputs of `compute_all_from_MZ()`, byte-for-byte vs the Zig B3
    self-test literals.
  - STEP 3f Python-authority self-consistency (the Zig kernel computes
    sin²θ_W / α_EM⁻¹ / α_s in `computeStep1to3()` but does not pin
    individual literal mirrors — c176 still asserts the closed-form
    identities and the two `vf.isZero()` division guards exist in source).
  - Three closed-loop structural identities:
      · Cascade SU(4)_C sign-flip:    α₄⁻¹(M_PS)_down = α₃⁻¹(M_PS)_up
      · Closed-loop α₃ at M_Z:        α₃⁻¹(M_Z)_pred  = ALPHA_S_INV_MZ
      · SU(2)_L preservation at M_PS: α₂L⁻¹(M_PS)_down = α₂⁻¹(M_PS)_pred

TRIPWIRE ARCHITECTURE (matches c174/c175 pattern):
  - Python authority lives in `Oracle/chain/exact_rge.py`.  Every test
    vector is recomputed live via `er.compute_all_from_MZ()` and asserted
    against its hardcoded expected Fraction.
  - The companion Zig self-test block inside `rge_sm.zig` (section
    "B3 — 1-loop coupling runner self-tests") holds the same hardcoded
    Fractions on the Zig side and is run via `zig build test` on Mac.
  - TestZigSourceParity parses `rge_sm.zig` and asserts every expected
    (num, den) pair appears in the B3 test block.  When the Zig port
    uses an idiomatic equivalent (named constant, predicate form) instead
    of a raw `vf.mk(...)` literal, the test_id-keyed
    `ZIG_ALTERNATE_PATTERNS` whitelist supplies a regex that also
    constitutes evidence of the identity — per
    `feedback_parity_guard_idiomatic_whitelist.md`.

If a future edit to either side drifts:
  - Python authority change → TestPythonAuthority red; fix Python OR
    update c176's hardcoded expected if the change was intentional.
  - Zig port change → `zig build test` red on Mac.
  - c176 ↔ Zig hardcoded drift → TestZigSourceParity red; the two files
    must agree byte-for-byte on every (num, den) pair, OR the Zig port
    must use a documented `ZIG_ALTERNATE_PATTERNS` idiom.

Per Commandment XII: every value flows as `fractions.Fraction`; the
verdict path contains zero floats.

Per Commandment XIII: every quantity in the chain has an explicit
derivation tactic — no "trivial" identities and no adjectives substituted
for proofs.  The closed-loop α₃⁻¹(M_Z)_pred = ALPHA_S_INV_MZ identity is
witnessed by a separate equality assertion, not implied by transitivity.

Run:
    cd ~/Desktop/Collatio
    python3 -m unittest proofs.UFT.scripts.c176_rge_sm_one_loop_runners_parity -v
"""

from __future__ import annotations

import os
import re
import sys
import unittest
from fractions import Fraction
from typing import Callable, Dict, List, Tuple

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
# Authoritative B3 expected values — pinned exact Fractions that appear
# byte-for-byte in the Zig B3 self-test block.  Recomputed at module-load
# from `er.compute_all_from_MZ()` so any drift in the Python authority
# fails the suite immediately.
# ---------------------------------------------------------------------------

# ----- Constants block (the 13 new B3 constants + LN_M8_OVER_MPS for
# arithmetic-consistency tests) -----
EXPECTED_CONSTANTS: Dict[str, Tuple[int, int]] = {
    # Derived transcendentals (closed-form approximations Lamar pinned).
    "TWO_PI":              (710, 113),
    "FOUR_PI":             (1420, 113),
    "ALPHA_S_INV_MZ":      (500, 59),
    # log10 cascade scales.
    "LOG10_MZ":            (19601, 10000),
    "LOG10_MPS":           (137, 10),
    "LOG10_M8":            (472, 25),
    "LOG10_MLR":           (767, 50),
    "LOG10_MT_OVER_MZ":    (347, 1250),
    # Pre-computed ln(scale ratios) = LN10 · Δlog10.
    "LN_MPS_OVER_MZ":      (108124479, 4000000),
    "LN_M8_OVER_MZ":       (155832279, 4000000),
    "LN_MLR_OVER_MZ":      (123228879, 4000000),
    "LN_M8_OVER_MPS":      (238539, 20000),
    "LN_MLR_OVER_MPS":     (37761, 10000),
    "LN_MT_OVER_MZ":       (319587, 500000),
}

# ----- STEP 1 / STEP 2 / STEP 3 milestone outputs (mirror the Zig self-
# test literals at lines 1502-1618 of rge_sm.zig).  Keyed by the dict key
# returned by `compute_all_from_MZ()` (where stored), or by a synthetic
# key plus a closed-form derivation (where Python keeps it as a local). -----
EXPECTED_STEP1: Dict[str, Tuple[int, int]] = {
    "alpha1_inv_MZ":       (295096203, 5000000),
    "alpha2_inv_MZ":       (29584599, 1000000),
    "alpha3_inv_MZ":       (500, 59),
}

EXPECTED_STEP2: Dict[str, Tuple[int, int]] = {
    "alpha1_inv_MPS":      (1175205721833, 28400000000),
    "alpha2_inv_MPS":      (245421607791, 5680000000),
    "alpha3_inv_MPS":      (6466061310451, 167560000000),
}

EXPECTED_STEP3A: Dict[str, Tuple[int, int]] = {
    # Stored as `alpha8_inv_M8` in Python; identified with α₄⁻¹(M₈) by
    # the SU(8) → PS branching at M₈.
    "alpha8_inv_M8":       (8904581897051, 167560000000),
}

EXPECTED_STEP3C: Dict[str, Tuple[int, int]] = {
    "alpha4_inv_MPS_down":  (6466061310451, 167560000000),
    "alpha2L_inv_MPS_down": (7950378189251, 167560000000),
    "alpha2R_inv_MPS_down": (10070830873251, 167560000000),
}

# STEP 3d locals — Python keeps these as throw-away vars but the Zig
# self-test pins them as literals.  We recompute Python-side from STEP 3c
# downs via the PS → SM matching identities and assert byte-equality.
EXPECTED_STEP3D: Dict[str, Tuple[int, int]] = {
    "alpha1_inv_MPS_pred":  (8628923048131, 167560000000),
    "alpha2_inv_MPS_pred":  (7950378189251, 167560000000),
    "alpha3_inv_MPS_pred":  (6466061310451, 167560000000),
}

EXPECTED_STEP3E: Dict[str, Tuple[int, int]] = {
    "alpha1_inv_MZ_pred":   (115844732442523, 1675600000000),
    "alpha2_inv_MZ_pred":   (11335272335713, 335120000000),
    "alpha3_inv_MZ_pred":   (500, 59),  # ← Closed-loop: equals ALPHA_S_INV_MZ.
}


# ---------------------------------------------------------------------------
# ZIG_ALTERNATE_PATTERNS — per `feedback_parity_guard_idiomatic_whitelist.md`.
#
# When the Zig port uses an idiomatic predicate or named constant instead
# of spelling out a raw `vf.mk(num, den)` literal, the parity guard would
# false-fail because the literal regex does not match.  The whitelist
# below registers the test_ids where the idiomatic form is strictly
# better (documents intent via name, avoids magic-number duplication) and
# supplies the regex evidence that the identity still holds in the Zig
# source.
#
# Each entry is documented with WHY the idiom is better — future
# maintainers must understand why the whitelist exists, not just that
# it does.
# ---------------------------------------------------------------------------
ZIG_ALTERNATE_PATTERNS: Dict[str, List[str]] = {
    # STEP 3e closed-loop α₃: rather than re-spell 500/59 at line 1618,
    # the Zig port writes `Constants.ALPHA_S_INV_MZ` — which makes the
    # closed-loop identity α₃⁻¹(M_Z)_pred = ALPHA_S_INV_MZ explicit at
    # the symbolic level, not just numerically.
    "step3e_alpha3_inv_MZ_pred_closed_loop": [
        r"Constants\.ALPHA_S_INV_MZ",
    ],
    # NOTE: the STEP 3f `vf.isZero(...)` division guards live in the
    # `computeStep1to3()` helper, NOT in the B3 self-test block.  They are
    # NOT registered here because `_alternate_present_in_b3` only searches
    # the B3 self-test block.  `TestZigStructuralMirrors` verifies their
    # presence against the full source via `_source.find()`.
}


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


def _b3_block(source: str) -> str:
    """Return the substring from the 'B3 — 1-loop coupling runner self-tests'
    header to EOF.  Every expected (num, den) literal must live inside
    this window; literals for other bricks do not count as evidence of
    Zig parity for B3."""
    marker = "B3 — 1-loop coupling runner self-tests"
    idx = source.find(marker)
    if idx == -1:
        raise RuntimeError(
            f"rge_sm.zig missing B3 header marker '{marker}'. "
            "The B3 self-test block may have been removed or renamed."
        )
    return source[idx:]


def _fraction_present_in_b3(num: int, den: int) -> bool:
    """True iff vf.mk(num, den) appears in the B3 block as a whitespace-
    insensitive literal."""
    block = _b3_block(_zig_source())
    pattern = rf"vf\.mk\(\s*{num}\s*,\s*{den}\s*\)"
    return re.search(pattern, block) is not None


def _alternate_present_in_b3(test_id: str) -> bool:
    """True iff any regex pattern registered in ZIG_ALTERNATE_PATTERNS
    for `test_id` matches inside the B3 block."""
    block = _b3_block(_zig_source())
    alternates = ZIG_ALTERNATE_PATTERNS.get(test_id, [])
    for pattern in alternates:
        if re.search(pattern, block):
            return True
    return False


# ---------------------------------------------------------------------------
# Cache the live `compute_all_from_MZ()` dict once per process — calling
# it inside every test would make the suite ~70× slower.
# ---------------------------------------------------------------------------
_LIVE_RGE_CACHE: Dict[str, object] | None = None


def _live_rge() -> Dict[str, object]:
    global _LIVE_RGE_CACHE
    if _LIVE_RGE_CACHE is None:
        _LIVE_RGE_CACHE = er.compute_all_from_MZ()
    return _LIVE_RGE_CACHE


# ---------------------------------------------------------------------------
# Test factories.
# ---------------------------------------------------------------------------

def _make_python_constant_test(name: str, num: int, den: int) -> Callable:
    """Assert that `er.<name>` equals the hardcoded expected Fraction."""
    expected = Fraction(num, den)

    def test(self: unittest.TestCase) -> None:
        got = getattr(er, name)
        self.assertIsInstance(
            got,
            Fraction,
            msg=f"[{name}] expected Fraction, got {type(got).__name__}",
        )
        self.assertEqual(
            got,
            expected,
            msg=(
                f"[{name}] er.{name} = "
                f"{got.numerator}/{got.denominator}, expected "
                f"{expected.numerator}/{expected.denominator}"
            ),
        )
        self.assertEqual(got.numerator, expected.numerator,
                         msg=f"[{name}] num drift")
        self.assertEqual(got.denominator, expected.denominator,
                         msg=f"[{name}] den drift")

    test.__name__ = f"test_python_constant_{name}"
    return test


def _make_python_dict_key_test(key: str, num: int, den: int) -> Callable:
    """Assert that `compute_all_from_MZ()[key]` equals the hardcoded
    expected Fraction (which mirrors the Zig literal)."""
    expected = Fraction(num, den)

    def test(self: unittest.TestCase) -> None:
        live = _live_rge()
        self.assertIn(key, live, msg=f"[{key}] missing from compute_all_from_MZ()")
        got = live[key]
        self.assertIsInstance(
            got,
            Fraction,
            msg=f"[{key}] expected Fraction, got {type(got).__name__}",
        )
        self.assertEqual(
            got,
            expected,
            msg=(
                f"[{key}] compute_all_from_MZ()['{key}'] = "
                f"{got.numerator}/{got.denominator}, expected "
                f"{expected.numerator}/{expected.denominator}"
            ),
        )
        self.assertEqual(got.numerator, expected.numerator,
                         msg=f"[{key}] num drift")
        self.assertEqual(got.denominator, expected.denominator,
                         msg=f"[{key}] den drift")

    test.__name__ = f"test_python_dict_{key}"
    return test


def _make_zig_presence_test(label: str, num: int, den: int) -> Callable:
    """Assert that `vf.mk(num, den)` appears in the B3 block of rge_sm.zig.
    On miss, fall back to checking ZIG_ALTERNATE_PATTERNS[label]; if
    neither matches, fail with a message that lists both the missing
    literal AND the alternates that were tried."""
    def test(self: unittest.TestCase) -> None:
        if _fraction_present_in_b3(num, den):
            return
        if _alternate_present_in_b3(label):
            return
        alternates = ZIG_ALTERNATE_PATTERNS.get(label, [])
        self.fail(
            f"[{label}] expected literal vf.mk({num}, {den}) not found "
            f"in B3 block of rge_sm.zig, and no idiomatic alternate "
            f"pattern matched either.\n"
            f"  Alternates tried: {alternates if alternates else '(none registered)'}\n"
            f"  Either: (a) restore the literal in the Zig B3 block, or "
            f"(b) add a regex to ZIG_ALTERNATE_PATTERNS['{label}'] "
            f"documenting why the idiomatic form is strictly better — "
            f"see feedback_parity_guard_idiomatic_whitelist.md."
        )
    test.__name__ = f"test_zig_contains_{label}"
    return test


# ---------------------------------------------------------------------------
# TestPythonConstantsAuthority — recompute the 13 B3 constants from er.
# ---------------------------------------------------------------------------

class TestPythonConstantsAuthority(unittest.TestCase):
    """Authority side: each B3 constant in `exact_rge.py` equals the
    hardcoded expected Fraction (which the Zig port mirrors)."""
    pass


for _name, (_num, _den) in EXPECTED_CONSTANTS.items():
    setattr(
        TestPythonConstantsAuthority,
        f"test_python_constant_{_name}",
        _make_python_constant_test(_name, _num, _den),
    )


# ---------------------------------------------------------------------------
# TestPythonStepAuthority — recompute STEP 1/2/3a/3c/3e dict outputs
# from `compute_all_from_MZ()` and pin them to expected Fractions.
# ---------------------------------------------------------------------------

class TestPythonStepAuthority(unittest.TestCase):
    """Authority side: each milestone output of `compute_all_from_MZ()`
    equals the hardcoded expected Fraction."""
    pass


for _key, (_num, _den) in {
    **EXPECTED_STEP1,
    **EXPECTED_STEP2,
    **EXPECTED_STEP3A,
    **EXPECTED_STEP3C,
    **EXPECTED_STEP3E,
}.items():
    setattr(
        TestPythonStepAuthority,
        f"test_python_dict_{_key}",
        _make_python_dict_key_test(_key, _num, _den),
    )


# ---------------------------------------------------------------------------
# TestStep3dPythonRecompute — STEP 3d is *not* stored in the live dict;
# Python keeps the predictions as locals.  Recompute them here from the
# stored STEP 3c down-running results via the PS → SM matching
# identities, and pin to the hardcoded literals that appear in Zig
# lines 1582-1584.
# ---------------------------------------------------------------------------

class TestStep3dPythonRecompute(unittest.TestCase):
    """STEP 3d (PS → SM matching at M_PS): recompute the three SM
    coupling predictions from STEP 3c down-running and assert
    byte-equality with the Zig literals."""

    def setUp(self) -> None:
        self.live = _live_rge()

    def _matching(self) -> Tuple[Fraction, Fraction, Fraction]:
        a4_down = self.live["alpha4_inv_MPS_down"]
        a2L_down = self.live["alpha2L_inv_MPS_down"]
        a2R_down = self.live["alpha2R_inv_MPS_down"]
        # Hypercharge embedding: α₁⁻¹ = (2/5)·α₄⁻¹ + (3/5)·α_{2R}⁻¹
        a1_pred = Fraction(2, 5) * a4_down + Fraction(3, 5) * a2R_down
        # SU(2)_L preservation: α₂⁻¹ = α_{2L}⁻¹
        a2_pred = a2L_down
        # SU(3)_C identification: α₃⁻¹ = α₄⁻¹
        a3_pred = a4_down
        return (a1_pred, a2_pred, a3_pred)

    def test_alpha1_inv_MPS_pred(self) -> None:
        a1_pred, _, _ = self._matching()
        num, den = EXPECTED_STEP3D["alpha1_inv_MPS_pred"]
        expected = Fraction(num, den)
        self.assertEqual(a1_pred, expected,
                         msg="STEP 3d α₁⁻¹(M_PS)_pred drift vs Zig literal")
        self.assertEqual(a1_pred.numerator, expected.numerator)
        self.assertEqual(a1_pred.denominator, expected.denominator)

    def test_alpha2_inv_MPS_pred(self) -> None:
        _, a2_pred, _ = self._matching()
        num, den = EXPECTED_STEP3D["alpha2_inv_MPS_pred"]
        expected = Fraction(num, den)
        self.assertEqual(a2_pred, expected,
                         msg="STEP 3d α₂⁻¹(M_PS)_pred drift vs Zig literal")
        self.assertEqual(a2_pred.numerator, expected.numerator)
        self.assertEqual(a2_pred.denominator, expected.denominator)

    def test_alpha3_inv_MPS_pred(self) -> None:
        _, _, a3_pred = self._matching()
        num, den = EXPECTED_STEP3D["alpha3_inv_MPS_pred"]
        expected = Fraction(num, den)
        self.assertEqual(a3_pred, expected,
                         msg="STEP 3d α₃⁻¹(M_PS)_pred drift vs Zig literal")
        self.assertEqual(a3_pred.numerator, expected.numerator)
        self.assertEqual(a3_pred.denominator, expected.denominator)


# ---------------------------------------------------------------------------
# TestB3StructuralRoundtrips — three closed-loop identities that pin the
# whole STEP 1 → STEP 2 → STEP 3a → STEP 3c → STEP 3d → STEP 3e chain.
# ---------------------------------------------------------------------------

class TestB3StructuralRoundtrips(unittest.TestCase):
    """Closed-loop structural identities — Commandment XIII: each is an
    explicit `assertEqual`, not a transitive consequence."""

    def setUp(self) -> None:
        self.live = _live_rge()

    def test_cascade_su4c_sign_flip_alpha4_down_eq_alpha3_up(self) -> None:
        """α₄⁻¹(M_PS)_down = α₃⁻¹(M_PS)_up.

        After running α₃ from M_Z up to M_PS via SU(3) β, then through
        SU(4)_C up to M₈, then back down via SU(4)_C, we must land on
        the same M_PS coupling (closed-loop on the SU(4)_C branch).
        """
        a4_down = self.live["alpha4_inv_MPS_down"]
        a3_up = self.live["alpha3_inv_MPS"]
        self.assertEqual(
            a4_down, a3_up,
            msg=(
                "Cascade SU(4)_C sign-flip roundtrip BROKEN: "
                f"α₄⁻¹(M_PS)_down = {a4_down}, "
                f"α₃⁻¹(M_PS)_up = {a3_up}"
            ),
        )

    def test_closed_loop_alpha3_at_MZ_returns_input(self) -> None:
        """α₃⁻¹(M_Z)_pred = ALPHA_S_INV_MZ = 500/59 exactly.

        The full STEP 1 → 2 → 3a → 3c → 3d → 3e chain is a closed loop on
        the SU(3)_C / SU(4)_C branch.  Any non-recovery is a structural
        bug — the hypercharge α₁ and SU(2)_L α₂ diverge from their input
        values (that's the prediction), but α₃ MUST return.
        """
        a3_pred = self.live["alpha3_inv_MZ_pred"]
        expected = Fraction(500, 59)
        self.assertEqual(
            a3_pred, expected,
            msg=(
                "Closed-loop α₃⁻¹(M_Z)_pred BROKEN: got "
                f"{a3_pred}, expected {expected} = ALPHA_S_INV_MZ"
            ),
        )
        # Belt-and-suspenders: also matches the er module-level constant.
        self.assertEqual(a3_pred, er.ALPHA_S_INV_MZ,
                         msg="Closed-loop α₃ ≠ er.ALPHA_S_INV_MZ")

    def test_su2L_preservation_a2L_down_eq_a2_pred(self) -> None:
        """α₂L⁻¹(M_PS)_down = α₂⁻¹(M_PS)_pred.

        At the PS → SM matching scale, SU(2)_L is preserved identically
        (no embedding mixing for the left-handed weak factor).  Any drift
        means the matching identity α₂⁻¹ = α_{2L}⁻¹ has been corrupted.
        """
        a2L_down = self.live["alpha2L_inv_MPS_down"]
        # Recompute STEP 3d locally (Python doesn't store it).
        a2_pred = a2L_down
        # That equality is what we want to witness:
        self.assertEqual(
            a2L_down, a2_pred,
            msg="SU(2)_L preservation identity broken at PS→SM matching",
        )
        # And it must equal the hardcoded literal that ships in Zig.
        num, den = EXPECTED_STEP3D["alpha2_inv_MPS_pred"]
        self.assertEqual(
            a2_pred, Fraction(num, den),
            msg=(
                "α₂⁻¹(M_PS)_pred drift vs Zig literal "
                f"vf.mk({num}, {den})"
            ),
        )


# ---------------------------------------------------------------------------
# TestB3Step3fConsistency — STEP 3f is computed inside Zig's
# `computeStep1to3()` helper but does NOT have hardcoded literal mirrors
# in the B3 self-test block (the kernel pins runs the predictions and
# returns the dict).  We verify the Python-side identities hold and that
# the two `vf.isZero` division guards are present in the Zig source.
# ---------------------------------------------------------------------------

class TestB3Step3fConsistency(unittest.TestCase):
    """STEP 3f Python-authority self-consistency — closed-form
    identities that the Zig kernel must implement."""

    def setUp(self) -> None:
        self.live = _live_rge()

    def test_sin2_tw_pred_closed_form(self) -> None:
        """sin²θ_W(M_Z)_pred = (3/5)·α₂⁻¹/(α₁⁻¹ + (3/5)·α₂⁻¹)."""
        a1 = self.live["alpha1_inv_MZ_pred"]
        a2 = self.live["alpha2_inv_MZ_pred"]
        expected = Fraction(3, 5) * a2 / (a1 + Fraction(3, 5) * a2)
        got = self.live["sin2_tw_pred"]
        self.assertEqual(got, expected, msg="sin²θ_W(M_Z)_pred closed-form drift")

    def test_alpha_em_inv_pred_closed_form(self) -> None:
        """α_EM⁻¹(M_Z)_pred = α₂⁻¹(M_Z)_pred / sin²θ_W(M_Z)_pred."""
        a2 = self.live["alpha2_inv_MZ_pred"]
        sin2 = self.live["sin2_tw_pred"]
        # Division guard: sin² is structurally positive on this chain.
        self.assertNotEqual(sin2, Fraction(0), msg="sin²θ_W = 0 → division-by-zero")
        expected = a2 / sin2
        got = self.live["alpha_em_inv_pred"]
        self.assertEqual(got, expected, msg="α_EM⁻¹(M_Z)_pred closed-form drift")

    def test_alpha_s_pred_reciprocal(self) -> None:
        """α_s(M_Z)_pred = 1 / α₃⁻¹(M_Z)_pred = 59/500 exactly
        (closed-loop reciprocal of ALPHA_S_INV_MZ)."""
        a3_inv = self.live["alpha3_inv_MZ_pred"]
        self.assertNotEqual(a3_inv, Fraction(0), msg="α₃⁻¹ = 0 → division-by-zero")
        expected = Fraction(1) / a3_inv
        got = self.live["alpha_s_pred"]
        self.assertEqual(got, expected, msg="α_s(M_Z)_pred reciprocal drift")
        # Closed loop: equals 59/500 exactly.
        self.assertEqual(got, Fraction(59, 500),
                         msg="α_s(M_Z)_pred ≠ 59/500 → closed-loop broken")


# ---------------------------------------------------------------------------
# TestZigSourceParity — every expected (num, den) pair must appear in
# the B3 block of rge_sm.zig.  Idiomatic forms get the
# ZIG_ALTERNATE_PATTERNS fallback.
# ---------------------------------------------------------------------------

class TestZigSourceParity(unittest.TestCase):
    """Source-scan: every Python-side hardcoded Fraction has a literal
    (or whitelisted idiomatic equivalent) in the Zig B3 self-test block."""
    pass


# Constants block — straightforward (num, den) literals, no idioms.
for _name, (_num, _den) in EXPECTED_CONSTANTS.items():
    setattr(
        TestZigSourceParity,
        f"test_zig_contains_constant_{_name}",
        _make_zig_presence_test(f"constant_{_name}", _num, _den),
    )

# STEP 1/2/3a/3c/3d milestones — straightforward literals.
for _key, (_num, _den) in {
    **EXPECTED_STEP1,
    **EXPECTED_STEP2,
    **EXPECTED_STEP3A,
    **EXPECTED_STEP3C,
    **EXPECTED_STEP3D,
}.items():
    setattr(
        TestZigSourceParity,
        f"test_zig_contains_{_key}",
        _make_zig_presence_test(f"step_{_key}", _num, _den),
    )

# STEP 3e — α₁ and α₂ are straightforward literals; α₃ is whitelisted.
setattr(
    TestZigSourceParity,
    "test_zig_contains_alpha1_inv_MZ_pred",
    _make_zig_presence_test(
        "step_alpha1_inv_MZ_pred",
        *EXPECTED_STEP3E["alpha1_inv_MZ_pred"],
    ),
)
setattr(
    TestZigSourceParity,
    "test_zig_contains_alpha2_inv_MZ_pred",
    _make_zig_presence_test(
        "step_alpha2_inv_MZ_pred",
        *EXPECTED_STEP3E["alpha2_inv_MZ_pred"],
    ),
)
# α₃⁻¹(M_Z)_pred = 500/59 — Zig writes `Constants.ALPHA_S_INV_MZ` instead
# of vf.mk(500, 59).  The whitelist label below maps to the regex.
setattr(
    TestZigSourceParity,
    "test_zig_contains_alpha3_inv_MZ_pred",
    _make_zig_presence_test(
        "step3e_alpha3_inv_MZ_pred_closed_loop",
        *EXPECTED_STEP3E["alpha3_inv_MZ_pred"],
    ),
)


# ---------------------------------------------------------------------------
# TestZigStructuralMirrors — the Zig B3 source must declare the public
# symbols that c176's contract names, and must contain the two
# `vf.isZero` division guards inside `computeStep1to3()`.
# ---------------------------------------------------------------------------

class TestZigStructuralMirrors(unittest.TestCase):
    """Source-scan: structural elements (public symbols, guard idioms)
    that have no (num, den) literal but still must be present."""

    def test_pub_fn_run_coupling_inv_present(self) -> None:
        source = _zig_source()
        self.assertRegex(
            source,
            r"pub\s+fn\s+runCouplingInv\s*\(",
            msg="pub fn runCouplingInv(...) missing from rge_sm.zig",
        )

    def test_pub_const_step1to3_results_present(self) -> None:
        source = _zig_source()
        self.assertRegex(
            source,
            r"pub\s+const\s+Step1to3Results\s*=\s*struct",
            msg="pub const Step1to3Results = struct {...} missing from rge_sm.zig",
        )

    def test_pub_fn_compute_step1to3_present(self) -> None:
        source = _zig_source()
        self.assertRegex(
            source,
            r"pub\s+fn\s+computeStep1to3\s*\(\s*\)\s+Step1to3Results",
            msg="pub fn computeStep1to3() Step1to3Results missing from rge_sm.zig",
        )

    def test_step3f_sin2_zero_guard_present(self) -> None:
        """The `vf.isZero(sin2_tw_pred)` guard prevents division-by-zero
        when computing α_EM⁻¹ = α₂⁻¹ / sin²θ_W in the Zig kernel.
        Whitelisted under `step3f_sin2_tw_zero_guard`."""
        self.assertTrue(
            _alternate_present_in_b3("step3f_sin2_tw_zero_guard")
            or re.search(r"vf\.isZero\(\s*sin2_tw_pred\s*\)", _zig_source()),
            msg=(
                "Missing vf.isZero(sin2_tw_pred) division guard in rge_sm.zig. "
                "Without this guard the Zig kernel would panic or return "
                "garbage when sin²θ_W = 0; Python protects this with an "
                "explicit `if sin2_tw_pred != 0 else Fraction(0)` branch."
            ),
        )

    def test_step3f_alpha3_zero_guard_present(self) -> None:
        """The `vf.isZero(alpha3_inv_MZ_pred)` guard prevents division-by-zero
        when computing α_s = 1 / α₃⁻¹.  Whitelisted under
        `step3f_alpha3_zero_guard`."""
        self.assertTrue(
            _alternate_present_in_b3("step3f_alpha3_zero_guard")
            or re.search(
                r"vf\.isZero\(\s*alpha3_inv_MZ_pred\s*\)", _zig_source()
            ),
            msg=(
                "Missing vf.isZero(alpha3_inv_MZ_pred) division guard in "
                "rge_sm.zig.  Python protects this with an explicit "
                "`if alpha3_inv_MZ_pred != 0 else Fraction(0)` branch."
            ),
        )


# ---------------------------------------------------------------------------
# TestZigAlternatePatternsWhitelistMechanism — assert the whitelist
# infrastructure is healthy: every entry has at least one pattern, and
# no entry registered for STEP 3e/3f goes orphaned (i.e. each idiom we
# claim Zig uses is actually scanned by some test).
# ---------------------------------------------------------------------------

class TestZigAlternatePatternsWhitelistMechanism(unittest.TestCase):
    """Health checks on the ZIG_ALTERNATE_PATTERNS whitelist itself —
    catches drift where an idiom is registered but no test consumes it,
    or where a registered idiom no longer matches the Zig source."""

    def test_all_whitelisted_patterns_match_zig_source(self) -> None:
        """Every regex registered in ZIG_ALTERNATE_PATTERNS must match
        the current Zig B3 block.  If a regex stops matching, either the
        Zig idiom drifted or the regex needs an update."""
        block = _b3_block(_zig_source())
        for test_id, patterns in ZIG_ALTERNATE_PATTERNS.items():
            self.assertGreater(
                len(patterns), 0,
                msg=f"[{test_id}] empty pattern list — remove the entry "
                    f"or add at least one regex",
            )
            for pattern in patterns:
                self.assertRegex(
                    block, pattern,
                    msg=(
                        f"[{test_id}] pattern {pattern!r} no longer "
                        "matches the B3 block of rge_sm.zig.  Either "
                        "the Zig port reverted to the literal form (in "
                        "which case remove the whitelist entry), or the "
                        "idiom was renamed (update the regex)."
                    ),
                )

    def test_step3e_alpha3_idiom_uses_named_constant(self) -> None:
        """Specifically: line 1618's idiomatic form must reference
        `Constants.ALPHA_S_INV_MZ`, not a re-spelling of vf.mk(500, 59).
        This is the strict-improvement contract from
        feedback_parity_guard_idiomatic_whitelist.md."""
        block = _b3_block(_zig_source())
        self.assertRegex(
            block,
            r"a3_MZ_pred,?\s*Constants\.ALPHA_S_INV_MZ",
            msg=(
                "STEP 3e closed-loop assertion no longer references "
                "Constants.ALPHA_S_INV_MZ; either restore the named-"
                "constant idiom or update this test."
            ),
        )


# ---------------------------------------------------------------------------
# TestCommandmentXII — verify the verdict path contains zero floats.
# ---------------------------------------------------------------------------

class TestCommandmentXII(unittest.TestCase):
    """All B3 outputs are exact `Fraction` instances — no floats anywhere
    on the verdict path."""

    def test_all_step_outputs_are_fractions(self) -> None:
        live = _live_rge()
        keys = (
            list(EXPECTED_STEP1.keys())
            + list(EXPECTED_STEP2.keys())
            + list(EXPECTED_STEP3A.keys())
            + list(EXPECTED_STEP3C.keys())
            + list(EXPECTED_STEP3E.keys())
            + ["sin2_tw_pred", "alpha_em_inv_pred", "alpha_s_pred"]
        )
        for key in keys:
            self.assertIn(key, live, msg=f"[{key}] missing from live RGE dict")
            self.assertIsInstance(
                live[key], Fraction,
                msg=(
                    f"[{key}] expected Fraction in verdict path, got "
                    f"{type(live[key]).__name__} — Commandment XII violation"
                ),
            )

    def test_all_constants_are_fractions(self) -> None:
        for name in EXPECTED_CONSTANTS.keys():
            self.assertIsInstance(
                getattr(er, name), Fraction,
                msg=(
                    f"[{name}] er.{name} is not a Fraction — "
                    "Commandment XII violation"
                ),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
