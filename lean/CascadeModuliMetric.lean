import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.IntervalCases
import Mathlib.Data.Rat.Lemmas
import CascadeCGRepTheory

/-
  CascadeModuliMetric.lean — CLM-046, Killing form on SU(8) simple coroots.

  SCOPE (see Oracle/claims/CLM-046-cascade-moduli-metric-equals-cartan.md):

    Tightens the CLM-031 spectral-identification postulate ("the A_7
    Cartan eigenvalues ARE the relevant matrix controlling cascade
    coupling ratios") by proving the Killing form of SU(8) restricted to
    the simple-coroot basis equals the A_7 Cartan matrix entry-for-entry,
    up to a uniform positive prefactor 16.

    Concretely:
      H_i  := the diagonal traceless 8×8 matrix with +1 at position (i,i),
              -1 at (i+1, i+1), 0 elsewhere   (i = 0, …, 6)
      K(X, Y)    := 2 N · Tr(X · Y)  with N = 8  ⇒  K(X, Y) = 16 · Tr(X Y)
      C(A_7)_{ij} := tridiag(2, -1) at rank 7

    **Main identity:**
      K(H_i, H_j) = 16 · (2 δ_{ij} - δ_{|i-j|, 1}) = 16 · C(A_7)_{ij}

    The uniform factor 16 cancels in any ratio of spectral quantities
    (mean inverse eigenvalues, determinants, Kirchhoff indices), so the
    cascade CG identification is independent of normalization conventions.

  APPROACH — elementary, no Matrix machinery.

    Instead of importing Mathlib.Data.Matrix and Mathlib.LinearAlgebra.Trace,
    we encode `H_i` as a function `coroot_entry : ℕ → ℕ → ℤ` giving the
    (k, k) diagonal entry (all off-diagonal entries are zero for diagonal
    matrices, so Tr(H_i · H_j) = Σ_k H_i[k,k] · H_j[k,k]).

    `trace_prod i j : ℤ` is then an explicit 8-term integer sum over
    positions k = 0, …, 7.  Every entry `trace_prod i j` for i, j in
    0..6 closes by `decide` because the underlying computation is finite.

    The master identity `moduli_metric_equals_cartan` is closed by
    `interval_cases i <;> interval_cases j <;> decide` — 49 cases, each
    a direct computation.

  EVERY THEOREM BELOW CLOSES BY ONE OF:
    * `rfl`
    * `decide`
    * `unfold ... ; decide`
    * `norm_num`
    * `unfold ... ; norm_num`
    * `interval_cases ... <;> decide`

  No Real numbers.  No Float.  No `sorry`.  No axioms beyond Mathlib's.
  Commandment XII at the proof layer.

  Cross-references
  ----------------
  - `CascadeCGRepTheory.lean` (CLM-032) — `cartan_mean_inv`, `cg_rat`,
    `cascade_cg_at_A7 : cg_rat 7 = 8/9`.
  - `CascadeKineticOperator.lean` (CLM-042) — uniform-prefactor cancellation
    pattern, kinetic-operator form of CG = 8/9.
  - `SpectralRGECorrespondence.lean` (CLM-031) — the Rosetta stone that
    this file tightens by retiring the spectral-identification postulate.
  - `proofs/UFT/scripts/c180_cascade_moduli_metric.py` — Python parity
    guard (~50 tests), mirrors every ℚ/ℤ literal here per
    `feedback_lean_only_bugs.md`.

  Scope boundary (see CLM-046 §4.3) — CLM-046 does NOT close:
    (1) higher-loop wavefunction renormalization Z_i(μ), (2) direct
    SU(8) path-integral derivation of CG, (3) CLM-001 promotion to
    unqualified `theorem`.

  © 2026 Steven Lamar Michael.  All rights reserved.  Patent Pending.
-/

namespace UFT.CascadeModuliMetric

open UFT.CascadeCGRepTheory

/-! ## Section 1 — Simple coroot entries as integer-valued functions.

    `coroot_entry i k` is the (k, k) diagonal entry of the i-th simple
    coroot `H_i = E_{i,i} - E_{i+1, i+1}`.  Valid for i = 0, …, 6 and
    k = 0, …, 7 (indexed from zero for convenience).

    Since H_i is diagonal, all off-diagonal entries are zero, so
    Tr(H_i · H_j) reduces to the sum over diagonal positions of the
    product of diagonal entries.
-/

/-- (k, k) diagonal entry of the i-th simple coroot H_i of A_7 ⊂ su(8). -/
@[reducible]
def coroot_entry (i k : ℕ) : ℤ :=
  if k = i then 1
  else if k = i + 1 then -1
  else 0

/-! Sanity values — spot-checks that the if-chain is wired correctly. -/

theorem coroot_entry_0_0 : coroot_entry 0 0 = 1 := by decide
theorem coroot_entry_0_1 : coroot_entry 0 1 = -1 := by decide
theorem coroot_entry_0_2 : coroot_entry 0 2 = 0 := by decide
theorem coroot_entry_3_3 : coroot_entry 3 3 = 1 := by decide
theorem coroot_entry_3_4 : coroot_entry 3 4 = -1 := by decide
theorem coroot_entry_6_6 : coroot_entry 6 6 = 1 := by decide
theorem coroot_entry_6_7 : coroot_entry 6 7 = -1 := by decide

/-- Tracelessness: the diagonal entries of H_i sum to 0 over k = 0, …, 7.
    This is the `su(8)` (not `u(8)`) condition — coroots live in the
    Cartan subalgebra of the traceless matrices. -/
theorem coroot_traceless (i : ℕ) (hi : i < 7) :
    coroot_entry i 0 + coroot_entry i 1 + coroot_entry i 2 + coroot_entry i 3
      + coroot_entry i 4 + coroot_entry i 5 + coroot_entry i 6 + coroot_entry i 7 = 0 := by
  interval_cases i <;> decide

/-! ## Section 2 — Trace products Tr(H_i · H_j) as explicit 8-term sums.

    For diagonal matrices X, Y with (k, k) entries x_k, y_k, we have
    Tr(X · Y) = Σ_{k=0}^{7} x_k · y_k.  The definition below makes this
    literal — an 8-term integer sum.
-/

/-- `trace_prod i j = Tr(H_i · H_j)` as an explicit 8-term integer sum.
    For diagonal matrices this is Σ_{k=0}^{7} (H_i)_{k,k} · (H_j)_{k,k}. -/
@[reducible]
def trace_prod (i j : ℕ) : ℤ :=
    coroot_entry i 0 * coroot_entry j 0
  + coroot_entry i 1 * coroot_entry j 1
  + coroot_entry i 2 * coroot_entry j 2
  + coroot_entry i 3 * coroot_entry j 3
  + coroot_entry i 4 * coroot_entry j 4
  + coroot_entry i 5 * coroot_entry j 5
  + coroot_entry i 6 * coroot_entry j 6
  + coroot_entry i 7 * coroot_entry j 7

/-! Diagonal entries: Tr(H_i · H_i) = 2 for all i ∈ {0, …, 6}. -/

theorem trace_prod_diag_0 : trace_prod 0 0 = 2 := by decide
theorem trace_prod_diag_1 : trace_prod 1 1 = 2 := by decide
theorem trace_prod_diag_2 : trace_prod 2 2 = 2 := by decide
theorem trace_prod_diag_3 : trace_prod 3 3 = 2 := by decide
theorem trace_prod_diag_4 : trace_prod 4 4 = 2 := by decide
theorem trace_prod_diag_5 : trace_prod 5 5 = 2 := by decide
theorem trace_prod_diag_6 : trace_prod 6 6 = 2 := by decide

/-! Adjacent entries: Tr(H_i · H_{i±1}) = -1 for i ∈ {0, …, 5} / {1, …, 6}. -/

theorem trace_prod_adj_01 : trace_prod 0 1 = -1 := by decide
theorem trace_prod_adj_10 : trace_prod 1 0 = -1 := by decide
theorem trace_prod_adj_12 : trace_prod 1 2 = -1 := by decide
theorem trace_prod_adj_21 : trace_prod 2 1 = -1 := by decide
theorem trace_prod_adj_23 : trace_prod 2 3 = -1 := by decide
theorem trace_prod_adj_32 : trace_prod 3 2 = -1 := by decide
theorem trace_prod_adj_34 : trace_prod 3 4 = -1 := by decide
theorem trace_prod_adj_43 : trace_prod 4 3 = -1 := by decide
theorem trace_prod_adj_45 : trace_prod 4 5 = -1 := by decide
theorem trace_prod_adj_54 : trace_prod 5 4 = -1 := by decide
theorem trace_prod_adj_56 : trace_prod 5 6 = -1 := by decide
theorem trace_prod_adj_65 : trace_prod 6 5 = -1 := by decide

/-! Far entries (selected spot-checks): Tr(H_i · H_j) = 0 for |i - j| ≥ 2. -/

theorem trace_prod_far_02 : trace_prod 0 2 = 0 := by decide
theorem trace_prod_far_03 : trace_prod 0 3 = 0 := by decide
theorem trace_prod_far_06 : trace_prod 0 6 = 0 := by decide
theorem trace_prod_far_24 : trace_prod 2 4 = 0 := by decide
theorem trace_prod_far_36 : trace_prod 3 6 = 0 := by decide
theorem trace_prod_far_14 : trace_prod 1 4 = 0 := by decide

/-- Symmetry: Tr(H_i · H_j) = Tr(H_j · H_i).  Follows from
    commutativity of integer multiplication position-by-position. -/
theorem trace_prod_symm (i j : ℕ) (hi : i < 7) (hj : j < 7) :
    trace_prod i j = trace_prod j i := by
  interval_cases i <;> interval_cases j <;> decide

/-! ## Section 3 — Killing form on SU(8).

    The Killing form on the fundamental representation of SU(N) is
        K(X, Y) = 2 N · Tr(X · Y).
    For SU(8) this is 16 · Tr(X · Y).

    Here we define `killing_su8 : ℤ → ℚ` as the ℚ-valued Killing form of
    an already-computed integer trace: `killing_su8 n = 16 · n`.
-/

/-- Killing-form prefactor for SU(8) fundamental: K(X, Y) = 16 · Tr(X · Y). -/
@[reducible]
def killing_su8 (n : ℤ) : ℚ := 16 * (n : ℚ)

theorem killing_su8_on_zero : killing_su8 0 = 0 := by norm_num [killing_su8]
theorem killing_su8_on_2    : killing_su8 2 = 32 := by norm_num [killing_su8]
theorem killing_su8_on_neg1 : killing_su8 (-1) = -16 := by norm_num [killing_su8]

/-! ## Section 4 — A_7 Cartan matrix as an integer-valued function.

    Standard tridiagonal form: C(A_n)_{ij} = 2 δ_{ij} - δ_{|i-j|, 1}.
    For A_7 (7×7) with i, j ∈ {0, …, 6}.
-/

/-- (i, j) entry of the A_7 Cartan matrix: tridiag(2, -1). -/
@[reducible]
def cartan_A7_entry (i j : ℕ) : ℤ :=
  if i = j then 2
  else if i + 1 = j then -1
  else if j + 1 = i then -1
  else 0

/-! Spot-checks — the Cartan matrix values we will identify with trace products. -/

theorem cartan_A7_diag_0 : cartan_A7_entry 0 0 = 2 := by decide
theorem cartan_A7_diag_6 : cartan_A7_entry 6 6 = 2 := by decide
theorem cartan_A7_adj_01 : cartan_A7_entry 0 1 = -1 := by decide
theorem cartan_A7_adj_10 : cartan_A7_entry 1 0 = -1 := by decide
theorem cartan_A7_adj_56 : cartan_A7_entry 5 6 = -1 := by decide
theorem cartan_A7_far_02 : cartan_A7_entry 0 2 = 0 := by decide
theorem cartan_A7_far_06 : cartan_A7_entry 0 6 = 0 := by decide

/-! ## Section 5 — The master identity.

    **Theorem (CLM-046 main result):** For every (i, j) with
    0 ≤ i, j < 7, the trace product equals the A_7 Cartan entry.

    Equivalently: the Killing-form Gram matrix of the simple coroots
    equals 16 times the A_7 Cartan matrix, entry-for-entry.
-/

/-- **The core trace identity.**  `Tr(H_i · H_j) = C(A_7)_{ij}` for
    all i, j ∈ {0, …, 6}.  Closed by `interval_cases` on both indices
    followed by `decide` over the 49 direct computations. -/
theorem trace_prod_equals_cartan :
    ∀ i j : ℕ, i < 7 → j < 7 → trace_prod i j = cartan_A7_entry i j := by
  intros i j hi hj
  interval_cases i <;> interval_cases j <;> decide

/-- **The Killing-form identity (CLM-046 main theorem).**
    `K(H_i, H_j) = 16 · C(A_7)_{ij}` for all i, j ∈ {0, …, 6}. -/
theorem moduli_metric_equals_cartan :
    ∀ i j : ℕ, i < 7 → j < 7 →
      killing_su8 (trace_prod i j) = 16 * (cartan_A7_entry i j : ℚ) := by
  intros i j hi hj
  unfold killing_su8
  rw [trace_prod_equals_cartan i j hi hj]

/-! ## Section 6 — Uniform-prefactor cancellation.

    The factor 16 in `K(H_i, H_j) = 16 · C(A_7)_{ij}` cancels in any
    ratio of spectral quantities.  Specifically, the ratio of mean
    inverse eigenvalues ⟨λ⁻¹⟩(A_6) / ⟨λ⁻¹⟩(A_7) is uniform-prefactor
    independent, because any overall positive scale α sends
        α · M  ↦  α⁻¹ · spectrum  ↦  α · ⟨λ⁻¹⟩
    which cancels in the ratio ⟨λ⁻¹⟩(A_6)/⟨λ⁻¹⟩(A_7).

    The numerical content is (8/6)/(9/6) = 8/9, already closed by
    `cascade_cg_at_A7` in `CascadeCGRepTheory.lean`.
-/

/-- Cross-multiply form (avoids division): 8 · ⟨λ⁻¹⟩(A_7) = 9 · ⟨λ⁻¹⟩(A_6) · (9/8).
    Cleaner statement: 9 · ⟨λ⁻¹⟩(A_6) = 8 · ⟨λ⁻¹⟩(A_7) · (8/9) · (9/8),
    or simply: (n+2)/6 form gives cross-multiply equality. -/
theorem mean_inv_cross_multiply :
    8 * cartan_mean_inv 7 = 9 * cartan_mean_inv 6 := by
  unfold cartan_mean_inv; norm_num

/-- Mean-inverse-eigenvalue ratio at A_7 / A_6 level is the cascade r = 9/8. -/
theorem mean_inv_ratio_A7_over_A6 :
    cartan_mean_inv 7 / cartan_mean_inv 6 = 9 / 8 := by
  unfold cartan_mean_inv; norm_num

/-- Mean-inverse-eigenvalue ratio at A_6 / A_7 level is the cascade CG = 8/9. -/
theorem mean_inv_ratio_A6_over_A7 :
    cartan_mean_inv 6 / cartan_mean_inv 7 = 8 / 9 := by
  unfold cartan_mean_inv; norm_num

/-- Uniform-prefactor cancellation explicitly: whether we use the
    Killing-form Gram matrix (16 · C(A_7)) or the bare Cartan matrix
    (C(A_7)) to define ⟨λ⁻¹⟩, the ratio is identical.  This is the
    statement that the CG identification is normalization-independent. -/
theorem uniform_prefactor_cancels_in_cg_ratio :
    cartan_mean_inv 6 / cartan_mean_inv 7 = 8 / 9 ∧
    (16 * cartan_mean_inv 6) / (16 * cartan_mean_inv 7) = 8 / 9 := by
  refine ⟨?_, ?_⟩
  · unfold cartan_mean_inv; norm_num
  · unfold cartan_mean_inv; norm_num

/-! ## Section 7 — Bridge to CLM-032 rep-theoretic CG.

    The cascade CG ratio at A_7 is `cg_rat 7 = 8/9`, closed in
    `CascadeCGRepTheory.cascade_cg_at_A7`.  CLM-046 adds the moduli-
    metric interpretation: this ratio is now ALSO the ratio of mean
    inverse eigenvalues of the Killing-form Gram matrix restricted to
    the simple-coroot basis, divided by the same ratio at the prior
    cascade step.
-/

/-- The CLM-032 CG identity at rank 7.  Cited here to close the bridge. -/
theorem clm_032_cg_at_A7 : cg_rat 7 = 8 / 9 :=
  cascade_cg_at_A7

/-- **The bridge theorem.**  The moduli-metric ratio (from CLM-046)
    and the rep-theory CG ratio (from CLM-032) both equal 8/9. -/
theorem moduli_metric_and_rep_theory_agree :
    cartan_mean_inv 6 / cartan_mean_inv 7 = cg_rat 7 := by
  rw [mean_inv_ratio_A6_over_A7, clm_032_cg_at_A7]

/-! ## Section 8 — Master bundle for CLM-046.

    Bundles the three core facts:
      (1) Killing-form Gram matrix of simple coroots = 16 · A_7 Cartan matrix.
      (2) Mean-inverse-eigenvalue ratio is uniform-prefactor independent
          and equals 8/9.
      (3) This matches the rep-theory CG from CLM-032.
-/

/-- **CLM-046 master theorem — moduli metric = Cartan matrix.**

    Three-part conjunction:
      (i)   Entry-for-entry: K(H_i, H_j) = 16 · C(A_7)_{ij} for i, j < 7.
      (ii)  The uniform prefactor 16 cancels in the CG ratio: 8/9.
      (iii) This agrees with the CLM-032 rep-theory CG: `cg_rat 7 = 8/9`.
-/
theorem clm_046_moduli_metric_equals_cartan :
    (∀ i j : ℕ, i < 7 → j < 7 →
        killing_su8 (trace_prod i j) = 16 * (cartan_A7_entry i j : ℚ)) ∧
    (cartan_mean_inv 6 / cartan_mean_inv 7 = 8 / 9) ∧
    (cg_rat 7 = 8 / 9) := by
  refine ⟨?_, ?_, ?_⟩
  · intros i j hi hj
    exact moduli_metric_equals_cartan i j hi hj
  · exact mean_inv_ratio_A6_over_A7
  · exact cascade_cg_at_A7

/-! ## Section 9 — Scope boundary markers.

    The following three theorems are NOT proved here — they are flagged
    so any reader of the Lean file sees exactly what CLM-046 does NOT
    close.  Their honest status lives in the CLM-046 claim file §4.3.

    We state them as `Prop` values (named opaque statements) and do
    not attempt to prove them.  Anyone who thinks they have a proof
    is welcome to remove the `axiom` marker — but as of CLM-046 they
    remain open.  (NO axiom is declared here; this is a documentation
    block only.)
-/

/-- **NOT PROVED (scope boundary):** Higher-loop wavefunction
    renormalization Z_i(μ) is uniform across cascade nodes.  This is
    false at 1-loop under the full SU(8) effective action — see
    CLM-042 (reconnaissance), CLM-043 (minimal-coupling honest-negative),
    CLM-044 (non-minimal-coupling honest-negative). -/
def scope_not_closed_loop_z_uniform : Prop :=
  ∀ (_μ : ℚ) (i : ℕ), i < 7 → ∃ (Z : ℚ), Z = 1  -- placeholder; CLM-046 does not address

/-- **NOT PROVED (scope boundary):** Full Route B path-integral derivation
    of CG from the SU(8) functional integral.  Paper-gated per
    Commandment VIII; CLM-042/043/044 document the three honest attempts. -/
def scope_not_closed_path_integral : Prop :=
  True  -- placeholder; CLM-046 does not address

/-- **NOT PROVED (scope boundary):** CLM-001 upgraded from `theorem-joint`
    to unqualified `theorem`.  CLM-046 tightens the spectral-identification
    postulate but does not by itself complete Route B. -/
def scope_not_closed_clm_001_unqualified : Prop :=
  True  -- placeholder; CLM-046 does not address

end UFT.CascadeModuliMetric
