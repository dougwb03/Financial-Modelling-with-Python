# Lab 2 — Colab main-submission base (generated source: lab2)

This folder is the complete Week 2 working set. It deliberately does not change the Week 1 data or silently assert any result that has not been pulled.

## Use in Google Colab

1. In Colab, upload `Lab2_Colab_Submission.ipynb` and the entire `lab2` folder (including `lab2.py`). If your course uses Drive, place this course directory in Drive and update the mount path in the first notebook cell instead.
2. Open the notebook and run cells top to bottom. The first code cell installs `yfinance`, `pandas`, `requests`, and `tabulate`; the next runs `lab2.py`.
3. Do **not** edit output CSVs by hand. Change the documented `REQUESTED`, `SAMPLE_START`, and `SAMPLE_END` constants in `lab2.py` only if you choose a different universe, then rerun all cells.
4. Download the generated `lab2/output/` folder and `lab2/data_quality_issues.md`. Copy the Lab 2 source entries from `lab2/source_log_lab2.md` into the root `source_log.md` after recording the actual run date and access results.
5. Complete the narrative prompts in the notebook. Replace bracketed text only with your own evidence from the generated files and your independent second source / documented WRDS attempt.

## What the run produces

`coverage_inventory.csv` is the Step 2 table. It retains zero-row names, which a panel dataframe cannot show. `current_ticker_resolution.csv` is the SBNY-type label check. `fundamental_knowability_JPM.csv` records an SEC fact for a company actually in the starter panel. `panel_security_master.csv` is the only file to hand to Week 3; first check that it loads and that `permanent_identifier` is populated on every row.

`data_quality_issues.md` has all six catalog fields and an explicit Week 3 limitation. Review severity and current state rather than treating the generated draft as a final personal judgment.

## Required human work

The script supplies evidence; it cannot responsibly invent the two-source comparison, a WRDS access attempt, a public narrative for missing companies, or your Step 7/8 judgment. The notebook identifies exactly where those belong.
