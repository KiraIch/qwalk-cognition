# Reproduce everything from the code/ directory:  make all
PY ?= python3
PYTHONDONTWRITEBYTECODE := 1
export PYTHONDONTWRITEBYTECODE

.PHONY: all test results figures sync manifest report clean

all: test results sync manifest report

test:
	$(PY) -m pytest -q -p no:cacheprovider

# Runs E1-E6 and writes results/raw, results/processed and figures/.
# E4 includes the robustness sweep and takes more than 10 minutes.
results:
	$(PY) -m src.experiments

# Copies the figures used by the paper into ../report/figures.
sync:
	cp figures/E1_scaling.pdf ../report/figures/fig_e1_scaling.pdf
	cp figures/E1_speedup.pdf ../report/figures/fig_e1_speedup.pdf
	cp figures/E2_success.pdf ../report/figures/fig_e2_success.pdf
	cp figures/E2_ht.pdf ../report/figures/fig_e2_ht.pdf
	cp figures/E3_semantic.pdf ../report/figures/fig_e3_semantic.pdf
	cp figures/E4_robustness.pdf ../report/figures/fig_e4_robustness.pdf
	cp figures/E5_robustness.pdf ../report/figures/fig_e5_robustness.pdf
	cp figures/E6_smallworld.pdf ../report/figures/fig_e6_smallworld.pdf

manifest:
	$(PY) -m src.manifest

report:
	cd ../report && tectonic -X compile main.tex

clean:
	rm -f results/MANIFEST.json
