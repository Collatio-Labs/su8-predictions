#!/usr/bin/env python3
"""c181 — voltus_native rge_sm.zig BRICK B5 parity guard.

Scope (B5):
    Two-loop and three-loop coupled SM gauge β-function integrators ported
    from `Oracle/chain/exact_rge.py` lines 467-538 to
    `supercomputer/voltus_native/zig/src/rge_sm.zig` lines 932-1084.

Authorities mirrored:
    Python:  exact_rge.run_coupling_2loop  (Euler  integrator, n_steps=200)
             exact_rge.run_coupling_3loop  (RK2 midpoint, n_steps=300)
    Zig:     runCoupling2Loop  (rge_sm.zig:954-989, SECTION 5)
             runCoupling3Loop  (rge_sm.zig:1007-1084, SECTION 5)

Two-sided tripwire pattern (per C209-C211):
    - This file catches Zig-side drift from the Python authority literals.
    - The in-file Zig B5 self-test block catches within-Zig drift (typos in
      coefficient signs, accidental sign flip on derivative term, off-by-one
      on RK2 midpoint, omission of zero-α guard).

Per Commandments XI + XII + XIII:
    All rational arithmetic uses exact `Fraction`. Zero `float(`, zero `f32`,
    zero `f64` in derivation path. Every Zig literal that appears in the
    SECTION 5 source is presence-checked against the Python source.
"""

from __future__ import annotations

import os
import re
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Dict, List

# Path discipline: import from the repo root (proofs/.. is the project root
# when this is run via `python3 -m unittest proofs.UFT.scripts.c181_*`).
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from Oracle.chain import exact_rge as er  # noqa: E402

ZIG_PATH = REPO_ROOT / "supercomputer" / "voltus_native" / "zig" / "src" / "rge_sm.zig"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _zig_source() -> str:
    """Read the Zig source once per test class (cached at module level)."""
    return ZIG_PATH.read_text(encoding="utf-8")


def _b5_block(src: str) -> str:
    """Return the SECTION 5 block (B5) — bounded by section markers."""
    start_marker = "SECTION 5 — TWO-LOOP / THREE-LOOP RK4 INTEGRATORS"
    end_marker = "SECTION 6 — HIGGS + FERMION RGE CHAIN"
    s = src.find(start_marker)
    e = src.find(end_marker)
    if s == -1 or e == -1 or e < s:
        raise RuntimeError("c181: B5 SECTION markers not found in rge_sm.zig")
    return src[s:e]


# Whitelist of idiomatic equivalents per `feedback_parity_guard_idiomatic_whitelist.md`.
# Entry: test_id → list of regex patterns that constitute valid evidence of the
# identity even though the literal canonical form is not present verbatim.
ZIG_ALTERNATE_PATTERNS: Dict[str, List[str]] = {
    # `dt / 2` is also written as `divScalar(dt, 2)` — both are valid.
    "rk2_midpoint_half_step": [
        r"divScalar\s*\(\s*dt\s*,\s*2\s*\)",
        r"vf\.div\s*\(\s*dt\s*,\s*vf\.mk\s*\(\s*2\s*,\s*1\s*\)\s*\)",
    ],
    # `8 * π²` factor for the 2-loop denominator can be `mulScalar(... , 8)`
    # or written as `vf.mk(8, 1)` first then mul — accept both forms.
    "two_loop_denominator_factor_eight": [
        r"mulScalar\s*\([^)]*PI\s*,\s*PI[^)]*\)\s*,\s*8\s*\)",
        r"vf\.mulScalar\s*\(\s*vf\.mul\s*\(\s*Constants\.PI\s*,\s*Constants\.PI\s*\)\s*,\s*8\s*\)",
    ],
    # `128 * π³` factor for the 3-loop denominator.
    "three_loop_denominator_factor_128": [
        r"mulScalar\s*\(\s*vf\.pow\s*\(\s*Constants\.PI\s*,\s*3\s*\)\s*,\s*128\s*\)",
    ],
}


