# Results Summary

Working notes for the Results and Discussion sections. All numbers come from
`code/results/processed/` and `code/results/raw/`.

Updated 2026-10-31. All Szegedy/AGJK experiments use the lazy walk
$P_\eta=(1-\eta)P+\eta I$ with $\eta=0.1$ (adversarial torus: $\eta=0.2$).
Two earlier claims are retracted: the E5 "12x deadline gain at $p=0.2$, $T=20$"
and the E4 non-monotone choice probabilities. Both were artifacts of oscillation
phase. See the E4 and E5 sections below.

## E1: Classical versus quantum scaling

| Family | Classical exponent $\HT\sim N^\alpha$ | Quantum exponent $T_q\sim N^\beta$ | $T_q\sim \HT^\gamma$ | Max speedup |
|---|---:|---:|---:|---:|
| Complete $K_N$ | 1.06 | 0.53 | 0.50 | 4.7 |
| Cycle $C_N$ | 1.95 | 1.02 | 0.52 | 11.7 |
| 2D grid $L\times L$ | 1.26 | 0.61 | 0.48 | 7.9 |
| Hypercube $Q_d$ | 1.07 | 0.47 | 0.44 | 5.4 |

Success probability at the optimal time is $0.84$--$1.00$ across all instances.
The fitted $T_q$--$\HT$ exponents $\gamma$ are $0.50$, $0.52$, $0.48$, $0.44$
for complete, cycle, grid, and hypercube, respectively.

## E2: Single versus multiple marked vertices

Means over seeds from `code/results/raw/E2_marked.csv` (single: seed 0 only).

| Graph | Marked set | Mean $\HT$ | Mean $\HT^+$ | $\HT^+/\HT$ | Mean $T_q$ | Mean $p_{\max}$ |
|---|---|---:|---:|---:|---:|---:|
| Grid $6\times6$ | single | 46.1 | 46.1 | 1.00 | 12.0 | 0.904 |
| Grid $6\times6$ | independent | 14.4 | 14.6 | 1.01 | 6.7 | 0.938 |
| Grid $6\times6$ | clustered | 50.0 | 54.7 | 1.09 | 14.7 | 0.907 |
| Grid $8\times8$ | single | 95.5 | 95.5 | 1.00 | 17.0 | 0.914 |
| Grid $8\times8$ | independent | 34.7 | 35.3 | 1.02 | 10.7 | 0.886 |
| Grid $8\times8$ | clustered | 79.5 | 85.3 | 1.07 | 20.3 | 0.845 |
| Barbell $n=8$ | single | 373.6 | 373.6 | 1.00 | 51.0 | 0.959 |
| Barbell $n=8$ | independent | 7.6 | 10.5 | 1.38 | 5.0 | 0.966 |
| Barbell $n=8$ | clustered | 349.8 | 358.8 | 1.03 | 41.3 | 0.972 |
| Barbell $n=16$ | single | 2558.0 | 2557.9 | 1.00 | 134.0 | 0.958 |
| Barbell $n=16$ | independent | 16.8 | 25.4 | 1.52 | 7.0 | 0.968 |
| Barbell $n=16$ | clustered | 2478.6 | 2507.4 | 1.01 | 115.3 | 0.970 |

Adversarial torus (AGJK marked-set pattern):

| $L$ | $N$ | $m$ | $p_M$ | $\HT$ | $\HT^+$ | $\HT^+/\HT$ |
|---:|---:|---:|---:|---:|---:|---:|
| 18 | 324 | 76 | 0.235 | 10.3 | 57.1 | 5.5 |
| 24 | 576 | 108 | 0.188 | 20.5 | 150.9 | 7.4 |
| 30 | 900 | 148 | 0.164 | 34.9 | 295.9 | 8.5 |
| 36 | 1296 | 252 | 0.194 | 50.5 | 443.1 | 8.8 |

For $L=18$, the interpolated walk still reaches $p_{\max}=0.978$ at $t=6$.

## E3: Toy semantic graph

Spectral gap $\lambda_1=0.03335$, relaxation time $1/\lambda_1=30.0$.

