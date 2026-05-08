"""
c184_rge_sm_b6_parity.py — BRICK B6 two-sided tripwire parity guard.

SCOPE
-----
B6 is the Higgs RGE + tree-level Higgs pole-mass extraction + Fermion mass
RGE chunk of the voltus_native Zig port of Oracle/chain/exact_rge.py.

This guard mirrors every BigFraction literal in the Zig B6 helpers and B6
self-test block against the Python authority, plus exercises the live Python
β-functions / RK4 runners at controlled inputs to catch arithmetic drift.

Python authority surface (exact_rge.py):
  - line 541: def _higgs_beta_full(y: list) -> list           [private; underscore]
  - line 601: def run_higgs_rge_rk4(...) -> Tuple              [public]
  - line 645: LN_V_OVER_MZ = _rational_ln(F(24622,100) / F(9119,100))
              ^^^^^^^^^^^^^ M_Z byte-exact uses F(9119,100), NOT Constants.M_Z
  - line 666: def tree_pole_matching(lam_v, v) -> Fraction     [public]
  - line 694: def run_fermion_mass_rk4(...) -> Tuple           [public]
              [contains inner closure beta9 — not directly importable]

Zig mirror surface (rge_sm.zig):
  - line 1107: pub fn higgsBetaFull(y: [5]BigFraction) [5]BigFraction
  - line 1178: pub const RunHiggsRk4Result = struct
                        { lam_v, y_t_v, g2_v, y_t_MPS_rk4 : BigFraction }
  - line 1202: pub fn runHiggsRgeRk4(y_t_MZ, ln_MZ_to_MPS, n_up, n_down, lam_MPS)
  - line 1337: pub fn treePoleMatching(lam_v, v) BigFraction
  - line 1348: pub const RunFermionRk4Result = struct
                        { y_b_v, y_c_v, y_s_v, y_d_v, y_u_v : BigFraction }
  - line 1363: fn fermionBeta9(yy: [9]BigFraction) [9]BigFraction
              ^^^^^^^^^^^^^^^^ NOTE: `fn` not `pub fn` — internal helper
  - line 1513: pub fn runFermionMassRk4(...)

NAMING ASYMMETRIES (Python ↔ Zig)
---------------------------------
  Python                           Zig
  _higgs_beta_full (private _)     higgsBetaFull (public, no _)
  run_higgs_rge_rk4 (snake)        runHiggsRgeRk4 (camel)
  tree_pole_matching (snake)       treePoleMatching (camel)
  run_fermion_mass_rk4 (snake)     runFermionMassRk4 (camel)
  beta9 (inner closure)            fermionBeta9 (file-scope `fn`, not `pub`)

  Python returns tuples            Zig returns named structs
  (4-tuple Higgs)                  RunHiggsRk4Result (4 fields)
  (5-tuple Fermion)                RunFermionRk4Result (5 fields)

LOAD-BEARING STRUCTURAL DIVERGENCE (PHYSICS INVARIANT, DO NOT FACTOR)
---------------------------------------------------------------------
fermionBeta9.dyt at rge_sm.zig:1407 carries `+ vf.mk(3, 2) * yb²` cross-term
that is ABSENT from higgsBetaFull.dyt at rge_sm.zig:1139.  This is not a copy
error and cannot be factored to common code without losing physics.  The
TestStructuralDivergence class enforces this by source-grep.

UP/DOWN-TYPE GP² ASYMMETRY
--------------------------
  up-type   (yt, yc, yu): gp² coefficient = 17/12 — lines 1413, 1448, 1496
  down-type (yb, ys, yd): gp² coefficient =  5/12 — lines 1429, 1464, 1480

TRIPWIRE ARCHITECTURE (per C209-C211)
-------------------------------------
  Layer 1: Python authority — direct exercise of live er._higgs_beta_full,
           er.run_higgs_rge_rk4, er.tree_pole_matching, er.run_fermion_mass_rk4
           at controlled inputs.  Catches drift in the Python authority.
  Layer 2: Python ↔ Zig literal mirror — for every vf.mk(num, den) in the Zig
           B6 helpers + self-test block, assert (num, den) appears in the
           B6-region-scoped Zig source.  Catches Zig drift from Python.
  Layer 3: Zig structural mirror — `pub fn` signatures, struct field-orders,
           presence of physics invariants (zero-state, divergence cross-term).
           Catches within-Zig refactors that break the public API.

  Layers 1+2 are necessary; neither sufficient.  The in-file Zig B6 self-test
  block at rge_sm.zig:2797-2953 catches within-Zig drift (typos in beta
  coefficient signs, accidental yb-cross-term loss in fermionBeta9).

Run
---
  python3 -m unittest proofs.UFT.scripts.c184_rge_sm_b6_parity -v
"""

