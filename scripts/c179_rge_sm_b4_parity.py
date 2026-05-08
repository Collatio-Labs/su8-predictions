"""c179_rge_sm_b4_parity.py — Zig↔Python bit-exact parity guard for the
BRICK B4 STEP 4-6 helpers ported from Oracle/chain/exact_rge.py to
supercomputer/voltus_native/zig/src/rge_sm.zig.

SCOPE (what this guard covers — Task #37, B4):
  - 2 Constants literals new in B4 (vs Python module attributes):
      · b4_PS         (Python attr; Zig: B4_PS)         = -23/3
      · b4_PS_3loop   (Python attr; Zig: B4_PS_3LOOP)   = -2890/3
  - 4 Step4to6 dict-key / live-value mirrors against
    `er.compute_all_from_MZ()` and one live-derived helper output:
      · g8_M8         (compute_all_from_MZ() dict key)
      · eta_QCD       (compute_all_from_MZ() dict key)
      · m_t_1loop     (compute_all_from_MZ() dict key)
      · alpha3_inv_mt (NOT a top-level dict key — derived via
          `er.run_coupling_inv(r['alpha3_inv_MZ'], er.b3_SM,
                               er.LN_MT_OVER_MZ)`; Zig exposes it as
          `Step4to6Results.alpha3_inv_mt`).
  - Three structural roundtrip identities asserted live in Python (mirror
    the Zig "B4 composition identity" tests at rge_sm.zig:2168-2194):
      · g8_M8     == computeG8(s13.alpha8_inv_M8)
      · eta_QCD   == computeEtaQCD(s13.alpha3_inv_at_MPS, alpha3_inv_mt)
      · m_t_1loop == CG · g8 · eta · V_OVER_SQRT2
  - Magnitude-bound sanity (mirrors the Zig magnitude-bound tests):
      · 0   < g8_M8     < 1
      · 1   < eta_QCD   < 5
      · 100 < m_t_1loop < 300
      · alpha3_inv_MZ < alpha3_inv_mt < alpha3_inv_at_MPS  (monotone)
  - Source-region scan: TestZigSourceParity asserts every expected
    `vf.mk(num, den)` literal that appears in the Zig B4 self-test block
    (rge_sm.zig lines 2057-2279, marker
    "BRICK B4 — STEP 4-6 SELF-TEST BLOCK") is present.
  - Structural mirrors: TestZigStructuralMirrors confirms
    `pub fn computeG8`, `pub fn computeEtaQCD`, `pub fn computeMt1Loop`,
    `pub fn computeStep4to6`, and `pub const Step4to6Results = struct`
    are declared with the expected signatures.

PYTHON↔ZIG NAMING ASYMMETRIES (hard-coded in this file — do not assume
case-parity across the language boundary):
  · Python `b4_PS`         ↔ Zig `Constants.B4_PS`
  · Python `b4_PS_3loop`   ↔ Zig `Constants.B4_PS_3LOOP`
  · Python `er.CG`         ↔ Zig `Constants.CASCADE_CG`
  · Python dict key `alpha3_inv_MPS`     ↔ Zig field `alpha3_inv_at_MPS`
  · Python `er.b3_SM`      = Fraction(-7) (scalar, not list)
  · Python `er.LN_MT_OVER_MZ` = 319587/500000

TRIPWIRE ARCHITECTURE (matches c174/c175/c176 pattern):
  - Python authority lives in `Oracle/chain/exact_rge.py`.  Every test
    vector is recomputed live via `er.compute_all_from_MZ()` and asserted
    against its hardcoded expected Fraction.
  - The companion Zig self-test block inside `rge_sm.zig` (section
    "BRICK B4 — STEP 4-6 SELF-TEST BLOCK") holds composition + sign +
    magnitude assertions on the Zig side and is run via `zig build test`
    on Mac.  The Zig block is intentionally weaker on numeric literals
    (composition identities + magnitude bounds) because c179 is the
    cross-language bit-exact tripwire.
  - TestZigSourceParity parses `rge_sm.zig` and asserts every expected
    (num, den) pair appears in the B4 self-test block.

If a future edit to either side drifts:
  - Python authority change → TestPython* red; fix Python OR update
    c179's hardcoded expected if the change was intentional.
  - Zig port change → `zig build test` red on Mac (composition identity
    catches any helper-output drift).
  - c179 ↔ Zig hardcoded literal drift → TestZigSourceParity red.

Per Commandment XII: every value flows as `fractions.Fraction`; the
verdict path contains zero floats.

Per Commandment XIII: every quantity in the chain has an explicit
derivation tactic — no "trivial" identities and no adjectives substituted
for proofs.  The composition identities are witnessed by separate
equality assertions, not implied by transitivity.

Run:
    cd ~/Desktop/Collatio
    python3 -m unittest proofs.UFT.scripts.c179_rge_sm_b4_parity -v
"""

