/-
# CLM-037 Phase 1: PS-Coset Anomaly Matching — Standard-Model side

Machine-verified proof that the four mixed 't Hooft anomaly polynomials of the
Standard Model (3 generations of 15 Weyl fermions with canonical hypercharges)
vanish as exact ℚ identities:

  1. `anom_SU3sq_U1Y`     = 0   ([SU(3)_C]² · U(1)_Y)
  2. `anom_SU2Lsq_U1Y`    = 0   ([SU(2)_L]² · U(1)_Y)
  3. `anom_U1Y_cubed`     = 0   ([U(1)_Y]³)
  4. `anom_gravsq_U1Y`    = 0   ([grav]² · U(1)_Y)

This file covers all three phases of CLM-037:
  Phase 1 (§1–§7): SM anomaly vanishing (15/45 Weyl)
  Phase 2 (§9):    PS → SM expansion (48 Weyl SM-tagged)
  Phase 3 (§10):   Full PS-coset composition (80 Weyl coset + composition)

## Scope (Commandment I — honest boundaries)

Phase 1 proves textbook SM anomaly vanishing as an exact ℚ identity with
zero floating-point contamination (Commandment XII).  The physics content
is classical (Peskin-Schroeder §20.2); Phase 1's contribution is the Lean
machine-verification and its parity with `c148_ps_coset_anomaly.py`.

Phase 1 does NOT:
  * establish anomaly matching across the PS → SM boundary;
  * establish anomaly matching across the Collatio → PS boundary;
  * reproduce or strengthen CLM-034's `clm_034_avenue_1_partial_positive`;
  * promote CLM-001 — label remains `structurally-forced` (set in C191).

Phase 1 DOES:
  * provide a machine-verified base that Phase 2/3 can cite with a theorem
    name rather than inlining the arithmetic;
  * tighten the evidence floor on the SM side of the PS-coset identity;
  * close every ℚ literal via Python parity guard (c148_ps_coset_anomaly).

## Python parity

Every ℚ and ℕ literal in this file is mirrored by `assertEqual` in
`proofs/UFT/scripts/c148_ps_coset_anomaly.py` per the discipline from
`feedback_lean_only_bugs.md` (C188): Python parity catches shared-literal
drift but CANNOT catch Lean-only arithmetic errors — those only surface
on Mac-side `lake build`.  Keep the two files in lockstep.
-/

import Mathlib.Data.Rat.Defs
import Mathlib.Data.Rat.Lemmas
import Mathlib.Data.List.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith

namespace UFT.PSCosetAnomalyMatching

/-! ## §1  SM fermion content (one generation, 15 Weyl)

Normalization: hypercharge `Y` satisfies `Q_EM = T_L^3 + Y` (Glashow-Salam-
Weinberg convention).  All fermions are written as left-handed Weyl spinors,
with conjugation taken where the physical particle is right-handed.

The five entries below MUST mirror `ONE_GENERATION` in
`proofs/UFT/scripts/c148_ps_coset_anomaly.py`.  Fields:
  * `d3` : dim of SU(3)_C rep (3 for fundamental, 1 for singlet)
  * `d2` : dim of SU(2)_L rep (2 for doublet, 1 for singlet)
  * `Y`  : hypercharge (exact ℚ)
  * `n`  : Weyl multiplicity = `d3 * d2`
-/

structure SMWeyl where
  d3 : ℕ
  d2 : ℕ
  Y  : ℚ
  n  : ℕ
  deriving Repr, DecidableEq

namespace SMWeyl

/-- Multiplicity invariant: `n = d3 * d2`.  Declared as a predicate so we
can assert it structurally for `one_generation`. -/
def mult_ok (f : SMWeyl) : Prop := f.n = f.d3 * f.d2

end SMWeyl

/-- The canonical one-generation SM content (no right-handed neutrino).
15 Weyl fermions total: 6 + 3 + 3 + 2 + 1 = 15. -/
def one_generation : List SMWeyl := [
  -- Q_L  = (u_L, d_L):   SU(3)=3, SU(2)=2, Y=+1/6,  6 Weyl
  ⟨3, 2,   1/6, 6⟩,
  -- u_Rᶜ :                SU(3)=3, SU(2)=1, Y=-2/3,  3 Weyl
  ⟨3, 1, -(2/3), 3⟩,
  -- d_Rᶜ :                SU(3)=3, SU(2)=1, Y=+1/3,  3 Weyl
  ⟨3, 1,   1/3, 3⟩,
  -- L_L  = (ν_L, e_L):   SU(3)=1, SU(2)=2, Y=-1/2,  2 Weyl
  ⟨1, 2, -(1/2), 2⟩,
  -- e_Rᶜ :                SU(3)=1, SU(2)=1, Y=+1,    1 Weyl
  ⟨1, 1,   1,   1⟩
]

/-- Three-generation SM content: `one_generation` concatenated three times
(45 Weyl fermions). -/
def three_generations (gen : List SMWeyl) : List SMWeyl :=
  gen ++ gen ++ gen

/-- The concrete 3-generation SM list, for convenience. -/
def sm_three_gen : List SMWeyl := three_generations one_generation

/-! ## §2  Anomaly polynomials (exact ℚ, zero float)

