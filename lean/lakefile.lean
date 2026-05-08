import Lake
open Lake DSL

-- Standalone lakefile for github.com/Collatio-Labs/su8-predictions
-- Mirrors the UFT library subset of the Collatio monorepo with the
-- Lean source files placed flat under this directory (srcDir := ".").
--
-- Reproduce:
--   cd lean
--   lake build UFT
-- Expected: 6,126 theorems verified, zero `sorry`.

package su8_predictions where
  leanOptions := #[
    ⟨`autoImplicit, false⟩
  ]

@[default_target]
lean_lib UFT where
  srcDir := "."
  roots := #[`SU8BreakingChain, `Triality, `FisherGravity, `IntermediateBreaking,
             `BranchingRules, `AnomalyCancellation, `SeesawFormula, `CKMUnitarity,
             `ComputationBridges, `CasimirInvariants, `ThresholdMatching,
             `TrialityUniqueness, `RootCountUniqueness, `AnomalyCancellationStructural,
             `ChargeQuantization, `BetaCoefficients, `DynkinIndex,
             `BranchingRulesStructural, `BranchingDimensions, `GoldstoneCounting,
             `SU8Uniqueness, `SpeciesBound, `QuadraticUniqueness,
             `OracleLiveness, `PMNSDerivation, `CKMDerivation,
             -- C162: cascade-forward live Oracle theorems (zero error budget)
             `TopMass3LoopCascade, `HiggsTreePoleCascade,
             -- C139: forward A_s honest derivation (Commandment XII clean)
             `ScalarAmplitudeForward,
             -- C179: Starobinsky A_s exact structural backbone (CLM-024 candidate (f))
             `StarobinskyAmplitude,
             -- C137: cosmology essence (N_e, n_s, r, Ω_b h²; A_s non-derivation)
             `CosmologyEssence,
             -- C169: Physics Oracle (Commandment XI — proven-or-silent query interface)
             `PhysicsOracle,
             -- C169: Oracle exact-only purge — exact-rational structural backbones
             `BaryogenesisDerivation, `InflationSector, `PhaseTransitionParameters,
             `RunningCouplings, `StrongCPDerivation,
             -- CLM-030 (2026-04-17): charged-lepton Yukawa falsifier ledger
             -- (honest closure; no positive derivation — leptons stay INPUT)
             `LeptonYukawaDerivation,
             -- CLM-031 (2026-04-17): spectral ↔ RGE Rosetta stone —
             -- one exact-ℚ theorem per cascade scale node, plus the
             -- master chain identity r·CG·γ·18 = 7.  Closes the
             -- long-standing Commandment-IV gap where CLAUDE.md has
             -- asserted "PROVEN, not approximate" without a Lean witness.
             `SpectralRGECorrespondence,
             -- CLM-032 (2026-04-17): rep-theoretic form of CG = 8/9 via
             -- Cartan-matrix mean-inverse-eigenvalue ratio ⟨λ⁻¹⟩(A_{n-1})
             -- / ⟨λ⁻¹⟩(A_n) = (n+1)/(n+2), n=7 → 8/9.  Does NOT promote
             -- CLM-001 (physics identification still postulate per
             -- c99_cg_derivation.py's 9-avenue exhaustion).
             `CascadeCGRepTheory,
             -- CLM-033 (2026-04-17): Δ_R = (10,1,3) vacuum locked at
             -- M_PS via 1-loop CW with (4,1,2) Yukawa tadpole.
             -- Closes CLM-024 Task B **structurally** (the factor-3
             -- Starobinsky A_s agreement with M_R = M_PS is now pinned
             -- to a cascade-locked scale identification, not a
             -- coincidence).  Master theorem
             -- `delta_R_vacuum_at_M_PS` bundles:  dim(10,1,3) = 30,
             -- Goldstone budget = 11, physical scalars = 19,
             -- leading-order v_R²/M_PS² = 1.
             `DeltaRVacuumDerivation,
             -- CLM-034 (2026-04-17): Avenue 1 of Route A — 't Hooft
             -- anomaly matching.  Establishes that combining
             -- Banks-Georgi anomaly freedom + SM Weyl count ≥ 48 +
             -- PS fundamental embedding uniquely selects N = 8 among
             -- enumerated candidates {6,7,8,9,10} and that the cascade
             -- CG at N = 8 evaluates to 8/9 as a pure rational.
             -- Master theorem `clm_034_avenue_1_partial_positive`
             -- bundles anomaly sum = 0, Weyl total = 128, filter
             -- uniqueness, cascade_cg 8 = 8/9, and N=8 vs N=7
             -- distinctness.  Evidence-floor tightening only; CLM-001
             -- label remains `structurally-forced`.
             `AnomalyMatchingDerivation,
             -- CLM-034 GAP #3 (2026-04-18): Explicit Koszul/Vandermonde
             -- decomposition of [1]⊕[3]⊕[5]⊕[7] of SU(8) into Pati-Salam
             -- irreps, with declared SM tagging per c121.  Master theorem
             -- `collatio_128_to_48_SM_plus_80_exotic` bundles:
             -- total dim = 128, SM subtotal = 48, exotic subtotal = 80,
             -- and complementarity.  Replaces the C192 citation-only
             -- arithmetic `collatio_weyl_decomposition : 48 + 80 = 128`
             -- with structural per-[k] derivation.
             `CollatioPSBranching,
             -- CLM-037 Phase 1 (2026-04-19): PS-coset anomaly polynomial
             -- as exact-ℚ identity — Standard-Model side.  Establishes the
             -- four mixed SM 't Hooft anomaly polynomials
             -- ([SU(3)_C]²U(1)_Y, [SU(2)_L]²U(1)_Y, [U(1)_Y]³,
             -- [grav]²U(1)_Y) vanish as exact ℚ identities over one
             -- generation (15 Weyl fermions with canonical hypercharges
             -- Y = Q_EM − T_L^3) and extend via linearity to 3 generations
             -- (45 Weyl).  Master theorem
             -- `clm_037_phase1_sm_anomalies_vanish` bundles all 8 facts
             -- (4 polynomials × 2 generation counts).  Does NOT establish
             -- matching across PS → SM or Collatio → PS (Phase 2/3
             -- deferred).  Does NOT move CLM-001 label
             -- (remains `structurally-forced`).  Closes the SM-facing
             -- foundation that Phase 2 + Phase 3 of Route A Avenue 1
             -- sharpening will cite.  Python parity: c148_ps_coset_anomaly
             -- at 66/66 sandbox-side.
             `PSCosetAnomalyMatching,
             -- CLM-038 (2026-04-20): Avenue 3 of Route A — holographic
             -- duality.  AdS/CFT central charge c(N) = N²−1, a-theorem
             -- monotonicity Δa > 0, large-N 't Hooft coupling from
             -- cascade-locked α_GUT = 10/457, PS-fundamental filter.
             -- Under the joint holographic + PS filter, N = 8 uniquely
             -- selected among {6,7,8,9,10}.  Master theorem
             -- `clm_038_holographic_partial_positive` bundles:
             -- c(8) = 63, R_c(8) = 21/16, Δa(8) > 0, λ(8)/π = 320/457,
             -- admits_ps 8, ¬admits_ps {6,7,9,10}, cascade_cg 8 = 8/9.
             -- CLM-001 label REMAINS `structurally-forced`.
             `HolographicDuality,
             -- CLM-041 (2026-04-20): Avenue 6 of Route A — BRST
             -- cohomology / Seiberg duality.  Three exact-ℚ/ℤ filter
             -- conditions (asymptotic freedom β₀ > 0, non-degenerate
             -- conjugate pairing n_proper_pairs = 2, combined) jointly
             -- select N = 8 uniquely among {6,7,8,9,10}.  Master theorem
             -- `clm_041_avenue_6_partial_positive` bundles: admits_N8,
             -- ¬admits {6,7,9,10}, uniqueness, cascade_cg 8 = 8/9.
             -- Sixth and final Route A avenue.
             -- CLM-001 label REMAINS `structurally-forced`.
             `BRSTSeibergDuality,
             -- CLM-035 (2026-04-20): Avenue 2 of Route A — conformal
             -- bootstrap.  Banks-Zaks confinement constraint excludes
             -- N = 9 (β₁ < 0 → BZ IR fixed point → conformal, no
             -- confinement) and N = 10 (AF fails, β₀ < 0).  Under
             -- joint conformal filter (AF + confining), viable set
             -- narrows from {6,7,8,9,10} to {6,7,8}.  Master theorem
             -- `clm_035_conformal_partial_positive` bundles: viable
             -- {6,7,8}, ¬viable {9,10}, cascade_cg 8 = 8/9.
             -- CLM-001 label REMAINS `structurally-forced`.
             `ConformalBootstrap,
             -- CLM-042 (2026-04-20): Route B partial reconnaissance —
             -- cascade kinetic operator.  SU(8) classical kinetic
             -- operator restricted to cascade flat direction produces
             -- M² ∝ Cartan(A₇); uniform prefactor cancels in CG ratio,
             -- yielding CG = ⟨C⁻¹⟩(A₆)/⟨C⁻¹⟩(A₇) = 8/9.  Master
             -- theorem `clm_042_route_b_master` bundles: VEV traceless,
             -- r = -1 stability, det = 8, CG = 8/9, CLM-032 agreement,
             -- Rosetta chain.  Gaps B.1/B.2/B.3 remain open (§6).
             -- CLM-001 label UNCHANGED.
             `CascadeKineticOperator,
             -- CLM-043 (2026-04-20): 1-loop R² coefficient from SU(8)
             -- gauge + matter content.  Seeley-DeWitt a₂ heat kernel:
             -- γ₀ = 1/72 per minimally coupled scalar, fermion/gauge = 0
             -- (conformal invariance).  N₀ = 63 adjoint → σ₀×16π² = 7/8,
             -- scalaron mass prefactor c_MR = 32/21.  Gap ≥ 4 orders:
             -- 1-loop insufficient for Starobinsky.  2-loop / non-minimal
             -- ξ paper-gated (BS-2008, Commandment VIII).
             `OneLoopR2FromSU8,
             -- CLM-044 (2026-04-20): Non-minimal coupling ξ R φ² →
             -- induced Starobinsky R² scalaron mass (Route B second
             -- attempt).  Forward formula (6ξ−1)² = (32/21)π²/L × (M_Pl/M_PS)²
             -- for M_R = M_PS gives required ξ ∈ [3689, 14548]; central
             -- ξ ≈ 6462.  Enumeration of 10 natural SU(8) cascade group
             -- invariants {8, 36, 56, 63, 64, 504, 512, 2016, 3969, 32256}
             -- — closest is (N²−1)² = 3969 at factor-1.71 miss (M_R/M_PS
             -- at central values), within widest-bound interval but no
             -- structural derivation without BS-2008 paper access
             -- (Commandment VIII).  HONEST-NEGATIVE: cascade-locked ξ
             -- does NOT structurally produce M_R = M_PS at 1-loop.
             -- Master theorem `clm_044_non_minimal_coupling_honest_negative`
             -- bundles 16 facts.  Combined with CLM-043, both paper-free
             -- 1-loop Route B bridging attempts are ruled out structurally;
             -- only 2-loop Barvinsky-Vilkovisky remains (also paper-blocked).
             -- CLM-001 label UNCHANGED at `structurally-forced`.
             `NonMinimalCouplingDerivation,
             -- CLM-039 (2026-04-20): Avenue 4 of Route A — lattice SU(8)
             -- strong coupling.  Content non-triviality (dim([k]) ≥ 2
             -- for all k ∈ {1,3,5,7}) + AF → survivors {8,9}.  N=6
             -- excluded (dim([7])=0), N=7 excluded (dim([7])=1 singlet),
             -- N=10 excluded (AF fails).  PARTIAL-POSITIVE.
             -- CLM-001 label REMAINS `structurally-forced`.
             `LatticeSU8StrongCoupling,
             -- CLM-040 (2026-04-20): Avenue 5 of Route A — asymptotic
             -- safety uniqueness.  Spectral half-count n_gen=3 + content
             -- non-triviality → {8}.  N=6 excluded (n_gen=2 AND
             -- dim([7])=0), N=7 excluded (dim([7])=1), N=9 excluded
             -- (n_gen=4), N=10 excluded (n_gen=4).  UNIQUELY-POSITIVE.
             -- CLM-001 label REMAINS `structurally-forced`.
             `AsymptoticSafetyUniqueness,
             -- CLM-046 (2026-04-20): Cascade moduli metric = 16 · A₇ Cartan.
             -- The Killing form K(X,Y) = 2N·Tr(XY) on SU(8) simple coroots
             -- H_i = E_{i,i} − E_{i+1,i+1} (i=0..6) evaluates entry-for-entry
             -- to 16 · (Cartan A₇)_{ij}: diagonal → 32 = 16·2, adjacent →
             -- −16 = 16·(−1), far → 0.  Master theorem
             -- `clm_046_moduli_metric_equals_cartan` bundles three facts:
             -- (i) ∀ i,j < 7, killing_su8 (trace_prod i j) = 16 · cartan_A7_entry,
             -- (ii) cartan_mean_inv 6 / cartan_mean_inv 7 = 8/9 (CLM-032 bridge),
             -- (iii) cg_rat 7 = 8/9.  Paper-free, loop-free, observation-free —
             -- tightens the CLM-031 Rosetta-stone postulate (that spectral
             -- ratios on A₇ correspond to RGE cascade ratios) by proving
             -- the moduli-space metric on SU(8)'s Cartan subalgebra IS
             -- A₇'s Cartan matrix up to a uniform prefactor that cancels
             -- in the spectral ratio.  Closes the "why does A₇ appear?"
             -- structural question at the algebra level.  CLM-001 label
             -- UNCHANGED at `theorem-joint` (per C204) — this is algebra-
             -- side postulate tightening, not a new Route A avenue.
             `CascadeModuliMetric,
             -- CLM-047 (2026-04-21): One-loop SU(8) path-integral
             -- derivation of CG = 8/9 via Seeley-DeWitt a_4 heat-kernel
             -- coefficients on the cascade flat direction.  Route B
             -- closure for CLM-001 upgrade theorem-joint → theorem.
             -- Imports CascadeCGRepTheory (CLM-032) and CascadeModuliMetric
             -- (CLM-046).  Paper-backed by Vassilevich 2003, BS-2008,
             -- Barvinsky 2015 (all three in hand as of 2026-04-21).
             -- Python parity guard: c177 (124/124).
             `OneLoopCascadeSU8HeatKernel,
             -- CLM-047 Phase 2 (2026-04-21): Route B derivation of
             -- CG = 8/9 from heat-kernel trace ratio on cascade flat
             -- direction.  τ̄(A₆)/τ̄(A₇) = (4/3)/(3/2) = 8/9.
             -- Imports CascadeCGRepTheory (CLM-032) and
             -- OneLoopCascadeSU8HeatKernel (Phase 1).  Three-way
             -- convergence: Route A + cascade spectral + Route B all
             -- give 8/9.  Master theorem bundles 8 facts.
             -- Python parity guard: c178 (80/80).
             `HeatKernelCGDerivation,
             -- CLM-001 brute-force CG exhaustion (2026-04-20):
             -- Brute-force computational exhaustion of all 49 = 7 × 7
             -- tensor products [a] ⊗ [b] (a, b ∈ {1,…,7}) of SU(8)
             -- antisymmetric representations.  Confirms CG = 8/9 is
             -- UNIVERSAL across every decomposition channel — the Cartan-
             -- matrix ratio is an algebra-level invariant, not rep-dependent.
             -- Python parity guard: c173_cg_brute_force_enumeration (71/71).
             -- CLM-001 label UNCHANGED at `theorem-joint`.
             `CGBruteForceExhaustion,
             -- C213 100% certainty push (2026-04-21):
             -- GAP B: CC Fisher-holographic formalization with explicit
             -- FisherHolographicBridge axiom (the ONE physics postulate),
             -- self-consistent flatness algebra (Ω_m = 189/253),
             -- lambda ratio bounds (640000/1732291 ∈ (1/3, 1/2)),
             -- and master chain theorem.  Python parity: c182.
             `CosmologicalConstant,
             -- GAP C: Perturbative truncation bounds — exact upper bounds
             -- on higher-loop corrections for m_t, sin²θ_W, α_s, m_H.
             -- Geometric series convergence at α_s/π < 1/25.
             -- Master bound: all truncation errors < 0.3%.
             -- Python parity: c181.
             `PerturbativeBounds,
             -- GAP D: Baryogenesis structural claims — sphaleron 28/79
             -- (Harvey-Turner 1990), Davidson-Ibarra 3/16, CP phase count 5,
             -- Sakharov conditions 3, g* = 427/4.  The ONLY non-exact step
             -- is Boltzmann ODE integration (Bessel functions).
             -- Python parity: c183.
             `BaryogenesisStructural]


require mathlib from git
  "https://github.com/leanprover-community/mathlib4"