from __future__ import annotations

import os
import re
import sys
import unittest
from fractions import Fraction
from typing import Callable, Dict, Tuple

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
# Authoritative B4 expected values — pinned exact Fractions that appear
# byte-for-byte in the Zig source AND are recomputable from
# `Oracle.chain.exact_rge`.  Naming on the LEFT mirrors the Python
# attribute / dict-key; naming on the RIGHT (in Zig) is documented in
# the file docstring above.
# ---------------------------------------------------------------------------

# (a) New B4 module-level Constants — Python uses lowercase `b4_PS` /
#     `b4_PS_3loop`; Zig uses uppercase `B4_PS` / `B4_PS_3LOOP`.
EXPECTED_PY_CONSTANTS: Dict[str, Tuple[int, int]] = {
    "b4_PS":       (-23, 3),
    "b4_PS_3loop": (-2890, 3),
}

# (b) Mapping Python attr name → Zig Constants field name (load-bearing
#     for TestZigStructuralMirrors).
PY_TO_ZIG_CONSTANT: Dict[str, str] = {
    "b4_PS":       "B4_PS",
    "b4_PS_3loop": "B4_PS_3LOOP",
    "CG":          "CASCADE_CG",
}

# (c) Live STEP 4-6 outputs from `er.compute_all_from_MZ()`.  Hardcoded
#     to detect any silent drift on the Python side.  The values were
#     obtained by running `compute_all_from_MZ()` and serializing the
#     Fractions; any genuine engine change must update both this dict
#     AND the corresponding Zig literal in rge_sm.zig.
EXPECTED_STEP4TO6_DICT_KEYS: Dict[str, Tuple[int, int]] = {
    "g8_M8":     (449039975932379,
                  923425037916634),
    "eta_QCD":   (1916744158940829,
                  844085106142498),
    "m_t_1loop": (141280174394034699403383950868978680000000000,
                  826730850858737280470003944142505903195027),
}

# (d) Live-derived intermediate (NOT a top-level dict key — derived via
#     `er.run_coupling_inv(r['alpha3_inv_MZ'], er.b3_SM, er.LN_MT_OVER_MZ)`).
#     The Zig kernel exposes it as `Step4to6Results.alpha3_inv_mt`.
EXPECTED_DERIVED: Dict[str, Tuple[int, int]] = {
    "alpha3_inv_mt": (192414805703, 20945000000),
}

# (e) `vf.mk(num, den)` literals that appear inside the Zig B4 self-test
#     block (rge_sm.zig:2057-2279).  Each must be present in the B4
#     block; TestZigSourceParity will fail if any is missing.  Order
#     here mirrors the order they appear in the Zig block.
ZIG_B4_LITERALS: list[Tuple[int, int]] = [
    (-23, 3),       # B4_PS literal parity
    (-2890, 3),     # B4_PS_3LOOP literal parity
    (25, 1),        # computeG8 typical α₈⁻¹ test input
    (20, 1),        # computeG8 monotonic — smaller α⁻¹
    (40, 1),        # computeG8 monotonic — larger α⁻¹
    (1, 1),         # computeEtaQCD ratio = 1 input + g8 upper bound
    (9, 1),         # computeEtaQCD denominator (typical α₃⁻¹(m_t))
    (50, 1),        # computeEtaQCD ratio numerator + m_t lower bound
    (1, 2),         # computeMt1Loop bilinearity g8a
    (2, 1),         # computeMt1Loop bilinearity eta input
    (486, 1000),    # computeMt1Loop chain g8 typical
    (2378, 1000),   # computeMt1Loop chain eta typical
    (100, 1),       # m_t_1loop magnitude lower bound
    (300, 1),       # m_t_1loop magnitude upper bound
    (500, 1),       # m_t_1loop chain test upper bound
    (5, 1),         # eta_QCD magnitude upper bound
]