Each of the four mixed triangle anomalies is a rational sum over Weyl
fermions weighted by group-theory factors.  The Dynkin-index coefficient
`1/2` from `Tr(T^a T^b) = (1/2) δ^{ab}` is factored out — what remains is
the CHARGED part, whose vanishing IS anomaly freedom.

Per Commandment XIII: no step is "trivial" — every contribution is
written explicitly as a `ℚ`-valued helper and the vanishing theorems
name the arithmetic pattern that closes them.
-/

/-- `[SU(3)_C]² · U(1)_Y` anomaly coefficient.

For each SU(3) fundamental (d3 = 3), the SU(3) trace contributes 1 (i.e.
Dynkin index of the fundamental with the 1/2 factored out); SU(3) singlets
(d3 ≠ 3) contribute 0.  The SU(2)_L multiplet contributes its dimension
`d2` as the Weyl-count factor along the isospin direction.

Formula (per generation):
  Σ_{f : gen, d3(f) = 3}  (d2(f) : ℚ) · Y(f)
-/
def anom_SU3sq_U1Y (gen : List SMWeyl) : ℚ :=
  (gen.map (fun f => if f.d3 = 3 then (f.d2 : ℚ) * f.Y else 0)).foldr (· + ·) 0

/-- `[SU(2)_L]² · U(1)_Y` anomaly coefficient.

For each SU(2) doublet (d2 = 2), the SU(2) trace contributes 1; singlets
contribute 0.  The SU(3)_C multiplet contributes its dimension `d3` as
the Weyl-count factor along the color direction.

Formula (per generation):
  Σ_{f : gen, d2(f) = 2}  (d3(f) : ℚ) · Y(f)
-/
def anom_SU2Lsq_U1Y (gen : List SMWeyl) : ℚ :=
  (gen.map (fun f => if f.d2 = 2 then (f.d3 : ℚ) * f.Y else 0)).foldr (· + ·) 0

/-- `[U(1)_Y]³` anomaly coefficient: every Weyl fermion contributes
`n · Y³` where `n = d3 · d2` is the full Weyl multiplicity.

Formula (per generation):
  Σ_{f : gen}  (n(f) : ℚ) · Y(f)^3
-/
def anom_U1Y_cubed (gen : List SMWeyl) : ℚ :=
  (gen.map (fun f => (f.n : ℚ) * f.Y^3)).foldr (· + ·) 0

/-- `[grav]² · U(1)_Y` mixed gravitational-hypercharge anomaly: every
Weyl fermion contributes `n · Y`.  This is the sum of hypercharges
weighted by Weyl count — a pure linear Σ_i n_i Y_i.

Formula (per generation):
  Σ_{f : gen}  (n(f) : ℚ) · Y(f)
-/
def anom_gravsq_U1Y (gen : List SMWeyl) : ℚ :=
  (gen.map (fun f => (f.n : ℚ) * f.Y)).foldr (· + ·) 0

/-! ## §3  Vanishing theorems (one generation)

Every theorem below closes by unfolding the definitions into an explicit
sum of five `ℚ` literals and discharging the rational arithmetic with
`norm_num`.  No `sorry`, no new `axiom`.

The parallel Python assertions live in
`c148_ps_coset_anomaly.py::AnomalyPolynomial*Tests`.
-/

/-- [SU(3)_C]² · U(1)_Y vanishes on one generation:
      Q_L contributes 2·(1/6) = 1/3
    u_Rᶜ contributes 1·(-2/3) = -2/3
    d_Rᶜ contributes 1·(1/3)  = 1/3
    L_L, e_Rᶜ contribute 0 (SU(3) singlets)
    Sum: 1/3 + (-2/3) + 1/3 = 0. -/
theorem anom_SU3sq_U1Y_vanishes_one_gen :
    anom_SU3sq_U1Y one_generation = 0 := by
  unfold anom_SU3sq_U1Y one_generation
  simp only [List.map, List.foldr]
  norm_num

/-- [SU(2)_L]² · U(1)_Y vanishes on one generation:
      Q_L contributes 3·(1/6)  =  1/2
      L_L contributes 1·(-1/2) = -1/2
    u_Rᶜ, d_Rᶜ, e_Rᶜ contribute 0 (SU(2) singlets)
    Sum: 1/2 + (-1/2) = 0. -/
theorem anom_SU2Lsq_U1Y_vanishes_one_gen :
    anom_SU2Lsq_U1Y one_generation = 0 := by
  unfold anom_SU2Lsq_U1Y one_generation
  simp only [List.map, List.foldr]
  norm_num

/-- [U(1)_Y]³ vanishes on one generation.  Per-term breakdown (common
denominator 216):
      6·(1/6)³    =  6/216
      3·(-2/3)³   = -192/216
      3·(1/3)³    =  24/216
      2·(-1/2)³   = -54/216
      1·(1)³      =  216/216
    Sum: (6 − 192 + 24 − 54 + 216)/216 = 0/216 = 0. -/
theorem anom_U1Y_cubed_vanishes_one_gen :
    anom_U1Y_cubed one_generation = 0 := by
  unfold anom_U1Y_cubed one_generation
  simp only [List.map, List.foldr]
  norm_num

/-- [grav]² · U(1)_Y vanishes on one generation (integer sum):
      6·(1/6)   =  1
      3·(-2/3)  = -2
      3·(1/3)   =  1
      2·(-1/2)  = -1
      1·(1)     =  1
    Sum: 1 − 2 + 1 − 1 + 1 = 0. -/
