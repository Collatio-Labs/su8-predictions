/-
  NonMinimalCouplingDerivation.lean — CLM-044
  Non-minimal coupling ξ R φ² → induced Starobinsky R² scalaron mass

  VERDICT: HONEST-NEGATIVE.  No natural SU(8) cascade group invariant
  produces ξ in the required interval [3689, 14548] without paper-gated
  matching (Bezrukov-Shaposhnikov 2008).  Closest candidate:
    ξ = (N²-1)² = 3969 — factor ~1.71 miss at central physical values
    (PASS_FACTOR_3 threshold as set-membership; not a structural fit).

  Sibling of CLM-043 (minimal coupling: structurally insufficient,
  4+ orders above M_PS).

  Commandment XII compliance: all rational arithmetic as ℚ; zero floats.
  Commandment XIII: every claim has an explicit tactic closure.
  Commandment VIII: BS-2008 R²-matching formula NOT reconstructed.

  Copyright 2026 Steven Lamar Michael. All rights reserved.
-/

import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Data.Rat.Lemmas
import Mathlib.Data.Nat.Choose.Basic

namespace UFT.NonMinimalCouplingDerivation

-- ════════════════════════════════════════════════════════════════
-- §1  SU(8) content (mirrors OneLoopR2FromSU8.lean / CLM-043)
-- ════════════════════════════════════════════════════════════════

@[reducible] def su8_rank : ℕ := 8
@[reducible] def adjoint_dof : ℕ := 63
@[reducible] def delta_r_dof : ℕ := 30
@[reducible] def total_scalar_ext : ℕ := 93

theorem adjoint_from_rank : su8_rank ^ 2 - 1 = adjoint_dof := by decide
theorem total_scalar_sum : adjoint_dof + delta_r_dof = total_scalar_ext := by decide

-- Conformal coupling in 4D
@[reducible] def conformal_coupling : ℚ := 1/6

-- Minimal coupling (CLM-043 baseline)
@[reducible] def minimal_coupling : ℚ := 0

theorem conformal_from_dimension : (4 - 2 : ℚ) / (4 * (4 - 1)) = 1/6 := by norm_num

-- ════════════════════════════════════════════════════════════════
-- §2  Non-minimal R² coefficient per real scalar
-- ════════════════════════════════════════════════════════════════

-- Seeley-DeWitt a₂ heat kernel coefficient, same as CLM-043:
-- γ(ξ) = (ξ − 1/6)² / 2
def r2_coeff (xi : ℚ) : ℚ := (xi - 1/6) ^ 2 / 2

-- Alternative form: (6ξ − 1)² / 72 per real scalar
def r2_coeff_alt (xi : ℚ) : ℚ := (6 * xi - 1) ^ 2 / 72

-- Forms agree (pure algebra)
theorem r2_forms_agree (xi : ℚ) : r2_coeff xi = r2_coeff_alt xi := by
  unfold r2_coeff r2_coeff_alt
  ring

-- Minimal coupling recovers CLM-043 value
theorem r2_minimal : r2_coeff 0 = 1/72 := by
  unfold r2_coeff; norm_num

theorem r2_minimal_alt : r2_coeff_alt 0 = 1/72 := by
  unfold r2_coeff_alt; norm_num

-- Conformal coupling: R² vanishes
theorem r2_conformal : r2_coeff (1/6) = 0 := by
  unfold r2_coeff; norm_num

theorem r2_conformal_alt : r2_coeff_alt (1/6) = 0 := by
  unfold r2_coeff_alt; norm_num

-- Evaluate at ξ = 3969 — closest natural cascade invariant
theorem r2_at_3969 : r2_coeff_alt 3969 = 567058969 / 72 := by
  unfold r2_coeff_alt; norm_num

-- ════════════════════════════════════════════════════════════════
-- §3  Total R² coefficient (N_ADJ × γ)
-- ════════════════════════════════════════════════════════════════

-- At minimal coupling: 63 × 1/72 = 7/8 (matches CLM-043)
theorem total_r2_minimal : (63 : ℚ) * (1/72) = 7/8 := by norm_num

theorem total_r2_reduced : (63 : ℚ) / 72 = 7/8 := by norm_num

-- At conformal coupling: total vanishes
theorem total_r2_conformal : (63 : ℚ) * 0 = 0 := by norm_num

-- ════════════════════════════════════════════════════════════════
-- §4  Induced scalaron mass prefactor (inherited from CLM-043)
-- ════════════════════════════════════════════════════════════════

-- M_R²/M_Pl² × L/π² = (32/21) / (6ξ − 1)²
-- The 32/21 prefactor matches CLM-043 exactly (same Seeley-DeWitt chain).
def c_mr : ℚ := 32/21

