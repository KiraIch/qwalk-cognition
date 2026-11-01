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
| Complete $K_N$ | 1.06 | 0.53 | 0.50 [0.41, 0.59] | 4.7 |
| Cycle $C_N$ | 1.95 | 1.02 | 0.52 [0.51, 0.54] | 11.7 |
| 2D grid $L\times L$ | 1.26 | 0.61 | 0.48 [0.39, 0.57] | 7.9 |
| Hypercube $Q_d$ | 1.07 | 0.47 | 0.44 [0.32, 0.55] | 5.4 |

Success probability at the optimal time is $0.84$--$1.00$ across all instances.
The fitted $T_q$--$\HT$ exponents $\gamma$ are $0.50$, $0.52$, $0.48$, $0.44$
for complete, cycle, grid, and hypercube, respectively.

## E2: Single versus multiple marked vertices

Seeds 0--19, duplicate marked sets removed so each configuration uses distinct
sets (single target: one set). Medians and ranges over distinct sets, from
`code/results/raw/E2_marked.csv`.

| Graph | Marked set | # sets | Median $\HT$ [min, max] | Median $\HT^+/\HT$ (max) | Median $T_q$ |
|---|---|---:|---|---|---:|
| Grid $6\times6$ | single | 1 | 46.1 | 1.00 | 12 |
| Grid $6\times6$ | independent | 14 | 15.7 [12.7, 17.4] | 1.01 (1.02) | 7 |
| Grid $6\times6$ | clustered | 17 | 40.1 [17.6, 54.9] | 1.09 (1.10) | 14 |
| Grid $8\times8$ | single | 1 | 95.5 | 1.00 | 17 |
| Grid $8\times8$ | independent | 18 | 34.8 [26.9, 39.7] | 1.02 (1.05) | 10 |
| Grid $8\times8$ | clustered | 18 | 85.0 [41.5, 131.1] | 1.06 (1.09) | 20 |
| Barbell $n=8$ | single | 1 | 373.6 | 1.00 | 51 |
| Barbell $n=8$ | independent | 11 | 7.6 [7.1, 7.6] | 1.38 (1.38) | 5 |
| Barbell $n=8$ | clustered | 9 | 425.3 [196.6, 433.2] | 1.01 (1.09) | 48 |
| Barbell $n=16$ | single | 1 | 2558.0 | 1.00 | 134 |
| Barbell $n=16$ | independent | 18 | 16.8 [16.4, 415.1] | 1.53 (2.94) | 7 |
| Barbell $n=16$ | clustered | 16 | 2768.0 [1893.1, 2781.3] | 1.00 (1.04) | 133 |

Every independent set is easier than every clustered set on all four graphs.
Clustered sets can be easier or harder than a single target: barbell $n=16$
clustered is $0.74$--$1.09\times$ the single value, grid $8\times8$ clustered is
$0.43$--$1.37\times$ (median $0.89\times$). The barbell $n=16$ independent maximum
$\HT^+/\HT=2.94$ comes from one set ($\{0,21,25,29\}$, $\HT=415$); the other 17
independent sets lie in $1.35$--$1.53$.

Adversarial torus (AGJK marked-set pattern):

| $L$ | $N$ | $m$ | $p_M$ | $\HT$ | $\HT^+$ | $\HT^+/\HT$ |
|---:|---:|---:|---:|---:|---:|---:|
| 18 | 324 | 76 | 0.235 | 10.3 | 57.1 | 5.5 |
| 24 | 576 | 108 | 0.188 | 20.5 | 150.9 | 7.35 |
| 30 | 900 | 148 | 0.164 | 34.9 | 295.9 | 8.5 |
| 36 | 1296 | 252 | 0.194 | 50.5 | 443.1 | 8.8 |

For $L=18$, the interpolated walk still reaches $p_{\max}=0.978$ at $t=6$.

## E3: Toy semantic graph

Spectral gap $\lambda_1=0.03335$, relaxation time $1/\lambda_1=30.0$.

Window $\tau\le50$; peak = global maximum over the window; AUC over $\tau\le8$.
CTQW curves oscillate strongly, so the peak is window dependent and AUC is the
more stable comparison. Expected radius is no longer reported.

| Cue $\to$ target | Model | $p_{\text{peak}}$ | $\tau_{\text{peak}}$ | AUC ($\tau\le8$) |
|---|---|---:|---:|---:|
| animal $\to$ dog (distance 1) | CTQW | 0.337 | 47.5 | 0.481 |
| animal $\to$ dog (distance 1) | CRW | 0.158 | 0.125 | 0.579 |
| animal $\to$ violin (distance 4) | CTQW | 0.268 | 19.3 | 0.360 |
| animal $\to$ violin (distance 4) | CRW | no interior peak | -- | 0.323 |

Dog CTQW peak is a single recurrence spike; dog CRW decays to the stationary
value $0.061$. Violin CRW rises monotonically to stationary $\pi=0.0455$.

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

## E6: Small-world and scale-free graphs

Watts--Strogatz ($\beta\in\{0,0.05,0.2,1\}$, $N\in\{32,64\}$, $k=4$) and
Barabási--Albert ($m=2$, $N\in\{32,64\}$), 5 seeds, hub versus peripheral target.
Pooled fit $T_q\sim\HT^{0.52}$ (95\% CI $0.49$--$0.54$, $R^2=0.94$, 100 instances);
WS exponent $0.54$, BA exponent $0.45$. Hub speedup falls with rewiring
($N=64$: $8.0\to4.0$); peripheral speedup is $4$--$9$. BA hub speedup $1.8$--$2.4$
versus peripheral $6.8$--$11.5$.

Sources: `code/results/raw/E6_smallworld.csv`, figure `E6_smallworld.pdf`.
Test suite: 71 tests.