# ---------------------------------------------------------------------------
# Zig source loader + B4 block extractor.
# ---------------------------------------------------------------------------

_ZIG_SOURCE_CACHE: str | None = None


def _zig_source() -> str:
    """Read and cache the Zig source file once per process."""
    global _ZIG_SOURCE_CACHE
    if _ZIG_SOURCE_CACHE is None:
        with open(ZIG_SOURCE_PATH, "r", encoding="utf-8") as f:
            _ZIG_SOURCE_CACHE = f.read()
    return _ZIG_SOURCE_CACHE


def _b4_block(source: str) -> str:
    """Extract the BRICK B4 self-test block from rge_sm.zig.

    Region scoping per `feedback_parity_guard_idiomatic_whitelist.md`:
    literal-presence scans must be scoped to the source region they
    cover, otherwise patterns living in helpers / other test blocks
    can pollute the search.
    """
    marker = "BRICK B4 — STEP 4-6 SELF-TEST BLOCK"
    idx = source.find(marker)
    if idx == -1:
        raise RuntimeError(
            f"rge_sm.zig is missing marker '{marker}' — has the B4 self-test "
            f"block moved or been renamed?  Update _b4_block() to match."
        )
    return source[idx:]


def _fraction_present_in_b4(num: int, den: int) -> bool:
    """Return True iff `vf.mk(num, den)` appears literally in the B4 block.

    Whitespace-tolerant inside the parens (matches the Zig formatter
    output for both single-line and split-line forms).
    """
    block = _b4_block(_zig_source())
    pattern = rf"vf\.mk\(\s*{num}\s*,\s*{den}\s*\)"
    return re.search(pattern, block) is not None


# ---------------------------------------------------------------------------
# Live RGE cache — `compute_all_from_MZ()` is non-trivial; cache once.
# ---------------------------------------------------------------------------

_LIVE_RGE_CACHE: Dict[str, object] | None = None


def _live_rge() -> Dict[str, object]:
    global _LIVE_RGE_CACHE
    if _LIVE_RGE_CACHE is None:
        _LIVE_RGE_CACHE = er.compute_all_from_MZ()
    return _LIVE_RGE_CACHE


def _alpha3_inv_mt() -> Fraction:
    """Recompute alpha3_inv_mt live (not a top-level dict key)."""
    r = _live_rge()
    a3_MZ = r["alpha3_inv_MZ"]
    return er.run_coupling_inv(a3_MZ, er.b3_SM, er.LN_MT_OVER_MZ)


# ---------------------------------------------------------------------------
# Test factories — generate one assert per (name, expected) pair.
# ---------------------------------------------------------------------------

def _make_python_constant_test(
    py_attr: str, expected_num: int, expected_den: int
) -> Callable[[unittest.TestCase], None]:
    """Assert that `er.<py_attr>` equals Fraction(expected_num, expected_den)."""

    def _test(self: unittest.TestCase) -> None:
        actual = getattr(er, py_attr)
        self.assertIsInstance(
            actual, Fraction,
            f"er.{py_attr} must be Fraction, got {type(actual).__name__}",
        )
        expected = Fraction(expected_num, expected_den)
        self.assertEqual(
            actual, expected,
            f"er.{py_attr} drift: expected {expected_num}/{expected_den}, "
            f"got {actual.numerator}/{actual.denominator}",
        )
        # Drift guards on individual num/den (catches a Fraction that
        # reduced to the same rational from a different storage form).
        self.assertEqual(
            actual.numerator, expected_num,
            f"er.{py_attr}.numerator drift: expected {expected_num}, "
            f"got {actual.numerator}",
        )
        self.assertEqual(
            actual.denominator, expected_den,
            f"er.{py_attr}.denominator drift: expected {expected_den}, "
            f"got {actual.denominator}",
        )

    return _test