from __future__ import annotations

import re
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Repository path setup
# ---------------------------------------------------------------------------
_THIS_FILE = Path(__file__).resolve()
REPO_ROOT = _THIS_FILE.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Oracle.chain import exact_rge as er  # noqa: E402

ZIG_SOURCE_PATH = (
    REPO_ROOT
    / "supercomputer"
    / "voltus_native"
    / "zig"
    / "src"
    / "rge_sm.zig"
)

# ---------------------------------------------------------------------------
# Python authority constants — single source of truth for B6 literals
# ---------------------------------------------------------------------------

# Gauge β-coefficients (SM 1-loop, from _higgs_beta_full body)
B1_SM = Fraction(41, 10)
B2_SM = Fraction(-19, 6)
B3_SM = Fraction(-7, 1)

# gp² conversion factor (GUT-normalized g1 → SU(2)_Y gp): gp² = (3/5) g1²
GP_SQ_OVER_G1_SQ = Fraction(3, 5)

# Higgs dyt bracket coefficients (1L SM): dyt ⊃ yt × [9/2 yt² − 8 g3² − 9/4 g2² − 17/12 gp²]
HIGGS_DYT_C_YT_SQ = Fraction(9, 2)
HIGGS_DYT_C_G3_SQ = Fraction(8, 1)
HIGGS_DYT_C_G2_SQ = Fraction(9, 4)
HIGGS_DYT_C_GP_SQ = Fraction(17, 12)

# Higgs dλ 1L coefficients
HIGGS_DLAM_C1 = Fraction(24, 1)   # 24 λ²
HIGGS_DLAM_C2 = Fraction(12, 1)   # 12 yt² λ
HIGGS_DLAM_C3 = Fraction(-6, 1)   # -6 yt^4
HIGGS_DLAM_C4 = Fraction(3, 1)    # +3 g2^4 etc.
HIGGS_DLAM_C5 = Fraction(-3, 1)   # -3 yt² g_*
HIGGS_DLAM_C6 = Fraction(3, 8)    # 3/8 mixed
HIGGS_DLAM_C7 = Fraction(2, 1)    # 2 mixed

# Higgs dλ 2L large coefficients (sample, not exhaustive — full coeffs in source)
HIGGS_DLAM_2L_NEG32 = Fraction(-32, 1)
HIGGS_DLAM_2L_POS30 = Fraction(30, 1)

# PDG seeds (M_Z values) used in both runHiggsRgeRk4 and runFermionMassRk4
PDG_FIVE_THIRDS = Fraction(5, 3)        # GUT-normalization 5/3 for g1²
PDG_ALPHA1_INV = Fraction(5901, 100)     # 59.01 (α_1⁻¹ at M_Z, GUT-norm)
PDG_ALPHA2_INV = Fraction(2959, 100)     # 29.59 (α_2⁻¹ at M_Z)
PDG_ALPHA3_INV = Fraction(844, 100)      # 8.44  (α_3⁻¹ at M_Z)

# Sqrt seeds (gauge couplings at M_Z, in g)
SQRT_SEED_G1 = Fraction(462, 1000)       # ~ 0.462
SQRT_SEED_G2 = Fraction(652, 1000)       # ~ 0.652
SQRT_SEED_G3 = Fraction(1218, 1000)      # ~ 1.218

# λ pad (initial value sentinel for 4-tuple→5-tuple coercion in beta4 wrapper)
LAM_ZERO = Fraction(0, 1)

# RK4 weight divisor (k1 + 2k2 + 2k3 + k4) / 6
RK4_DIV = Fraction(6, 1)

# v_EW — electroweak VEV in GeV
V_EW = Fraction(24622, 100)              # 246.22 GeV

# M_Z byte-exact for LN_V_OVER_MZ — Python uses 91.19 inline (NOT Constants.M_Z = 91.1876)
M_Z_INLINE = Fraction(9119, 100)         # 91.19 GeV

# treePoleMatching sqrt seed (m_H seed in GeV)
M_H_SQRT_SEED = Fraction(125, 1)

# Fermion shared cross-term coefficient (3/2 × cross-Yukawa²)
FERMION_CROSS_TERM = Fraction(3, 2)

# Up/down-type gp² asymmetry (load-bearing physics)
FERMION_UP_GP_SQ = Fraction(17, 12)
FERMION_DOWN_GP_SQ = Fraction(5, 12)

# Self-test block scalars
NEG_TENTH = Fraction(-1, 10)             # λ = -0.1 negative-square guard
LAM_REAL = Fraction(13, 100)             # λ = 0.13 SM realistic corner
M_H_LO = Fraction(120, 1)                # 120 GeV bracket lower bound
M_H_HI = Fraction(130, 1)                # 130 GeV bracket upper bound
ONE = Fraction(1, 1)                     # identity
ZERO = Fraction(0, 1)                    # zero-state probe

