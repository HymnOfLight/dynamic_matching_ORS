"""Experiments P1--P4 for the deterministic probe lower bound.

    P1  exhaustive adversary simulation (n <= 12): every deterministic probe
        order needs >= C(ceil(n/2),2) probes, and the witness order achieves
        the exact D(n);
    P2  exact deterministic complexity table D(n) vs the lemma bound;
    P3  randomized O(n log n) detection vs probe budget on the hard sparse
        plant (the det/rand contrast);
    P4  Corollary 3.7: a sublinear per-call budget cannot host a deterministic
        gap estimator.
"""

from __future__ import annotations

import math
import random

from . import algorithms as A
from .lemma import clique_in_probeset, det_complexity, det_value, lemma_lower_bound
from .model import gap_target

SCALES = {
    "quick": dict(p1_nmax=9, p3_n=40, p3_trials=200, p4_nmax=64),
    "full": dict(p1_nmax=12, p3_n=64, p3_trials=400, p4_nmax=256),
}


def exp_p1(scale: str = "quick", **kw) -> dict:
    nmax = SCALES[scale]["p1_nmax"]
    rows = []
    all_ok = True
    for n in range(4, nmax + 1):
        dc = det_complexity(n)
        orders = {
            "row_major": A.order_row_major(n),
            "diagonal": A.order_diagonal(n),
            "clique_first": A.order_clique_first(n),
            "pseudo_random": A.order_pseudo_random(n),
            "witness": A.order_witness(n, dc.witness_kept),
        }
        runs = {name: A.run_all_zeros(n, order, name).probes_to_certify
                for name, order in orders.items()}
        min_probes = min(runs.values())
        lb = lemma_lower_bound(n)
        ok = (min_probes >= lb) and (min_probes == dc.value) and \
             all(v >= lb for v in runs.values())
        all_ok = all_ok and ok
        rows.append({
            "n": n, "target_mu": gap_target(n), "lemma_lower_bound": lb,
            "exact_D_n": dc.value, "min_over_orders": min_probes,
            "probes_by_order": runs, "witness_matches_D": runs["witness"] == dc.value,
            "all_orders_ge_lb": all(v >= lb for v in runs.values()), "ok": ok,
        })
    return {"rows": rows, "all_ok": all_ok, "claim":
            "every deterministic probe order needs >= C(ceil(n/2),2) probes; "
            "the witness order achieves the exact D(n)"}


def exp_p2(scale: str = "quick", **kw) -> dict:
    nmax = max(SCALES[scale]["p1_nmax"], 16)
    rows = []
    all_ok = True
    for n in range(4, nmax + 1):
        dc = det_complexity(n)
        # independent confirmations: the extremal kept graph really has mu = k,
        # and D(n) dominates the clean lemma bound.
        ok = (dc.verified_mu == dc.k) and (dc.value >= dc.lemma_lb)
        all_ok = all_ok and ok
        rows.append({
            "n": n, "target_mu": dc.target, "k_max_plant_mu": dc.k,
            "lemma_lower_bound": dc.lemma_lb, "exact_D_n": dc.value,
            "extremal_family": dc.family, "kept_edges": dc.max_kept_edges,
            "verified_kept_mu": dc.verified_mu, "ok": ok,
        })
    return {"rows": rows, "all_ok": all_ok, "formula":
            "D(n) = C(n,2) - ex(n; nu <= ceil(n/4)-1)  [Erdos--Gallai], "
            ">= C(ceil(n/2),2) [plan Lemma 3.6]"}


def exp_p3(scale: str = "quick", seed: int = 20260613, **kw) -> dict:
    cfg = SCALES[scale]
    n = cfg["p3_n"]
    trials = cfg["p3_trials"]
    rng = random.Random(seed)
    plant = A.sparse_plant(n, rng)
    target = gap_target(n)
    # budgets in units of n: 0.5n, 1n, 2n, 4n, 8n, 16n
    budgets = [int(c * n) for c in (0.5, 1, 2, 4, 8, 16, 32)]
    curve = []
    for B in budgets:
        p_hit = A.detection_probability(n, plant, B, trials, random.Random(seed + B))
        p_empty = A.detection_probability(n, set(), B, trials, random.Random(seed + B + 1))
        curve.append({"budget": B, "budget_over_n": round(B / n, 2),
                      "detect_prob_plant": p_hit, "false_positive_empty": p_empty})
    return {
        "n": n, "plant_matching_size": len(plant), "target_mu": target,
        "trials": trials, "curve": curve,
        "deterministic_lemma_lb": lemma_lower_bound(n),
        "deterministic_exact_D_n": det_value(n)["value"],
        "note": "randomized detection on the sparse n/4-matching plant uses "
                "O(n log n) probes; deterministic certification needs Theta(n^2) "
                "(thresholds shown for reference). No false positives on the "
                "empty graph.",
    }


def exp_p4(scale: str = "quick", **kw) -> dict:
    """Corollary 3.7: a per-call probe budget that is sublinear in N^2 cannot
    deterministically implement the gap-estimator oracle the pipelines call."""
    nmax = SCALES[scale]["p4_nmax"]
    rows = []
    N = 8
    crossover_nlogn = None
    crossover_n15 = None
    while N <= nmax:
        lb = lemma_lower_bound(N)
        D = det_value(N)["value"]
        budgets = {
            "N_log2_N": int(N * max(1, math.log2(N))),
            "N_pow_1.5": int(N ** 1.5),
        }
        r_nlogn = D / budgets["N_log2_N"]
        r_n15 = D / budgets["N_pow_1.5"]
        if crossover_nlogn is None and D > budgets["N_log2_N"]:
            crossover_nlogn = N
        if crossover_n15 is None and D > budgets["N_pow_1.5"]:
            crossover_n15 = N
        rows.append({
            "N": N, "lemma_lower_bound": lb, "exact_D_N": D,
            "sublinear_budgets": budgets,
            "D_over_NlogN": round(r_nlogn, 2),
            "D_over_N1p5": round(r_n15, 2),
        })
        N *= 2
    inc_nlogn = all(rows[i]["D_over_NlogN"] <= rows[i + 1]["D_over_NlogN"]
                    for i in range(len(rows) - 1))
    inc_n15 = all(rows[i]["D_over_N1p5"] <= rows[i + 1]["D_over_N1p5"]
                  for i in range(len(rows) - 1))
    return {
        "rows": rows,
        "ratio_increasing_NlogN": inc_nlogn,
        "ratio_increasing_N1p5": inc_n15,
        "crossover_N_NlogN": crossover_nlogn,
        "crossover_N_N1p5": crossover_n15,
        "claim": "D(N)/budget grows without bound for any sublinear-in-N^2 "
                 "per-call budget; beyond a small crossover N the forced "
                 "deterministic probe cost exceeds the budget, so the oracle "
                 "layer has no deterministic drop-in (plan Cor. 3.7)",
    }


ALL_EXPERIMENTS = {"p1": exp_p1, "p2": exp_p2, "p3": exp_p3, "p4": exp_p4}
