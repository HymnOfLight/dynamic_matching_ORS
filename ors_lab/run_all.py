"""ors_lab orchestrator (Task B1).

Usage
-----
    python3 run_all.py --scale quick     # CI-sized, ~seconds
    python3 run_all.py --scale full      # report run, ~1-3 min
    python3 run_all.py --only grid       # subset: grid | extremal | separations

Outputs (under ``results/``)
    grid.json, extremal.json, separations.json   raw verified cells
    grid_table.{tex,md}                           exact (O)RS grid
    extremal_table.{tex,md}                       near-n/2 regime
    separations.{tex,md}                          ORS>RS findings + witnesses
    witnesses.tex                                 separation witnesses (LaTeX)
    RESULTS.md                                    human-readable summary
    ors_rs_r2.png                                 RS vs ORS in the r=2 regime
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

from orslib import render, tables
from orslib.solve import available_backends

RESULTS_DIR = pathlib.Path(__file__).parent / "results"

SCALES = {
    "quick": dict(grid_n=7, extremal_n=7, sep_n=7),
    "full": dict(grid_n=9, extremal_n=20, sep_n=9),
}


def _dump(name: str, obj) -> None:
    (RESULTS_DIR / f"{name}.json").write_text(json.dumps(obj, indent=2))


def build_grid(n_max: int) -> list[tables.Cell]:
    print(f"[run] grid up to n={n_max} ...", flush=True)
    cells = tables.grid_table(n_max=n_max, r_min=2)
    _dump("grid", [c.to_json() for c in cells])
    return cells


def build_extremal(n_max: int) -> list[tables.Cell]:
    print(f"[run] extremal (near-n/2) up to n={n_max} ...", flush=True)
    cells = tables.extremal_table(n_max=n_max, n_min=6, j_max=2)
    _dump("extremal", [c.to_json() for c in cells])
    return cells


def build_separations(n_max: int) -> list[tables.Separation]:
    print(f"[run] separation search up to n={n_max} ...", flush=True)
    seps = tables.separation_search(n_max=n_max, r_min=2)
    _dump("separations", [s.__dict__ for s in seps])
    return seps


def write_outputs(grid, extremal, seps) -> None:
    if grid:
        (RESULTS_DIR / "grid_table.tex").write_text(
            render.render_grid_tex(
                grid, "Exact $\\RS_r(n)$ / $\\ORS_r(n)$ (bold: a separation; "
                "$\\ge$: verified lower bound).", "tab:grid")
        )
        (RESULTS_DIR / "grid_table.md").write_text(
            render.render_grid_md(grid, "Exact RS / ORS grid")
        )
    if extremal:
        (RESULTS_DIR / "extremal_table.tex").write_text(
            render.render_grid_tex(
                extremal, "The near-$n/2$ (linear matching size) regime "
                "$r=\\lfloor n/2\\rfloor-j$.", "tab:extremal")
        )
        (RESULTS_DIR / "extremal_table.md").write_text(
            render.render_grid_md(extremal, "Near-n/2 regime")
        )
    (RESULTS_DIR / "separations.tex").write_text(
        render.render_separations_tex(
            seps, "Small-$n$ ordered-vs-unordered separations found by "
            "exhaustive search.", "tab:sep")
    )
    (RESULTS_DIR / "separations.md").write_text(render.render_separations_md(seps))

    wlines = ["% Witnesses for the proven separations (auto-generated)."]
    for s in seps:
        if s.status == "proven" and s.ors_witness:
            wlines.append(f"\\paragraph{{$\\ORS_{{{s.r}}}({s.n})={s.ors_value}>"
                          f"\\RS_{{{s.r}}}({s.n})={s.rs_value}$.}}")
            wlines.append(render.render_witness_tex(s.n, s.r, s.ors_witness, True))
    (RESULTS_DIR / "witnesses.tex").write_text("\n".join(wlines) + "\n")
    print("[ok ] tables, separations, witnesses written")


def write_summary(grid, extremal, seps, scale: str, elapsed: float) -> None:
    lines = [
        "# ors_lab run summary (Task B1)",
        "",
        f"Scale `{scale}`; backends `{available_backends()}`; "
        f"elapsed {elapsed:.1f}s.",
        "",
        "Every value below is produced by CP-SAT and (for n<=8) independently "
        "by a CNF/SAT encoding and a dependency-free branch-and-bound search; "
        "every witness is checked by `orslib.core.verify_decomposition`, which "
        "shares no code with the solvers.",
        "",
    ]
    if grid:
        n_exact = sum(1 for c in grid if c.exact)
        lines += [f"- grid: {len(grid)} cells, {n_exact} exact, "
                  f"{len(grid)-n_exact} verified lower bounds.", ""]
        lines.append(render.render_grid_md(grid, "Exact RS / ORS grid"))
    if extremal:
        lines.append(render.render_grid_md(extremal, "Near-n/2 regime"))
    lines.append(render.render_separations_md(seps))
    if seps:
        lines += ["", "## Separation witnesses (verified)", ""]
        for s in seps:
            if s.status == "proven" and s.ors_witness:
                lines.append(
                    f"- `ORS_{s.r}({s.n})={s.ors_value} > RS_{s.r}({s.n})="
                    f"{s.rs_value}`; ordered decomposition "
                    f"(checked ordered-only): `{s.ors_witness}`")
    (RESULTS_DIR / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("[ok ] RESULTS.md written")


def maybe_plot(grid) -> None:
    if not grid:
        return
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:  # pragma: no cover
        print("[..] matplotlib unavailable; skipping plot")
        return
    r0 = 2
    pts = {}
    for c in grid:
        if c.r == r0:
            pts.setdefault(c.ordered, []).append((c.n, c.value, c.exact))
    if not pts:
        return
    fig, ax = plt.subplots(figsize=(5.4, 3.6))
    for ordered, marker, lbl in [(False, "o", "RS"), (True, "s", "ORS")]:
        data = sorted(pts.get(ordered, []))
        ns = [d[0] for d in data]
        vs = [d[1] for d in data]
        ax.plot(ns, vs, marker + "-", label=f"${lbl}_2(n)$")
        lb = [(d[0], d[1]) for d in data if not d[2]]
        if lb:
            ax.scatter([d[0] for d in lb], [d[1] for d in lb],
                       marker="^", s=80, facecolors="none",
                       edgecolors="red", label=f"{lbl} lower bound")
    ax.set_xlabel("n")
    ax.set_ylabel(r"max # induced matchings of size $2$")
    ax.set_title("ors_lab: RS vs ORS in the $r=2$ regime")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "ors_rs_r2.png", dpi=150)
    plt.close(fig)
    print("[ok ] ors_rs_r2.png written")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scale", choices=list(SCALES), default="quick")
    p.add_argument("--only", nargs="*",
                   choices=["grid", "extremal", "separations"],
                   default=["grid", "extremal", "separations"])
    args = p.parse_args(argv)
    cfg = SCALES[args.scale]
    RESULTS_DIR.mkdir(exist_ok=True)

    t0 = time.perf_counter()
    grid = build_grid(cfg["grid_n"]) if "grid" in args.only else []
    extremal = build_extremal(cfg["extremal_n"]) if "extremal" in args.only else []
    seps = build_separations(cfg["sep_n"]) if "separations" in args.only else []
    elapsed = time.perf_counter() - t0

    write_outputs(grid, extremal, seps)
    write_summary(grid, extremal, seps, args.scale, elapsed)
    maybe_plot(grid)
    print(f"[done] {elapsed:.1f}s; see results/RESULTS.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
