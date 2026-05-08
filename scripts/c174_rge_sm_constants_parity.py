"""
c174 — B1 parity guard for supercomputer/voltus_native/zig/src/rge_sm.zig.

Every exact-ℚ constant and β-matrix entry declared in the Zig skeleton
(Brick B1 of the rge_sm port) must match its counterpart in the Python
authoritative source (`Oracle/chain/exact_rge.py`) bit-for-bit on both
numerator and denominator.

Commandments satisfied:
 I   — Honesty: the Zig file's rational literals ARE what Python computes.
 III — Receipts: every assertion is an executable bit-exact check.
 XII — Zero numerical error: all comparisons are integer/integer.
 XIII — Nothing trivial: every literal — including 1/1, 3/1, 2/1 — is mirrored.

Method: parse `rge_sm.zig` with a regex, extract every `vf.mk(NUM, DEN)`
literal declared inside the `pub const Constants` block and the
`pub const BetaTables` block, build a lookup table {name → (num, den)},
and assert each entry matches a known Python Fraction. Any extra Zig
literal (unknown name) is flagged; any missing Python mirror is flagged.

Invocation:
    python3 -m unittest proofs.UFT.scripts.c174_rge_sm_constants_parity -v

This is the sandbox-side half of B1 closure. The Mac-side half is
`zig build test` at supercomputer/voltus_native/zig/; that receipt
is deferred to Lamar's local run.
"""

from __future__ import annotations

import os
import re
import unittest
from fractions import Fraction

# ──────────────────────────────────────────────────────────────────────────
# Locate the Zig source file and import Python authoritative constants.
# ──────────────────────────────────────────────────────────────────────────

REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

ZIG_SRC = os.path.join(
    REPO_ROOT,
    "supercomputer",
    "voltus_native",
    "zig",
    "src",
    "rge_sm.zig",
)

# Import the Python authority.
import sys
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from Oracle.chain import exact_rge as er  # noqa: E402


# ──────────────────────────────────────────────────────────────────────────
# Zig parser — extract (name, num, den) triples from `vf.mk(...)` literals
# under `pub const Constants` and `pub const BetaTables`.
# ──────────────────────────────────────────────────────────────────────────

VF_MK_RE = re.compile(
    r"vf\.mk\(\s*(-?\d+)\s*,\s*(\d+)\s*\)"
)

# Matches `pub const NAME: BigFraction = vf.mk(NUM, DEN);`
SCALAR_RE = re.compile(
    r"pub\s+const\s+([A-Z0-9_]+)\s*:\s*BigFraction\s*=\s*vf\.mk\(\s*(-?\d+)\s*,\s*(\d+)\s*\)\s*;"
)

# Matches `pub const NAME: i128 = LITERAL;` for scalar integer constants
# (i128 literals, not Fractions — used for `M_PS_LOG10_NUM`, etc.)
I128_RE = re.compile(
    r"pub\s+const\s+([A-Z0-9_]+)\s*:\s*i128\s*=\s*(-?[\d_]+)\s*;"
)

# Matches a 3×3 β-matrix literal:  pub const NAME: BetaMatrix3x3 = .{ ... };
BETA_MATRIX_RE = re.compile(
    r"pub\s+const\s+(b2_SM_matrix|b2_PS_matrix)\s*:\s*BetaMatrix3x3\s*=\s*\.\{(.*?)\}\s*;",
    re.DOTALL,
)


def _read_zig_source() -> str:
    with open(ZIG_SRC, "r", encoding="utf-8") as fh:
        return fh.read()


def _parse_scalar_fractions(source: str) -> dict[str, tuple[int, int]]:
    """Return {name → (num, den)} for every `pub const NAME: BigFraction = vf.mk(...)`."""
    return {
        name: (int(num), int(den))
        for name, num, den in SCALAR_RE.findall(source)
    }


def _parse_i128_literals(source: str) -> dict[str, int]:
    """Return {name → value} for every `pub const NAME: i128 = LITERAL;`."""
    return {
        name: int(val.replace("_", ""))
        for name, val in I128_RE.findall(source)
    }