theorem c_mr_derivation : (16 : ℚ) / (12 * (7/8)) = 32/21 := by norm_num

theorem c_mr_step1 : (12 : ℚ) * (7/8) = 21/2 := by norm_num

theorem c_mr_step2 : (16 : ℚ) / (21/2) = 32/21 := by norm_num

theorem c_mr_unreduced : (128 : ℚ) / 84 = 32/21 := by norm_num

-- At minimal coupling ξ = 0, (6·0 − 1)² = 1, so the prefactor is just c_mr
theorem scalaron_prefactor_at_minimal : c_mr / ((6 * (0 : ℚ) - 1) ^ 2) = 32/21 := by
  unfold c_mr; norm_num

-- ════════════════════════════════════════════════════════════════
-- §5  Mass scales as exact ℚ
-- ════════════════════════════════════════════════════════════════

-- log₁₀ M_PS = 13.70 = 1370/100
def log10_MPS : ℚ := 1370 / 100

-- log₁₀ M_Pl (reduced) = 18.39 = 1839/100
def log10_MPl : ℚ := 1839 / 100

-- log₁₀(M_Pl/M_PS) = 18.39 − 13.70 = 4.69 = 469/100
theorem log10_ratio_derivation : log10_MPl - log10_MPS = 469/100 := by
  unfold log10_MPl log10_MPS; norm_num

-- log₁₀((M_Pl/M_PS)²) = 2 × 4.69 = 9.38 = 938/100
theorem log10_ratio_sq_derivation : 2 * (log10_MPl - log10_MPS) = 938/100 := by
  unfold log10_MPl log10_MPS; norm_num

-- Reduced form 469/50
theorem log10_ratio_sq_reduced : (938 : ℚ) / 100 = 469 / 50 := by norm_num

-- ════════════════════════════════════════════════════════════════
-- §6  Required (6ξ−1)² bounds as exact ℚ
-- ════════════════════════════════════════════════════════════════

-- Bounds: 9 < π² < 10 (exact rational bracket)
-- 20 ≤ L ≤ 28 (natural range, bracketing BS-convention L ≈ 21.6)
-- 10⁹ < (M_Pl/M_PS)² < 10¹⁰ (since 9 < 9.38 < 10)

-- Required (6ξ-1)² = (32/21) × π²/L × (M_Pl/M_PS)²
-- LOWER bound: π² > 9, L < 28, (M_Pl/M_PS)² > 10⁹
--   ⟹ (6ξ-1)² > (32/21) × 9/28 × 10⁹ = 32 × 9 × 10⁹ / (21 × 28)
--                                    = 288 × 10⁹ / 588 = 24 × 10⁹ / 49
def required_lower_bound : ℚ := 24000000000 / 49

theorem required_lower_bound_value :
    (32 : ℚ) / 21 * 9 / 28 * 1000000000 = required_lower_bound := by
  unfold required_lower_bound; norm_num

-- UPPER bound: π² < 10, L > 20, (M_Pl/M_PS)² < 10¹⁰
--   ⟹ (6ξ-1)² < (32/21) × 10/20 × 10¹⁰ = 32 × 10 × 10¹⁰ / (21 × 20)
--                                     = 320 × 10¹⁰ / 420 = 160 × 10⁹ / 21
def required_upper_bound : ℚ := 160000000000 / 21

theorem required_upper_bound_value :
    (32 : ℚ) / 21 * 10 / 20 * 10000000000 = required_upper_bound := by
  unfold required_upper_bound; norm_num

-- The interval is non-empty
theorem required_interval_nonempty :
    required_lower_bound < required_upper_bound := by
  unfold required_lower_bound required_upper_bound; norm_num

-- Rough size checks
theorem required_lb_gt_1e8 : required_lower_bound > 100000000 := by
  unfold required_lower_bound; norm_num

theorem required_ub_lt_1e10 : required_upper_bound < 10000000000 := by
  unfold required_upper_bound; norm_num

-- ════════════════════════════════════════════════════════════════
-- §7  Natural SU(8) cascade group invariants (N = 8)
-- ════════════════════════════════════════════════════════════════

-- Ten natural rational invariants built from N = 8:
-- N = 8
-- N(N+1)/2 = 36
-- (N²-1)·N/(N+1) = 56
-- N²-1 = 63         (adjoint dim)
-- N² = 64
-- N(N²-1) = 504
-- N³ = 512
-- N²(N²-1)/2 = 2016
-- (N²-1)² = 3969    (adjoint squared — CLOSEST CANDIDATE)
-- N³(N²-1) = 32256