theorem anom_gravsq_U1Y_vanishes_one_gen :
    anom_gravsq_U1Y one_generation = 0 := by
  unfold anom_gravsq_U1Y one_generation
  simp only [List.map, List.foldr]
  norm_num

/-! ## §4  Linearity over list concatenation

These lemmas are the scaffolding for lifting one-generation vanishing to
the three-generation case.  Each anomaly polynomial distributes over
`List.++` because it is a fold of `(+)` over a mapped list.
-/

/-- Distributivity of `anom_SU3sq_U1Y` over list concatenation. -/
theorem anom_SU3sq_U1Y_append (a b : List SMWeyl) :
    anom_SU3sq_U1Y (a ++ b)
      = anom_SU3sq_U1Y a + anom_SU3sq_U1Y b := by
  unfold anom_SU3sq_U1Y
  rw [List.map_append, List.foldr_append]
  induction a.map (fun f => if f.d3 = 3 then (f.d2 : ℚ) * f.Y else 0) with
  | nil => simp
  | cons h t ih => simp [List.foldr, ih]; ring

/-- Distributivity of `anom_SU2Lsq_U1Y` over list concatenation. -/
theorem anom_SU2Lsq_U1Y_append (a b : List SMWeyl) :
    anom_SU2Lsq_U1Y (a ++ b)
      = anom_SU2Lsq_U1Y a + anom_SU2Lsq_U1Y b := by
  unfold anom_SU2Lsq_U1Y
  rw [List.map_append, List.foldr_append]
  induction a.map (fun f => if f.d2 = 2 then (f.d3 : ℚ) * f.Y else 0) with
  | nil => simp
  | cons h t ih => simp [List.foldr, ih]; ring

/-- Distributivity of `anom_U1Y_cubed` over list concatenation. -/
theorem anom_U1Y_cubed_append (a b : List SMWeyl) :
    anom_U1Y_cubed (a ++ b)
      = anom_U1Y_cubed a + anom_U1Y_cubed b := by
  unfold anom_U1Y_cubed
  rw [List.map_append, List.foldr_append]
  induction a.map (fun f => (f.n : ℚ) * f.Y^3) with
  | nil => simp
  | cons h t ih => simp [List.foldr, ih]; ring

/-- Distributivity of `anom_gravsq_U1Y` over list concatenation. -/
theorem anom_gravsq_U1Y_append (a b : List SMWeyl) :
    anom_gravsq_U1Y (a ++ b)
      = anom_gravsq_U1Y a + anom_gravsq_U1Y b := by
  unfold anom_gravsq_U1Y
  rw [List.map_append, List.foldr_append]
  induction a.map (fun f => (f.n : ℚ) * f.Y) with
  | nil => simp
  | cons h t ih => simp [List.foldr, ih]; ring

/-! ## §5  Three-generation corollaries (via linearity)

Three-gen vanishing = 3 × one-gen vanishing = 3 · 0 = 0.  No new physics;
this is just linearity of the anomaly polynomials.
-/

theorem anom_SU3sq_U1Y_vanishes_three_gen :
    anom_SU3sq_U1Y sm_three_gen = 0 := by
  unfold sm_three_gen three_generations
  rw [anom_SU3sq_U1Y_append, anom_SU3sq_U1Y_append]
  rw [anom_SU3sq_U1Y_vanishes_one_gen]
  ring

theorem anom_SU2Lsq_U1Y_vanishes_three_gen :
    anom_SU2Lsq_U1Y sm_three_gen = 0 := by
  unfold sm_three_gen three_generations
  rw [anom_SU2Lsq_U1Y_append, anom_SU2Lsq_U1Y_append]
  rw [anom_SU2Lsq_U1Y_vanishes_one_gen]
  ring

theorem anom_U1Y_cubed_vanishes_three_gen :
    anom_U1Y_cubed sm_three_gen = 0 := by
  unfold sm_three_gen three_generations
  rw [anom_U1Y_cubed_append, anom_U1Y_cubed_append]
  rw [anom_U1Y_cubed_vanishes_one_gen]
  ring

theorem anom_gravsq_U1Y_vanishes_three_gen :
    anom_gravsq_U1Y sm_three_gen = 0 := by
  unfold sm_three_gen three_generations
  rw [anom_gravsq_U1Y_append, anom_gravsq_U1Y_append]
  rw [anom_gravsq_U1Y_vanishes_one_gen]
  ring

/-! ## §6  Weyl-count sanity theorems

The one-generation SM has exactly 15 Weyl fermions.  The three-generation
SM has exactly 45.  These closures are structural — they guarantee the
list we wrote matches the physical content we claim.
-/

/-- Total Weyl count over a generation (sum of `n` fields). -/
def total_weyl (gen : List SMWeyl) : ℕ :=
  (gen.map SMWeyl.n).foldr (· + ·) 0

theorem total_weyl_one_gen : total_weyl one_generation = 15 := by
  unfold total_weyl one_generation
  simp only [List.map, List.foldr]

theorem total_weyl_three_gen : total_weyl sm_three_gen = 45 := by
  unfold total_weyl sm_three_gen three_generations one_generation
  simp only [List.map_append, List.map, List.foldr_append, List.foldr]

/-! ## §7  Master bundle theorem