def _parse_beta_matrices(source: str) -> dict[str, list[list[tuple[int, int]]]]:
    """Extract b2_SM_matrix and b2_PS_matrix as [row][col] → (num, den)."""
    out: dict[str, list[list[tuple[int, int]]]] = {}
    for name, body in BETA_MATRIX_RE.findall(source):
        rows = []
        # Each row is a `.{ vf.mk(...), vf.mk(...), vf.mk(...) }` block.
        # Split on top-level closing braces that end a row.
        for row_match in re.finditer(r"\.\{([^{}]*?)\}\s*,?", body):
            row_body = row_match.group(1)
            entries = VF_MK_RE.findall(row_body)
            if len(entries) == 3:
                rows.append([(int(n), int(d)) for n, d in entries])
        assert len(rows) == 3, f"{name} did not parse as 3×3 (got {len(rows)} rows)"
        out[name] = rows
    return out


# ──────────────────────────────────────────────────────────────────────────
# Expected Zig-name → Python-value mapping.
#
# The LHS is the exact Zig identifier under Constants.NAME.
# The RHS is either:
#   (a) a Python Fraction object already declared in exact_rge, or
#   (b) a literal Fraction built inline from the Python authority.
#
# Every entry in this dict MUST also appear in rge_sm.zig under
# `pub const Constants = struct { ... }`. Any mismatch is a B1 violation.
# ──────────────────────────────────────────────────────────────────────────

# Helper: pre-reduce to Fraction terms so both sides compare on reduced form.
def _F(num: int, den: int) -> Fraction:
    return Fraction(num, den)


