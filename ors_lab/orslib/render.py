"""Render computed cells to LaTeX (booktabs) and Markdown tables."""

from __future__ import annotations

from .tables import Cell, Separation


def _val(cell: Cell) -> str:
    s = str(cell.value)
    if not cell.exact:
        s = f">={cell.value}"
    return s


def _index(cells: list[Cell]) -> dict:
    return {(c.n, c.r, c.ordered): c for c in cells}


# ----------------------------------------------------------------------
# grid: rows = n, for each r show "RS / ORS"
# ----------------------------------------------------------------------

def _grid_axes(cells: list[Cell]):
    ns = sorted({c.n for c in cells})
    rs = sorted({c.r for c in cells})
    return ns, rs


def render_grid_md(cells: list[Cell], title: str) -> str:
    idx = _index(cells)
    ns, rs = _grid_axes(cells)
    head = "| n \\\\ r | " + " | ".join(f"r={r}" for r in rs) + " |"
    sep = "|---" * (len(rs) + 1) + "|"
    lines = [f"### {title}", "", "Each cell is `RS_r(n) / ORS_r(n)`; `>=k` marks a "
             "verified lower bound (exact value not pinned within budget); "
             "**bold** marks an ordered-vs-unordered separation.", "", head, sep]
    for n in ns:
        row = [f"n={n}"]
        for r in rs:
            rsc = idx.get((n, r, False))
            orc = idx.get((n, r, True))
            if rsc is None or orc is None:
                row.append("--")
                continue
            cell = f"{_val(rsc)} / {_val(orc)}"
            if rsc.exact and orc.value > rsc.value:
                cell = f"**{cell}**"
            row.append(cell)
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def render_grid_tex(cells: list[Cell], caption: str, label: str) -> str:
    idx = _index(cells)
    ns, rs = _grid_axes(cells)
    cols = "l" + "c" * len(rs)
    out = [
        r"\begin{table}[t]\centering\small",
        r"\begin{tabular}{@{}" + cols + r"@{}}",
        r"\toprule",
        r"$n \backslash r$ & " + " & ".join(f"$r={r}$" for r in rs) + r" \\",
        r"\midrule",
    ]
    for n in ns:
        cells_row = [f"${n}$"]
        for r in rs:
            rsc = idx.get((n, r, False))
            orc = idx.get((n, r, True))
            if rsc is None or orc is None:
                cells_row.append(r"$\cdot$")
                continue
            a = _val(rsc).replace(">=", r"\ge ")
            b = _val(orc).replace(">=", r"\ge ")
            txt = f"${a}/{b}$"
            if rsc.exact and orc.value > rsc.value:
                txt = r"$\mathbf{" + f"{a}/{b}" + r"}$"
            cells_row.append(txt)
        out.append(" & ".join(cells_row) + r" \\")
    out += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\caption{" + caption + r"}",
        r"\label{" + label + r"}",
        r"\end{table}",
    ]
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------------
# separations
# ----------------------------------------------------------------------

def render_separations_md(seps: list[Separation]) -> str:
    lines = ["### Ordered-vs-unordered separations  `ORS_r(n) > RS_r(n)`", ""]
    if not seps:
        lines.append("None found in the searched range.")
        return "\n".join(lines) + "\n"
    lines += [
        "| n | r | RS_r(n) | ORS_r(n) | gap | status | ORS witness breaks RS? |",
        "|---|---|---|---|---|---|---|",
    ]
    for s in seps:
        rsv = str(s.rs_value)
        orv = str(s.ors_value) if s.ors_exact else f">={s.ors_value}"
        lines.append(
            f"| {s.n} | {s.r} | {rsv} | {orv} | {s.gap} | {s.status} | "
            f"{'yes' if s.ors_witness_breaks_rs else 'no'} |"
        )
    return "\n".join(lines) + "\n"


def render_separations_tex(seps: list[Separation], caption: str, label: str) -> str:
    out = [
        r"\begin{table}[t]\centering\small",
        r"\begin{tabular}{@{}cccccl@{}}",
        r"\toprule",
        r"$n$ & $r$ & $\RS_r(n)$ & $\ORS_r(n)$ & gap & status \\",
        r"\midrule",
    ]
    if not seps:
        out.append(r"\multicolumn{6}{c}{none in searched range} \\")
    for s in seps:
        orv = str(s.ors_value) if s.ors_exact else r"\ge " + str(s.ors_value)
        status = s.status.replace("_", "-")
        out.append(
            f"${s.n}$ & ${s.r}$ & ${s.rs_value}$ & ${orv}$ & ${s.gap}$ & "
            f"\\textsf{{{status}}} \\\\"
        )
    out += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\caption{" + caption + r"}",
        r"\label{" + label + r"}",
        r"\end{table}",
    ]
    return "\n".join(out) + "\n"


def render_witness_tex(n: int, r: int, witness, ordered: bool) -> str:
    name = r"\ORS" if ordered else r"\RS"
    lines = [f"% extremal {name}_{{{r}}}({n}) witness"]
    for i, m in enumerate(witness, 1):
        edges = ",\\ ".join(f"\\{{{u},{v}\\}}" for (u, v) in m)
        lines.append(f"$M_{{{i}}} = \\{{{edges}\\}}$\\\\")
    return "\n".join(lines) + "\n"