Conjoins the four one-generation and four three-generation vanishing
identities into a single statement that downstream claims can cite by
name without unfolding the internals.
-/

/-- CLM-037 Phase 1 master theorem: all four mixed SM anomaly polynomials
vanish on one generation AND on three generations, as exact ℚ identities.

Eight-clause conjunction:
  (1) [SU(3)_C]² · U(1)_Y  one-gen  = 0
  (2) [SU(2)_L]² · U(1)_Y  one-gen  = 0
  (3) [U(1)_Y]³            one-gen  = 0
  (4) [grav]²  · U(1)_Y    one-gen  = 0
  (5) [SU(3)_C]² · U(1)_Y  three-gen = 0
  (6) [SU(2)_L]² · U(1)_Y  three-gen = 0
  (7) [U(1)_Y]³            three-gen = 0
  (8) [grav]²  · U(1)_Y    three-gen = 0
-/
theorem clm_037_phase1_sm_anomalies_vanish :
    anom_SU3sq_U1Y  one_generation = 0 ∧
    anom_SU2Lsq_U1Y one_generation = 0 ∧
    anom_U1Y_cubed  one_generation = 0 ∧
    anom_gravsq_U1Y one_generation = 0 ∧
    anom_SU3sq_U1Y  sm_three_gen   = 0 ∧
    anom_SU2Lsq_U1Y sm_three_gen   = 0 ∧
    anom_U1Y_cubed  sm_three_gen   = 0 ∧
    anom_gravsq_U1Y sm_three_gen   = 0 :=
  ⟨anom_SU3sq_U1Y_vanishes_one_gen,
   anom_SU2Lsq_U1Y_vanishes_one_gen,
   anom_U1Y_cubed_vanishes_one_gen,
   anom_gravsq_U1Y_vanishes_one_gen,
   anom_SU3sq_U1Y_vanishes_three_gen,
   anom_SU2Lsq_U1Y_vanishes_three_gen,
   anom_U1Y_cubed_vanishes_three_gen,
   anom_gravsq_U1Y_vanishes_three_gen⟩

/-! ## §8  Hypercharge sanity (GSW identity mirrors)

Cross-check that the Y literals in `one_generation` reproduce canonical
SM electric charges via `Q = T_L^3 + Y`.  These are not part of the
anomaly proof — they just guarantee the Y values match the physics.
-/

/-- Up-quark charge: T_L^3(u_L) + Y(Q_L) = 1/2 + 1/6 = 2/3. -/
theorem gsw_up_quark_charge : (1/2 : ℚ) + 1/6 = 2/3 := by norm_num

/-- Down-quark charge: T_L^3(d_L) + Y(Q_L) = -1/2 + 1/6 = -1/3. -/
theorem gsw_down_quark_charge : -(1/2 : ℚ) + 1/6 = -(1/3) := by norm_num

/-- Neutrino charge: T_L^3(ν_L) + Y(L_L) = 1/2 + (-1/2) = 0. -/
theorem gsw_neutrino_charge : (1/2 : ℚ) + -(1/2) = 0 := by norm_num

/-- Electron charge: T_L^3(e_L) + Y(L_L) = -1/2 + (-1/2) = -1. -/
theorem gsw_electron_charge : -(1/2 : ℚ) + -(1/2) = -1 := by norm_num

/-- Up-antiquark charge (u_Rᶜ): 0 + (-2/3) = -2/3.  (Physical u_R has
charge +2/3; conjugating flips sign, so u_Rᶜ = -2/3 matches Y.) -/
theorem gsw_up_antiquark_charge : (0 : ℚ) + -(2/3) = -(2/3) := by norm_num

/-- Positron charge (e_Rᶜ): 0 + 1 = 1.  (Physical e_R has charge -1;
conjugating gives e_Rᶜ = +1 which matches Y.) -/
theorem gsw_positron_charge : (0 : ℚ) + 1 = 1 := by norm_num

/-! ## §9  Phase 2: PS → SM expansion under Y = T_R^3 + (B−L)/2

The 48 SM-tagged Weyl fermions from `CollatioPSBranching.lean`'s
`allPSReps` table are expanded to Standard Model irreps under the
Pati-Salam → SM embedding:

  SU(4)_C → SU(3)_C × U(1)_{B−L}:
    4  (a=1): (3, B−L=+1/3) ⊕ (1, B−L=−1)
    6  (a=2): (3, B−L=+2/3) ⊕ (3̄, B−L=−2/3)
    4̄  (a=3): (3̄, B−L=−1/3) ⊕ (1, B−L=+1)
    1  (a=0,4): (1, B−L=0)

  SU(2)_R → U(1)_{T_R^3}:
    2  (c=1): T_R^3 ∈ {+1/2, −1/2}
    1  (c=0,2): T_R^3 = 0

  Hypercharge: Y = T_R^3 + (B−L)/2

The critical insight resolving the §4 structural tension: the [3]
and [5] bidoublets have CONJUGATE SU(4)_C embeddings (Koszul a=1
vs a=3), giving conjugate B−L charges.  Their anomaly contributions
cancel pairwise.  Similarly [1] ↔ [7] form a conjugate pair.

Python parity: `c149_ps_to_sm_expansion.py` (93/93 PASS).
-/