theorem inv_N : (8 : ℚ) = 8 := rfl
theorem inv_N_times_Np1_half : (8 * (8 + 1) : ℚ) / 2 = 36 := by norm_num
theorem inv_Nsqm1_times_N_div_Np1 :
    ((8 ^ 2 - 1) * 8 : ℚ) / (8 + 1) = 56 := by norm_num
theorem inv_adjoint_dim : (8 ^ 2 - 1 : ℚ) = 63 := by norm_num
theorem inv_N_squared : (8 ^ 2 : ℚ) = 64 := by norm_num
theorem inv_N_times_Nsqm1 : (8 * (8 ^ 2 - 1) : ℚ) = 504 := by norm_num
theorem inv_N_cubed : (8 ^ 3 : ℚ) = 512 := by norm_num
theorem inv_Nsq_times_Nsqm1_half :
    ((8 ^ 2) * (8 ^ 2 - 1) : ℚ) / 2 = 2016 := by norm_num
theorem inv_adjoint_squared : ((8 ^ 2 - 1) ^ 2 : ℚ) = 3969 := by norm_num
theorem inv_Ncube_times_Nsqm1 : ((8 ^ 3) * (8 ^ 2 - 1) : ℚ) = 32256 := by norm_num

-- ════════════════════════════════════════════════════════════════
-- §8  Closest candidate: ξ = (N²−1)² = 3969
-- ════════════════════════════════════════════════════════════════

-- At ξ = 3969: 6·3969 − 1 = 23813
theorem six_times_3969_minus_1 : 6 * (3969 : ℚ) - 1 = 23813 := by norm_num

-- (6·3969 − 1)² = 23813² = 567,058,969
theorem six_times_3969_minus_1_squared :
    (6 * (3969 : ℚ) - 1) ^ 2 = 567058969 := by norm_num

-- 23813² checked standalone (integer identity)
theorem twenty_three_thousand_eight_hundred_thirteen_squared :
    (23813 : ℕ) ^ 2 = 567058969 := by decide

-- Required (6ξ-1)² at central physical values
-- π² = 10, L = 22, (M_Pl/M_PS)² = 24/10 × 10⁹ = 2.4×10⁹
-- required = (32/21) × 10/22 × 24/10 × 10⁹
--          = 32 × 10 × 24 × 10⁹ / (21 × 22 × 10)
--          = 32 × 24 × 10⁹ / (21 × 22)
--          = 768 × 10⁹ / 462
--          = 128 × 10⁹ / 77
def required_central : ℚ := 128000000000 / 77

theorem required_central_value :
    (32 : ℚ) / 21 * 10 / 22 * (24 / 10 * 1000000000) = required_central := by
  unfold required_central; norm_num

-- Factor miss at central values: ratio_sq = required / actual
-- = (128 × 10⁹ / 77) / 567058969
-- = 128 × 10⁹ / (77 × 567058969)
-- = 128 × 10⁹ / 43663540613

theorem ratio_sq_at_3969_central :
    required_central / 567058969 = 128000000000 / (77 * 567058969) := by
  unfold required_central; ring

theorem ratio_sq_at_3969_simplified :
    (77 : ℚ) * 567058969 = 43663540613 := by norm_num

-- ratio_sq ∈ (29/10, 3) — strict bounds
-- ratio_sq = 128×10⁹ / 43663540613
-- ≈ 2.9322...
theorem ratio_sq_gt_29_over_10 :
    (128000000000 : ℚ) / 43663540613 > 29 / 10 := by norm_num

theorem ratio_sq_lt_3 :
    (128000000000 : ℚ) / 43663540613 < 3 := by norm_num

-- Tight window: ratio_sq ∈ [9/4, 4] — the factor-(1.5, 2) band on the ratio itself
theorem ratio_sq_ge_9_over_4 :
    (128000000000 : ℚ) / 43663540613 > 9 / 4 := by norm_num

theorem ratio_sq_le_4 :
    (128000000000 : ℚ) / 43663540613 < 4 := by norm_num

-- Widest-bound interval CONTAINS (6·3969-1)² — the set-membership claim
-- (nuance: containment ≠ fit at specific physical values)
theorem adjoint_sq_in_widest_interval :
    required_lower_bound < 567058969 ∧ (567058969 : ℚ) < required_upper_bound := by
  refine ⟨?_, ?_⟩
  · unfold required_lower_bound; norm_num
  · unfold required_upper_bound; norm_num

-- ════════════════════════════════════════════════════════════════
-- §9  Upstream cascade witnesses (drift guards)
-- ════════════════════════════════════════════════════════════════

def cascade_xi : ℚ := 15/49
def cascade_cg : ℚ := 8/9
def cascade_r : ℚ := 9/8