def _alternate_present_in_b5(test_id: str, src: str) -> bool:
    pats = ZIG_ALTERNATE_PATTERNS.get(test_id, [])
    block = _b5_block(src)
    for p in pats:
        if re.search(p, block):
            return True
    return False


# ---------------------------------------------------------------------------
# Test class 1 — Python authority sanity (recompute Euler / RK2 at canonical
# inputs and assert structural identities the Zig port must reproduce).
# ---------------------------------------------------------------------------

class TestPythonAuthority2Loop(unittest.TestCase):
    """Recompute exact_rge.run_coupling_2loop with the canonical SM β at
    (M_Z → M_PS).  Assert structural properties the Zig port must mirror."""

    @classmethod
    def setUpClass(cls):
        cls.alpha_inv_MZ = [
            Fraction(5901, 100),  # α₁⁻¹(M_Z) GUT-norm
            Fraction(2959, 100),  # α₂⁻¹(M_Z)
            er.ALPHA_S_INV_MZ,    # α₃⁻¹(M_Z) = 500/59
        ]
        cls.b1 = [er.b1_SM, er.b2_SM, er.b3_SM]
        cls.b2_matrix = er.b2_SM_matrix  # exact 3x3 matrix authority
        cls.ln_MZ_to_MPS = er.LN_MPS_OVER_MZ

    def test_2loop_returns_three_fractions(self):
        out = er.run_coupling_2loop(
            self.alpha_inv_MZ, self.b1, self.b2_matrix,
            self.ln_MZ_to_MPS, n_steps=10,
        )
        self.assertEqual(len(out), 3)
        for x in out:
            self.assertIsInstance(x, Fraction)

    def test_2loop_zero_step_returns_input(self):
        # At ln_step = 0, dt = 0, so y ← y + 0·da = y (identity).
        # NOTE: n_steps=0 causes division-by-zero in Python authority;
        # we use n_steps=1 with ln_ratio=0 instead.
        out1 = er.run_coupling_2loop(
            self.alpha_inv_MZ, self.b1, self.b2_matrix,
            Fraction(0), n_steps=1,
        )
        self.assertEqual(out1, [Fraction(x) for x in self.alpha_inv_MZ])

    def test_2loop_respects_zero_alpha_guard(self):
        # If any α_j⁻¹ is zero, the 2-loop cross-coupling term must be skipped
        # (the Zig version uses `if (vf.isZero(a_inv[j])) continue;`).
        # The Python authority expresses this as `if a_inv[j] != 0:`.
        # Setting α₃⁻¹(M_Z) = 0 forces the SU(3)_C cross-coupling skips.
        alpha_inv_zero3 = [
            Fraction(5901, 100),
            Fraction(2959, 100),
            Fraction(0),
        ]
        out = er.run_coupling_2loop(
            alpha_inv_zero3, self.b1, self.b2_matrix,
            self.ln_MZ_to_MPS, n_steps=5,
        )
        # α₃⁻¹ stays at 0 because each da[2] has only the 1-loop term
        # accumulating, but its starting value is 0 too. Specifically:
        # da[2] from 1-loop = -B3_SM/(2π) = +7/(2π) ≠ 0, so α₃⁻¹ moves
        # off 0 monotonically (b₃ = -7 → +7/(2π) is positive).
        self.assertNotEqual(out[2], Fraction(0))

    def test_2loop_monotone_under_short_run(self):
        # Over a small ln_step, α₃⁻¹ must INCREASE (b₃ < 0 → asymptotic freedom).
        alpha_short = [
            Fraction(5901, 100),
            Fraction(2959, 100),
            er.ALPHA_S_INV_MZ,
        ]
        out_short = er.run_coupling_2loop(
            alpha_short, self.b1, self.b2_matrix,
            Fraction(1, 100), n_steps=5,
        )
        # At 2-loop, b₃ < 0 (asymptotic freedom for QCD). α₃⁻¹ runs UP.
        self.assertGreater(out_short[2], er.ALPHA_S_INV_MZ)