/-- SM content of the SM-tagged PS irreps, expanded under
Y = T_R^3 + (B−L)/2.  18 entries, 48 total Weyl.

  [1] content (8 Weyl): (4,1,1) a=1 + (1,2,1) a=0 + (1,1,2) a=0
  [3] bidoublet (16 Weyl): (4,2,2) a=1 — fundamental SU(4)_C
  [5] bidoublet (16 Weyl): (4,2,2) a=3 — anti-fundamental SU(4)_C
  [7] content (8 Weyl): (4,1,1) a=3 + (1,2,1) a=0 + (1,1,2) a=0
-/
def ps_sm_expansion : List SMWeyl := [
  -- ═══ [1] SM content (8 Weyl) ═══
  -- (4,1,1) a=1: fund → (3, B-L=+1/3) ⊕ (1, B-L=-1), c=0 → T_R^3=0
  ⟨3, 1,   1/6,  3⟩,     -- Y = 0 + (1/3)/2 = 1/6
  ⟨1, 1, -(1/2), 1⟩,     -- Y = 0 + (-1)/2 = -1/2
  -- (1,2,1) a=0: singlet → (1, B-L=0), c=0 → T_R^3=0
  ⟨1, 2,   0,    2⟩,     -- Y = 0 + 0 = 0
  -- (1,1,2) a=0: singlet → (1, B-L=0), c=1 → T_R^3 ∈ {+1/2, -1/2}
  ⟨1, 1,   1/2,  1⟩,     -- Y = +1/2 + 0 = 1/2
  ⟨1, 1, -(1/2), 1⟩,     -- Y = -1/2 + 0 = -1/2

  -- ═══ [3] bidoublet SM content (16 Weyl, a=1 fundamental) ═══
  -- (4,2,2) a=1: fund → (3, B-L=+1/3) ⊕ (1, B-L=-1), c=1 → T_R^3 ∈ {+1/2, -1/2}
  ⟨3, 2,   2/3,  6⟩,     -- Y = +1/2 + (1/3)/2 = 1/2 + 1/6 = 2/3
  ⟨3, 2, -(1/3), 6⟩,     -- Y = -1/2 + (1/3)/2 = -1/2 + 1/6 = -1/3
  ⟨1, 2,   0,    2⟩,     -- Y = +1/2 + (-1)/2 = 1/2 - 1/2 = 0
  ⟨1, 2,  -1,    2⟩,     -- Y = -1/2 + (-1)/2 = -1/2 - 1/2 = -1

  -- ═══ [5] bidoublet SM content (16 Weyl, a=3 anti-fundamental) ═══
  -- (4,2,2) a=3: anti-fund → (3̄, B-L=-1/3) ⊕ (1, B-L=+1), c=1 → T_R^3 ∈ {+1/2, -1/2}
  ⟨3, 2,   1/3,  6⟩,     -- Y = +1/2 + (-1/3)/2 = 1/2 - 1/6 = 1/3
  ⟨3, 2, -(2/3), 6⟩,     -- Y = -1/2 + (-1/3)/2 = -1/2 - 1/6 = -2/3
  ⟨1, 2,   1,    2⟩,     -- Y = +1/2 + (1)/2 = 1/2 + 1/2 = 1
  ⟨1, 2,   0,    2⟩,     -- Y = -1/2 + (1)/2 = -1/2 + 1/2 = 0

  -- ═══ [7] SM content (8 Weyl, conjugate of [1]) ═══
  -- (4,1,1) a=3: anti-fund → (3̄, B-L=-1/3) ⊕ (1, B-L=+1), c=0 → T_R^3=0
  ⟨3, 1, -(1/6), 3⟩,     -- Y = 0 + (-1/3)/2 = -1/6
  ⟨1, 1,   1/2,  1⟩,     -- Y = 0 + (1)/2 = 1/2
  -- (1,2,1) a=0: same as [1]
  ⟨1, 2,   0,    2⟩,     -- Y = 0
  -- (1,1,2) a=0: same as [1]
  ⟨1, 1,   1/2,  1⟩,     -- Y = +1/2
  ⟨1, 1, -(1/2), 1⟩      -- Y = -1/2
]

/-! ### §9.1  Weyl count sanity -/

/-- The PS → SM expansion of SM-tagged content has 48 Weyl fermions. -/
theorem total_weyl_ps_sm : total_weyl ps_sm_expansion = 48 := by
  unfold total_weyl ps_sm_expansion
  simp only [List.map, List.foldr]

/-! ### §9.2  Phase 2 anomaly vanishing theorems

Each polynomial is evaluated on the 18-entry `ps_sm_expansion` list.
The tactic pattern is identical to §3 (unfold + simp + norm_num).
-/

/-- [SU(3)_C]² · U(1)_Y vanishes on the PS → SM expansion.
Per-block contributions:
  [1]: 1·(1/6) = 1/6
  [3] BD: 2·(2/3) + 2·(-1/3) = 2/3
  [5] BD: 2·(1/3) + 2·(-2/3) = -2/3
  [7]: 1·(-1/6) = -1/6
  Sum: 1/6 + 2/3 - 2/3 - 1/6 = 0 -/
theorem anom_SU3sq_U1Y_ps_sm_vanishes :
    anom_SU3sq_U1Y ps_sm_expansion = 0 := by
  unfold anom_SU3sq_U1Y ps_sm_expansion
  simp only [List.map, List.foldr]
  norm_num