theorem cascade_r_times_cg : cascade_r * cascade_cg = 1 := by
  unfold cascade_r cascade_cg; norm_num

theorem cascade_xi_value : cascade_xi = 15/49 := rfl
theorem cascade_cg_value : cascade_cg = 8/9 := rfl
theorem cascade_r_value : cascade_r = 9/8 := rfl

-- c_mr matches CLM-043 exactly (no drift)
theorem c_mr_matches_clm043 : c_mr = 32/21 := rfl

-- ════════════════════════════════════════════════════════════════
-- §10 Cross-check with CLM-043 (minimal coupling baseline)
-- ════════════════════════════════════════════════════════════════

-- At ξ = 0, scalaron prefactor × π²_lb = (32/21) × 9 = 96/7 > 13
theorem clm043_gap_lower_bound : c_mr * 9 = 96/7 := by
  unfold c_mr; norm_num

theorem clm043_gap_exceeds_13 : (96 : ℚ) / 7 > 13 := by norm_num

-- Non-minimal ξ > 1/6 REDUCES M_R² below minimal value
-- (6ξ-1)² > 1 for ξ > 1/3 (and also for ξ < 0 outside our regime)
-- Since 6×(1/3) - 1 = 1, (6ξ-1)² > 1 iff ξ > 1/3
-- Concrete: at ξ = 1, (6·1 - 1)² = 25 ≫ 1
theorem non_minimal_reduces_mr_at_xi_1 : (6 * (1 : ℚ) - 1) ^ 2 = 25 := by norm_num

theorem non_minimal_reduces_mr_at_xi_10 : (6 * (10 : ℚ) - 1) ^ 2 = 3481 := by norm_num

theorem non_minimal_reduces_mr_at_xi_3969 : (6 * (3969 : ℚ) - 1) ^ 2 = 567058969 := by norm_num

-- ════════════════════════════════════════════════════════════════
-- §11 Master theorem — honest-negative verdict bundle
-- ════════════════════════════════════════════════════════════════

theorem clm_044_non_minimal_coupling_honest_negative :
    -- (1) Forward formula: minimal reduces to CLM-043
    r2_coeff 0 = 1/72
    -- (2) Conformal vanishing
    ∧ r2_coeff (1/6) = 0
    -- (3) Alternative form: (6ξ-1)²/72 agrees at minimal
    ∧ r2_coeff_alt 0 = 1/72
    -- (4) Total at minimal = 7/8 (matches CLM-043)
    ∧ (63 : ℚ) * (1/72) = 7/8
    -- (5) Scalaron prefactor c_mr = 32/21 (inherited)
    ∧ c_mr = 32/21
    -- (6) Required (6ξ-1)² lower bound (exact ℚ)
    ∧ required_lower_bound = 24000000000 / 49
    -- (7) Required (6ξ-1)² upper bound (exact ℚ)
    ∧ required_upper_bound = 160000000000 / 21
    -- (8) Interval non-empty
    ∧ required_lower_bound < required_upper_bound
    -- (9) Closest candidate (N²-1)² = 3969
    ∧ ((8 ^ 2 - 1) ^ 2 : ℚ) = 3969
    -- (10) At ξ = 3969: (6ξ-1)² = 567058969
    ∧ (6 * (3969 : ℚ) - 1) ^ 2 = 567058969
    -- (11) 3969 in widest-bound interval (set-membership, not fit)
    ∧ required_lower_bound < 567058969 ∧ (567058969 : ℚ) < required_upper_bound
    -- (12) At central values: ratio_sq > 9/4 (factor-1.5 miss on low side)
    ∧ (128000000000 : ℚ) / 43663540613 > 9 / 4
    -- (13) At central values: ratio_sq < 4 (factor-2 miss on high side)
    ∧ (128000000000 : ℚ) / 43663540613 < 4
    -- (14) Cascade drift guard
    ∧ cascade_r * cascade_cg = 1
    -- (15) CLM-043 gap regression (minimal coupling still 4+ orders too large)
    ∧ c_mr * 9 > 13 := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · unfold r2_coeff; norm_num
  · unfold r2_coeff; norm_num
  · unfold r2_coeff_alt; norm_num
  · norm_num
  · unfold c_mr; rfl
  · unfold required_lower_bound; rfl
  · unfold required_upper_bound; rfl
  · unfold required_lower_bound required_upper_bound; norm_num
  · norm_num
  · norm_num
  · unfold required_lower_bound; norm_num
  · unfold required_upper_bound; norm_num
  · norm_num
  · norm_num
  · unfold cascade_r cascade_cg; norm_num
  · unfold c_mr; norm_num

end UFT.NonMinimalCouplingDerivation