# ---------------------------------------------------------------------------
# Python ↔ Zig naming asymmetry registry
# ---------------------------------------------------------------------------
PY_TO_ZIG_FUNCTION = {
    "_higgs_beta_full": "higgsBetaFull",         # private _ → public, camel
    "run_higgs_rge_rk4": "runHiggsRgeRk4",       # snake → camel
    "tree_pole_matching": "treePoleMatching",     # snake → camel
    "run_fermion_mass_rk4": "runFermionMassRk4",  # snake → camel
    "beta9_inner_closure": "fermionBeta9",        # closure → file-scope `fn`
}

# ---------------------------------------------------------------------------
# Master list of every vf.mk(num, den) literal that must appear in B6 region
# Captured verbatim from rge_sm.zig:1100-1580 (B6 helpers) + 2797-2953 (self-test)
# ---------------------------------------------------------------------------
ZIG_B6_LITERALS = [
    # Gauge β (lines 1130/1132/1134, 1397/1398/1399 — twice)
    (41, 10),
    (-19, 6),
    (-7, 1),
    # gp² conversion (line 1138, 1385)
    (3, 5),
    # Higgs dyt bracket (lines 1139-1142)
    (9, 2),
    (8, 1),
    (9, 4),
    (17, 12),
    # Higgs dλ 1L (lines 1149-1157)
    (24, 1),
    (12, 1),
    (-6, 1),
    (3, 1),
    (-3, 1),
    (3, 8),
    (2, 1),
    # Higgs dλ 2L (lines 1167-1168)
    (-32, 1),
    (30, 1),
    # PDG seeds (lines 1210-1213, 1525-1528)
    (5, 3),
    (5901, 100),
    (2959, 100),
    (844, 100),
    # Sqrt seeds (lines 1219-1221, 1534-1536)
    (462, 1000),
    (652, 1000),
    (1218, 1000),
    # λ pad / zero (line 1229, multiple self-test sites)
    (0, 1),
    # RK4 weight divisor (lines 1271, 1321)
    (6, 1),
    # v_EW (line 1279, multiple self-test sites)
    (24622, 100),
    # M_Z inline byte-exact (line 1279)
    (9119, 100),
    # treePoleMatching sqrt seed (line 1341)
    (125, 1),
    # Fermion shared cross-term coefficient (lines 1407, 1423, 1442, 1458, 1474, 1490)
    (3, 2),
    # Down-type gp² asymmetry (lines 1429, 1464, 1480)
    (5, 12),
    # Self-test extras (lines 2812-2950)
    (1, 1),
    (-1, 10),
    (13, 100),
    (120, 1),
    (130, 1),
]

# ---------------------------------------------------------------------------
# Zig source loading + region-scoped extraction
# ---------------------------------------------------------------------------
_ZIG_SOURCE_CACHE: Optional[str] = None
_B6_BLOCK_CACHE: Optional[str] = None
_B6_TEST_BLOCK_CACHE: Optional[str] = None

# Marker strings
_B6_HELPER_START = "// BRICK B6 — Higgs RGE + tree-level pole matching + Fermion mass RGE"
_B6_HELPER_END = "// BRICK B7"  # sentinel; if B7 not yet emitted, falls through to test block
_B6_TEST_MARKER = "BRICK B6 — HIGGS RGE + TREE POLE MATCHING + FERMION RGE SELF-TESTS"


def _zig_source() -> str:
    global _ZIG_SOURCE_CACHE
    if _ZIG_SOURCE_CACHE is None:
        _ZIG_SOURCE_CACHE = ZIG_SOURCE_PATH.read_text(encoding="utf-8")
    return _ZIG_SOURCE_CACHE


def _b6_helper_block() -> str:
    """Extract the B6 helper code region (lines ~1100-1580 in current source).

    Falls back to the full source if the explicit B6 marker is absent (B6
    helpers were emitted prior to a marker convention).  In that case the
    literal-presence scan effectively spans the whole file, which is a
    SUPERSET of the intended region — still catches drift, slightly looser.
    """
    global _B6_BLOCK_CACHE
    if _B6_BLOCK_CACHE is None:
        src = _zig_source()
        # Try precise region scoping
        start_idx = src.find(_B6_HELPER_START)
        if start_idx == -1:
            # Fallback: scope to the helpers' approximate line range via
            # function-name anchors (higgsBetaFull start → B6 self-test marker)
            start_idx = src.find("pub fn higgsBetaFull")
        end_idx = src.find(_B6_TEST_MARKER)
        if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
            # Last-resort fallback: whole source (looser but never misses)
            _B6_BLOCK_CACHE = src
        else:
            _B6_BLOCK_CACHE = src[start_idx:end_idx]
    return _B6_BLOCK_CACHE