/-- [SU(2)_L]² · U(1)_Y vanishes on the PS → SM expansion.
Each bidoublet individually vanishes:
  [3] BD: 3·(2/3) + 3·(-1/3) + 1·0 + 1·(-1) = 0
  [5] BD: 3·(1/3) + 3·(-2/3) + 1·1 + 1·0 = 0
[1] and [7] contribute only SU(2) singlets except (1,2,1) with Y=0. -/
theorem anom_SU2Lsq_U1Y_ps_sm_vanishes :
    anom_SU2Lsq_U1Y ps_sm_expansion = 0 := by
  unfold anom_SU2Lsq_U1Y ps_sm_expansion
  simp only [List.map, List.foldr]
  norm_num

/-- [U(1)_Y]³ vanishes on the PS → SM expansion.
Per-block contributions:
  [1]: 3·(1/6)³ + 1·(-1/2)³ + 0 + 1·(1/2)³ + 1·(-1/2)³ = -1/9
  [3] BD: 6·(2/3)³ + 6·(-1/3)³ + 0 + 2·(-1)³ = -4/9
  [5] BD: 6·(1/3)³ + 6·(-2/3)³ + 2·1³ + 0 = +4/9
  [7]: 3·(-1/6)³ + 1·(1/2)³ + 0 + 1·(1/2)³ + 1·(-1/2)³ = +1/9
  Sum: -1/9 - 4/9 + 4/9 + 1/9 = 0 -/
theorem anom_U1Y_cubed_ps_sm_vanishes :
    anom_U1Y_cubed ps_sm_expansion = 0 := by
  unfold anom_U1Y_cubed ps_sm_expansion
  simp only [List.map, List.foldr]
  norm_num

/-- [grav]² · U(1)_Y vanishes on the PS → SM expansion.
Each block independently vanishes:
  [1]: 3·(1/6) + 1·(-1/2) + 0 + 1·(1/2) + 1·(-1/2) = 0
  [3] BD: 6·(2/3) + 6·(-1/3) + 0 + 2·(-1) = 0
  [5] BD: 6·(1/3) + 6·(-2/3) + 2·1 + 0 = 0
  [7]: 3·(-1/6) + 1·(1/2) + 0 + 1·(1/2) + 1·(-1/2) = 0 -/
theorem anom_gravsq_U1Y_ps_sm_vanishes :
    anom_gravsq_U1Y ps_sm_expansion = 0 := by
  unfold anom_gravsq_U1Y ps_sm_expansion
  simp only [List.map, List.foldr]
  norm_num

/-! ### §9.3  Phase 2 master theorem -/

/-- CLM-037 Phase 2 master theorem: all four mixed SM anomaly polynomials
vanish on the PS → SM expansion of the SM-tagged Collatio content
(48 Weyl from `[1]⊕[3]⊕[5]⊕[7]` SM-tagged entries), as exact ℚ
identities under `Y = T_R^3 + (B−L)/2`.

Five-clause conjunction:
  (1) total Weyl = 48
  (2) [SU(3)_C]² · U(1)_Y = 0
  (3) [SU(2)_L]² · U(1)_Y = 0
  (4) [U(1)_Y]³            = 0
  (5) [grav]²  · U(1)_Y    = 0
-/
theorem clm_037_phase2_ps_sm_anomalies_vanish :
    total_weyl ps_sm_expansion = 48 ∧
    anom_SU3sq_U1Y  ps_sm_expansion = 0 ∧
    anom_SU2Lsq_U1Y ps_sm_expansion = 0 ∧
    anom_U1Y_cubed  ps_sm_expansion = 0 ∧
    anom_gravsq_U1Y ps_sm_expansion = 0 :=
  ⟨total_weyl_ps_sm,
   anom_SU3sq_U1Y_ps_sm_vanishes,
   anom_SU2Lsq_U1Y_ps_sm_vanishes,
   anom_U1Y_cubed_ps_sm_vanishes,
   anom_gravsq_U1Y_ps_sm_vanishes⟩

/-! ## §10  Phase 3: Full PS-coset anomaly composition

The 80-Weyl exotic/coset content — everything in `[1]⊕[3]⊕[5]⊕[7]`
NOT tagged as SM in `CollatioPSBranching.lean` — is expanded to SM
irreps under `Y = T_R^3 + (B−L)/2`.  All four anomaly polynomials
vanish independently on this coset content, and the full composition
identity

    A_Collatio(SM ++ coset) = A(SM) + A(coset) = 0 + 0 = 0

holds by linearity (via §4 append lemmas).

The coset vanishing is the non-trivial result: the [3] and [5] exotic
contributions cancel pairwise under Koszul-index conjugation
([k] ↔ [N−k] maps a=1 fundamental to a=3 anti-fundamental in SU(4)_C,
flipping B−L signs and hence Y signs).

Python parity: `c150_ps_coset_full_composition.py` (64/64 PASS).
-/

/-- Exotic/coset content of the Collatio PS decomposition, expanded
under Y = T_R^3 + (B−L)/2.  30 entries, 80 total Weyl.

  [3] exotic (40 Weyl, 7 PS reps → 15 SM components):
    (3,0,0)a=3, (2,1,0)a=2, (2,0,1)a=2, (1,2,0)a=1,
    (1,0,2)a=1, (0,2,1)a=0, (0,1,2)a=0

  [5] exotic (40 Weyl, 7 PS reps → 15 SM components):
    (1,2,2)a=1, (2,2,1)a=2, (2,1,2)a=2, (3,2,0)a=3,
    (3,0,2)a=3, (4,1,0)a=4, (4,0,1)a=4
