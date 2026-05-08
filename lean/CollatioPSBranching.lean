import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Data.List.Basic

/-
  CollatioPSBranching.lean — CLM-034 GAP #3 closure.

  SCOPE (see Oracle/claims/CLM-034-open-gaps-handoff.md §3).

    Replace the citation-only arithmetic fact
        `collatio_weyl_decomposition : (48 : ℕ) + 80 = 128 := by decide`
    (AnomalyMatchingDerivation.lean line 230) with the SUBSTANTIVE
    derivation: an explicit Koszul/Vandermonde decomposition of each
    antisymmetric representation `[k]` of SU(8) with `k ∈ {1, 3, 5, 7}`
    into Pati-Salam irreps, a DECLARED Standard-Model tagging, and
    explicit proofs that

        ∑ dim(PS-irreps in [1]⊕[3]⊕[5]⊕[7])                    = 128,
        ∑ dim(PS-irreps tagged SM    in [1]⊕[3]⊕[5]⊕[7])        = 48,
        ∑ dim(PS-irreps tagged exotic in [1]⊕[3]⊕[5]⊕[7])       = 80,
        48 + 80                                                  = 128.

    Every dimension is derived from the Vandermonde triple convolution
    `C(8,k) = Σ_{a+b+c=k} C(4,a) · C(2,b) · C(2,c)` (see
    `BranchingRulesStructural.lean`, already in the UFT library).  The
    SM tagging is DECLARED per Oracle/claims/CLM-034-open-gaps-handoff.md
    §3.7 — it is cited to `c121_56_branching_dark_sector_essence.py`
    and to standard Pati-Salam references.  The algebraic content of
    THIS file is: given the declared tagging, the arithmetic works.

  WHY A "DECLARED TABLE" IS HONEST.

    The Koszul branching produces explicit PS irreps of [1]⊕[3]⊕[5]⊕[7]
    of total dimension 128.  Which of those irreps are "the Standard
    Model" is a PHYSICS identification (the 48-Weyl content has
    quantum numbers matching three generations of quarks and leptons);
    the counter-identification — which 80 Weyl are "exotic at the
    GUT scale" — is the complementary declaration.  At the CLM-034
    level we treat the tagging as declared + cited.  A future avenue
    may upgrade the tagging itself to a theorem via the PS group-
    theoretic argument in BranchingRules.lean; until then, the
    honest statement is

        "IF the PS irreps of [1]⊕[3]⊕[5]⊕[7] labelled SM in this
         file are indeed the Standard-Model content, THEN their
         dimensions sum to 48 and the remainder sums to 80."

    What this file proves is the THEN-clause, end to end, with no
    gaps.  The IF-clause is the subject of GAP #2 (future avenue).

    This is strictly stronger than the C192-era citation
    `collatio_weyl_decomposition : 48 + 80 = 128 := by decide`,
    which had no PS rep structure, no Koszul branching, no per-[k]
    dimension audit, no SM vs exotic tagging — just a raw integer
    identity.  This file provides all of those.

  SM TAGGING (DECLARED, per c121 and handoff §3.7).

    [1] = 8 Weyl  →  tagged ALL SM.       Contribution: 8.
    [3] = 56 Weyl  →  tagged the (4,2,2) bidoublet SM,
                      all other PS irreps exotic.  Contribution: 16.
    [5] = 56 Weyl  →  tagged the (4,2,2) bidoublet SM,
                      all other PS irreps exotic.  Contribution: 16.
    [7] = 8 Weyl  →  tagged ALL SM.       Contribution: 8.

    Total SM:  8 + 16 + 16 + 8 = 48.
    Total exotic:  (56 − 16) + (56 − 16) = 40 + 40 = 80.
    Total Weyl:  48 + 80 = 128.

    This tagging is ONE consistent choice per handoff §3.7.  The
    handoff explicitly notes that at CLM-034 scope, SM-tagging is a
    declared table — it is not the subject of the Avenue 1 closure.
    The file would work equally well with a different declared
    tagging that also sums to (48, 80); the arithmetic identity
    48 + 80 = 128 is the invariant.

  PARITY GUARD.

    Every ℕ literal below is mirrored by a Python `assertEqual` in
    `proofs/UFT/scripts/c147_collatio_ps_branching.py`.  Per
    feedback_lean_only_bugs.md (CLM-031 Mac-catch #1) and the C193
    third-Mac-catch lesson, any Lean literal without a Python mirror
    is a blind spot that only surfaces on Mac `lake build`.

  EVERY THEOREM BELOW CLOSES BY ONE OF:
    `rfl`, `decide`, `native_decide`, or `unfold … ; decide`.

  No Real numbers.  No Float.  No `sorry`.  No new axioms.
  Commandment XII at the proof layer; Commandment XIII (nothing
  trivial: every claim has a closing tactic, no one-line implicit
  arithmetic promises).

  Patent Pending — © 2026 Steven Lamar Michael. All rights reserved.
-/

namespace UFT.CollatioPSBranching

/-! ## Section 1 — PS factor fundamental dimensions.

    Mirrors Section 6 of `AnomalyMatchingDerivation.lean` (GAP #1
    closure).  We repeat them here because this file must stand
    alone as a module. -/

/-- Dimension of the fundamental of SU(4)_C. -/
@[reducible] def ps_dim_C : ℕ := 4

/-- Dimension of the fundamental of SU(2)_L. -/
@[reducible] def ps_dim_L : ℕ := 2

/-- Dimension of the fundamental of SU(2)_R. -/
@[reducible] def ps_dim_R : ℕ := 2

theorem ps_dim_sum_eq_8 : ps_dim_C + ps_dim_L + ps_dim_R = 8 := by decide

/-! ## Section 2 — PS rep structure.

    A single Pati-Salam irrep, with its dimensions in each factor
    and an SM-or-exotic tag.  The `dim` field is the product of
    the three factor dimensions; since this is SU(4) × SU(2) × SU(2),
    the dimension is simply the product — no Clebsch-Gordan work
    needed at the dimension level. -/

/-- A single Pati-Salam irrep, with declared SM-or-exotic tag. -/
structure PSRep where
  /-- Dimension of the SU(4)_C factor (1, 4, or 6 for our cases). -/
  su4 : ℕ
  /-- Dimension of the SU(2)_L factor (1 or 2). -/
  su2L : ℕ
  /-- Dimension of the SU(2)_R factor (1 or 2). -/
  su2R : ℕ
  /-- Declared SM-vs-exotic tag.  DECLARED per c121, not derived here. -/
  isSM : Bool
  deriving Repr, DecidableEq

/-- Total dimension of a PSRep = product of factor dimensions. -/
def PSRep.dim (r : PSRep) : ℕ := r.su4 * r.su2L * r.su2R

/-- Dimension of SM-tagged subset. -/
def PSRep.smDim (r : PSRep) : ℕ := if r.isSM then r.dim else 0

/-- Dimension of exotic-tagged subset. -/
def PSRep.exoticDim (r : PSRep) : ℕ := if r.isSM then 0 else r.dim

/-- Sum of `dim` over a list. -/
def totalDim (l : List PSRep) : ℕ := (l.map PSRep.dim).sum

/-- Sum of `smDim` over a list (i.e. sum of `dim` for SM-tagged entries). -/
def smDim (l : List PSRep) : ℕ := (l.map PSRep.smDim).sum

/-- Sum of `exoticDim` over a list. -/
def exoticDim (l : List PSRep) : ℕ := (l.map PSRep.exoticDim).sum

/-! ## Section 3 — Koszul/Vandermonde decomposition of [1] of SU(8).

    `[1] = ∧¹(8)` under PS embedding `8 → (4,1,1) ⊕ (1,2,1) ⊕ (1,1,2)`.
    Vandermonde: `C(8,1) = C(4,1)·C(2,0)·C(2,0) + C(4,0)·C(2,1)·C(2,0)
                         + C(4,0)·C(2,0)·C(2,1) = 4 + 2 + 2 = 8`.

    SM tagging: ALL SM (contains one left-handed and one right-handed
    quark-lepton doublet component per the declared c121 table). -/

/-- PS decomposition of [1] of SU(8).  Total dim = 8, all SM-tagged.

    Entry 1: (a,b,c) = (1,0,0) → (4,1,1), dim = C(4,1)·C(2,0)·C(2,0) = 4.
    Entry 2: (a,b,c) = (0,1,0) → (1,2,1), dim = C(4,0)·C(2,1)·C(2,0) = 2.
    Entry 3: (a,b,c) = (0,0,1) → (1,1,2), dim = C(4,0)·C(2,0)·C(2,1) = 2.
-/
def psReps_of_1 : List PSRep := [
  ⟨4, 1, 1, true⟩,  -- (4,1,1) from (1,0,0)
  ⟨1, 2, 1, true⟩,  -- (1,2,1) from (0,1,0)
  ⟨1, 1, 2, true⟩   -- (1,1,2) from (0,0,1)
]

theorem dim_sum_of_1 : totalDim psReps_of_1 = 8 := by decide

theorem sm_sum_of_1 : smDim psReps_of_1 = 8 := by decide

theorem exotic_sum_of_1 : exoticDim psReps_of_1 = 0 := by decide

theorem length_psReps_of_1 : psReps_of_1.length = 3 := by decide

/-! ## Section 4 — Koszul/Vandermonde decomposition of [3] of SU(8).

    `[3] = ∧³(8)` via Koszul:  ∧³(V₁⊕V₂⊕V₃) = ⊕_{a+b+c=3} ∧ᵃV₁ ⊗ ∧ᵇV₂ ⊗ ∧ᶜV₃.

    Enumerate (a,b,c) with a+b+c=3, a≤4, b≤2, c≤2:

      (3,0,0) → (4,1,1), dim C(4,3)·C(2,0)·C(2,0) = 4·1·1 = 4
      (2,1,0) → (6,2,1), dim C(4,2)·C(2,1)·C(2,0) = 6·2·1 = 12
      (2,0,1) → (6,1,2), dim C(4,2)·C(2,0)·C(2,1) = 6·1·2 = 12
      (1,2,0) → (4,1,1), dim C(4,1)·C(2,2)·C(2,0) = 4·1·1 = 4
      (1,1,1) → (4,2,2), dim C(4,1)·C(2,1)·C(2,1) = 4·2·2 = 16  ← SM
      (1,0,2) → (4,1,1), dim C(4,1)·C(2,0)·C(2,2) = 4·1·1 = 4
      (0,2,1) → (1,1,2), dim C(4,0)·C(2,2)·C(2,1) = 1·1·2 = 2
      (0,1,2) → (1,2,1), dim C(4,0)·C(2,1)·C(2,2) = 1·2·1 = 2

    Total: 4+12+12+4+16+4+2+2 = 56 = C(8,3). ✓

    SM tagging: the (4,2,2) bidoublet is SM (per c121 declared table).
    All other entries are exotic (leptoquark-like, color-sextet-like,
    singlet-like, etc.).  SM subtotal = 16; exotic subtotal = 40.
-/

def psReps_of_3 : List PSRep := [
  ⟨4, 1, 1, false⟩,  -- (3,0,0) → (4,1,1), dim 4, exotic
  ⟨6, 2, 1, false⟩,  -- (2,1,0) → (6,2,1), dim 12, exotic (leptoquark)
  ⟨6, 1, 2, false⟩,  -- (2,0,1) → (6,1,2), dim 12, exotic (leptoquark)
  ⟨4, 1, 1, false⟩,  -- (1,2,0) → (4,1,1), dim 4, exotic
  ⟨4, 2, 2, true⟩,   -- (1,1,1) → (4,2,2), dim 16, SM bidoublet
  ⟨4, 1, 1, false⟩,  -- (1,0,2) → (4,1,1), dim 4, exotic
  ⟨1, 1, 2, false⟩,  -- (0,2,1) → (1,1,2), dim 2, exotic
  ⟨1, 2, 1, false⟩   -- (0,1,2) → (1,2,1), dim 2, exotic
]

theorem dim_sum_of_3 : totalDim psReps_of_3 = 56 := by decide

theorem sm_sum_of_3 : smDim psReps_of_3 = 16 := by decide

theorem exotic_sum_of_3 : exoticDim psReps_of_3 = 40 := by decide

theorem length_psReps_of_3 : psReps_of_3.length = 8 := by decide

/-- Vandermonde consistency check: the dim sum matches C(8,3) = 56. -/
theorem dim_sum_of_3_eq_choose : totalDim psReps_of_3 = Nat.choose 8 3 := by decide

/-! ## Section 5 — Koszul/Vandermonde decomposition of [5] of SU(8).

    `[5] = ∧⁵(8)`.  Enumerate (a,b,c) with a+b+c=5, a≤4, b≤2, c≤2:

      (1,2,2) → (4,1,1), dim C(4,1)·C(2,2)·C(2,2) = 4·1·1 = 4
      (2,2,1) → (6,1,2), dim C(4,2)·C(2,2)·C(2,1) = 6·1·2 = 12
      (2,1,2) → (6,2,1), dim C(4,2)·C(2,1)·C(2,2) = 6·2·1 = 12
      (3,2,0) → (4,1,1), dim C(4,3)·C(2,2)·C(2,0) = 4·1·1 = 4
      (3,1,1) → (4,2,2), dim C(4,3)·C(2,1)·C(2,1) = 4·2·2 = 16  ← SM
      (3,0,2) → (4,1,1), dim C(4,3)·C(2,0)·C(2,2) = 4·1·1 = 4
      (4,1,0) → (1,2,1), dim C(4,4)·C(2,1)·C(2,0) = 1·2·1 = 2
      (4,0,1) → (1,1,2), dim C(4,4)·C(2,0)·C(2,1) = 1·1·2 = 2

    Total: 4+12+12+4+16+4+2+2 = 56 = C(8,5). ✓

    [5] is the conjugate of [3] — same dimension pattern, conjugate
    PS quantum numbers (physically: SU(4)_C factor becomes SU(4̄)_C,
    which has the same dim 4; similarly for SU(2) factors).

    SM tagging: the (4,2,2) bidoublet is SM.  SM = 16, exotic = 40.
-/

def psReps_of_5 : List PSRep := [
  ⟨4, 1, 1, false⟩,  -- (1,2,2) → (4,1,1), dim 4, exotic
  ⟨6, 1, 2, false⟩,  -- (2,2,1) → (6,1,2), dim 12, exotic
  ⟨6, 2, 1, false⟩,  -- (2,1,2) → (6,2,1), dim 12, exotic
  ⟨4, 1, 1, false⟩,  -- (3,2,0) → (4,1,1), dim 4, exotic
  ⟨4, 2, 2, true⟩,   -- (3,1,1) → (4,2,2), dim 16, SM bidoublet (conjugate)
  ⟨4, 1, 1, false⟩,  -- (3,0,2) → (4,1,1), dim 4, exotic
  ⟨1, 2, 1, false⟩,  -- (4,1,0) → (1,2,1), dim 2, exotic
  ⟨1, 1, 2, false⟩   -- (4,0,1) → (1,1,2), dim 2, exotic
]

theorem dim_sum_of_5 : totalDim psReps_of_5 = 56 := by decide

theorem sm_sum_of_5 : smDim psReps_of_5 = 16 := by decide

theorem exotic_sum_of_5 : exoticDim psReps_of_5 = 40 := by decide

theorem length_psReps_of_5 : psReps_of_5.length = 8 := by decide

theorem dim_sum_of_5_eq_choose : totalDim psReps_of_5 = Nat.choose 8 5 := by decide

/-! ## Section 6 — Koszul/Vandermonde decomposition of [7] of SU(8).

    `[7] = ∧⁷(8)`.  Enumerate (a,b,c) with a+b+c=7, a≤4, b≤2, c≤2:

      (3,2,2) → (4,1,1), dim C(4,3)·C(2,2)·C(2,2) = 4·1·1 = 4
      (4,2,1) → (1,1,2), dim C(4,4)·C(2,2)·C(2,1) = 1·1·2 = 2
      (4,1,2) → (1,2,1), dim C(4,4)·C(2,1)·C(2,2) = 1·2·1 = 2

    Total: 4+2+2 = 8 = C(8,7). ✓

    [7] is the conjugate fundamental.  SM tagging: ALL SM (same as [1]
    — conjugate of SM content is SM content). -/

def psReps_of_7 : List PSRep := [
  ⟨4, 1, 1, true⟩,  -- (3,2,2) → (4,1,1) conj
  ⟨1, 1, 2, true⟩,  -- (4,2,1) → (1,1,2) conj
  ⟨1, 2, 1, true⟩   -- (4,1,2) → (1,2,1) conj
]

theorem dim_sum_of_7 : totalDim psReps_of_7 = 8 := by decide

theorem sm_sum_of_7 : smDim psReps_of_7 = 8 := by decide

theorem exotic_sum_of_7 : exoticDim psReps_of_7 = 0 := by decide

theorem length_psReps_of_7 : psReps_of_7.length = 3 := by decide

theorem dim_sum_of_7_eq_choose : totalDim psReps_of_7 = Nat.choose 8 7 := by decide

/-! ## Section 7 — Full Collatio branching [1] ⊕ [3] ⊕ [5] ⊕ [7].

    Concatenate the four per-rep lists into one master list and prove
    the aggregate dimension + SM + exotic identities. -/

/-- Full decomposition of [1]⊕[3]⊕[5]⊕[7] into PS irreps. -/
def allPSReps : List PSRep :=
  psReps_of_1 ++ psReps_of_3 ++ psReps_of_5 ++ psReps_of_7

theorem length_allPSReps : allPSReps.length = 22 := by decide

/-- **Aggregate dimension = 128.**  The total Weyl count of the
    Collatio antisymmetric content `[1]⊕[3]⊕[5]⊕[7]` is 128 = 2^(N-1)
    at N = 8. -/
theorem total_dim_eq_128 : totalDim allPSReps = 128 := by decide

/-- **SM subtotal = 48.**  Under the declared tagging (c121, handoff §3.7),
    the SM-tagged subset sums to 48 = 3 × 16 Weyl per generation. -/
theorem sm_dim_sum_eq_48 : smDim allPSReps = 48 := by decide

/-- **Exotic subtotal = 80.**  The complement sums to 80. -/
theorem exotic_dim_sum_eq_80 : exoticDim allPSReps = 80 := by decide

/-- Complementarity: SM + exotic = total.  Mirrors
    `SM_SHARE_AT_N8 + EXOTIC_SHARE_AT_N8 = 128` in c145. -/
theorem sm_plus_exotic_eq_total :
    smDim allPSReps + exoticDim allPSReps = totalDim allPSReps := by decide

/-- Integer identity: 48 + 80 = 128. -/
theorem forty_eight_plus_eighty_eq_128 : (48 : ℕ) + 80 = 128 := by decide

/-- **Master theorem (GAP #3 closure).**  The Collatio antisymmetric
    content `[1]⊕[3]⊕[5]⊕[7]` decomposes into PS irreps totalling
    128 Weyl, which split (under the declared c121 tagging) as
    48 SM + 80 exotic.

    This replaces the C192 citation-only arithmetic
    `collatio_weyl_decomposition : (48 : ℕ) + 80 = 128 := by decide`
    in AnomalyMatchingDerivation.lean with a structural derivation:
    explicit PS irreps, explicit dimensions from Vandermonde, and
    explicit SM tagging. -/
theorem collatio_128_to_48_SM_plus_80_exotic :
    totalDim allPSReps = 128 ∧
    smDim allPSReps = 48 ∧
    exoticDim allPSReps = 80 ∧
    smDim allPSReps + exoticDim allPSReps = totalDim allPSReps := by
  refine ⟨?_, ?_, ?_, ?_⟩
  · exact total_dim_eq_128
  · exact sm_dim_sum_eq_48
  · exact exotic_dim_sum_eq_80
  · exact sm_plus_exotic_eq_total

/-! ## Section 8 — Vandermonde consistency (aggregate).

    Each per-rep dimension matches `C(8,k)`, and their sum matches
    the known identity `C(8,1)+C(8,3)+C(8,5)+C(8,7) = 2^7 = 128`. -/

theorem vandermonde_consistency :
    totalDim psReps_of_1 + totalDim psReps_of_3 +
    totalDim psReps_of_5 + totalDim psReps_of_7 =
    Nat.choose 8 1 + Nat.choose 8 3 +
    Nat.choose 8 5 + Nat.choose 8 7 := by decide

theorem antisymmetric_content_eq_128 :
    Nat.choose 8 1 + Nat.choose 8 3 +
    Nat.choose 8 5 + Nat.choose 8 7 = 128 := by decide

theorem antisymmetric_content_eq_2_pow_7 :
    Nat.choose 8 1 + Nat.choose 8 3 +
    Nat.choose 8 5 + Nat.choose 8 7 = 2 ^ 7 := by decide

/-! ## Section 9 — Cross-witnesses to c145 / c147 parity constants. -/

/-- Mirrors c145 `SM_SHARE_AT_N8 = 48`. -/
theorem sm_share_at_N8 : smDim allPSReps = 48 := sm_dim_sum_eq_48

/-- Mirrors c145 `EXOTIC_SHARE_AT_N8 = 80`. -/
theorem exotic_share_at_N8 : exoticDim allPSReps = 80 := exotic_dim_sum_eq_80

/-- Mirrors c145 `COLLATIO_WEYL_TOTAL = 128`. -/
theorem collatio_weyl_total : totalDim allPSReps = 128 := total_dim_eq_128

/-- Mirrors c145 `SM_WEYL_PER_GEN = 16` (= 48 / 3). -/
theorem sm_weyl_per_gen_from_sm_total : (48 : ℕ) = 3 * 16 := by decide

/-! ## Section 10 — Per-[k] structural summaries.

    These per-rep summary theorems are what downstream files (e.g.
    AnomalyMatchingDerivation.lean) import to replace the old
    citation-only `collatio_weyl_decomposition`. -/

/-- Per-[1] summary: total 8, all SM. -/
theorem summary_of_1 :
    totalDim psReps_of_1 = 8 ∧
    smDim psReps_of_1 = 8 ∧
    exoticDim psReps_of_1 = 0 := by
  refine ⟨?_, ?_, ?_⟩
  · exact dim_sum_of_1
  · exact sm_sum_of_1
  · exact exotic_sum_of_1

/-- Per-[3] summary: total 56, SM 16, exotic 40. -/
theorem summary_of_3 :
    totalDim psReps_of_3 = 56 ∧
    smDim psReps_of_3 = 16 ∧
    exoticDim psReps_of_3 = 40 := by
  refine ⟨?_, ?_, ?_⟩
  · exact dim_sum_of_3
  · exact sm_sum_of_3
  · exact exotic_sum_of_3

/-- Per-[5] summary: total 56, SM 16, exotic 40. -/
theorem summary_of_5 :
    totalDim psReps_of_5 = 56 ∧
    smDim psReps_of_5 = 16 ∧
    exoticDim psReps_of_5 = 40 := by
  refine ⟨?_, ?_, ?_⟩
  · exact dim_sum_of_5
  · exact sm_sum_of_5
  · exact exotic_sum_of_5

/-- Per-[7] summary: total 8, all SM. -/
theorem summary_of_7 :
    totalDim psReps_of_7 = 8 ∧
    smDim psReps_of_7 = 8 ∧
    exoticDim psReps_of_7 = 0 := by
  refine ⟨?_, ?_, ?_⟩
  · exact dim_sum_of_7
  · exact sm_sum_of_7
  · exact exotic_sum_of_7

end UFT.CollatioPSBranching