# (name, python-authority) pairs. The python side must equal the Zig side
# AFTER both are reduced to lowest terms — that's what BigFraction and
# Python Fraction both do on construction.
EXPECTED_SCALARS: dict[str, Fraction] = {
    # ── Energy scales / EWSB ──
    "M_Z":                 er.M_Z,
    "ALPHA_EM_INV_MZ":     er.ALPHA_EM_INV_MZ,
    "SIN2_TW_MZ":          er.SIN2_TW_MZ,
    "ALPHA_S_MZ":          er.ALPHA_S_MZ,
    "V_HIGGS":             er.V_HIGGS,

    # ── Transcendentals ──
    "PI":                  er.PI,
    "LN10":                er.LN10,
    "SQRT2":               er.SQRT2,

    # ── Cascade theorems ──
    "CASCADE_R":           er.r,
    "CASCADE_XI":          er.xi,
    "CASCADE_CG":          er.CG,
    "GAMMA_GRAV":          er.gamma_grav,
    "GAMMA_INFO":          er.gamma_info,

    # ── 1-loop β ──
    "B1_SM":               er.b1_SM,
    "B2_SM":               er.b2_SM,
    "B3_SM":               er.b3_SM,
    "B4_PS":               er.b4_PS,
    "B2L_PS":              er.b2L_PS,
    "B2R_PS":              er.b2R_PS,
    "B8":                  er.b8,

    # ── 3-loop β ──
    "B3_SM_3LOOP_NF6":     er.b3_SM_3loop_nf6,
    "B3_SM_3LOOP_NF5":     er.b3_SM_3loop_nf5,
    "B1_SM_3LOOP":         er.b1_SM_3loop,
    "B2_SM_3LOOP":         er.b2_SM_3loop,
    "B4_PS_3LOOP":         er.b4_PS_3loop,
    "B2L_PS_3LOOP":        er.b2L_PS_3loop,
    "B2R_PS_3LOOP":        er.b2R_PS_3loop,

    # ── Threshold + Casimir ──
    "T_FUND":              er.T_FUND,
    "T_ADJ_SU4":           er.T_ADJ_SU4,
    "T_ADJ_SU2":           er.T_ADJ_SU2,
    "T_10_SU4":            er.T_10_SU4,
    "C_VECTOR":            er.C_VECTOR,
    "LN_ETA_MPS":          er.LN_ETA_MPS,
    "DELTA_C2":            er.DELTA_C2,

    # ── VEV ratios ──
    "VEV_A":               er.VEV_A,
    "VEV_B":               er.VEV_B,
    "VEV_C":               er.VEV_C,

    # ── Fermion mass-chain ──
    "GJ_3RD_GEN":          er.GJ_3RD_GEN,
    "GJ_2ND_GEN":          er.GJ_2ND_GEN,
    "GJ_1ST_GEN":          er.GJ_1ST_GEN,
    "CG_CHARM":            er.CG_CHARM,
    "CG_UP":               er.CG_UP,
    "CG_VUB":              er.CG_VUB,
    "EPSILON_FN":          er.EPSILON_FN,

    # ── Measured fermion masses (GeV) ──
    "M_TAU":               er.M_TAU,
    "M_MUON":              er.M_MUON,
    "M_ELECTRON":          er.M_ELECTRON,
    "M_TOP_MEAS":          er.M_TOP_MEAS,
    "M_BOTTOM_MEAS":       er.M_BOTTOM_MEAS,
    "M_CHARM_MEAS":        er.M_CHARM_MEAS,
    "M_STRANGE_MEAS":      er.M_STRANGE_MEAS,
    "M_DOWN_MEAS":         er.M_DOWN_MEAS,
    "M_UP_MEAS":           er.M_UP_MEAS,

    # ── CKM measured ──
    "V_US_MEAS":           er.V_US_MEAS,
    "V_CB_MEAS":           er.V_CB_MEAS,
    "V_UB_MEAS":           er.V_UB_MEAS,

    # ── ν mass-squared splittings ──
    "DM2_ATM":             er.DM2_ATM,
    "DM2_SOL":             er.DM2_SOL,

    # ── PMNS measured (degrees) ──
    "THETA_23_MEAS_DEG":   er.THETA_23_MEAS,
    "THETA_12_MEAS_DEG":   er.THETA_12_MEAS,
    "THETA_13_MEAS_DEG":   er.THETA_13_MEAS,

    # ── Anomalous dimensions ──
    "GAMMA_0_QCD":         er.GAMMA_0_QCD,
    "GAMMA_1_QCD":         er.GAMMA_1_QCD,
    "BETA_0_QCD":          er.BETA_0_QCD,
    "BETA_1_QCD":          er.BETA_1_QCD,
    "D1_QCD":              er.D1_QCD,
    "GAMMA_0_PS":          er.GAMMA_0_PS,

    # ── Chetyrkin pole-matching ──
    "K2_CHETYRKIN":        er.K2_CHETYRKIN,
    "K3_CHETYRKIN":        er.K3_CHETYRKIN,

    # ── Cosmology ──
    "OMEGA_M_OBS":         er.OMEGA_M_OBS,
    "OMEGA_LAMBDA_OBS":    er.OMEGA_LAMBDA_OBS,
    "OMEGA_M_SC":          er.OMEGA_M_SC,
    "M_HIGGS_MEAS":        er.M_HIGGS_MEAS,

    # ── B3 additions (C211): 2π, 4π, 1/α_s(M_Z), log₁₀ & ln scale ratios ──
    # These land as direct BigFraction constants in the Zig Constants block
    # (not as i128 pairs) — range-reduced ln pre-computed at comptime to
    # avoid re-reducing on every runCouplingInv call.
    "TWO_PI":              er.TWO_PI,
    "FOUR_PI":             er.FOUR_PI,
    "ALPHA_S_INV_MZ":      er.ALPHA_S_INV_MZ,
    "LOG10_MZ":            er.LOG10_MZ,
    "LOG10_MPS":           er.LOG10_MPS,
    "LOG10_M8":            er.LOG10_M8,
    "LOG10_MLR":           er.LOG10_MLR,
    "LOG10_MT_OVER_MZ":    er.LOG10_MT_OVER_MZ,
    "LN_MPS_OVER_MZ":      er.LN_MPS_OVER_MZ,
    "LN_M8_OVER_MZ":       er.LN_M8_OVER_MZ,
    "LN_MLR_OVER_MZ":      er.LN_MLR_OVER_MZ,
    "LN_M8_OVER_MPS":      er.LN_M8_OVER_MPS,
    "LN_MLR_OVER_MPS":     er.LN_MLR_OVER_MPS,
    "LN_MT_OVER_MZ":       er.LN_MT_OVER_MZ,
}


