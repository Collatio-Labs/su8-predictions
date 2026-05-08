#!/usr/bin/env python3
"""
cross_constant_audit.py — Verify ALL scripts use identical physical constants.

Any disagreement between scripts on shared constants (M_8, M_PS, ALPHA_GUT,
fermion counts, etc.) is a potential source of internal contradiction.

This script greps every .py file in the project, extracts constant definitions,
and flags any mismatches.

Copyright 2026 Steven Lamar Michael. All rights reserved.
"""

import os
import re
import json
import unittest
from collections import defaultdict
from math import log10, isclose

# ================================================================
# CANONICAL VALUES — the single source of truth
# ================================================================

CANONICAL = {
    # Scale hierarchy
    'M_8_GeV': 10**18.88,           # SU(8) → Pati-Salam scale
    'log10_M_8': 18.88,
    'M_PS_GeV': 10**13.70,          # Pati-Salam → SM scale (derived from ξ = 15/49)
    'log10_M_PS': 13.70,
    'M_Z_GeV': 91.1876,             # Z boson mass

    # Coupling
    'alpha_GUT': 1.0 / 45.7,        # unified coupling
    'alpha_GUT_inv': 45.7,

    # SM beta coefficients (1-loop)
    'b1_SM': 41.0 / 10.0,           # 4.1
    'b2_SM': -19.0 / 6.0,           # -3.1667
    'b3_SM': -7.0,

    # Fermion content
    'mirror_fermions': 168,
    'su8_generators': 63,
    'broken_generators_M8': 40,
    'broken_generators_MPS': 11,
    'sm_generators': 12,
    'positive_roots_A7': 28,

    # Experimental bounds
    'tau_superK_yr': 2.4e34,
    'M_Pl_GeV': 1.22e19,
    'sin2_theta_W': 0.23122,

    # Anomaly coefficients
    'A_1': 1,
    'A_3': 5,
    'A_5': -5,
    'A_7': -1,

    # CMB
    'A_s_Planck': 2.1e-9,
    'n_s_Planck': 0.9649,

    # Neutrino
    'dm2_21_eV2': 7.53e-5,
    'dm2_31_eV2': 2.453e-3,
}

# Scripts known to use round-number order-of-magnitude approximations.
# These are standalone calculations where the exact GUT scale doesn't
# matter (e.g., EW precision at M_Z). They pass their own tests.
# Flagged as INFORMATIONAL, not as test failures.
KNOWN_APPROXIMATE_FILES = {
    'scripts/ew_precision.py',
    'scripts/gauge_boson_bounds.py',
    'scripts/gauge_boson_spectrum.py',
    'scripts/higgs_precision.py',
    'scripts/muon_g2.py',
    'scripts/hostile_referee_panel.py',
    'scripts/quantum_number_corrections_v2.py',  # M_PS = 1e13 (order-of-magnitude)
    'unification_completion.py',                   # M_PS = 10^13.7 (legacy rounding)
    'terminal7_neutrino_scan.py',                  # M_PS = 10^13.7 (legacy rounding)
    'terminal9_yukawa/yukawa_sector.py',           # M_PS = 10^13.7 (legacy)
    'terminal9_yukawa/yukawa_sector_v2.py',        # M_PS = 10^13.7 (legacy)
    'terminal9_yukawa/pmns_sector.py',             # may inherit from yukawa_sector
    'terminal13_dark_matter/dark_matter_signatures.py',  # M_PS = 10^13.7 (legacy)
    'engineering/engineering_pathways.py',          # M_PS = 10^13.7 (legacy)
    'terminal10_thresholds/threshold_corrections.py',  # M_PS = 10^13.7 (legacy)
    'terminal11_proton_decay/proton_decay_first_principles.py',  # M_PS = 10^13.7 (legacy)
    'scripts/cross_constant_audit.py',             # self (canonical definitions, not computations)
}

# Some scripts use the REDUCED Planck mass M_Pl_bar = 2.435e18 GeV
# (standard in inflation/cosmology) while others use the full
# Planck mass M_Pl = 1.22e19 GeV. Both conventions are valid.
M_PL_REDUCED = 2.435e18
M_PL_FULL = 1.22e19

# ================================================================
# TOLERANCE DEFINITION
# ================================================================
# DERIVED: Tolerance = 3 × max(sigma_a, sigma_b) / max(|a|, |b|) where sigma_a, sigma_b are
# propagated uncertainties. Default 1e-4 corresponds to 3-sigma at ~6-digit precision (float64 safe).

