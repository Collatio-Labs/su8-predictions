# SU(8) Predictions

Verification repository for the paper *SU(8) Gauge Unification via the A_7 Cascade: Spectral Generation Count, Fermion Masses, and Precision Predictions from a Single Input* by S. Lamar Michael, Collatio Labs LLC, 2026.

## What is here

- `paper1_su8_gut_submission.pdf`: the keystone paper, currently in peer review at Physical Review Letters (companion Letter) and Physical Review D (full Article)
- `lean/`: 107 Lean 4 proof files. 6,126 theorem-grade declarations. Zero `sorry` axioms.
- `scripts/`: 103 Python parity-guard scripts that mirror every Lean rational literal and check it against the engine's exact-rational output. Roughly 9,400 unit tests.
- `LICENSE`: MIT for code, CC-BY 4.0 for prose

## What the framework predicts

From a single irreducible input (M_Z), the framework derives 29+ quantitative Standard Model predictions with zero free parameters. The cascade theorem r = 9/8 is the structural anchor.

| Observable        | Predicted              | Measured (PDG 2024)   | Accuracy |
|-------------------|------------------------|-----------------------|----------|
| m_t (pole)        | 172.7 GeV              | 172.76 +/- 0.30 GeV   | 0.04%    |
| m_H               | 124.8 GeV              | 125.1 +/- 0.1 GeV     | 0.25%    |
| sin^2(theta_W)    | 0.2318                 | 0.23122               | 0.25%    |
| alpha_s(M_Z)      | 0.1185                 | 0.1180 +/- 0.0009     | 0.4%     |
| m_W               | 80.0 GeV               | 80.379 GeV            | 0.47%    |
| n_s               | 0.9595                 | 0.9649                | 0.56%    |
| Omega_DM/Omega_b  | 5.38                   | 5.36 +/- 0.05         | 0.4%     |

## The central theorem

The cascade ratio r = tau_mean(P_8) / tau_mean(P_7) = 9/8 is a mathematical theorem on the path graph P_8, which is the Dynkin diagram of A_7. Three convergent derivations:

1. CLM-032: Cartan mean-inverse-eigenvalue ratio
2. CLM-031: Cascade spectral graph theory
3. CLM-047: One-loop SU(8) heat-kernel trace ratio (Vassilevich-Barvinsky-Seeley-DeWitt)

All three machine-verified. CLM-001 promoted to `theorem` status on 2026-04-22.

## The experimental test

The cascade theorem admits a direct experimental test in an 8-level rubidium-87 Bose-Einstein condensate. The coherence propagation rate ratio between the full 8-component system and a 7-component system (one sublevel selectively depopulated) is predicted at:

```
r_BEC = v_8 / v_7 = 9/8 = 1.125 +/- 0.003
```

This discriminates SU(8) from competing GUT predictions at roughly 12 sigma. SU(5) predicts 1.200. SO(10) predicts 1.15. E_6 predicts 1.10. Apparatus cost is around $150 in consumables on standard cold-atom hardware. A measurement of r outside 1.125 +/- 0.003 falsifies the framework cleanly.

## Reproduction

To reproduce every numerical claim in the paper from scratch on a Mac with TeX Live and Lean 4 installed:

```bash
git clone https://github.com/Collatio-Labs/su8-predictions
cd su8-predictions/lean
lake build UFT
cd ../scripts
python3 -m unittest discover . -p "c*.py"
```

Expected output: `lake build UFT` returns 6,126 theorems verified, zero `sorry`. Python suite returns roughly 9,400 tests passing.

## Citation

The paper is currently in peer review. Citation will be updated here once published.

## Author

S. Lamar Michael  
Collatio Labs LLC  
Portland, Oregon  
ORCID: 0000-0001-5272-2780  
collatiolabs.com  
contact@collatiolabs.com

## License

Code (Lean proofs, Python parity-guard scripts): MIT.  
Prose (this README, the paper): CC-BY 4.0.

Both licenses permit redistribution and reuse with attribution.