EXPECTED_I128: dict[str, int] = {
    # ── Cascade integer theorems ──
    "N_GAUGE":             int(er.N_GAUGE),
    "N_GEN":               int(er.n_gen),

    # ── Scale log₁₀ numerators/denominators ──
    # Python stores LOG10_MPS = Fraction(1370, 100); Zig splits into NUM/DEN.
    "M_PS_LOG10_NUM":      er.LOG10_MPS.numerator,
    "M_PS_LOG10_DEN":      er.LOG10_MPS.denominator,
    "M_LR_LOG10_NUM":      er.LOG10_MLR.numerator,
    "M_LR_LOG10_DEN":      er.LOG10_MLR.denominator,
    "M_8_LOG10_NUM":       er.LOG10_M8.numerator,
    "M_8_LOG10_DEN":       er.LOG10_M8.denominator,

    # ── H₀ pre-power (10⁻⁴² applied at use site) ──
    # H0_POW_OF_10 is typed `i32` in Zig (not i128) — covered by
    # TestDerivedIdentities.test_h0_reconstruction which verifies
    # H0_PRE * 10^H0_POW_OF_10 == Python er.H0_GEV bit-exactly.
    "H0_PRE_NUM":          14369,
    "H0_PRE_DEN":          10000,

    # ── Numerical limiter ──
    "FRACTION_PRECISION":  er.FRACTION_PRECISION,
}


# ── β-matrix authority — mirrors exact_rge.b2_SM_matrix / b2_PS_matrix ──

EXPECTED_B2_SM_MATRIX: list[list[Fraction]] = [
    [er.b2_SM_matrix[i][j] for j in range(3)] for i in range(3)
]

EXPECTED_B2_PS_MATRIX: list[list[Fraction]] = [
    [er.b2_PS_matrix[i][j] for j in range(3)] for i in range(3)
]


# ──────────────────────────────────────────────────────────────────────────
# Test class 1 — scalar BigFraction constants.
# ──────────────────────────────────────────────────────────────────────────

class TestScalarConstantsParity(unittest.TestCase):
    """Every Zig Constants.NAME BigFraction matches Python exact_rge bit-for-bit."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_zig_source()
        cls.zig_scalars = _parse_scalar_fractions(cls.source)

    def test_parser_captured_at_least_60_scalar_fractions(self):
        """Guard against regex regression — skeleton has ≥60 BigFraction constants."""
        self.assertGreaterEqual(
            len(self.zig_scalars),
            60,
            f"Only {len(self.zig_scalars)} BigFraction constants parsed — "
            "regex likely regressed or constants deleted.",
        )

    def test_every_expected_name_present_in_zig(self):
        """Every entry in EXPECTED_SCALARS appears in the Zig source."""
        missing = [
            name for name in EXPECTED_SCALARS
            if name not in self.zig_scalars
        ]
        self.assertEqual(
            missing,
            [],
            f"Python expects these Zig constants but they aren't declared: {missing}",
        )

    def test_every_zig_name_has_python_mirror(self):
        """Every Zig BigFraction in Constants has a Python mirror in EXPECTED_SCALARS.

        No unmirrored literals — Commandment XIII forbids silent literals.
        """
        unknown = [
            name for name in self.zig_scalars
            if name not in EXPECTED_SCALARS
        ]
        self.assertEqual(
            unknown,
            [],
            f"Zig declares BigFraction constants without a Python mirror: {unknown}. "
            "Every literal must have an EXPECTED_SCALARS entry (Commandment XIII).",
        )


def _make_scalar_test(name: str, expected: Fraction):
    """Factory generating one assertEqual method per scalar literal."""
    def test(self):
        self.assertIn(
            name,
            self.zig_scalars,
            f"Zig missing Constants.{name}",
        )
        zig_num, zig_den = self.zig_scalars[name]
        zig_frac = Fraction(zig_num, zig_den)
        self.assertEqual(
            zig_frac,
            expected,
            (
                f"Constants.{name} drift:\n"
                f"  Zig    = {zig_num}/{zig_den} = {zig_frac}\n"
                f"  Python = {expected.numerator}/{expected.denominator} = {expected}"
            ),
        )
    test.__name__ = f"test_scalar_{name}"
    test.__doc__ = f"Zig Constants.{name} == Python authority (bit-exact)"
    return test


# Attach one test method per scalar. This way every literal shows up
# as its own green line in the unittest output — receipts, Commandment III.
for _name, _expected in EXPECTED_SCALARS.items():
    setattr(
        TestScalarConstantsParity,
        f"test_scalar_{_name}",
        _make_scalar_test(_name, _expected),
    )


# ──────────────────────────────────────────────────────────────────────────
# Test class 2 — i128 integer constants (log10 splits, FRACTION_PRECISION).
# ──────────────────────────────────────────────────────────────────────────

class TestI128ConstantsParity(unittest.TestCase):
    """Every Zig `pub const NAME: i128` matches the Python authoritative value."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_zig_source()
        cls.zig_i128 = _parse_i128_literals(cls.source)

    def test_parser_captured_at_least_10_i128_literals(self):
        self.assertGreaterEqual(
            len(self.zig_i128),
            10,
            f"Only {len(self.zig_i128)} i128 literals parsed — "
            "regex likely regressed or constants deleted.",
        )