-/
def ps_coset_expansion : List SMWeyl := [
  -- ═══ [3] exotic content (40 Weyl) ═══
  -- (3,0,0) a=3: anti-fund → (3̄, B-L=-1/3) ⊕ (1, B-L=+1), c=0
  ⟨3, 1, -(1/6), 3⟩,
  ⟨1, 1,   1/2,  1⟩,
  -- (2,1,0) a=2: antisym → (3, B-L=+2/3) ⊕ (3̄, B-L=-2/3), c=0
  ⟨3, 2,   1/3,  6⟩,
  ⟨3, 2, -(1/3), 6⟩,
  -- (2,0,1) a=2: antisym, c=1 → T_R^3 ∈ {+1/2, -1/2}
  ⟨3, 1,   5/6,  3⟩,
  ⟨3, 1, -(1/6), 3⟩,
  ⟨3, 1,   1/6,  3⟩,
  ⟨3, 1, -(5/6), 3⟩,
  -- (1,2,0) a=1: fund → (3, B-L=+1/3) ⊕ (1, B-L=-1), c=0
  ⟨3, 1,   1/6,  3⟩,
  ⟨1, 1, -(1/2), 1⟩,
  -- (1,0,2) a=1: fund, c=2 → T_R^3=0
  ⟨3, 1,   1/6,  3⟩,
  ⟨1, 1, -(1/2), 1⟩,
  -- (0,2,1) a=0: singlet → (1, B-L=0), c=1
  ⟨1, 1,   1/2,  1⟩,
  ⟨1, 1, -(1/2), 1⟩,
  -- (0,1,2) a=0: singlet, c=2 → T_R^3=0
  ⟨1, 2,   0,    2⟩,

  -- ═══ [5] exotic content (40 Weyl) ═══
  -- (1,2,2) a=1: fund, c=2 → T_R^3=0
  ⟨3, 1,   1/6,  3⟩,
  ⟨1, 1, -(1/2), 1⟩,
  -- (2,2,1) a=2: antisym, c=1 → T_R^3 ∈ {+1/2, -1/2}
  ⟨3, 1,   5/6,  3⟩,
  ⟨3, 1, -(1/6), 3⟩,
  ⟨3, 1,   1/6,  3⟩,
  ⟨3, 1, -(5/6), 3⟩,
  -- (2,1,2) a=2: antisym, c=2 → T_R^3=0
  ⟨3, 2,   1/3,  6⟩,
  ⟨3, 2, -(1/3), 6⟩,
  -- (3,2,0) a=3: anti-fund, c=0 → T_R^3=0
  ⟨3, 1, -(1/6), 3⟩,
  ⟨1, 1,   1/2,  1⟩,
  -- (3,0,2) a=3: anti-fund, c=2 → T_R^3=0
  ⟨3, 1, -(1/6), 3⟩,
  ⟨1, 1,   1/2,  1⟩,
  -- (4,1,0) a=4: det → (1, B-L=0), c=0
  ⟨1, 2,   0,    2⟩,
  -- (4,0,1) a=4: det, c=1 → T_R^3 ∈ {+1/2, -1/2}
  ⟨1, 1,   1/2,  1⟩,
  ⟨1, 1, -(1/2), 1⟩
]

/-! ### §10.1  Coset Weyl count -/

/-- The coset expansion has 80 Weyl fermions. -/
theorem total_weyl_ps_coset : total_weyl ps_coset_expansion = 80 := by
  unfold total_weyl ps_coset_expansion
  simp only [List.map, List.foldr]

/-! ### §10.2  Coset anomaly vanishing theorems

Each polynomial is evaluated on the 30-entry `ps_coset_expansion` list.
The tactic pattern is identical to §3 and §9 (unfold + simp + norm_num).
Per-block arithmetic:
  SU3sq:  [3] exotic = +1/6,  [5] exotic = −1/6,  sum = 0
  SU2Lsq: [3] exotic = 0,     [5] exotic = 0,      sum = 0
  U1Y3:   [3] exotic = −1/9,  [5] exotic = +1/9,  sum = 0
  gravsq:  [3] exotic = 0,     [5] exotic = 0,      sum = 0
-/

theorem anom_SU3sq_U1Y_ps_coset_vanishes :
    anom_SU3sq_U1Y ps_coset_expansion = 0 := by
  unfold anom_SU3sq_U1Y ps_coset_expansion
  simp only [List.map, List.foldr]
  norm_num

theorem anom_SU2Lsq_U1Y_ps_coset_vanishes :
    anom_SU2Lsq_U1Y ps_coset_expansion = 0 := by
  unfold anom_SU2Lsq_U1Y ps_coset_expansion
  simp only [List.map, List.foldr]
  norm_num

theorem anom_U1Y_cubed_ps_coset_vanishes :
    anom_U1Y_cubed ps_coset_expansion = 0 := by
  unfold anom_U1Y_cubed ps_coset_expansion
  simp only [List.map, List.foldr]
  norm_num