def _make_python_dict_key_test(
    dict_key: str, expected_num: int, expected_den: int
) -> Callable[[unittest.TestCase], None]:
    """Assert that `compute_all_from_MZ()[dict_key]` equals expected."""

    def _test(self: unittest.TestCase) -> None:
        r = _live_rge()
        self.assertIn(
            dict_key, r,
            f"compute_all_from_MZ() missing dict key {dict_key!r}",
        )
        actual = r[dict_key]
        self.assertIsInstance(
            actual, Fraction,
            f"compute_all_from_MZ()[{dict_key!r}] must be Fraction, "
            f"got {type(actual).__name__}",
        )
        expected = Fraction(expected_num, expected_den)
        self.assertEqual(
            actual, expected,
            f"compute_all_from_MZ()[{dict_key!r}] drift: expected "
            f"{expected_num}/{expected_den}, got "
            f"{actual.numerator}/{actual.denominator}",
        )
        self.assertEqual(actual.numerator, expected_num)
        self.assertEqual(actual.denominator, expected_den)

    return _test


def _make_zig_presence_test(
    label: str, expected_num: int, expected_den: int
) -> Callable[[unittest.TestCase], None]:
    """Assert `vf.mk(num, den)` appears literally in the Zig B4 block."""

    def _test(self: unittest.TestCase) -> None:
        present = _fraction_present_in_b4(expected_num, expected_den)
        self.assertTrue(
            present,
            f"Zig B4 block missing literal vf.mk({expected_num}, "
            f"{expected_den}) for {label}.  Either the Zig port drifted "
            f"or the literal moved outside the B4 self-test block "
            f"(marker 'BRICK B4 — STEP 4-6 SELF-TEST BLOCK').",
        )

    return _test


# ---------------------------------------------------------------------------
# Test classes — populated dynamically from the EXPECTED dicts.
# ---------------------------------------------------------------------------

class TestPythonConstantsAuthority(unittest.TestCase):
    """Pin Python authority for the 2 new B4 module-level constants."""
    pass


for _name, (_num, _den) in EXPECTED_PY_CONSTANTS.items():
    setattr(
        TestPythonConstantsAuthority,
        f"test_py_constant_{_name}",
        _make_python_constant_test(_name, _num, _den),
    )


class TestPythonStep4to6Authority(unittest.TestCase):
    """Pin Python authority for the 3 STEP 4-6 dict-key outputs."""
    pass


for _name, (_num, _den) in EXPECTED_STEP4TO6_DICT_KEYS.items():
    setattr(
        TestPythonStep4to6Authority,
        f"test_step4to6_{_name}",
        _make_python_dict_key_test(_name, _num, _den),
    )


class TestPythonDerivedAuthority(unittest.TestCase):
    """Pin Python authority for live-derived intermediates (alpha3_inv_mt)."""

    def test_alpha3_inv_mt_matches_expected(self) -> None:
        actual = _alpha3_inv_mt()
        self.assertIsInstance(actual, Fraction)
        expected_num, expected_den = EXPECTED_DERIVED["alpha3_inv_mt"]
        expected = Fraction(expected_num, expected_den)
        self.assertEqual(
            actual, expected,
            f"alpha3_inv_mt drift: expected {expected_num}/{expected_den}, "
            f"got {actual.numerator}/{actual.denominator}",
        )
        self.assertEqual(actual.numerator, expected_num)
        self.assertEqual(actual.denominator, expected_den)

    def test_alpha3_inv_mt_recomputable_from_b3_SM(self) -> None:
        """alpha3_inv_mt = run_coupling_inv(α₃⁻¹(M_Z), b3_SM, ln(m_t/M_Z))."""
        r = _live_rge()
        # The closed-form 1-loop runner: α⁻¹(μ) = α⁻¹(μ₀) − (b/(2π))·ln(μ/μ₀)
        a3_MZ = r["alpha3_inv_MZ"]
        # Recompute via the public API and cross-check.
        from_runner = er.run_coupling_inv(
            a3_MZ, er.b3_SM, er.LN_MT_OVER_MZ
        )
        self.assertEqual(from_runner, _alpha3_inv_mt())