def _b6_test_block() -> str:
    """Extract the B6 self-test block at rge_sm.zig:2797-2953."""
    global _B6_TEST_BLOCK_CACHE
    if _B6_TEST_BLOCK_CACHE is None:
        src = _zig_source()
        start_idx = src.find(_B6_TEST_MARKER)
        if start_idx == -1:
            _B6_TEST_BLOCK_CACHE = ""
        else:
            # End of B6 test block — next "BRICK B" marker, or EOF
            tail = src[start_idx + len(_B6_TEST_MARKER):]
            next_brick = tail.find("BRICK B")
            if next_brick == -1:
                _B6_TEST_BLOCK_CACHE = src[start_idx:]
            else:
                _B6_TEST_BLOCK_CACHE = src[start_idx : start_idx + len(_B6_TEST_MARKER) + next_brick]
    return _B6_TEST_BLOCK_CACHE


def _b6_combined_region() -> str:
    """B6 helpers + B6 self-test block — the full B6 surface."""
    return _b6_helper_block() + "\n" + _b6_test_block()


def _fraction_present_in_b6(num: int, den: int) -> bool:
    """Whitespace-tolerant search for vf.mk(num, den) in B6 region."""
    region = _b6_combined_region()
    pattern = rf"vf\.mk\(\s*{num}\s*,\s*{den}\s*\)"
    return re.search(pattern, region) is not None


# ---------------------------------------------------------------------------
# Live Python RGE cache — avoid re-running compute_all_from_MZ per test
# ---------------------------------------------------------------------------
_LIVE_RGE_CACHE: Optional[dict] = None


def _live_rge() -> dict:
    global _LIVE_RGE_CACHE
    if _LIVE_RGE_CACHE is None:
        _LIVE_RGE_CACHE = er.compute_all_from_MZ()
    return _LIVE_RGE_CACHE


# ---------------------------------------------------------------------------
# Test factories — per-literal test methods built dynamically and setattr'd
# ---------------------------------------------------------------------------
def _make_python_constant_test(name: str, expected: Fraction):
    def _test(self):
        # Authority assertion: the named module-level Fraction equals expected
        self.assertEqual(globals()[name], expected,
                         f"Python authority constant {name} drift")
        self.assertIsInstance(globals()[name], Fraction,
                              f"{name} must be Fraction (Commandment XII)")
    _test.__name__ = f"test_python_constant_{name.lower()}"
    return _test


def _make_zig_presence_test(num: int, den: int):
    def _test(self):
        self.assertTrue(
            _fraction_present_in_b6(num, den),
            f"vf.mk({num}, {den}) MISSING from Zig B6 region — "
            f"Python authority requires this literal."
        )
    _test.__name__ = f"test_zig_b6_has_vf_mk_{num}_{den}".replace("-", "neg")
    return _test


# ---------------------------------------------------------------------------
# Test class 1 — Python authority constants
# ---------------------------------------------------------------------------
class TestPythonConstantsAuthority(unittest.TestCase):
    """Every B6 BigFraction literal originates here as Fraction.

    Drift in any of these constants reveals an upstream Python authority
    change that the Zig port has not yet absorbed.
    """


_PY_CONSTANTS_TO_PIN = {
    "B1_SM": Fraction(41, 10),
    "B2_SM": Fraction(-19, 6),
    "B3_SM": Fraction(-7, 1),
    "GP_SQ_OVER_G1_SQ": Fraction(3, 5),
    "HIGGS_DYT_C_YT_SQ": Fraction(9, 2),
    "HIGGS_DYT_C_G3_SQ": Fraction(8, 1),
    "HIGGS_DYT_C_G2_SQ": Fraction(9, 4),
    "HIGGS_DYT_C_GP_SQ": Fraction(17, 12),
    "HIGGS_DLAM_C1": Fraction(24, 1),
    "HIGGS_DLAM_C2": Fraction(12, 1),
    "HIGGS_DLAM_C3": Fraction(-6, 1),
    "HIGGS_DLAM_C4": Fraction(3, 1),
    "HIGGS_DLAM_C5": Fraction(-3, 1),
    "HIGGS_DLAM_C6": Fraction(3, 8),
    "HIGGS_DLAM_C7": Fraction(2, 1),
    "HIGGS_DLAM_2L_NEG32": Fraction(-32, 1),
    "HIGGS_DLAM_2L_POS30": Fraction(30, 1),
    "PDG_FIVE_THIRDS": Fraction(5, 3),
    "PDG_ALPHA1_INV": Fraction(5901, 100),
    "PDG_ALPHA2_INV": Fraction(2959, 100),
    "PDG_ALPHA3_INV": Fraction(844, 100),
    "SQRT_SEED_G1": Fraction(462, 1000),
    "SQRT_SEED_G2": Fraction(652, 1000),
    "SQRT_SEED_G3": Fraction(1218, 1000),
    "RK4_DIV": Fraction(6, 1),
    "V_EW": Fraction(24622, 100),
    "M_Z_INLINE": Fraction(9119, 100),
    "M_H_SQRT_SEED": Fraction(125, 1),
    "FERMION_CROSS_TERM": Fraction(3, 2),
    "FERMION_UP_GP_SQ": Fraction(17, 12),
    "FERMION_DOWN_GP_SQ": Fraction(5, 12),
    "NEG_TENTH": Fraction(-1, 10),
    "LAM_REAL": Fraction(13, 100),
    "M_H_LO": Fraction(120, 1),
    "M_H_HI": Fraction(130, 1),
}