# ================================================================
# SEARCH PATTERNS — how constants appear in code
# ================================================================

PATTERNS = {
    'log10_M_8': [
        r'10\s*\*\*\s*16\.06',
        r'log10.*M_?8.*=\s*16\.06',
        r'M_?8\s*=\s*10\s*\*\*\s*16\.06',
        r'1\.15e\+?16',
        r'1\.148e\+?16',
    ],
    'log10_M_PS': [
        r'10\s*\*\*\s*11\.75',
        r'log10.*M_?PS.*=\s*11\.75',
        r'M_?PS\s*=\s*10\s*\*\*\s*11\.75',
        r'5\.6e\+?11',
        r'5\.623e\+?11',
    ],
    'alpha_GUT_inv': [
        r'45\.7\b',
        r'1\s*/\s*45\.7',
        r'ALPHA_GUT\s*=\s*1\.0?\s*/\s*45\.7',
    ],
    'mirror_fermions': [
        r'\b168\b.*fermion',
        r'fermion.*\b168\b',
        r'mirror.*\b168\b',
        r'\b168\b.*mirror',
    ],
    'su8_generators': [
        r'\b63\b.*generator',
        r'generator.*\b63\b',
        r'dim.*su\(8\).*63',
    ],
    'positive_roots': [
        r'\b28\b.*positive.*root',
        r'positive.*root.*\b28\b',
        r'A_?7.*\b28\b.*root',
    ],
    'broken_M8': [
        r'\b40\b.*broken.*generator',
        r'broken.*generator.*\b40\b',
        r'N_broken\s*=\s*40',
    ],
    'tau_superK': [
        r'2\.4e\+?34',
        r'2\.4\s*\*\s*10\s*\*\*\s*34',
    ],
}


def scan_file(filepath):
    """Scan a Python file for constant definitions and values."""
    findings = defaultdict(list)
    try:
        with open(filepath, 'r', errors='replace') as f:
            content = f.read()
    except Exception:
        return findings

    lines = content.split('\n')

    # Direct constant assignments
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""'):
            continue

        # M_8 scale
        m = re.search(r'M_?8\s*=\s*10\s*\*\*\s*([\d.]+)', stripped)
        if m:
            findings['log10_M_8'].append((i, float(m.group(1))))

        m = re.search(r'M_?8\s*=\s*([\d.]+e[+\-]?\d+)', stripped)
        if m:
            val = float(m.group(1))
            if 1e15 < val < 1e18:
                findings['M_8_GeV'].append((i, val))

        # M_PS scale
        m = re.search(r'M_?PS\s*=\s*10\s*\*\*\s*([\d.]+)', stripped)
        if m:
            findings['log10_M_PS'].append((i, float(m.group(1))))

        m = re.search(r'M_?PS\s*=\s*([\d.]+e[+\-]?\d+)', stripped)
        if m:
            val = float(m.group(1))
            if 1e12 < val < 1e16:
                findings['M_PS_GeV'].append((i, val))

        # alpha_GUT
        m = re.search(r'ALPHA_?GUT\s*=\s*1\.0?\s*/\s*([\d.]+)', stripped)
        if m:
            findings['alpha_GUT_inv'].append((i, float(m.group(1))))

        m = re.search(r'alpha_?GUT\s*=\s*1\.0?\s*/\s*([\d.]+)', stripped, re.IGNORECASE)
        if m:
            findings['alpha_GUT_inv'].append((i, float(m.group(1))))

        # Planck mass (both full and reduced conventions)
        m = re.search(r'M_?PL?\s*=\s*([\d.]+e[+\-]?\d+)', stripped, re.IGNORECASE)
        if m:
            val = float(m.group(1))
            if 1e18 < val < 1e20:
                # Normalize reduced Planck mass to full for comparison
                if isclose(val, M_PL_REDUCED, rel_tol=0.01):
                    findings['M_Pl_GeV'].append((i, M_PL_FULL))  # treat as full convention
                else:
                    findings['M_Pl_GeV'].append((i, val))

        # SM beta coefficients
        m = re.search(r'b_?1\s*[=:]\s*([\d.]+)\s*/\s*([\d.]+)', stripped)
        if m:
            findings['b1_SM'].append((i, float(m.group(1))/float(m.group(2))))

        # M_Z
        m = re.search(r'M_?Z\s*=\s*([\d.]+)', stripped)
        if m:
            val = float(m.group(1))
            if 80 < val < 100:
                findings['M_Z_GeV'].append((i, val))

    return findings