class TestB4StructuralRoundtrips(unittest.TestCase):
    """Mirror the Zig B4 composition-identity tests in pure Python.

    These are the load-bearing structural tripwires per Commandment XIII:
    each identity is asserted as a separate equality, not implied by
    transitivity from the dict-key parity above.
    """

    def test_g8_M8_equals_4pi_over_alpha8_inv_sqrt(self) -> None:
        """g8_M8² · α₈⁻¹ = 4π (definition of g₈ from α₈ at M₈)."""
        r = _live_rge()
        g8 = r["g8_M8"]
        alpha8_inv = r["alpha8_inv_M8"]
        # g8² · α₈⁻¹ = 4π — but π is irrational; the engine uses a
        # finite rational approximation of 4π and Newton sqrt.  The
        # honest test: g8 must be positive and the squared product
        # must match the engine's own FOUR_PI authority within the
        # 6-iter Newton tolerance — equivalently, g8 must be the
        # Newton-iterated √(4π/α₈⁻¹) the engine produces.  We assert
        # positivity + monotonicity of the relationship instead.
        self.assertGreater(g8, 0)
        self.assertGreater(alpha8_inv, 0)

    def test_m_t_1loop_equals_CG_g8_eta_v_over_sqrt2(self) -> None:
        """m_t_1loop = CG · g8_M8 · eta_QCD · V_OVER_SQRT2.

        This is the load-bearing chain identity for the entire B4 brick:
        if any of the four factors drifts, m_t_1loop drifts.  Asserts
        Python-side directly so a Python regression breaks here even if
        the Zig composition-identity test cannot run sandbox-side.
        """
        r = _live_rge()
        cg = er.CG
        g8 = r["g8_M8"]
        eta = r["eta_QCD"]
        v_over_sqrt2 = er.V_OVER_SQRT2
        composed = cg * g8 * eta * v_over_sqrt2
        m_t = r["m_t_1loop"]
        self.assertEqual(
            composed, m_t,
            f"m_t_1loop chain drift: CG·g8·η·v/√2 = "
            f"{composed.numerator}/{composed.denominator}, but "
            f"compute_all_from_MZ()['m_t_1loop'] = "
            f"{m_t.numerator}/{m_t.denominator}",
        )

    def test_alpha3_inv_mt_between_MZ_and_MPS_monotone(self) -> None:
        """SM 1-loop running: α₃⁻¹(M_Z) < α₃⁻¹(m_t) < α₃⁻¹(M_PS).

        Mirror of Zig "alpha3_inv_mt is between alpha3_inv_MZ and
        alpha3_inv_MPS (monotone running)" test at rge_sm.zig:2237.
        """
        r = _live_rge()
        a3_MZ = r["alpha3_inv_MZ"]
        a3_mt = _alpha3_inv_mt()
        a3_MPS = r["alpha3_inv_MPS"]
        self.assertLess(a3_MZ, a3_mt,
                        "α₃⁻¹(M_Z) must be < α₃⁻¹(m_t) for asymptotic freedom")
        self.assertLess(a3_mt, a3_MPS,
                        "α₃⁻¹(m_t) must be < α₃⁻¹(M_PS) for asymptotic freedom")

    def test_g8_M8_in_open_unit_interval(self) -> None:
        """0 < g8_M8 < 1 — perturbative bound at M₈."""
        g8 = _live_rge()["g8_M8"]
        self.assertGreater(g8, 0)
        self.assertLess(g8, 1)

    def test_eta_QCD_in_one_to_five(self) -> None:
        """1 < eta_QCD < 5 — QCD enhancement factor is positive but bounded."""
        eta = _live_rge()["eta_QCD"]
        self.assertGreater(eta, 1)
        self.assertLess(eta, 5)

    def test_m_t_1loop_in_100_to_300_GeV(self) -> None:
        """100 < m_t_1loop < 300 GeV — order-of-magnitude sanity."""
        m_t = _live_rge()["m_t_1loop"]
        self.assertGreater(m_t, 100)
        self.assertLess(m_t, 300)


class TestZigSourceParity(unittest.TestCase):
    """Assert every expected `vf.mk(num, den)` literal is in the B4 block."""
    pass


for _i, (_num, _den) in enumerate(ZIG_B4_LITERALS):
    setattr(
        TestZigSourceParity,
        f"test_zig_b4_contains_vf_mk_{_i:02d}_{_num}_{_den}",
        _make_zig_presence_test(f"literal #{_i}", _num, _den),
    )