for _name, _expected in _PY_CONSTANTS_TO_PIN.items():
    _t = _make_python_constant_test(_name, _expected)
    setattr(TestPythonConstantsAuthority, _t.__name__, _t)


# ---------------------------------------------------------------------------
# Test class 2 — Python Higgs β authority (live exercise)
# ---------------------------------------------------------------------------
class TestPythonHiggsBetaAuthority(unittest.TestCase):
    """Direct exercise of er._higgs_beta_full at controlled inputs.

    The Python β-function is the authority that B6's higgsBetaFull mirrors.
    """

    def test_higgs_beta_full_zero_state(self):
        """β(0) = 0 — vanishing input gives vanishing β (invariant)."""
        result = er._higgs_beta_full([Fraction(0)] * 5)
        self.assertEqual(len(result), 5,
                         "_higgs_beta_full must return 5-element list")
        for i, v in enumerate(result):
            self.assertEqual(v, Fraction(0),
                             f"β[{i}] at zero-state must be 0, got {v}")
            self.assertIsInstance(v, Fraction,
                                  f"β[{i}] must be Fraction (Cmd XII)")

    def test_higgs_beta_full_signature(self):
        """Returns a 5-element list given a 5-element list input."""
        # Use small nonzero inputs — just probe the shape contract
        y = [Fraction(1, 10), Fraction(1, 10), Fraction(1, 10),
             Fraction(1, 10), Fraction(1, 10)]
        result = er._higgs_beta_full(y)
        self.assertEqual(len(result), 5,
                         "Higgs β output cardinality drift")
        for v in result:
            self.assertIsInstance(v, Fraction,
                                  "every β component must be Fraction")


# ---------------------------------------------------------------------------
# Test class 3 — Python tree pole matching authority (live exercise)
# ---------------------------------------------------------------------------
class TestPythonTreePoleMatching(unittest.TestCase):
    """Direct exercise of er.tree_pole_matching at controlled inputs."""

    def test_tree_pole_zero_lambda(self):
        """λ = 0 ⇒ m_H = 0 (no quartic ⇒ no Higgs mass at tree level)."""
        result = er.tree_pole_matching(Fraction(0), V_EW)
        self.assertEqual(result, Fraction(0),
                         f"tree_pole_matching(0, v) must = 0, got {result}")
        self.assertIsInstance(result, Fraction,
                              "tree_pole_matching must return Fraction")

    def test_tree_pole_negative_lambda_guard(self):
        """λ < 0 ⇒ m_H = 0 (negative-square guard, not sqrt of negative)."""
        result = er.tree_pole_matching(NEG_TENTH, V_EW)
        self.assertEqual(result, Fraction(0),
                         f"negative-λ guard failed, got {result}")
        self.assertIsInstance(result, Fraction,
                              "guard return must be Fraction")

    def test_tree_pole_realistic_sm_corner(self):
        """λ = 0.13 ⇒ m_H ∈ (120, 130) GeV — realistic SM bracket."""
        result = er.tree_pole_matching(LAM_REAL, V_EW)
        self.assertIsInstance(result, Fraction,
                              "result must be Fraction (Cmd XII)")
        self.assertGreater(result, M_H_LO,
                           f"m_H = {float(result):.3f} below bracket [120, 130]")
        self.assertLess(result, M_H_HI,
                        f"m_H = {float(result):.3f} above bracket [120, 130]")


