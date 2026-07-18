# Command Log (verified execution record)

## Corrected rerun (2026-06-10, commits 9dd97c2 -> 02b1b6e; logs committed in outputs/logs/)
    python3 src/preprocessing/build_panel.py      # rerun_panel.log
    python3 src/features/build_features.py        # rerun_features.log
    python3 scripts/run_forecasting.py            # rerun_forecasting.log
    python3 scripts/run_decision.py               # rerun_decision.log
    python3 scripts/run_inference.py              # rerun_inference.log
    python3 scripts/make_tables_figures.py        # rerun_artifacts.log
    python3 scripts/make_paper_stats.py

## Amendment C11 rerun (2026-06-10/11; logs rerun2_*.log committed)
    python3 scripts/run_forecasting.py            # rerun2_forecasting.log
    python3 scripts/run_decision.py               # rerun2_decision.log
    python3 scripts/run_inference.py              # rerun2_inference.log
    python3 scripts/make_tables_figures.py        # rerun2_artifacts.log
    python3 scripts/make_paper_stats.py

## Prof 1 / Prof 2 revision pass (2026-06-12; no core experiment rerun)
    python3 scripts/run_diagnostics.py            # W2 trend diagnostic; asserts
                                                  # identity with E7 totals to 1e-6
    python3 scripts/make_paper_stats.py           # regenerates corrected caption
    python3 scripts/make_tables_figures.py        # regenerates tables + tab10 + provenance
    (cd paper && make && make anonymous)
    (cd supplement && pdflatex/bibtex/pdflatex x2)
    python3 -m pytest tests -v | tee reproducibility/pytest_final.log

## Verification status
- VERIFIED by committed artifacts: all rerun logs (outputs/logs/, tracked in
  git), provenance hashes (outputs/tables/_provenance.json), proof manifests
  (frozen_budgets.json, pooled_censoring.json), pytest_final.log.
- An earlier external mirror lacked outputs/logs and a pytest
  artifact; both are present and tracked in this repository. Nothing in this
  log is reconstructed from memory alone; every command above corresponds to
  a committed log file or a committed artifact it produced.

## Authoritative reproduction
    pip install -r reproducibility/pip-freeze.txt   # Python 3.11.15, pandas 3.0.3
    make all && python3 scripts/run_diagnostics.py && python3 -m pytest tests -q
Bit-exact reproduction is expected under the frozen environment (the
pipeline is seeded and the decision layer Monte-Carlo-free); under other
environments only artifact-level (qualitative) reproduction is claimed.