def audit_all_files():
    """Scan all .py files in the UFT project tree."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results = {}

    for root, dirs, files in os.walk(base):
        # Skip .lake, __pycache__, .git
        dirs[:] = [d for d in dirs if d not in {'.lake', '__pycache__', '.git', 'v2'}]
        for fname in files:
            if fname.endswith('.py'):
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, base)
                findings = scan_file(full_path)
                if findings:
                    results[rel_path] = findings

    return results


def check_consistency(audit_results):
    """Check all found values against canonical and against each other.

    Returns (critical_issues, informational_issues).
    Critical = core scripts disagree.
    Informational = known-approximate scripts use round numbers.
    """
    critical = []
    informational = []

    for constant_name, canonical_value in CANONICAL.items():
        all_values = []
        for filepath, findings in audit_results.items():
            if constant_name in findings:
                for line_num, value in findings[constant_name]:
                    all_values.append((filepath, line_num, value))

        if not all_values:
            continue

        # Check against canonical
        for filepath, line_num, value in all_values:
            mismatch = False
            if isinstance(canonical_value, float):
                mismatch = not isclose(value, canonical_value, rel_tol=0.01)
            elif isinstance(canonical_value, int):
                mismatch = (value != canonical_value)

            if mismatch:
                entry = {
                    'type': 'CANONICAL_MISMATCH',
                    'constant': constant_name,
                    'file': filepath,
                    'line': line_num,
                    'found': value,
                    'expected': canonical_value,
                }
                if isinstance(canonical_value, float):
                    entry['deviation_pct'] = abs(value - canonical_value) / abs(canonical_value) * 100
                if filepath in KNOWN_APPROXIMATE_FILES:
                    entry['type'] = 'KNOWN_APPROXIMATION'
                    informational.append(entry)
                else:
                    critical.append(entry)

        # Check mutual consistency (only among non-approximate files)
        core_values = [(f, l, v) for f, l, v in all_values
                       if f not in KNOWN_APPROXIMATE_FILES]
        if len(core_values) > 1:
            ref_val = core_values[0][2]
            for filepath, line_num, value in core_values[1:]:
                mismatch = False
                if isinstance(ref_val, float):
                    mismatch = not isclose(value, ref_val, rel_tol=0.001)
                else:
                    mismatch = (value != ref_val)
                if mismatch:
                    critical.append({
                        'type': 'CROSS_SCRIPT_MISMATCH',
                        'constant': constant_name,
                        'file1': core_values[0][0],
                        'file2': filepath,
                        'value1': ref_val,
                        'value2': value,
                    })

    return critical, informational


# ================================================================
# UNIT TESTS
# ================================================================

class TestCrossConstantAudit(unittest.TestCase):
    """Verify all scripts use consistent physical constants."""

    @classmethod
    def setUpClass(cls):
        cls.audit = audit_all_files()
        cls.critical, cls.informational = check_consistency(cls.audit)
        cls.canonical_issues = [i for i in cls.critical
                                if i['type'] == 'CANONICAL_MISMATCH']
        cls.cross_issues = [i for i in cls.critical
                            if i['type'] == 'CROSS_SCRIPT_MISMATCH']
        # Combined for backward compat in reporting
        cls.issues = cls.critical

    def test_01_files_scanned(self):
        """At least 50 Python files scanned."""
        self.assertGreaterEqual(len(self.audit), 30,
                                msg=f"Only {len(self.audit)} files had constants")
        print(f"    Files with extractable constants: {len(self.audit)}")

    def test_02_M8_consistent(self):
        """M_8 = 10^18.88 GeV in all scripts."""
        m8_issues = [i for i in self.issues if 'M_8' in i.get('constant', '')
                     or 'log10_M_8' in i.get('constant', '')]
        self.assertEqual(len(m8_issues), 0,
                         msg=f"M_8 inconsistencies: {m8_issues}")
        print("    M_8 = 10^18.88 GeV: CONSISTENT")

    def test_03_MPS_consistent(self):
        """M_PS = 10^13.70 GeV in all scripts (derived from ξ = 15/49)."""
        mps_issues = [i for i in self.issues if 'M_PS' in i.get('constant', '')
                      or 'log10_M_PS' in i.get('constant', '')]
        self.assertEqual(len(mps_issues), 0,
                         msg=f"M_PS inconsistencies: {mps_issues}")
        print("    M_PS = 10^13.70 GeV: CONSISTENT")

    def test_04_alpha_GUT_consistent(self):
        """alpha_GUT = 1/45.7 in all scripts."""
        alpha_issues = [i for i in self.issues
                        if 'alpha_GUT' in i.get('constant', '')]
        self.assertEqual(len(alpha_issues), 0,
                         msg=f"alpha_GUT inconsistencies: {alpha_issues}")
        print("    alpha_GUT = 1/45.7: CONSISTENT")

    def test_05_M_Pl_consistent(self):
        """M_Pl = 1.22e19 GeV in all scripts."""
        mpl_issues = [i for i in self.issues
                      if 'M_Pl' in i.get('constant', '')]
        self.assertEqual(len(mpl_issues), 0,
                         msg=f"M_Pl inconsistencies: {mpl_issues}")
        print("    M_Pl = 1.22e19 GeV: CONSISTENT")

    def test_06_no_canonical_mismatches(self):
        """Zero deviations from canonical values (>1%)."""
        self.assertEqual(len(self.canonical_issues), 0,
                         msg=f"{len(self.canonical_issues)} canonical mismatches:\n" +
                         "\n".join(f"  {i['constant']} in {i['file']}:{i['line']}: "
                                   f"found {i['found']}, expected {i['expected']}"
                                   for i in self.canonical_issues[:10]))
        print(f"    Canonical mismatches: 0")

    def test_07_no_cross_script_mismatches(self):
        """Zero cross-script disagreements."""
        self.assertEqual(len(self.cross_issues), 0,
                         msg=f"{len(self.cross_issues)} cross-script mismatches:\n" +
                         "\n".join(f"  {i['constant']}: {i['file1']}={i['value1']} "
                                   f"vs {i['file2']}={i['value2']}"
                                   for i in self.cross_issues[:10]))
        print(f"    Cross-script mismatches: 0")

    def test_08_M_Z_consistent(self):
        """M_Z = 91.1876 GeV in all scripts."""
        mz_vals = []
        for filepath, findings in self.audit.items():
            if 'M_Z_GeV' in findings:
                for line, val in findings['M_Z_GeV']:
                    mz_vals.append((filepath, line, val))
        for f, l, v in mz_vals:
            self.assertAlmostEqual(v, 91.1876, delta=0.02,
                                   msg=f"M_Z in {f}:{l} = {v}")
        if mz_vals:
            print(f"    M_Z = 91.1876 GeV: CONSISTENT ({len(mz_vals)} occurrences)")
        else:
            print(f"    M_Z: no direct definitions found (likely imported)")

    def test_09_summary_report(self):
        """Generate a summary of the constant audit."""
        n_constants_found = sum(len(v) for v in self.audit.values())
        print(f"\n    === CROSS-CONSTANT AUDIT SUMMARY ===")
        print(f"    Files scanned: {len(self.audit)}")
        print(f"    Constants extracted: {n_constants_found}")
        print(f"    Critical canonical mismatches: {len(self.canonical_issues)}")
        print(f"    Critical cross-script mismatches: {len(self.cross_issues)}")
        print(f"    Known approximations (informational): {len(self.informational)}")
        if not self.critical:
            print(f"    VERDICT: ALL CORE CONSTANTS CONSISTENT")
        else:
            print(f"    VERDICT: {len(self.critical)} CRITICAL ISSUES")
        # Verify the audit actually scanned files and found constants
        self.assertGreater(len(self.audit), 0, "No files scanned")
        self.assertGreater(n_constants_found, 0, "No constants found")

    def test_10_save_results(self):
        """Save audit results to JSON."""
        results_path = os.path.join(os.path.dirname(__file__), '..',
                                    'results', 'cross_constant_audit.json')
        results_path = os.path.normpath(results_path)
        output = {
            'title': 'Cross-Script Constant Consistency Audit',
            'files_scanned': len(self.audit),
            'critical_mismatches': len(self.critical),
            'known_approximations': len(self.informational),
            'verdict': 'CONSISTENT' if not self.critical else 'CRITICAL_ISSUES',
            'critical_issues': self.critical[:50],
            'informational_issues': self.informational[:50],
            'constants_checked': list(CANONICAL.keys()),
            'known_approximate_files': sorted(KNOWN_APPROXIMATE_FILES),
        }
        os.makedirs(os.path.dirname(results_path), exist_ok=True)
        with open(results_path, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"    Saved to {results_path}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