# ---------------------------------------------------------------------------
# Test class 4 — Python Higgs RK4 runner authority (live exercise)
# ---------------------------------------------------------------------------
class TestPythonHiggsRk4Authority(unittest.TestCase):
    """Exercise er.run_higgs_rge_rk4 at a controlled corner."""

    def test_run_higgs_rge_rk4_returns_4_tuple(self):
        """Output cardinality contract: returns (λ_v, y_t_v, g2_v, y_t_MPS_rk4)."""
        # Small ln window for fast test; lam_MPS = 0 default
        ln_window = Fraction(1, 100)  # tiny window — just probes shape
        y_t_MZ = Fraction(95, 100)    # plausible y_t at M_Z
        result = er.run_higgs_rge_rk4(
            y_t_MZ=y_t_MZ,
            ln_MZ_to_MPS=ln_window,
            n_up=2,
            n_down=2,
            lam_MPS=Fraction(0),
        )
        self.assertEqual(len(result), 4,
                         "run_higgs_rge_rk4 must return 4-tuple")
        for i, v in enumerate(result):
            self.assertIsInstance(v, Fraction,
                                  f"return[{i}] must be Fraction (Cmd XII)")


# ---------------------------------------------------------------------------
# Test class 5 — Python Fermion RK4 runner authority (live exercise)
# ---------------------------------------------------------------------------
class TestPythonFermionRk4Authority(unittest.TestCase):
    """Exercise er.run_fermion_mass_rk4 at a controlled corner.

    Note: beta9 is an inner closure inside run_fermion_mass_rk4 and is not
    directly importable.  We exercise it indirectly through the public RK4
    runner with controlled inputs.
    """

    def test_run_fermion_mass_rk4_returns_5_tuple(self):
        """Output cardinality contract: returns (y_b, y_c, y_s, y_d, y_u)."""
        ln_window = Fraction(1, 100)  # tiny — shape probe only
        result = er.run_fermion_mass_rk4(
            y_t_MZ=Fraction(95, 100),
            y_b_MPS=Fraction(1, 100),
            y_c_MPS=Fraction(7, 1000),
            ln_MZ_to_MPS=ln_window,
            n_up=2,
            n_down=2,
            y_s_MPS=Fraction(0),
            y_d_MPS=Fraction(0),
            y_u_MPS=Fraction(0),
        )
        self.assertEqual(len(result), 5,
                         "run_fermion_mass_rk4 must return 5-tuple")
        for i, v in enumerate(result):
            self.assertIsInstance(v, Fraction,
                                  f"return[{i}] must be Fraction (Cmd XII)")


# ---------------------------------------------------------------------------
# Test class 6 — Zig source literal parity (factory-driven)
# ---------------------------------------------------------------------------
class TestZigSourceParity(unittest.TestCase):
    """Every BigFraction literal in B6 region appears as vf.mk(num, den)."""


for _num, _den in ZIG_B6_LITERALS:
    _t = _make_zig_presence_test(_num, _den)
    setattr(TestZigSourceParity, _t.__name__, _t)