theorem anom_gravsq_U1Y_ps_coset_vanishes :
    anom_gravsq_U1Y ps_coset_expansion = 0 := by
  unfold anom_gravsq_U1Y ps_coset_expansion
  simp only [List.map, List.foldr]
  norm_num

/-! ### §10.3  Total-Weyl distributivity over list concatenation

Needed for the full-composition Weyl count `48 + 80 = 128`.
Same tactic pattern as §4 (map_append + foldr_append + induction),
but over ℕ instead of ℚ.
-/

theorem total_weyl_append (a b : List SMWeyl) :
    total_weyl (a ++ b) = total_weyl a + total_weyl b := by
  unfold total_weyl
  rw [List.map_append, List.foldr_append]
  induction a.map SMWeyl.n with
  | nil => simp
  | cons h t ih => simp [List.foldr, ih]; ring

/-! ### §10.4  Full composition corollaries

The full 128-Weyl Collatio content = SM (48) ++ coset (80).
Each anomaly polynomial on the full content decomposes via §4 append
lemmas into two pieces, both of which vanish (§9 + §10.2).
-/

/-- Full Collatio content has 128 Weyl fermions: 48 SM + 80 coset. -/
theorem total_weyl_full :
    total_weyl (ps_sm_expansion ++ ps_coset_expansion) = 128 := by
  rw [total_weyl_append, total_weyl_ps_sm, total_weyl_ps_coset]

theorem anom_SU3sq_U1Y_full_vanishes :
    anom_SU3sq_U1Y (ps_sm_expansion ++ ps_coset_expansion) = 0 := by
  rw [anom_SU3sq_U1Y_append, anom_SU3sq_U1Y_ps_sm_vanishes,
      anom_SU3sq_U1Y_ps_coset_vanishes]
  ring

theorem anom_SU2Lsq_U1Y_full_vanishes :
    anom_SU2Lsq_U1Y (ps_sm_expansion ++ ps_coset_expansion) = 0 := by
  rw [anom_SU2Lsq_U1Y_append, anom_SU2Lsq_U1Y_ps_sm_vanishes,
      anom_SU2Lsq_U1Y_ps_coset_vanishes]
  ring

theorem anom_U1Y_cubed_full_vanishes :
    anom_U1Y_cubed (ps_sm_expansion ++ ps_coset_expansion) = 0 := by
  rw [anom_U1Y_cubed_append, anom_U1Y_cubed_ps_sm_vanishes,
      anom_U1Y_cubed_ps_coset_vanishes]
  ring

theorem anom_gravsq_U1Y_full_vanishes :
    anom_gravsq_U1Y (ps_sm_expansion ++ ps_coset_expansion) = 0 := by
  rw [anom_gravsq_U1Y_append, anom_gravsq_U1Y_ps_sm_vanishes,
      anom_gravsq_U1Y_ps_coset_vanishes]
  ring

/-! ### §10.5  Phase 3 master theorem -/

/-- CLM-037 Phase 3 master theorem: the full PS-coset anomaly composition.

Nine-clause conjunction:
  (1) coset Weyl = 80
  (2) [SU(3)_C]² · U(1)_Y on coset = 0
  (3) [SU(2)_L]² · U(1)_Y on coset = 0
  (4) [U(1)_Y]³ on coset = 0
  (5) [grav]² · U(1)_Y on coset = 0
  (6) [SU(3)_C]² · U(1)_Y on full = 0  (composition)
  (7) [SU(2)_L]² · U(1)_Y on full = 0  (composition)
  (8) [U(1)_Y]³ on full = 0             (composition)
  (9) [grav]² · U(1)_Y on full = 0      (composition)

Together with Phase 1 (SM: 15/45 Weyl) and Phase 2 (PS→SM: 48 Weyl),
this completes the anomaly matching: all four mixed 't Hooft anomaly
polynomials vanish on the SM content, the exotic/coset content, and the
full Collatio content independently — as exact ℚ identities, with zero
floating-point contamination.
-/
theorem clm_037_phase3_full_composition :
    total_weyl ps_coset_expansion = 80 ∧
    anom_SU3sq_U1Y  ps_coset_expansion = 0 ∧
    anom_SU2Lsq_U1Y ps_coset_expansion = 0 ∧
    anom_U1Y_cubed  ps_coset_expansion = 0 ∧
    anom_gravsq_U1Y ps_coset_expansion = 0 ∧
    anom_SU3sq_U1Y  (ps_sm_expansion ++ ps_coset_expansion) = 0 ∧
    anom_SU2Lsq_U1Y (ps_sm_expansion ++ ps_coset_expansion) = 0 ∧
    anom_U1Y_cubed  (ps_sm_expansion ++ ps_coset_expansion) = 0 ∧
    anom_gravsq_U1Y (ps_sm_expansion ++ ps_coset_expansion) = 0 :=
  ⟨total_weyl_ps_coset,
   anom_SU3sq_U1Y_ps_coset_vanishes,
   anom_SU2Lsq_U1Y_ps_coset_vanishes,
   anom_U1Y_cubed_ps_coset_vanishes,
   anom_gravsq_U1Y_ps_coset_vanishes,
   anom_SU3sq_U1Y_full_vanishes,
   anom_SU2Lsq_U1Y_full_vanishes,
   anom_U1Y_cubed_full_vanishes,
   anom_gravsq_U1Y_full_vanishes⟩

end UFT.PSCosetAnomalyMatching