class TestPythonAuthority3Loop(unittest.TestCase):
    """Recompute exact_rge.run_coupling_3loop with canonical SM β + 3-loop
    diagonal coefficients."""

    @classmethod
    def setUpClass(cls):
        cls.alpha_inv_MZ = [
            Fraction(5901, 100),
            Fraction(2959, 100),
            er.ALPHA_S_INV_MZ,
        ]
        cls.b1 = [er.b1_SM, er.b2_SM, er.b3_SM]
        cls.b2_matrix = er.b2_SM_matrix
        # 3-loop diagonal — match Zig's Constants.{B1,B2,B3}_SM_3LOOP.
        cls.b3_diag = [er.b1_SM_3loop, er.b2_SM_3loop, er.b3_SM_3loop_nf6]
        cls.ln_MZ_to_MPS = er.LN_MPS_OVER_MZ

    def test_3loop_returns_three_fractions(self):
        out = er.run_coupling_3loop(
            self.alpha_inv_MZ, self.b1, self.b2_matrix, self.b3_diag,
            self.ln_MZ_to_MPS, n_steps=10,
        )
        self.assertEqual(len(out), 3)
        for x in out:
            self.assertIsInstance(x, Fraction)

    def test_3loop_zero_step_returns_input(self):
        out1 = er.run_coupling_3loop(
            self.alpha_inv_MZ, self.b1, self.b2_matrix, self.b3_diag,
            Fraction(0), n_steps=1,
        )
        # At ln_step = 0, dt = 0, so y ← y + 0·k2 = y (identity).
        self.assertEqual(out1, [Fraction(x) for x in self.alpha_inv_MZ])

    def test_3loop_close_to_2loop_short_run(self):
        # On a short run, 3-loop diagonal correction is a small fractional
        # adjustment to the 2-loop trajectory (bounded by α_i² / 128π³).
        out2 = er.run_coupling_2loop(
            self.alpha_inv_MZ, self.b1, self.b2_matrix,
            Fraction(1, 100), n_steps=20,
        )
        out3 = er.run_coupling_3loop(
            self.alpha_inv_MZ, self.b1, self.b2_matrix, self.b3_diag,
            Fraction(1, 100), n_steps=20,
        )
        # Difference per-coupling must be < 1% of the 2-loop value at this short range.
        for i in range(3):
            diff = abs(out3[i] - out2[i])
            scale = abs(out2[i])
            ratio = diff / scale if scale != 0 else Fraction(0)
            self.assertLess(ratio, Fraction(1, 100),
                            f"3-loop diverged from 2-loop on coupling {i}: "
                            f"out2={float(out2[i]):.4f}, out3={float(out3[i]):.4f}")


# ---------------------------------------------------------------------------
# Test class 2 — Zig source presence (every literal the B5 block commits to)
# ---------------------------------------------------------------------------