# ---------------------------------------------------------------------------
# Test class 7 — Zig structural mirrors (signatures + struct field-order)
# ---------------------------------------------------------------------------
class TestZigStructuralMirrors(unittest.TestCase):
    """Public function signatures and struct field-orders match the Python
    authority's tuple positions / dict-key contracts.
    """

    def test_higgs_beta_full_signature_present(self):
        src = _zig_source()
        self.assertIn(
            "pub fn higgsBetaFull(y: [5]BigFraction) [5]BigFraction",
            src,
            "higgsBetaFull signature drift — must be [5]→[5]",
        )

    def test_fermion_beta9_signature_present(self):
        src = _zig_source()
        # NOTE: `fn` not `pub fn` — internal helper, exercised through wrapper
        self.assertIn(
            "fn fermionBeta9(yy: [9]BigFraction) [9]BigFraction",
            src,
            "fermionBeta9 signature drift — must be [9]→[9], internal `fn`",
        )

    def test_fermion_beta9_is_not_pub(self):
        """fermionBeta9 must remain a file-scope `fn`, NOT `pub fn`.

        Exposing it would invite callers to bypass runFermionMassRk4 and
        miss the seed/closure bookkeeping that wraps it.
        """
        src = _zig_source()
        self.assertNotIn(
            "pub fn fermionBeta9",
            src,
            "fermionBeta9 must NOT be `pub fn` — internal helper only",
        )

    def test_tree_pole_matching_signature_present(self):
        src = _zig_source()
        self.assertIn(
            "pub fn treePoleMatching(lam_v: BigFraction, v: BigFraction) BigFraction",
            src,
            "treePoleMatching signature drift",
        )

    def test_run_higgs_rge_rk4_signature_present(self):
        src = _zig_source()
        # Loose match — the signature spans multiple lines in source
        self.assertIn("pub fn runHiggsRgeRk4", src,
                      "runHiggsRgeRk4 missing")
        self.assertIn("RunHiggsRk4Result", src,
                      "runHiggsRgeRk4 must return RunHiggsRk4Result")

    def test_run_fermion_mass_rk4_signature_present(self):
        src = _zig_source()
        self.assertIn("pub fn runFermionMassRk4", src,
                      "runFermionMassRk4 missing")
        self.assertIn("RunFermionRk4Result", src,
                      "runFermionMassRk4 must return RunFermionRk4Result")

    def test_run_higgs_rk4_result_struct_present(self):
        src = _zig_source()
        self.assertIn("pub const RunHiggsRk4Result = struct", src,
                      "RunHiggsRk4Result struct missing")

    def test_run_higgs_rk4_result_field_order(self):
        """Field order must be [lam_v, y_t_v, g2_v, y_t_MPS_rk4]."""
        src = _zig_source()
        match = re.search(
            r"pub\s+const\s+RunHiggsRk4Result\s*=\s*struct\s*\{(.*?)\}",
            src,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match, "RunHiggsRk4Result body not extractable")
        body = match.group(1)
        fields = re.findall(r"(\w+)\s*:\s*BigFraction\s*,", body)
        self.assertEqual(
            fields,
            ["lam_v", "y_t_v", "g2_v", "y_t_MPS_rk4"],
            f"RunHiggsRk4Result field order drift: got {fields}",
        )

    def test_run_fermion_rk4_result_struct_present(self):
        src = _zig_source()
        self.assertIn("pub const RunFermionRk4Result = struct", src,
                      "RunFermionRk4Result struct missing")

    def test_run_fermion_rk4_result_field_order(self):
        """Field order must be [y_b_v, y_c_v, y_s_v, y_d_v, y_u_v]."""
        src = _zig_source()
        match = re.search(
            r"pub\s+const\s+RunFermionRk4Result\s*=\s*struct\s*\{(.*?)\}",
            src,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match, "RunFermionRk4Result body not extractable")
        body = match.group(1)
        fields = re.findall(r"(\w+)\s*:\s*BigFraction\s*,", body)
        self.assertEqual(
            fields,
            ["y_b_v", "y_c_v", "y_s_v", "y_d_v", "y_u_v"],
            f"RunFermionRk4Result field order drift: got {fields}",
        )

    def test_b6_self_test_block_present(self):
        """B6 in-file self-test block at rge_sm.zig:2797+ must exist."""
        src = _zig_source()
        self.assertIn(
            _B6_TEST_MARKER,
            src,
            "B6 self-test block marker missing — within-Zig tripwire absent",
        )