| Cue $\to$ target | Model | $p_{\text{peak}}$ | $\tau_{\text{peak}}$ | AUC | Entropy | Expected radius |
|---|---|---:|---:|---:|---:|---:|
| animal $\to$ dog (distance 1) | CTQW | 0.237 | 4.75 | 0.481 | 3.41 | 1.80 |
| animal $\to$ dog (distance 1) | CRW | 0.158 | 0.13 | 0.580 | 3.24 | 0.97 |
| animal $\to$ violin (distance 4) | CTQW | 0.247 | 6.86 | 0.360 | 3.28 | 2.99 |
| animal $\to$ violin (distance 4) | CRW | 0.046 | 8.00 | 0.324 | 4.18 | 2.36 |

## E4: Multi-alternative decision (retracted non-monotonicity)

Readout is decisive here. Under the detection readout ($p=0.2$), option coupling
monotonically shifts choice probability toward the uncoupled option. The earlier
"first-crossing readout, $0.333\to0.966$, non-monotone asymmetric case" is retracted.

Spread (variation under $\eta$ and $\pm20\%$ edge-weight perturbation):

| Readout | Spread median | Spread max |
|---|---:|---:|
| Random stopping | 0.08 | 0.26 |
| Detection, $p=0.2$ | to confirm | 0.045 |
| Classical absorption | to confirm | 0.065 |
| Old first-crossing readout (retracted) | 0.44 | 0.78 |

Uncoupled-option choice probability (detection readout):

| Case | Before coupling | After coupling |
|---|---:|---:|
| Symmetric three-option | 1/3 | 0.499 |
| Four-option (uncoupled total) | 0.500 | 0.653 |
| Asymmetric three-option | 0.342 | 0.470 |
| Symmetric three-option, classical | 1/3 | 1/3 (unchanged) |

Decision time: 31--44 steps (detection), 17--27 steps (classical).

## E5: Decoherence sweep (retracted deadline gain)

The earlier "deadline $T=20$, $p\approx0.2$ optimal, 12x" result is retracted.
It came from an oscillation-phase artifact. After the lazy walk the gain is about
1.6x, and it disappears after averaging over the deadline.

Readout model ($\eta=0.1$, `max_steps` $=120$). Pure quantum ($p=0$) has the best
time-averaged success in 3 of 4 cases. Measurement mainly smooths the curve:

| Case | $p_{\text{avg},120}$, $p=0$ | $p_{\text{avg},120}$, $p=0.2$ | Oscillation index, $p=0$ | Oscillation index, $p=0.2$ |
|---|---:|---:|---:|---:|
| Grid single | 0.042 | 0.020 | 1.50 | 0.37 |
| Grid clustered | 0.156 | 0.103 | 0.75 | 0.28 |
| Toy single | 0.038 | 0.037 | 0.97 | 0.26 |
| Toy clustered | 0.178 | 0.200 | 0.41 | 0.24 |

Pure-quantum peak, grid single: $p_{\max}=0.449$ at $t=13$.

Detection model (measurement hit ends the walk; $p=0$ pure quantum, $p=1$ classical $P(\tau\le T)$):

| Case | $T$ | $p=0$ | $p=0.2$ | $p=0.3$ | $p=1$ |
|---|---:|---:|---:|---:|---:|
| Grid single | 40 | 0.021 | 0.146 | 0.159 | 0.136 |
| Grid single | 120 | 0.098 | 0.373 | 0.447 | 0.516 |
| Grid clustered | 40 | 0.055 | 0.455 | 0.448 | 0.326 |
| Grid clustered | 120 | 0.271 | 0.837 | 0.862 | 0.811 |
| Toy single | 40 | 0.039 | 0.183 | 0.216 | 0.261 |
| Toy single | 120 | 0.004 | 0.503 | 0.582 | 0.621 |
| Toy clustered | 40 | 0.158 | 0.449 | 0.451 | 0.342 |
| Toy clustered | 120 | 0.134 | 0.837 | 0.844 | 0.703 |

Summary: for $T\lesssim15$, pure quantum is best. For clustered targets with
$T\gtrsim20$, $p\approx0.2$--$0.3$ beats both pure quantum and classical. For single
targets, the best $p$ moves irregularly toward classical as $T$ changes.

Sources: `code/results/raw/E5_sweep.csv`, `code/results/raw/E5_curves.csv`,
`code/results/processed/E5_decoherence.json`, figure `E5_robustness.pdf`.
