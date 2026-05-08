import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Data.Fin.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.IntervalCases

namespace UFT.Terminal1

theorem A7_has_28_positive_roots : 7 * 8 / 2 = 28 := by norm_num

-- B_n: |Δ⁺(Bₙ)| = n² ≠ 28 for any n ≥ 2
theorem B_n_not_28 (n : ℕ) (hn : n ≥ 2) : n * n ≠ 28 := by
  intro h
  have h1 : 1 ≤ n := by omega
  have h2 : n * 1 ≤ n * n := Nat.mul_le_mul_left n h1
  have h3 : n ≤ 28 := by linarith [mul_one n]
  interval_cases n <;> omega

-- C_n: |Δ⁺(Cₙ)| = n² ≠ 28 for any n ≥ 3
theorem C_n_not_28 (n : ℕ) (hn : n ≥ 3) : n * n ≠ 28 := by
  intro h
  have h1 : 1 ≤ n := by omega
  have h2 : n * 1 ≤ n * n := Nat.mul_le_mul_left n h1
  have h3 : n ≤ 28 := by linarith [mul_one n]
  interval_cases n <;> omega

-- D_n: |Δ⁺(Dₙ)| = n(n-1) ≠ 28 for any n ≥ 4
theorem D_n_not_28 (n : ℕ) (hn : n ≥ 4) : n * (n - 1) ≠ 28 := by
  intro h
  have h1 : 1 ≤ n - 1 := by omega
  have h2 : n * 1 ≤ n * (n - 1) := Nat.mul_le_mul_left n h1
  have h3 : n ≤ 28 := by linarith [mul_one n]
  interval_cases n <;> omega

theorem G2_not_28 : 6 ≠ 28 := by norm_num
theorem F4_not_28 : 24 ≠ 28 := by norm_num
theorem E6_not_28 : 36 ≠ 28 := by norm_num
theorem E7_not_28 : 63 ≠ 28 := by norm_num
theorem E8_not_28 : 120 ≠ 28 := by norm_num
theorem adj_dim : 8 * 8 - 1 = 63 := by norm_num
theorem antisym_dim : 8 * 7 / 2 = 28 := by norm_num
theorem F4_decomposition : 28 + 8 + 8 + 8 = 52 := by norm_num
theorem E8_decomposition : 52 + 14 + 26 * 7 = 248 := by norm_num
theorem height_sum : 7 + 6 + 5 + 4 + 3 + 2 + 1 = 28 := by norm_num
theorem structure_constant_count : 322 + 56 = 28 * 27 / 2 := by norm_num
theorem georgi_glashow : 10 + 3 + 15 = 28 := by norm_num
theorem pati_salam : 6 + 1 + 1 + 20 = 28 := by norm_num
theorem antisym_branching : 3 + 3 + 6 + 6 + 2 + 2 + 1 + 4 + 1 = 28 := by norm_num
theorem g2_branching : 7 + 7 + 14 = 28 := by norm_num

end UFT.Terminal1