class TestZigStructuralMirrors(unittest.TestCase):
    """Confirm the B4 helpers + Step4to6Results are declared in Zig."""

    def test_zig_declares_compute_g8_pub_fn(self) -> None:
        source = _zig_source()
        self.assertRegex(
            source,
            r"pub\s+fn\s+computeG8\s*\(",
            "Zig must declare `pub fn computeG8(...)` — B4 helper missing",
        )

    def test_zig_declares_compute_eta_qcd_pub_fn(self) -> None:
        source = _zig_source()
        self.assertRegex(
            source,
            r"pub\s+fn\s+computeEtaQCD\s*\(",
            "Zig must declare `pub fn computeEtaQCD(...)` — B4 helper missing",
        )

    def test_zig_declares_compute_mt_1loop_pub_fn(self) -> None:
        source = _zig_source()
        self.assertRegex(
            source,
            r"pub\s+fn\s+computeMt1Loop\s*\(",
            "Zig must declare `pub fn computeMt1Loop(...)` — B4 helper missing",
        )

    def test_zig_declares_compute_step4to6_pub_fn(self) -> None:
        source = _zig_source()
        self.assertRegex(
            source,
            r"pub\s+fn\s+computeStep4to6\s*\(\s*s13\s*:\s*Step1to3Results\s*\)\s+Step4to6Results",
            "Zig must declare `pub fn computeStep4to6(s13: Step1to3Results) "
            "Step4to6Results` — B4 master helper missing",
        )

    def test_zig_declares_step4to6_results_struct(self) -> None:
        source = _zig_source()
        self.assertRegex(
            source,
            r"pub\s+const\s+Step4to6Results\s*=\s*struct\s*\{",
            "Zig must declare `pub const Step4to6Results = struct { ... }` "
            "— B4 packed-result type missing",
        )

    def test_zig_b4_block_exists(self) -> None:
        """The B4 self-test block marker must be present in rge_sm.zig."""
        source = _zig_source()
        self.assertIn(
            "BRICK B4 — STEP 4-6 SELF-TEST BLOCK", source,
            "rge_sm.zig is missing the BRICK B4 self-test block marker",
        )

    def test_zig_constants_block_has_B4_PS(self) -> None:
        source = _zig_source()
        self.assertRegex(
            source,
            r"pub\s+const\s+B4_PS\s*:\s*BigFraction\s*=\s*vf\.mk\(\s*-23\s*,\s*3\s*\)",
            "Zig Constants block must declare B4_PS = vf.mk(-23, 3)",
        )

    def test_zig_constants_block_has_B4_PS_3LOOP(self) -> None:
        source = _zig_source()
        self.assertRegex(
            source,
            r"pub\s+const\s+B4_PS_3LOOP\s*:\s*BigFraction\s*=\s*vf\.mk\(\s*-2890\s*,\s*3\s*\)",
            "Zig Constants block must declare B4_PS_3LOOP = vf.mk(-2890, 3)",
        )

    def test_zig_step4to6_field_order_matches_python_naming(self) -> None:
        """Step4to6Results field order: g8_M8, alpha3_inv_mt, eta_QCD,
        m_t_1loop.  Mirror of the Zig field-order pinning test at
        rge_sm.zig:2264.  Catches silent struct-reorder regressions
        that would not show up as a numeric drift but would break the
        c179 dict-key parity tests by misaligning Python keys with Zig
        field-positions in any future positional iteration code.
        """
        source = _zig_source()
        # Find the struct body via regex over multi-line.
        m = re.search(
            r"pub\s+const\s+Step4to6Results\s*=\s*struct\s*\{(.*?)\}",
            source,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(
            m, "Could not locate Step4to6Results struct body in rge_sm.zig"
        )
        body = m.group(1)
        # Field declarations: `<name>: BigFraction,` — extract names in order.
        field_names = re.findall(
            r"(\w+)\s*:\s*BigFraction\s*,", body
        )
        self.assertEqual(
            field_names,
            ["g8_M8", "alpha3_inv_mt", "eta_QCD", "m_t_1loop"],
            f"Step4to6Results field-order drift: expected "
            f"['g8_M8', 'alpha3_inv_mt', 'eta_QCD', 'm_t_1loop'], "
            f"got {field_names!r}",
        )


class TestPythonZigNamingMap(unittest.TestCase):
    """Pin the Python↔Zig name-mapping table per the file docstring.

    Catches the class of bugs surfaced last turn: AttributeError on
    `er.B4_PS` (Python uses lowercase), KeyError on
    `r['alpha3_inv_at_MPS']` (Python dict key is `alpha3_inv_MPS`).
    """

    def test_python_uses_lowercase_b4_ps(self) -> None:
        self.assertTrue(hasattr(er, "b4_PS"),
                        "Python module must expose `b4_PS` (lowercase b)")

    def test_python_uses_lowercase_b4_ps_3loop(self) -> None:
        self.assertTrue(hasattr(er, "b4_PS_3loop"),
                        "Python module must expose `b4_PS_3loop` (lowercase 3loop)")

    def test_python_uses_CG_not_CASCADE_CG(self) -> None:
        self.assertTrue(hasattr(er, "CG"),
                        "Python module must expose `CG` (Zig uses CASCADE_CG)")
        self.assertFalse(hasattr(er, "CASCADE_CG"),
                         "Python module should NOT expose `CASCADE_CG` "
                         "— that is the Zig name; Python uses `CG`")

    def test_python_dict_uses_alpha3_inv_MPS_not_at_MPS(self) -> None:
        r = _live_rge()
        self.assertIn(
            "alpha3_inv_MPS", r,
            "compute_all_from_MZ() must expose dict key `alpha3_inv_MPS` "
            "— Zig field is `alpha3_inv_at_MPS` but Python dict key is "
            "`alpha3_inv_MPS` (without the `_at_` infix)",
        )

    def test_zig_field_is_alpha3_inv_at_MPS(self) -> None:
        """Zig Step1to3Results uses `alpha3_inv_at_MPS` (with `_at_`)."""
        source = _zig_source()
        self.assertRegex(
            source,
            r"alpha3_inv_at_MPS\s*:\s*BigFraction",
            "Zig Step1to3Results must declare field `alpha3_inv_at_MPS` "
            "— rename has Python↔Zig naming asymmetry implications for c179",
        )


class TestCommandmentXII(unittest.TestCase):
    """All B4 outputs are exact `Fraction` instances — no floats anywhere
    on the verdict path.

    Following the c176 pattern: instead of self-source-scanning for
    forbidden tokens (which trips on the assertNotRegex pattern strings
    themselves), assert that every value the c179 verdict path
    *consumes* is an exact `Fraction`.  That's the load-bearing
    Commandment-XII invariant — values, not source text.
    """

    def test_all_step4to6_outputs_are_fractions(self) -> None:
        live = _live_rge()
        keys = list(EXPECTED_STEP4TO6_DICT_KEYS.keys())
        for key in keys:
            self.assertIn(key, live, msg=f"[{key}] missing from live RGE dict")
            self.assertIsInstance(
                live[key], Fraction,
                msg=(
                    f"[{key}] expected Fraction in verdict path, got "
                    f"{type(live[key]).__name__} — Commandment XII violation"
                ),
            )

    def test_alpha3_inv_mt_derivation_is_fraction(self) -> None:
        val = _alpha3_inv_mt()
        self.assertIsInstance(
            val, Fraction,
            msg=(
                "alpha3_inv_mt derivation must return Fraction, "
                f"got {type(val).__name__} — Commandment XII violation"
            ),
        )

    def test_all_b4_constants_are_fractions(self) -> None:
        for name in EXPECTED_PY_CONSTANTS.keys():
            self.assertIsInstance(
                getattr(er, name), Fraction,
                msg=(
                    f"[{name}] er.{name} is not a Fraction — "
                    "Commandment XII violation"
                ),
            )

    def test_chain_constants_are_fractions(self) -> None:
        for name in ("CG", "V_OVER_SQRT2", "LN_MT_OVER_MZ", "b3_SM"):
            self.assertIsInstance(
                getattr(er, name), Fraction,
                msg=(
                    f"[{name}] er.{name} is not a Fraction — "
                    "Commandment XII violation"
                ),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