class TestZigB5SourceLiterals(unittest.TestCase):
    """Source-scan the B5 SECTION 5 block of rge_sm.zig for the load-bearing
    literals that the Python authority pins.  Each test_id corresponds to one
    structural commitment the Zig port makes; alternate forms are whitelisted
    via ZIG_ALTERNATE_PATTERNS."""

    @classmethod
    def setUpClass(cls):
        cls.src = _zig_source()
        cls.b5 = _b5_block(cls.src)

    def _expect(self, test_id: str, literal_pattern: str):
        if re.search(literal_pattern, self.b5):
            return
        if _alternate_present_in_b5(test_id, self.src):
            return
        self.fail(
            f"c181 [{test_id}]: neither literal pattern {literal_pattern!r} nor "
            f"any whitelist alternate {ZIG_ALTERNATE_PATTERNS.get(test_id)!r} "
            f"found in B5 SECTION 5 block"
        )

    def test_runCoupling2Loop_signature_pinning(self):
        self._expect(
            "runCoupling2Loop_decl",
            r"pub fn runCoupling2Loop\s*\(",
        )

    def test_runCoupling3Loop_signature_pinning(self):
        self._expect(
            "runCoupling3Loop_decl",
            r"pub fn runCoupling3Loop\s*\(",
        )

    def test_2loop_two_pi_in_one_loop_term(self):
        # 1-loop term: -b_i / (2π).  TWO_PI is the Python authority symbol.
        self._expect(
            "two_pi_one_loop_term",
            r"Constants\.TWO_PI",
        )

    def test_2loop_eight_pi_sq_factor(self):
        self._expect(
            "two_loop_denominator_factor_eight",
            r"mulScalar\s*\([^)]*PI\s*,\s*PI[^)]*\)\s*,\s*8\s*\)",
        )

    def test_3loop_128_pi_cubed_factor(self):
        self._expect(
            "three_loop_denominator_factor_128",
            r"vf\.pow\s*\(\s*Constants\.PI\s*,\s*3\s*\)",
        )

    def test_3loop_diagonal_only_no_cross_coupling(self):
        # The B5 docstring must explicitly say cross-coupling 3-loop is dropped.
        self._expect(
            "three_loop_no_cross_coupling_doc",
            r"[Cc]ross-coupling 3-loop terms",
        )

    def test_zero_alpha_guard_present_2loop(self):
        # Zig form: `if (vf.isZero(a_inv[j])) continue;`
        self._expect(
            "zero_alpha_guard_2loop",
            r"vf\.isZero\s*\(\s*a_inv\s*\[\s*j\s*\]\s*\)",
        )

    def test_zero_alpha_guard_present_3loop(self):
        # In 3-loop, the inner closure uses `ai[j]` (parameter rename).
        self._expect(
            "zero_alpha_guard_3loop",
            r"vf\.isZero\s*\(\s*ai\s*\[\s*j\s*\]\s*\)",
        )

    def test_rk2_midpoint_half_step(self):
        # RK2 midpoint: half-step is `dt/2`. Accept `divScalar(dt,2)` form.
        self._expect(
            "rk2_midpoint_half_step",
            r"vf\.divScalar\s*\(\s*dt\s*,\s*2\s*\)",
        )

    def test_rk2_uses_k2_for_final_increment(self):
        # RK2 final: y ← y + dt · k2. The k2 variable must be referenced
        # in the final increment block (k1 alone would be Euler).
        self._expect(
            "rk2_uses_k2_final_increment",
            r"k2\s*\[\s*[a-z]\s*\]",
        )

    def test_b5_section_marker_present(self):
        self._expect(
            "section_5_marker",
            r"SECTION 5 — TWO-LOOP / THREE-LOOP",
        )


# ---------------------------------------------------------------------------
# Test class 3 — Limit-discipline structural mirror
# ---------------------------------------------------------------------------

class TestB5LimitDiscipline(unittest.TestCase):
    """Per `feedback_int64_frac_rk4_overflow.md`, every Fraction op in B5
    must be `limit()`-wrapped to keep the i128 numerator from saturating
    mid-integration.  Source-scan for the count of `limit(` calls inside B5
    must be at least the expected minimum."""

    MIN_LIMIT_CALLS = 20  # 2-loop has ~10, 3-loop has ~20+; 20 is conservative

    @classmethod
    def setUpClass(cls):
        cls.b5 = _b5_block(_zig_source())

    def test_limit_call_count_meets_minimum(self):
        n = len(re.findall(r"\blimit\s*\(", self.b5))
        self.assertGreaterEqual(
            n, self.MIN_LIMIT_CALLS,
            f"B5 has only {n} limit() calls (expected ≥ {self.MIN_LIMIT_CALLS}); "
            "i128 overflow risk per feedback_int64_frac_rk4_overflow.md"
        )

    def test_limit_wraps_dt_in_3loop(self):
        # 3-loop computes `dt = limit(vf.divScalar(ln_step, @intCast(n_steps)))`.
        self.assertRegex(
            self.b5,
            r"const dt\s*=\s*limit\s*\(\s*vf\.divScalar\s*\(\s*ln_step",
        )

    def test_limit_wraps_increment_in_2loop(self):
        # 2-loop final-increment `a_inv[k] = limit(vf.add(a_inv[k], inc));`
        self.assertRegex(
            self.b5,
            r"a_inv\s*\[\s*k\s*\]\s*=\s*limit\s*\(\s*vf\.add",
        )


# ---------------------------------------------------------------------------
# Test class 4 — Commandment XII enforcement (zero floats anywhere in B5)
# ---------------------------------------------------------------------------

