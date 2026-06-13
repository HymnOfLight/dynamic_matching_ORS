"""probe_lb orchestrator (Task C1).

Usage
-----
    python3 run_all.py --scale quick      # CI-sized, ~seconds
    python3 run_all.py --scale full       # report run, ~1 min
    python3 run_all.py --only p1 p3       # subset of experiments

Outputs (under ``results/``)
    p1.json .. p4.json        raw experiment results (deterministic / seeded)
    RESULTS.md                human-readable summary
    complexity_table.{tex,md} exact D(n) vs the lemma bound
    p1_table.md, p3_table.md, p4_table.md
    det_vs_rand.png           the Theta(n^2) vs O(n log n) contrast figure
    barrier.png               Cor. 3.7 ratio growth
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

from probelib import experiments as E
from probelib import render

RESULTS_DIR = pathlib.Path(__file__).parent / "results"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scale", choices=list(E.SCALES), default="quick")
    p.add_argument("--only", nargs="*", choices=sorted(E.ALL_EXPERIMENTS),
                   default=sorted(E.ALL_EXPERIMENTS))
    args = p.parse_args(argv)
    RESULTS_DIR.mkdir(exist_ok=True)

    results: dict[str, dict] = {}
    t0 = time.perf_counter()
    for name in args.only:
        ts = time.perf_counter()
        print(f"[run] {name} (scale={args.scale}) ...", flush=True)
        res = E.ALL_EXPERIMENTS[name](scale=args.scale)
        res["elapsed_sec"] = round(time.perf_counter() - ts, 2)
        results[name] = res
        (RESULTS_DIR / f"{name}.json").write_text(json.dumps(res, indent=2))
        print(f"[ok ] {name} in {res['elapsed_sec']}s", flush=True)
    elapsed = time.perf_counter() - t0

    write_outputs(results)
    write_summary(results, args.scale, elapsed)
    maybe_plot(results)
    print(f"[done] {elapsed:.1f}s; see results/RESULTS.md")
    return 0


def write_outputs(results: dict) -> None:
    if "p2" in results:
        (RESULTS_DIR / "complexity_table.tex").write_text(
            render.render_complexity_tex(
                results["p2"],
                "Exact deterministic probe complexity $D(n)$ of the "
                "$\\mu{=}0$ vs $\\mu{\\ge}\\lceil n/4\\rceil$ gap, and the "
                "plan's lower bound.", "tab:detcomplexity"))
        (RESULTS_DIR / "complexity_table.md").write_text(
            render.render_complexity_md(results["p2"]))
    if "p1" in results:
        (RESULTS_DIR / "p1_table.md").write_text(render.render_p1_md(results["p1"]))
    if "p3" in results:
        (RESULTS_DIR / "p3_table.md").write_text(render.render_p3_md(results["p3"]))
    if "p4" in results:
        (RESULTS_DIR / "p4_table.md").write_text(render.render_p4_md(results["p4"]))
    print("[ok ] tables written")


def write_summary(results: dict, scale: str, elapsed: float) -> None:
    lines = [
        "# probe_lb run summary (Task C1)",
        "",
        f"Scale `{scale}`; elapsed {elapsed:.1f}s.",
        "",
        "Deterministic probe complexity of approximate matching size, and the "
        "architectural barrier for derandomizing dynamic matching (plan "
        "Lemma 3.6 + Cor. 3.7). All values are exact (P1/P2/P4) or seeded and "
        "reproducible (P3).",
        "",
    ]
    if "p1" in results:
        lines += [f"- **P1** exhaustive simulation: all_ok = "
                  f"`{results['p1']['all_ok']}` (every deterministic order "
                  f">= C(ceil(n/2),2); witness order = exact D(n)).", ""]
        lines.append(render.render_p1_md(results["p1"]))
    if "p2" in results:
        lines += [f"- **P2** all_ok = `{results['p2']['all_ok']}`.", ""]
        lines.append(render.render_complexity_md(results["p2"]))
    if "p3" in results:
        lines.append(render.render_p3_md(results["p3"]))
    if "p4" in results:
        lines.append(render.render_p4_md(results["p4"]))
    (RESULTS_DIR / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("[ok ] RESULTS.md written")


def maybe_plot(results: dict) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:  # pragma: no cover
        print("[..] matplotlib unavailable; skipping plots")
        return

    if "p3" in results:
        p3 = results["p3"]
        bs = [c["budget"] for c in p3["curve"]]
        det = [c["detect_prob_plant"] for c in p3["curve"]]
        fp = [c["false_positive_empty"] for c in p3["curve"]]
        fig, ax = plt.subplots(figsize=(5.6, 3.6))
        ax.plot(bs, det, "o-", label="randomized detection (plant)")
        ax.plot(bs, fp, "s--", label="false positive (empty graph)")
        ax.axvline(p3["deterministic_lemma_lb"], color="red", ls=":",
                   label=r"det. lower bound $\binom{\lceil n/2\rceil}{2}$")
        ax.axvline(p3["deterministic_exact_D_n"], color="darkred", ls="-.",
                   label="det. exact $D(n)$")
        ax.set_xlabel("probe budget B")
        ax.set_ylabel("probability")
        ax.set_title(f"det $\\Theta(n^2)$ vs rand $O(n\\log n)$ (n={p3['n']})")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / "det_vs_rand.png", dpi=150)
        plt.close(fig)

    if "p4" in results:
        rows = results["p4"]["rows"]
        Ns = [r["N"] for r in rows]
        fig, ax = plt.subplots(figsize=(5.6, 3.6))
        ax.plot(Ns, [r["D_over_NlogN"] for r in rows], "o-",
                label=r"$D(N)/(N\log_2 N)$")
        ax.plot(Ns, [r["D_over_N1p5"] for r in rows], "s-",
                label=r"$D(N)/N^{1.5}$")
        ax.axhline(1.0, color="gray", ls=":")
        ax.set_xscale("log", base=2)
        ax.set_xlabel("implicit graph size N")
        ax.set_ylabel("forced det. cost / sublinear budget")
        ax.set_title("Cor. 3.7: no deterministic drop-in")
        ax.legend()
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / "barrier.png", dpi=150)
        plt.close(fig)
    print("[ok ] plots written (where applicable)")


if __name__ == "__main__":
    sys.exit(main())
