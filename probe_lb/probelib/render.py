"""Render probe_lb experiment results to LaTeX (booktabs) and Markdown."""

from __future__ import annotations


# ----------------------------------------------------------------- P1 / P2

def render_complexity_md(p2: dict) -> str:
    lines = [
        "### Deterministic probe complexity of the gap problem",
        "",
        "`D(n)` is the exact number of probes the all-zeros adversary forces "
        "(Erdős–Gallai); `C(ceil(n/2),2)` is the plan's clean lower bound. "
        "Gap target: distinguish `mu=0` from `mu>=ceil(n/4)`.",
        "",
        "| n | target mu | lemma LB C(ceil(n/2),2) | exact D(n) | extremal | D(n)>=LB |",
        "|---|---|---|---|---|---|",
    ]
    for r in p2["rows"]:
        lines.append(
            f"| {r['n']} | {r['target_mu']} | {r['lemma_lower_bound']} | "
            f"{r['exact_D_n']} | {r['extremal_family']} | "
            f"{'yes' if r['exact_D_n'] >= r['lemma_lower_bound'] else 'NO'} |"
        )
    return "\n".join(lines) + "\n"


def render_complexity_tex(p2: dict, caption: str, label: str) -> str:
    out = [
        r"\begin{table}[t]\centering\small",
        r"\begin{tabular}{@{}cccccc@{}}",
        r"\toprule",
        r"$n$ & target $\mu$ & $\binom{\lceil n/2\rceil}{2}$ (lemma LB) & "
        r"$D(n)$ (exact) & extremal & $D\ge$LB \\",
        r"\midrule",
    ]
    for r in p2["rows"]:
        out.append(
            f"${r['n']}$ & ${r['target_mu']}$ & ${r['lemma_lower_bound']}$ & "
            f"${r['exact_D_n']}$ & \\textsf{{{r['extremal_family']}}} & "
            f"{'$\\checkmark$' if r['exact_D_n'] >= r['lemma_lower_bound'] else 'NO'} \\\\"
        )
    out += [r"\bottomrule", r"\end{tabular}",
            r"\caption{" + caption + r"}", r"\label{" + label + r"}",
            r"\end{table}"]
    return "\n".join(out) + "\n"


def render_p1_md(p1: dict) -> str:
    lines = [
        "### Exhaustive adversary simulation (every deterministic order)",
        "",
        "Probes each order needs to certify `mu<ceil(n/4)` against the "
        "all-zeros adversary; the minimum equals the exact `D(n)`, and every "
        "order is `>= C(ceil(n/2),2)`.",
        "",
        "| n | lemma LB | exact D(n) | min over orders | witness=D(n) | all orders >= LB |",
        "|---|---|---|---|---|---|",
    ]
    for r in p1["rows"]:
        lines.append(
            f"| {r['n']} | {r['lemma_lower_bound']} | {r['exact_D_n']} | "
            f"{r['min_over_orders']} | {'yes' if r['witness_matches_D'] else 'NO'} | "
            f"{'yes' if r['all_orders_ge_lb'] else 'NO'} |"
        )
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------- P3

def render_p3_md(p3: dict) -> str:
    lines = [
        f"### Randomized detection vs probe budget (n={p3['n']})",
        "",
        f"Hard instance: a planted matching of size {p3['plant_matching_size']} "
        f"(`mu>=ceil(n/4)={p3['target_mu']}`). Deterministic certification needs "
        f"`D(n)={p3['deterministic_exact_D_n']}` probes "
        f"(lemma LB {p3['deterministic_lemma_lb']}); randomized detection:",
        "",
        "| budget B | B/n | detect prob (plant) | false positive (empty) |",
        "|---|---|---|---|",
    ]
    for c in p3["curve"]:
        lines.append(
            f"| {c['budget']} | {c['budget_over_n']} | "
            f"{c['detect_prob_plant']:.3f} | {c['false_positive_empty']:.3f} |"
        )
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------- P4

def render_p4_md(p4: dict) -> str:
    lines = [
        "### Corollary 3.7: no deterministic drop-in at the oracle layer",
        "",
        "`D(N)` is the forced deterministic probe cost on an N-vertex implicit "
        "graph; the ratio to any sublinear-in-`N^2` per-call budget grows "
        "without bound.",
        "",
        "| N | lemma LB | exact D(N) | budget N·log2 N | budget N^1.5 | D/(N log N) | D/N^1.5 |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in p4["rows"]:
        b = r["sublinear_budgets"]
        lines.append(
            f"| {r['N']} | {r['lemma_lower_bound']} | {r['exact_D_N']} | "
            f"{b['N_log2_N']} | {b['N_pow_1.5']} | {r['D_over_NlogN']} | "
            f"{r['D_over_N1p5']} |"
        )
    lines += ["", f"Ratio increasing (N·logN): {p4['ratio_increasing_NlogN']}; "
              f"crossover N (N·logN): {p4['crossover_N_NlogN']}; "
              f"crossover N (N^1.5): {p4['crossover_N_N1p5']}."]
    return "\n".join(lines) + "\n"