def _make_i128_test(name: str, expected: int):
    def test(self):
        self.assertIn(
            name,
            self.zig_i128,
            f"Zig missing Constants.{name}",
        )
        self.assertEqual(
            self.zig_i128[name],
            expected,
            f"Constants.{name}: Zig = {self.zig_i128[name]}, Python = {expected}",
        )
    test.__name__ = f"test_i128_{name}"
    test.__doc__ = f"Zig Constants.{name} == Python authority (integer)"
    return test


for _name, _expected in EXPECTED_I128.items():
    setattr(
        TestI128ConstantsParity,
        f"test_i128_{_name}",
        _make_i128_test(_name, _expected),
    )


# ──────────────────────────────────────────────────────────────────────────
# Test class 3 — 2-loop β-matrices (SM and PS, 3×3 each = 18 entries total).
# ──────────────────────────────────────────────────────────────────────────

class TestBetaMatricesParity(unittest.TestCase):
    """Every entry of b2_SM_matrix and b2_PS_matrix matches Python bit-for-bit."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_zig_source()
        cls.zig_matrices = _parse_beta_matrices(cls.source)

    def test_both_matrices_parsed(self):
        self.assertIn("b2_SM_matrix", self.zig_matrices)
        self.assertIn("b2_PS_matrix", self.zig_matrices)

    def test_shapes_are_3x3(self):
        for name in ("b2_SM_matrix", "b2_PS_matrix"):
            self.assertEqual(len(self.zig_matrices[name]), 3,
                             f"{name}: wrong number of rows")
            for i, row in enumerate(self.zig_matrices[name]):
                self.assertEqual(len(row), 3,
                                 f"{name}[{i}]: wrong number of columns")


def _make_matrix_entry_test(matrix_name: str, i: int, j: int, expected: Fraction):
    def test(self):
        mat = self.zig_matrices[matrix_name]
        zig_num, zig_den = mat[i][j]
        zig_frac = Fraction(zig_num, zig_den)
        self.assertEqual(
            zig_frac,
            expected,
            (
                f"{matrix_name}[{i}][{j}] drift:\n"
                f"  Zig    = {zig_num}/{zig_den} = {zig_frac}\n"
                f"  Python = {expected.numerator}/{expected.denominator} = {expected}"
            ),
        )
    test.__name__ = f"test_{matrix_name}_{i}_{j}"
    test.__doc__ = f"{matrix_name}[{i}][{j}] == Python exact_rge authority"
    return test


for _i in range(3):
    for _j in range(3):
        setattr(
            TestBetaMatricesParity,
            f"test_b2_SM_matrix_{_i}_{_j}",
            _make_matrix_entry_test(
                "b2_SM_matrix", _i, _j, EXPECTED_B2_SM_MATRIX[_i][_j]
            ),
        )
        setattr(
            TestBetaMatricesParity,
            f"test_b2_PS_matrix_{_i}_{_j}",
            _make_matrix_entry_test(
                "b2_PS_matrix", _i, _j, EXPECTED_B2_PS_MATRIX[_i][_j]
            ),
        )


# ──────────────────────────────────────────────────────────────────────────
# Test class 4 — cross-check DERIVED identities.
#
# The Zig file sometimes stores a derived constant directly (e.g. VEV_C =
# -201/250) rather than the Python-style expression (VEV_C = -2·VEV_A - VEV_B).
# This class confirms the *derived* values are algebraically correct so that
# any silent drift in the underlying theorems gets caught.
# ──────────────────────────────────────────────────────────────────────────

class TestDerivedIdentities(unittest.TestCase):
    """Algebraic identities that the Zig literals must satisfy."""

    def test_cascade_r_times_CG_equals_1(self):
        """r · CG = 1 at N=8 (cascade Rosetta-stone identity)."""
        self.assertEqual(er.r * er.CG, Fraction(1))

    def test_vev_tracelessness(self):
        """4·VEV_A + 2·VEV_B + 2·VEV_C = 0 (SU(8) adjoint tracelessness)."""
        total = 4 * er.VEV_A + 2 * er.VEV_B + 2 * er.VEV_C
        self.assertEqual(total, Fraction(0))

    def test_omega_m_sc_from_gamma(self):
        """Ω_m(sc) = 3γ/(3γ+8) with γ = 63/8 → 189/253."""
        gamma = er.gamma_info
        expected = 3 * gamma / (3 * gamma + 8)
        self.assertEqual(expected, Fraction(189, 253))
        self.assertEqual(er.OMEGA_M_SC, Fraction(189, 253))

    def test_d1_qcd_equals_4_over_7(self):
        """d₁^QCD = γ₀/(2β₀) = 8/14 = 4/7."""
        self.assertEqual(er.D1_QCD, Fraction(4, 7))

    def test_delta_c2_equals_13_over_24(self):
        """ΔC₂ = C₂(SU(4)) − C₂(SU(3)) = 15/8 − 4/3 = 13/24."""
        c2_su4 = Fraction(15, 8)
        c2_su3 = Fraction(4, 3)
        self.assertEqual(c2_su4 - c2_su3, Fraction(13, 24))
        self.assertEqual(er.DELTA_C2, Fraction(13, 24))

    def test_n_gen_is_3(self):
        """n_gen = 3 (spectral half-count theorem, C96)."""
        self.assertEqual(int(er.n_gen), 3)

    def test_n_gauge_is_8(self):
        """SU(N_gauge) = SU(8)."""
        self.assertEqual(int(er.N_GAUGE), 8)

    def test_gamma_grav_7_over_18(self):
        """Fisher gravity coefficient γ_grav = 7/18 (cascade chain → G_N)."""
        self.assertEqual(er.gamma_grav, Fraction(7, 18))

    def test_gamma_info_63_over_8(self):
        """Fisher CC coefficient γ_info = (N²-1)/N = 63/8."""
        self.assertEqual(er.gamma_info, Fraction(63, 8))

    def test_cascade_xi_15_over_49(self):
        """Cascade parameter ξ = 15/49 (proven, Cartan = Laplacian)."""
        self.assertEqual(er.xi, Fraction(15, 49))

    def test_cascade_r_9_over_8(self):
        """Cascade ratio r = (N+1)/N = 9/8 (9-part proof, C128)."""
        self.assertEqual(er.r, Fraction(9, 8))

    def test_cascade_cg_8_over_9(self):
        """Cascade CG = N/(N+1) = 8/9 (spectral suppression at PS)."""
        self.assertEqual(er.CG, Fraction(8, 9))

    def test_h0_reconstruction(self):
        """Zig H0_PRE × 10^H0_POW_OF_10 == Python er.H0_GEV (bit-exact).

        Python authority (exact_rge.py line 354):
            H0_GEV = Fraction(14369, 10000) * Fraction(1, 10**42)

        Zig stores this as three separate constants:
            H0_PRE_NUM  = 14369  (i128)
            H0_PRE_DEN  = 10000  (i128)
            H0_POW_OF_10 = -42   (i32)

        The combined rational must equal Python's H0_GEV exactly.
        """
        # Parse Zig H0 constants from the file
        src = _read_zig_source()
        m_pre_num = re.search(r"pub\s+const\s+H0_PRE_NUM\s*:\s*i128\s*=\s*(-?\d+)\s*;", src)
        m_pre_den = re.search(r"pub\s+const\s+H0_PRE_DEN\s*:\s*i128\s*=\s*(-?\d+)\s*;", src)
        m_pow     = re.search(r"pub\s+const\s+H0_POW_OF_10\s*:\s*i32\s*=\s*(-?\d+)\s*;", src)
        self.assertIsNotNone(m_pre_num, "Zig Constants.H0_PRE_NUM not found")
        self.assertIsNotNone(m_pre_den, "Zig Constants.H0_PRE_DEN not found")
        self.assertIsNotNone(m_pow,     "Zig Constants.H0_POW_OF_10 not found")
        zig_num = int(m_pre_num.group(1))
        zig_den = int(m_pre_den.group(1))
        zig_pow = int(m_pow.group(1))

        # Reconstruct: H0 = (num/den) × 10^pow, assembled as exact Fraction
        if zig_pow >= 0:
            zig_h0 = Fraction(zig_num, zig_den) * Fraction(10 ** zig_pow, 1)
        else:
            zig_h0 = Fraction(zig_num, zig_den) * Fraction(1, 10 ** (-zig_pow))

        self.assertEqual(
            zig_h0,
            er.H0_GEV,
            f"H0 reconstruction mismatch: Zig {zig_h0} vs Python er.H0_GEV {er.H0_GEV}",
        )


# ──────────────────────────────────────────────────────────────────────────
# Test class 5 — source invariants (size, version string, no-drift markers).
# ──────────────────────────────────────────────────────────────────────────

class TestZigSourceInvariants(unittest.TestCase):
    """Structural invariants of rge_sm.zig that aren't literal-level."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_zig_source()

    def test_file_has_reasonable_size(self):
        """rge_sm.zig skeleton ≥ 500 lines — guard against accidental truncation."""
        nlines = self.source.count("\n")
        self.assertGreaterEqual(nlines, 500,
                                f"rge_sm.zig only {nlines} lines — truncated?")

    def test_python_source_path_declared(self):
        """PYTHON_SOURCE_PATH must point at Oracle/chain/exact_rge.py."""
        self.assertIn(
            'PYTHON_SOURCE_PATH: []const u8 = "Oracle/chain/exact_rge.py"',
            self.source,
        )

    def test_python_source_lines_declared(self):
        """PYTHON_SOURCE_LINES must be the current line count of exact_rge.py."""
        # Must match actual Python file size (± a few lines for tolerance
        # with trailing newlines — but this catches catastrophic drift).
        py_path = os.path.join(REPO_ROOT, "Oracle", "chain", "exact_rge.py")
        with open(py_path, "r") as fh:
            actual_lines = sum(1 for _ in fh)
        m = re.search(r"PYTHON_SOURCE_LINES:\s*u32\s*=\s*(\d+)", self.source)
        self.assertIsNotNone(m, "PYTHON_SOURCE_LINES declaration missing")
        declared = int(m.group(1))
        # Allow up to 10% drift (exact_rge.py may gain tests/comments)
        self.assertLessEqual(
            abs(declared - actual_lines),
            max(50, actual_lines // 10),
            f"PYTHON_SOURCE_LINES={declared} but exact_rge.py has {actual_lines} lines",
        )

    def test_commandment_xii_comptime_check_present(self):
        """constants_compile_check block must exist (forces comptime eval)."""
        self.assertIn("constants_compile_check", self.source)
        self.assertIn("beta_matrices_compile_check", self.source)

    def test_no_float_types_in_verdict_path(self):
        """Per Commandment XII: no f32/f64 in the compute path.

        We check that `f32` and `f64` do not appear as type annotations in
        pub const or pub fn signatures in the Constants / BetaTables blocks.
        """
        # Narrow search to the Constants and BetaTables blocks (not display
        # helpers or docstrings).
        m = re.search(
            r"pub\s+const\s+Constants\s*=\s*struct\s*\{(.*?)\};",
            self.source,
            re.DOTALL,
        )
        self.assertIsNotNone(m, "Constants struct not found")
        body = m.group(1)
        # Guard against f32 / f64 in type positions: ": f32" or ": f64".
        self.assertNotIn(": f32", body, "Constants contains f32 — Cmd XII violation")
        self.assertNotIn(": f64", body, "Constants contains f64 — Cmd XII violation")
        # Also no @floatFromInt / @floatCast in the block.
        self.assertNotIn("@floatFromInt", body)
        self.assertNotIn("@floatCast", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
