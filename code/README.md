# Quantum Walk Search × Quantum Cognition

Code for the EE5105 final project:

> Quantum Walk Search for Marked Vertices as a Model of Cognitive Search:
> From Semantic Memory Retrieval to Multi-Alternative Decision Making

The implementation follows `../ROADMAP.md`. The QIS core is the
Ambainis–Gilyén–Jeffery–Kokainis (AGJK) algorithm for finding marked vertices
with a quantum walk; the cognitive layer maps marked vertices to target
memories or decision alternatives on semantic and decision graphs.

## Layout

```text
code/
  configs/          base.yaml, experiments.yaml
  src/
    graphs.py       synthetic, semantic and decision graphs
    classical.py    stationary distribution, hitting times, diffusion
    szegedy.py      Szegedy walk operator, discriminant matrix, spectra
    agjk.py         interpolated walk and AGJK search (M2)
    semantic.py     CTQW/CRW on semantic graphs (M3)
    cognitive.py    choice probability, response time (M3)
    noise.py        partial measurement and dephasing (M5)
    metrics.py      search metrics, scaling fits, entropy
    experiments.py  experiment matrix runner (M2+)
    plotting.py     shared figure style (M2+)
  tests/
    test_classical.py
    test_quantum.py
    test_metrics.py
    test_semantic.py
    test_decision.py
    test_noise.py
  notebooks/        01 sanity checks, 02 scaling, 03 cognitive, 04 decoherence
  results/raw/       per-experiment CSV output
  results/processed/ per-experiment JSON summaries
  figures/           generated figures
```

## Environment (Miniforge)

Create and activate the conda environment:

```bash
mamba env create -f environment.yml
mamba activate qwalk-cognition
```

Alternatively, use `pip install -r requirements.txt` in an existing environment.

Run the tests from this directory:

```bash
python -m pytest -q
```

## Conventions

- Probability vectors are row vectors: `pi @ P = pi`.
- The walk state is stored as an `n x n` array indexed by `[first_register, second_register]`.
- The vertex register is the second register, matching `V(P)|0>|x> = sum_y sqrt(P_xy)|y,x>`.
- All random experiments take an explicit seed.
- Figures are written as PDF to `figures/`.

## Reproducing figures

E1 (classical versus quantum scaling):

```bash
mamba activate qwalk-cognition
python -m src.experiments --only E1
```

This writes:

- `results/raw/E1_scaling.csv`
- `results/processed/E1_scaling.json`
- `figures/E1_scaling.pdf` and `.png`
- `figures/E1_speedup.pdf` and `.png`

E2 (single, independent, and clustered marked vertices):

```bash
python -m src.experiments --only E2
```

This writes:

- `results/raw/E2_marked.csv` and `results/raw/E2_curves.csv`
- `results/raw/E2_adversarial_torus.csv`
- `results/processed/E2_marked.json` and `E2_adversarial_torus.json`
- `figures/E2_success.pdf` and `figures/E2_ht.pdf`

The adversarial-torus cases follow the marked-set pattern behind the
`HT+ >> HT` construction in AGJK 2019; only the smallest case (`L = 18`) is
simulated with `W(s)`, while the larger cases report the spectral `HT+` proxy.

E3 (semantic activation on the toy concept graph):

```bash
python -m src.experiments --only E3
```

This writes:

- `results/raw/E3_semantic_metrics.csv` and `E3_semantic_curves.csv`
- `results/processed/E3_semantic.json`
- `figures/E3_semantic.pdf` and `.png`

E3 compares a continuous-time quantum walk (CTQW) with a continuous-time
random walk (CRW) from the same cue. The CTQW uses the symmetric normalized
Laplacian; the CRW uses the corresponding random-walk generator with the same
spectrum. Time is normalized by the spectral gap, `tau = lambda_1 t`.

E4 (multi-alternative decision under option coupling):

```bash
python -m src.experiments --only E4
```

This writes:

- `results/raw/E4_metrics.csv`, `E4_choices.csv`, and `E4_curves.csv`
- `results/raw/E4_robustness.csv` and `results/processed/E4_robustness.json`
- `figures/E4_robustness.pdf`
- `results/processed/E4_decision.json`
- `figures/E4_decision.pdf` and `.png`

E4 uses a multi-branch decision graph with one terminal per option. Two
branches are coupled with strength `c` at matching depths. The quantum model
runs the interpolated Szegedy walk with `s = 0.9`; the classical model runs an
absorbing random walk. Four readouts are reported: `quantum_threshold`
(first crossing of total terminal probability `0.5`, phase sensitive),
`quantum_average` (uniform random stopping time), `quantum_detect`
(intermediate detection at rate 0.2), and `classical`. A robustness sweep
(laziness grid, edge-weight jitter) is also run; `max_steps` is 400. The E4
run takes more than 10 minutes.

E5 (partial-measurement decoherence sweep):

```bash
python -m src.experiments --only E5
```

This writes:

- `results/raw/E5_sweep.csv` and `E5_curves.csv`
- `results/processed/E5_decoherence.json`
- `figures/E5_decoherence.pdf` and `.png`

E5 uses the Szegedy walk W(0) of the lazy chain P_eta (eta = 0.1), i.e.
interpolation `s = 0`, from a cue vertex. Before each step, a
position measurement and reset occurs with probability `p`; `p = 0` is the pure
quantum walk and `p = 1` is exactly the classical random walk. The curves are
exact averages over measurement trajectories, computed from basis-state
ensembles, not Monte Carlo estimates. Two readouts are computed: a readout
model (uniform deadline over windows 1..H) and a detection model, with
`max_steps = 120` and horizons `[20, 40, 80, 120]`; `E5_robustness.pdf` is
also written.

For each graph instance, the interpolation parameter `s` is selected from
`configs/base.yaml` by maximizing the AGJK lower bound `q_t(s)` over
`t <= 3 sqrt(HT) + 5`. The reported `t_q` and `p_max` then come from the actual
interpolated walk `W(s)`.

The remaining experiments will be added here as they are frozen at M6.
