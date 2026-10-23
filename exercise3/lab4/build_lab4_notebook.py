"""Create the Lab 4 checkpoint notebook from the saved Lab 3 inputs.

Run from the repository root:
    source .venv/bin/activate && python lab4/build_lab4_notebook.py
"""
from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "lab4" / "lab4_notebook.ipynb"


def md(text):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text):
    # Every notebook code line is authored eight spaces inside this list.  Do not
    # use textwrap.dedent here: the report-writing cell intentionally contains
    # unindented Markdown inside a triple-quoted runtime string.
    return nbf.v4.new_code_cell("\n".join(
        line[8:] if line.startswith("        ") else line
        for line in text.strip().splitlines()
    ))


cells = [
    md(
        """
        # Lab 4 — Build the Optimizer, Break It, Then Constrain It

        **Thursday checkpoint: Steps 0–5 only.** This notebook loads the saved Lab 3
        excess-return panel and covariance matrix, estimates the requested portfolios,
        saves every required output under `lab4/outputs/`, and writes the companion
        submission narrative to `lab4/lab4_summary.md`.

        **Run order:** use **Run All** from the repository root. The sections must run
        in their numbered order: Step 0 checks the Week 3 inputs; Steps 1–2 use the two
        60-month windows; Steps 3–4 test the A weights in B; Step 5 saves the portfolio
        Week 5 will inherit. Step 6 is deliberately not included because it is outside
        this Thursday checkpoint.

        **Inputs from Lab 3:**

        - `lab3/week4_monthly_excess_returns.csv`
        - `lab3/week4_annualized_excess_covariance.csv`
        """
    ),
    code(
        """
        from pathlib import Path
        import json
        import numpy as np
        import pandas as pd
        from scipy.optimize import minimize

        MONTHS_PER_YEAR = 12
        ROOT = Path.cwd()
        if not (ROOT / "lab3").exists():
            ROOT = Path.cwd().parent
        LAB3 = ROOT / "lab3"
        LAB4 = ROOT / "lab4"
        OUTPUTS = LAB4 / "outputs"
        OUTPUTS.mkdir(parents=True, exist_ok=True)

        # Prework choices, recorded before executing any Lab 4 optimizer cells.
        # The 15% cap is feasible: 11 × 15% = 165% ≥ 100%, and it requires at least 7 names.
        CAP = 0.15
        PREDICTION = (
            "Before running the optimizer, I predict that 1/N will have the higher "
            "out-of-sample Sharpe ratio by roughly 0.30 because each 60-month fit estimates "
            "77 parameters from only 60 monthly observations."
        )
        CAP_TIMING = "Chosen before running Lab 4 weight calculations, after reviewing the Lab 3 panel."

        assert 0 < CAP <= 1, "CAP must be between 0 and 1."
        print(f"Working folder: {ROOT}")
        print(f"Declared cap: {CAP:.0%}; prediction: {PREDICTION}")
        """
    ),
    md(
        """
        ## Prework assumptions carried into Lab 4

        **Panel and conventions.** Lab 3 supplied 11 names and 120 simple monthly **excess**
        returns, formed using the Lab 3 conventions. The saved covariance file is annualized
        and is used for the Step 0 consistency check; each optimizer re-estimates a monthly
        covariance matrix from the applicable return window.

        **Cap chosen before optimization.** I chose a 15% cap after reviewing the panel but
        before calculating Lab 4 weights. It is feasible because 11 × 15% = 165%, and it
        forces at least seven holdings. That is a deliberate diversification floor for this
        small, bank-heavy panel; it still allows active relative weights instead of forcing
        the 9.09% equal-weight allocation.

        **Prediction committed before testing.** The configuration cell records the specific
        out-of-sample prediction. Its premise is the prework parameter count: a 60-month
        estimation window is small relative to 77 estimated means/covariances, so estimation
        error may make the optimized A portfolio less robust than 1/N in B.
        """
    ),
    md(
        """
        ## Step 0 — Load and verify what Lab 3 left

        Lab 3 saved **monthly excess returns** and an **annualized** covariance matrix.
        The covariance check below compares the saved annual covariance diagonal with the
        full-sample monthly-return volatilities annualized and squared. The optimiser itself
        uses monthly means and a monthly covariance within each estimation window, so units
        are internally consistent.

        The parameter count uses one 60-month estimation half: for `N` names there are
        `N(N+1)/2` distinct covariance entries plus `N` mean estimates. It is a complexity
        count—not degrees of freedom.
        """
    ),
    code(
        """
        excess = pd.read_csv(LAB3 / "week4_monthly_excess_returns.csv", index_col="Date")
        excess.index = pd.PeriodIndex(excess.index.astype(str), freq="M")
        cov_week3 = pd.read_csv(LAB3 / "week4_annualized_excess_covariance.csv", index_col="Security")
        cov_week3 = cov_week3.loc[excess.columns, excess.columns]

        n_names = excess.shape[1]
        n_months = len(excess)
        n_per_window = n_months // 2
        n_cov_parameters = n_names * (n_names + 1) // 2
        n_parameters = n_cov_parameters + n_names
        annual_vol_sq = (excess.std(ddof=1) * np.sqrt(MONTHS_PER_YEAR)) ** 2
        diagonal_check = pd.DataFrame({
            "saved_annual_covariance_diagonal": np.diag(cov_week3),
            "annualized_monthly_volatility_squared": annual_vol_sq,
        }, index=excess.columns)
        diagonal_check["difference"] = (
            diagonal_check.iloc[:, 0] - diagonal_check.iloc[:, 1]
        )
        checks = {
            "square": cov_week3.shape == (n_names, n_names),
            "same_name_order": cov_week3.index.equals(excess.columns) and cov_week3.columns.equals(excess.columns),
            "symmetric": np.allclose(cov_week3, cov_week3.T, atol=1e-12),
            "diagonal_matches_annual_vol_squared": np.allclose(
                diagonal_check.iloc[:, 0], diagonal_check.iloc[:, 1], atol=1e-12
            ),
        }
        assert all(checks.values()), checks
        diagonal_check.to_csv(OUTPUTS / "step0_covariance_diagonal_check.csv")

        parameter_count = pd.DataFrame({
            "names": [n_names],
            "months_per_estimation_window": [n_per_window],
            "distinct_covariance_entries": [n_cov_parameters],
            "mean_estimates": [n_names],
            "total_parameters": [n_parameters],
            "months_per_parameter": [n_per_window / n_parameters],
        })
        parameter_count.to_csv(OUTPUTS / "step0_parameter_count.csv", index=False)
        print("Input checks:", checks)
        display(parameter_count.style.format({"months_per_parameter": "{:.2f}"}))
        display(diagonal_check.style.format("{:.8f}"))
        """
    ),
    md(
        """
        ## Step 1 — Unconstrained tangency optimizer on window A

        The raw tangency direction is $\\Sigma^{-1}\\mu$. It is then scaled to sum to one.
        The required raw-sum diagnostic is printed before scaling; a non-positive value would
        stop the analysis because normalizing it into a fully invested tangency portfolio
        would reverse the direction. No short-sale or concentration remedy is applied here.
        """
    ),
    code(
        """
        window_a = excess.iloc[:n_per_window].copy()
        window_b = excess.iloc[n_per_window:2 * n_per_window].copy()
        assert len(window_a) == len(window_b) == n_per_window

        def unconstrained_tangency(returns):
            mu = returns.mean()
            sigma = returns.cov()
            raw = pd.Series(np.linalg.solve(sigma.to_numpy(), mu.to_numpy()), index=returns.columns)
            raw_sum = raw.sum()
            if raw_sum <= 0:
                raise ValueError(f"Raw tangency-weight sum is {raw_sum:.6f}, not clearly positive; stop and report it.")
            return raw / raw_sum, raw_sum

        def metrics(returns, weights):
            portfolio = returns @ weights
            ann_return = portfolio.mean() * MONTHS_PER_YEAR
            ann_vol = portfolio.std(ddof=1) * np.sqrt(MONTHS_PER_YEAR)
            sharpe = ann_return / ann_vol if ann_vol > 0 else np.nan
            return {"annualized_excess_return": ann_return, "annualized_volatility": ann_vol, "sharpe_ratio": sharpe}

        w_a_unconstrained, raw_sum_a = unconstrained_tangency(window_a)
        a_metrics = metrics(window_a, w_a_unconstrained)
        a_equal_metrics = metrics(window_a, pd.Series(1 / n_names, index=window_a.columns))
        print(f"Window A: {window_a.index.min()} through {window_a.index.max()}")
        print(f"Raw tangency-weight sum before scaling: {raw_sum_a:.6f}")
        print(f"Gross leverage: {w_a_unconstrained.abs().sum():.2f}")
        print(f"Largest long: {w_a_unconstrained.idxmax()} {w_a_unconstrained.max():.1%}")
        print(f"Largest short: {w_a_unconstrained.idxmin()} {w_a_unconstrained.min():.1%}")
        print(f"In-sample Sharpe: {a_metrics['sharpe_ratio']:.3f}")
        print(f"1/N Sharpe on the same window: {a_equal_metrics['sharpe_ratio']:.3f}")
        display(w_a_unconstrained.to_frame("window_A_weight").style.format("{:.2%}"))
        """
    ),
    md(
        """
        ## Step 2 — Move the window

        This fits the same unconstrained estimator to B only to measure how much the weights
        move. It is **not** the B performance test—that comes in Step 3 and holds A weights
        fixed through B. The final two sentences identify the largest movement and whether it
        is plausibly explained by a company-level change.
        """
    ),
    code(
        """
        w_b_unconstrained, raw_sum_b = unconstrained_tangency(window_b)
        unconstrained_swing = pd.DataFrame({"weight_A": w_a_unconstrained, "weight_B": w_b_unconstrained})
        unconstrained_swing["swing_percentage_points"] = (unconstrained_swing["weight_B"] - unconstrained_swing["weight_A"]) * 100
        unconstrained_swing["absolute_swing_percentage_points"] = unconstrained_swing["swing_percentage_points"].abs()
        unconstrained_swing = unconstrained_swing.sort_values("absolute_swing_percentage_points", ascending=False)
        unconstrained_swing.to_csv(OUTPUTS / "step2_unconstrained_two_window_weights.csv")
        largest_unconstrained_move = unconstrained_swing.index[0]
        largest_unconstrained_pp = unconstrained_swing.iloc[0]["absolute_swing_percentage_points"]
        gross_a_unconstrained = w_a_unconstrained.abs().sum()
        gross_b_unconstrained = w_b_unconstrained.abs().sum()
        print(f"Raw tangency-weight sum in B before scaling: {raw_sum_b:.6f}")
        print(f"Gross leverage — A: {gross_a_unconstrained:.2f}; B: {gross_b_unconstrained:.2f}")
        display(unconstrained_swing.style.format({"weight_A": "{:.2%}", "weight_B": "{:.2%}", "swing_percentage_points": "{:.1f}", "absolute_swing_percentage_points": "{:.1f}"}))
        print(
            f"{largest_unconstrained_move} moved most, by {largest_unconstrained_pp:.1f} percentage points. "
            "A company-level change alone is unlikely to justify a shift of that size over adjacent five-year windows; "
            "the change is more plausibly the optimizer reacting to noisy estimated means and covariances."
        )
        """
    ),
    md(
        """
        ## Step 3 — Out of sample against 1/N

        The A tangency weights and equal weights are held fixed for every monthly B return.
        “Reset monthly” means the portfolio is rebalanced each month back to the same target
        vector; it does **not** re-estimate weights. Annualized excess return is arithmetic
        monthly mean × 12, annual volatility is monthly standard deviation × √12, and
        Sharpe is their ratio. Gross leverage is the sum of absolute target weights.
        """
    ),
    code(
        """
        w_equal = pd.Series(1 / n_names, index=excess.columns, name="equal_weight")
        oos_rows = []
        for label, weights in {"tangency_from_A": w_a_unconstrained, "1/N": w_equal}.items():
            row = metrics(window_b, weights)
            row["gross_leverage"] = weights.abs().sum()
            oos_rows.append(pd.Series(row, name=label))
        oos_comparison = pd.DataFrame(oos_rows)
        oos_comparison.to_csv(OUTPUTS / "step3_oos_vs_equal_weight.csv")
        display(oos_comparison.style.format("{:.3f}"))
        sharpe_gap = oos_comparison.loc["tangency_from_A", "sharpe_ratio"] - oos_comparison.loc["1/N", "sharpe_ratio"]
        winner = "tangency-from-A" if sharpe_gap > 0 else "1/N"
        print(f"Prediction: {PREDICTION}")
        print(f"Winner: {winner}, by {abs(sharpe_gap):.3f} Sharpe points.")
        """
    ),
    md(
        """
        ## Step 4 — Long-only, with the predeclared cap

        **Cap choice and logic:** I set a **15%** maximum position before running this
        optimizer. With 11 names, 11 × 15% = 165%, so the constraint is feasible and
        a fully invested portfolio must hold at least $⌈1/0.15⌉ = 7$ names. This is a
        deliberately meaningful diversification floor for a small, bank-heavy panel whose
        60-month estimation windows contain only 0.78 months per estimated parameter.
        It still permits the optimizer to express relative conviction rather than forcing
        the 9.09% equal-weight portfolio that a cap of 1/11 would impose.

        The constrained problem maximizes in-sample Sharpe with `sum(weights)=1` and
        `0 ≤ weight ≤ 15%`. A uses the A fit in the performance test on B. B is fit only
        afterward to measure constrained weight swing.
        """
    ),
    code(
        """
        if n_names * CAP < 1 - 1e-12:
            raise ValueError(f"Infeasible cap: {n_names} × {CAP:.2%} < 100%.")

        def constrained_tangency(returns, cap):
            mu = returns.mean().to_numpy()
            sigma = returns.cov().to_numpy()
            def negative_sharpe(w):
                variance = float(w @ sigma @ w)
                return -(w @ mu) / np.sqrt(variance) if variance > 0 else 1e12
            result = minimize(
                negative_sharpe,
                x0=np.repeat(1 / n_names, n_names),
                method="SLSQP",
                bounds=[(0, cap)] * n_names,
                constraints={"type": "eq", "fun": lambda w: w.sum() - 1},
                options={"ftol": 1e-12, "maxiter": 1000},
            )
            if not result.success:
                raise RuntimeError(f"Constrained optimizer failed: {result.message}")
            weights = pd.Series(result.x, index=returns.columns)
            assert np.isclose(weights.sum(), 1, atol=1e-8)
            assert weights.ge(-1e-8).all() and weights.le(cap + 1e-8).all()
            return weights

        w_a_constrained = constrained_tangency(window_a, CAP)
        w_b_constrained = constrained_tangency(window_b, CAP)
        constrained_swing = pd.DataFrame({"weight_A": w_a_constrained, "weight_B": w_b_constrained})
        constrained_swing["swing_percentage_points"] = (constrained_swing["weight_B"] - constrained_swing["weight_A"]) * 100
        constrained_swing["absolute_swing_percentage_points"] = constrained_swing["swing_percentage_points"].abs()
        constrained_swing = constrained_swing.sort_values("absolute_swing_percentage_points", ascending=False)
        constrained_swing.to_csv(OUTPUTS / "step4_constrained_two_window_weights.csv")
        constrained_in_sample = metrics(window_a, w_a_constrained)
        constrained_oos_rows = []
        for label, weights in {"constrained_from_A": w_a_constrained, "1/N": w_equal}.items():
            row = metrics(window_b, weights)
            row["gross_leverage"] = weights.abs().sum()
            constrained_oos_rows.append(pd.Series(row, name=label))
        constrained_oos = pd.DataFrame(constrained_oos_rows)
        constrained_oos.to_csv(OUTPUTS / "step4_constrained_oos_vs_equal_weight.csv")
        held = int((w_a_constrained > 1e-6).sum())
        largest_constrained_pp = constrained_swing.iloc[0]["absolute_swing_percentage_points"]
        in_sample_cost = a_metrics["sharpe_ratio"] - constrained_in_sample["sharpe_ratio"]
        print(f"Cap: {CAP:.0%}; held: {held} of {n_names}; gross leverage: {w_a_constrained.abs().sum():.2f}")
        print(f"Constrained in-sample Sharpe: {constrained_in_sample['sharpe_ratio']:.3f} (unconstrained: {a_metrics['sharpe_ratio']:.3f})")
        print(f"Largest constrained A→B swing: {largest_constrained_pp:.1f} percentage points (unconstrained: {largest_unconstrained_pp:.1f})")
        print(f"In-sample Sharpe given up: {in_sample_cost:.3f}.")
        display(w_a_constrained.to_frame("constrained_A_weight").sort_values("constrained_A_weight", ascending=False).style.format("{:.2%}"))
        display(constrained_oos.style.format("{:.3f}"))
        """
    ),
    md(
        """
        ## Step 5 — Cap defence and the portfolio Week 5 inherits

        **Strongest objection:** the 15% cap is a judgment, so changing it changes the
        portfolio; it is not discovered objectively from these returns. Specifically, with
        11 names it requires at least seven holdings, while a 20% cap requires only five,
        so the choice materially changes the opportunity set.

        **Response:** I concede that the number is a choice. I selected it before running
        Lab 4 weights, based on the panel’s 11 highly related financial-sector names and the
        0.78 months-per-parameter complexity count in each five-year window. The cap is a
        transparent risk-control preference: it prevents a noisy mean–covariance fit from
        putting more than 15% into one name, while leaving non-equal relative weights. Its
        cost is explicit: it gives up the in-sample Sharpe printed below and no longer lets
        me express a large single-name long, any short, or a concentrated relative-value bet.

        The code saves the full-window constrained portfolio, its exact constraints, and its
        gross leverage for Week 5. The saved weight file is immediately reloaded and checked.
        """
    ),
    code(
        """
        w_full_constrained = constrained_tangency(excess, CAP)
        full_metrics = metrics(excess, w_full_constrained)
        portfolio = pd.DataFrame({"weight": w_full_constrained}).sort_values("weight", ascending=False)
        portfolio_path = OUTPUTS / "step5_week5_portfolio_weights.csv"
        portfolio.to_csv(portfolio_path)
        constraints = {
            "portfolio_label": "Lab 4 long-only capped tangency portfolio",
            "input_return_file": "lab3/week4_monthly_excess_returns.csv",
            "estimation_window": f"{excess.index.min()} through {excess.index.max()} (full 120-month Lab 3 sample)",
            "objective": "maximize monthly excess-return Sharpe ratio",
            "fully_invested": True,
            "long_only": True,
            "single_name_cap": CAP,
            "gross_leverage": float(w_full_constrained.abs().sum()),
            "number_of_names_held": int((w_full_constrained > 1e-6).sum()),
            "rebalance_intention": "Monthly reset to the saved target weights; turnover/cost analysis is deferred to Week 5.",
        }
        constraints_path = OUTPUTS / "step5_week5_portfolio_constraints.json"
        constraints_path.write_text(json.dumps(constraints, indent=2) + "\\n")
        reloaded = pd.read_csv(portfolio_path, index_col=0)["weight"].reindex(excess.columns)
        saved_constraints = json.loads(constraints_path.read_text())
        assert np.allclose(reloaded, w_full_constrained)
        assert saved_constraints["long_only"] and saved_constraints["single_name_cap"] == CAP
        print("Saved and reloaded successfully:", portfolio_path.name, "and", constraints_path.name)
        print(f"Full-window gross leverage: {constraints['gross_leverage']:.2f}")
        display(portfolio.style.format("{:.2%}"))
        """
    ),
    md(
        """
        ## Write the required companion files

        This last cell writes the one Markdown record for Steps 0–5 and a Lab 4 source log.
        It intentionally does not produce a Step 6 finding: that is the after-Thursday,
        Exercise 3 work and is outside the requested checkpoint.

        Before submitting, read the automatically generated narrative once, make sure the
        prediction still represents what you actually committed to before class, and retain
        the AI disclosure below.
        """
    ),
    code(
        """
        def markdown_table(frame, formats=None):
            shown = frame.copy()
            if formats:
                for col, fmt in formats.items():
                    if col in shown:
                        shown[col] = shown[col].map(lambda x: fmt.format(x))
            headers = [str(shown.index.name or "")] + [str(col) for col in shown.columns]
            lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
            for index, row in shown.iterrows():
                values = [str(index)] + [str(value) for value in row]
                lines.append("| " + " | ".join(values) + " |")
            return "\\n".join(lines)

        step2_for_report = unconstrained_swing[["weight_A", "weight_B", "swing_percentage_points"]]
        step4_for_report = constrained_swing[["weight_A", "weight_B", "swing_percentage_points"]]
        summary = f'''# Lab 4 — Thursday checkpoint record (Steps 0–5)

## Prework assumptions and conventions

Lab 3 supplied 11 names and 120 simple monthly excess returns under the previously stated Lab 3 conventions. The saved covariance matrix is annualized and is used only for the Step 0 verification; each optimizer below estimates a monthly mean vector and monthly covariance matrix from its applicable window.

**Cap chosen before optimization:** I selected a {CAP:.0%} single-name cap after reviewing the panel and before calculating Lab 4 weights. It is feasible because {n_names} × {CAP:.0%} = {n_names * CAP:.0%}, requires at least {int(np.ceil(1 / CAP))} holdings, and remains above the {1/n_names:.2%} cap that would force equal weight. This is a deliberate diversification preference for a small, bank-heavy panel, not a number discovered objectively from the data.

**Prediction committed before the test:** {PREDICTION} The premise was the prework complexity count: each 60-month estimation half supports {n_parameters} estimated means/covariances, making noisy optimized weights plausible.

## Step 0 — parameter count and input checks

The Lab 3 covariance matrix is square ({n_names} × {n_names}), has the same names and order as the excess-return panel, is symmetric, and its diagonal matches the annualized monthly volatilities squared. The detailed diagonal evidence is saved in `outputs/step0_covariance_diagonal_check.csv`.

{markdown_table(parameter_count, {"months_per_parameter": "{:.2f}"})}

This is a complexity count, not degrees of freedom: each 60-month estimation window informs all estimates, but 60 observations for {n_parameters} estimated quantities is a reason to expect noise.

## Step 1 — unconstrained tangency fit on window A

Window A is {window_a.index.min()} through {window_a.index.max()}. The raw tangency direction, $\\Sigma^{{-1}}\\mu$, summed to {raw_sum_a:.6f} before scaling—clearly positive, so normalization to fully invested weights did not reverse the direction. The normalized fit has gross leverage {gross_a_unconstrained:.2f}, largest long {w_a_unconstrained.idxmax()} at {w_a_unconstrained.max():.2%}, largest short {w_a_unconstrained.idxmin()} at {w_a_unconstrained.min():.2%}, and in-sample Sharpe {a_metrics['sharpe_ratio']:.3f}. The same-window 1/N Sharpe is {a_equal_metrics['sharpe_ratio']:.3f}. The A weights themselves are displayed in the notebook and repeated in the A column of the Step 2 table below.

## Step 2 — unconstrained two-window weight swing

Gross leverage: A = {gross_a_unconstrained:.2f}; B = {gross_b_unconstrained:.2f}.

{markdown_table(step2_for_report, {"weight_A": "{:.2%}", "weight_B": "{:.2%}", "swing_percentage_points": "{:.1f}"})}

{largest_unconstrained_move} moved most, by {largest_unconstrained_pp:.1f} percentage points. A company-level change alone is unlikely to justify a shift of that size over adjacent five-year windows; noisy estimated means and covariances are the more plausible explanation.

## Step 3 — out of sample: window-A weights held through B

Window B is {window_b.index.min()} through {window_b.index.max()}. Target weights were reset monthly but never re-estimated.

{markdown_table(oos_comparison, {"annualized_excess_return": "{:.2%}", "annualized_volatility": "{:.2%}", "sharpe_ratio": "{:.3f}", "gross_leverage": "{:.2f}"})}

**Prediction written before running:** {PREDICTION}

**Result:** {winner} won by {abs(sharpe_gap):.3f} Sharpe points. This {'agrees with' if winner == '1/N' else 'does not agree with'} the prediction.

## Step 4 — long-only portfolio with a {CAP:.0%} cap

The cap is feasible because {n_names} × {CAP:.0%} = {n_names * CAP:.0%}. It requires at least {int(np.ceil(1 / CAP))} names. The A fit holds {held} of {n_names} names and has gross leverage {w_a_constrained.abs().sum():.2f}.

Constrained weights estimated on A:

{markdown_table(w_a_constrained.sort_values(ascending=False).to_frame("weight"), {"weight": "{:.2%}"})}

In-sample Sharpe: constrained {constrained_in_sample['sharpe_ratio']:.3f}; unconstrained {a_metrics['sharpe_ratio']:.3f}. The remedy gave up {in_sample_cost:.3f} of in-sample Sharpe.

{markdown_table(constrained_oos, {"annualized_excess_return": "{:.2%}", "annualized_volatility": "{:.2%}", "sharpe_ratio": "{:.3f}", "gross_leverage": "{:.2f}"})}

Largest constrained A→B swing: {largest_constrained_pp:.1f} percentage points, compared with {largest_unconstrained_pp:.1f} percentage points unconstrained. The cost beyond Sharpe is expressive: the remedy rules out shorts, a position over {CAP:.0%}, and therefore a concentrated single-name or relative-value view.

## Step 5 — cap defence and saved Week 5 portfolio

**Choice and timing:** I chose the {CAP:.0%} cap before running Lab 4 weight calculations, after reviewing the Lab 3 panel. {CAP_TIMING}

**Strongest objection:** the cap is a judgment rather than a fact in the data. A {CAP:.0%} cap forces at least {int(np.ceil(1 / CAP))} names, but a 20% cap would force only five, so a different number can generate a different portfolio.

**Response:** I concede that the number is a choice. It is a documented risk-control preference for this small, bank-heavy panel: each five-year fit has only {n_per_window / n_parameters:.2f} months per estimated parameter. The cap prevents an estimated edge from becoming a position above {CAP:.0%}, while avoiding the equal-weight outcome that a {1/n_names:.2%} cap would force.

The saved Week 5 portfolio is `outputs/step5_week5_portfolio_weights.csv`; its constraints are beside it in `outputs/step5_week5_portfolio_constraints.json`. It is long-only, capped at {CAP:.0%}, fully invested, holds {constraints['number_of_names_held']} names, and has gross leverage **{constraints['gross_leverage']:.2f}**. I intend to reset it to these target weights monthly; the resulting turnover and cost are reserved for Week 5.

## Checkpoint status and AI disclosure

**Stopping point:** Completed Steps 0–5. Step 6 is intentionally not started because it belongs to the after-Thursday Exercise 3 work.

**AI disclosure:** AI was used to help structure and document the notebook, implement the optimization code, and explain the cap logic. I reviewed the calculations, the declared cap, the prediction, and the interpretations against the course instructions.
'''
        (LAB4 / "lab4_summary.md").write_text(summary)

        prior_log = ROOT / "lab2" / "source_log_lab2.md"
        source_log = f'''# Source log — Lab 4

This log extends, but does not overwrite, the Lab 2 source log at `{prior_log.relative_to(ROOT)}`. Lab 4 performs no new market-data download: it uses the saved Lab 3 inputs below.

| Source | Access route / record | Role in Lab 4 | Independence / limitation |
|---|---|---|---|
| Lab 3 saved excess-return panel | `lab3/week4_monthly_excess_returns.csv`; loaded {pd.Timestamp.now().date()} | 120 monthly excess returns for the 11-name panel; split into two 60-month windows | Derived Lab 3 analytical input; not an independent raw-data source |
| Lab 3 saved covariance matrix | `lab3/week4_annualized_excess_covariance.csv`; loaded {pd.Timestamp.now().date()} | Annual covariance sanity check in Step 0 | Derived Lab 3 analytical input; recalculated within each window for optimization |
| Fama/French Research Data Factors | Lab 3 file `lab3/F-F_Research_Data_Factors.csv` | Risk-free rate used upstream to form the saved excess returns | Public academic data source; retained as documented in Lab 3 |
| Yahoo Finance via `yfinance` | Lab 3 data acquisition, documented in `lab3/lab3_notebook.ipynb` | Adjusted prices used upstream to form monthly total returns | Public vendor feed; not survivorship-free; limitation carried forward from Lab 3 |
| Week 4 prework page | https://cinderzhang.github.io/PythonFinance2026-site/week4/prework.html; consulted {pd.Timestamp.now().date()} | Defines the cap feasibility floor and pre-optimization timing requirement | Course instruction, not a market-data source |

## Lab 4 convention carried forward

Returns are simple monthly **excess** returns. The saved Lab 3 covariance matrix is annualized; the optimizers in this notebook recompute covariance on monthly returns in the applicable estimation window. Performance annualizes arithmetic mean excess return by 12 and volatility by √12.
'''
        (LAB4 / "source_log.md").write_text(source_log)
        print("Wrote lab4/lab4_summary.md and lab4/source_log.md")
        """
    ),
    md(
        """
        ## AI disclosure

        AI was used to help structure and document this notebook, implement the optimization
        code, and explain the cap logic. I reviewed the calculations, the declared cap, the
        prediction, and the interpretations against the course instructions.
        """
    ),
]

nb = nbf.v4.new_notebook(cells=cells, metadata={
    "kernelspec": {"display_name": "Python (.venv)", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.12"},
})
nbf.write(nb, OUT)
print(f"Wrote {OUT}")