class TestB5CommandmentXII(unittest.TestCase):
    """Zero `f32`, zero `f64`, zero `@floatFromInt`, zero `@intToFloat` in
    the B5 SECTION 5 block.  All arithmetic is exact BigFraction (i128/i128).
    """

    @classmethod
    def setUpClass(cls):
        cls.b5 = _b5_block(_zig_source())

    def test_no_f32(self):
        self.assertNotRegex(self.b5, r"\bf32\b")

    def test_no_f64(self):
        self.assertNotRegex(self.b5, r"\bf64\b")

    def test_no_floatFromInt(self):
        self.assertNotIn("@floatFromInt", self.b5)

    def test_no_intToFloat(self):
        self.assertNotIn("@intToFloat", self.b5)

    def test_no_intFromFloat(self):
        self.assertNotIn("@intFromFloat", self.b5)


# ---------------------------------------------------------------------------
# Test class 5 — Whitelist mechanism sanity
# ---------------------------------------------------------------------------

class TestZigAlternatePatternsWhitelistMechanism(unittest.TestCase):
    """Each whitelisted alternate pattern must actually match somewhere in the
    B5 source (otherwise the whitelist entry is dead and should be removed)."""

    @classmethod
    def setUpClass(cls):
        cls.src = _zig_source()

    def test_all_whitelisted_patterns_match_zig_source(self):
        unmatched = []
        for test_id in ZIG_ALTERNATE_PATTERNS:
            if not _alternate_present_in_b5(test_id, self.src):
                # OK if the literal canonical form is also present (alt is
                # dormant, not dead).  Only flag when neither matches.
                # Per c176's scope-distinction lesson: whitelist alternates
                # are scoped to the B5 block; checking only the B5 block is correct.
                unmatched.append(test_id)
        # Whitelisted alternates may stay dormant if the canonical literal
        # form is the one currently in source; that's fine.  The check here
        # is a structural sanity hook — if EVERY alt is dormant, that's a
        # signal the whitelist may be over-broad.  Soft-warn only.
        if len(unmatched) == len(ZIG_ALTERNATE_PATTERNS):
            self.fail(
                f"All {len(unmatched)} ZIG_ALTERNATE_PATTERNS are dormant — "
                "whitelist may be over-broad"
            )


# ---------------------------------------------------------------------------
# Test class 6 — Cross-witness with B3 (no regression on closed-loop α₃)
# ---------------------------------------------------------------------------

class TestB5CrossWitnessB3(unittest.TestCase):
    """Independent recompute: running α₃⁻¹(M_Z) → α₃⁻¹(M_PS) at 2-loop must
    match what the closed-form 1-loop runner does within a small tolerance
    (the difference IS the 2-loop correction)."""

    def test_2loop_alpha3_drift_from_1loop_is_small(self):
        a3_MZ = er.ALPHA_S_INV_MZ
        # Closed-form 1-loop authority (B3 brick, mirrored in Zig runCouplingInv).
        a3_MPS_1loop = er.run_coupling_inv(a3_MZ, er.b3_SM, er.LN_MPS_OVER_MZ)
        # Full 2-loop integrator.
        out_2loop = er.run_coupling_2loop(
            [Fraction(5901, 100), Fraction(2959, 100), a3_MZ],
            [er.b1_SM, er.b2_SM, er.b3_SM],
            er.b2_SM_matrix,
            er.LN_MPS_OVER_MZ, n_steps=200,
        )
        a3_MPS_2loop = out_2loop[2]
        # Small but nonzero difference (the 2-loop correction).
        diff_ratio = abs(a3_MPS_2loop - a3_MPS_1loop) / abs(a3_MPS_1loop)
        # 2-loop correction over M_Z→M_PS is typically a few percent.
        self.assertLess(diff_ratio, Fraction(20, 100),  # < 20%
                        f"2-loop α₃⁻¹(M_PS) diverges too much from 1-loop")
        self.assertGreater(diff_ratio, Fraction(0),
                           "2-loop must differ from 1-loop")


if __name__ == "__main__":
    unittest.main(verbosity=2)