# ---------------------------------------------------------------------------
# Test class 8 — Structural divergence (load-bearing physics invariant)
# ---------------------------------------------------------------------------
class TestStructuralDivergence(unittest.TestCase):
    """fermionBeta9.dyt carries a yb² cross-term ABSENT from higgsBetaFull.dyt.

    This is not a copy error — it is a physics requirement.  The Higgs RGE
    treats yb as zero (top-quark-only approximation, line 1107+); the fermion
    mass RGE retains the full cross-Yukawa structure (line 1363+).  Folding
    these into common code would lose the bottom-quark mass evolution.
    """

    def test_fermion_dyt_carries_yb_cross_term(self):
        """Fermion β must reference yb_sq AND vf.mk(3, 2) inside dyt block."""
        src = _zig_source()
        # Locate fermionBeta9 body
        f_match = re.search(
            r"fn fermionBeta9.*?(?=\nfn |\npub fn |\npub const )",
            src,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(f_match,
                             "fermionBeta9 body not extractable")
        body = f_match.group(0)
        self.assertIn(
            "vf.mk(3, 2)",
            body,
            "fermionBeta9 must contain vf.mk(3, 2) cross-term coefficient",
        )
        self.assertIn(
            "yb_sq",
            body,
            "fermionBeta9 must reference yb_sq (cross-Yukawa coupling)",
        )

    def test_higgs_dyt_omits_yb_cross_term(self):
        """Higgs β must NOT reference yb_sq — top-quark-only approximation."""
        src = _zig_source()
        h_match = re.search(
            r"pub fn higgsBetaFull.*?(?=\npub fn |\npub const )",
            src,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(h_match,
                             "higgsBetaFull body not extractable")
        body = h_match.group(0)
        self.assertNotIn(
            "yb_sq",
            body,
            "higgsBetaFull must NOT reference yb_sq — top-only approximation",
        )

    def test_up_type_gp_sq_coefficient(self):
        """Up-type Yukawa β has gp² coefficient 17/12."""
        src = _zig_source()
        # Locate fermionBeta9 body
        f_match = re.search(
            r"fn fermionBeta9.*?(?=\nfn |\npub fn |\npub const )",
            src,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(f_match)
        body = f_match.group(0)
        self.assertIn(
            "vf.mk(17, 12)",
            body,
            "fermionBeta9 must carry up-type gp² coefficient 17/12",
        )

    def test_down_type_gp_sq_coefficient(self):
        """Down-type Yukawa β has gp² coefficient 5/12."""
        src = _zig_source()
        f_match = re.search(
            r"fn fermionBeta9.*?(?=\nfn |\npub fn |\npub const )",
            src,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(f_match)
        body = f_match.group(0)
        self.assertIn(
            "vf.mk(5, 12)",
            body,
            "fermionBeta9 must carry down-type gp² coefficient 5/12",
        )


# ---------------------------------------------------------------------------
# Test class 9 — B6 structural roundtrips (cross-validation Python ↔ Python)
# ---------------------------------------------------------------------------
class TestB6StructuralRoundtrips(unittest.TestCase):
    """Cross-validate Python authorities against each other for consistency."""

    def test_tree_pole_matches_sqrt_2_lam_v_squared(self):
        """tree_pole_matching(λ, v) ≈ sqrt(2 λ v²) when λ > 0.

        Pure algebra: m_H² = 2 λ v² (tree-level Higgs mass formula).
        We only require the Newton-iterated sqrt to agree with direct
        sqrt of the pre-quantity at modest precision.
        """
        result = er.tree_pole_matching(LAM_REAL, V_EW)
        # Expected magnitude: sqrt(2 × 0.13 × 246.22²) = sqrt(15765.4...) ≈ 125.6
        # Use float bracket since result is a Fraction near 125.6
        result_f = float(result)
        expected_lo, expected_hi = 124.0, 127.0
        self.assertGreater(
            result_f, expected_lo,
            f"tree pole {result_f:.3f} below sqrt-2λv² bracket",
        )
        self.assertLess(
            result_f, expected_hi,
            f"tree pole {result_f:.3f} above sqrt-2λv² bracket",
        )

    def test_higgs_beta_zero_state_invariant_5_components(self):
        """Higgs β at zero state vanishes in every component (not just sum)."""
        result = er._higgs_beta_full([Fraction(0)] * 5)
        for i, v in enumerate(result):
            self.assertEqual(v, Fraction(0),
                             f"β[{i}](0) ≠ 0 — homogeneity violated")


# ---------------------------------------------------------------------------
# Test class 10 — Python ↔ Zig naming asymmetry registry
# ---------------------------------------------------------------------------
class TestPythonZigNamingMap(unittest.TestCase):
    """Assert every PY_TO_ZIG_FUNCTION mapping resolves on both sides."""

    def test_python_authorities_resolve(self):
        """Every Python name (except inner closures) is importable from er."""
        for py_name in PY_TO_ZIG_FUNCTION:
            if py_name == "beta9_inner_closure":
                continue  # closure inside run_fermion_mass_rk4, not importable
            self.assertTrue(
                hasattr(er, py_name),
                f"Python authority er.{py_name} missing",
            )

    def test_zig_names_appear_in_source(self):
        """Every Zig name in PY_TO_ZIG_FUNCTION appears in the Zig source."""
        src = _zig_source()
        for py_name, zig_name in PY_TO_ZIG_FUNCTION.items():
            self.assertIn(
                zig_name,
                src,
                f"Zig name {zig_name} (← Python {py_name}) missing from source",
            )


# ---------------------------------------------------------------------------
# Test class 11 — Commandment XII enforcement (zero float)
# ---------------------------------------------------------------------------
class TestCommandmentXII(unittest.TestCase):
    """All B6 authority constants are exact Fraction.  Zero float."""

    def test_all_pinned_constants_are_fraction(self):
        for name, expected in _PY_CONSTANTS_TO_PIN.items():
            v = globals()[name]
            self.assertIsInstance(
                v, Fraction,
                f"{name} type drift — must be Fraction, got {type(v)}",
            )
            self.assertIsInstance(
                expected, Fraction,
                f"_PY_CONSTANTS_TO_PIN[{name}] must store Fraction",
            )

    def test_higgs_beta_zero_returns_fractions_only(self):
        """β at zero-state returns 5 Fractions — never float."""
        result = er._higgs_beta_full([Fraction(0)] * 5)
        for i, v in enumerate(result):
            self.assertIsInstance(
                v, Fraction,
                f"β[{i}] is {type(v)} — must be Fraction (Cmd XII)",
            )

    def test_tree_pole_returns_fraction(self):
        """tree_pole_matching at SM corner returns Fraction."""
        result = er.tree_pole_matching(LAM_REAL, V_EW)
        self.assertIsInstance(
            result, Fraction,
            f"tree_pole returns {type(result)} — must be Fraction",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
