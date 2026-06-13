"""Method C: an OR-Tools CP-SAT encoding.

Independent of both :mod:`orslib.search` (branch-and-bound) and
:mod:`orslib.sat_encode` (CNF).  CP-SAT can also *maximise* ``t`` directly,
which :func:`max_value` exposes as an extra cross-check on the decision
loop.
"""

from __future__ import annotations

import itertools
from typing import Optional

from .core import Decomposition, Edge
from .search import UNKNOWN, canonical_matching

try:  # pragma: no cover - import guard
    from ortools.sat.python import cp_model

    HAVE_ORTOOLS = True
except Exception:  # pragma: no cover
    HAVE_ORTOOLS = False


def available() -> bool:
    return HAVE_ORTOOLS


def _all_pairs(n: int) -> list[Edge]:
    return list(itertools.combinations(range(n), 2))


def _build(model, n: int, r: int, t: int, ordered: bool):
    pairs = _all_pairs(n)
    colors = list(range(1, t + 1))
    incident: dict[int, list[Edge]] = {w: [] for w in range(n)}
    for (u, v) in pairs:
        incident[u].append((u, v))
        incident[v].append((u, v))

    x = {(p, i): model.NewBoolVar(f"x_{p}_{i}") for p in pairs for i in colors}
    y = {(w, i): model.NewBoolVar(f"y_{w}_{i}") for w in range(n) for i in colors}

    # at most one colour per pair
    for p in pairs:
        model.AddAtMostOne(x[(p, i)] for i in colors)

    # each colour is a matching + exactly r edges
    for i in colors:
        for w in range(n):
            model.AddAtMostOne(x[(p, i)] for p in incident[w])
        model.Add(sum(x[(p, i)] for p in pairs) == r)

    # y[w,i] <-> OR incident x
    for i in colors:
        for w in range(n):
            inc = [x[(p, i)] for p in incident[w]]
            for lit in inc:
                model.AddImplication(lit, y[(w, i)])
            model.AddBoolOr(inc + [y[(w, i)].Not()])

    # induced condition
    for i in colors:
        others = [j for j in colors if (j > i if ordered else j != i)]
        for j in others:
            for (u, v) in pairs:
                model.AddBoolOr(
                    [x[((u, v), j)].Not(), y[(u, i)].Not(), y[(v, i)].Not()]
                )

    # symmetry break: M_1 = canonical
    canon = set(canonical_matching(r))
    for p in pairs:
        if p in canon:
            model.Add(x[(p, 1)] == 1)

    return x, pairs, colors


def feasible(n: int, r: int, t: int, *, ordered: bool, max_time_s: float = 30.0):
    if not HAVE_ORTOOLS:
        return UNKNOWN
    if t <= 0:
        return []
    if r <= 0 or 2 * r > n:
        return None

    model = cp_model.CpModel()
    x, pairs, colors = _build(model, n, r, t, ordered)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time_s
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        decomposition: Decomposition = []
        for i in colors:
            m = [p for p in pairs if solver.Value(x[(p, i)]) == 1]
            decomposition.append(sorted(m))
        return decomposition
    if status == cp_model.INFEASIBLE:
        return None
    return UNKNOWN


def max_value(n: int, r: int, *, ordered: bool, t_hi: int, max_time_s: float = 60.0):
    """Maximise ``t`` directly with one CP-SAT objective, capped at ``t_hi``.

    Returns ``(value, witness)`` or ``(UNKNOWN, None)``.  Models the choice of
    how many colours to *use* via per-colour activation variables.
    """
    if not HAVE_ORTOOLS:
        return UNKNOWN, None
    if r <= 0 or 2 * r > n:
        return 0, []

    model = cp_model.CpModel()
    pairs = _all_pairs(n)
    colors = list(range(1, t_hi + 1))
    incident: dict[int, list[Edge]] = {w: [] for w in range(n)}
    for (u, v) in pairs:
        incident[u].append((u, v))
        incident[v].append((u, v))

    x = {(p, i): model.NewBoolVar(f"x_{p}_{i}") for p in pairs for i in colors}
    y = {(w, i): model.NewBoolVar(f"y_{w}_{i}") for w in range(n) for i in colors}
    used = {i: model.NewBoolVar(f"used_{i}") for i in colors}

    for p in pairs:
        model.AddAtMostOne(x[(p, i)] for i in colors)
    for i in colors:
        for w in range(n):
            model.AddAtMostOne(x[(p, i)] for p in incident[w])
        # colour i has exactly r edges iff used, else 0
        model.Add(sum(x[(p, i)] for p in pairs) == r).OnlyEnforceIf(used[i])
        model.Add(sum(x[(p, i)] for p in pairs) == 0).OnlyEnforceIf(used[i].Not())
        for w in range(n):
            inc = [x[(p, i)] for p in incident[w]]
            for lit in inc:
                model.AddImplication(lit, y[(w, i)])
            model.AddBoolOr(inc + [y[(w, i)].Not()])
    # contiguous / ordered usage: used colours come first
    for i in colors[:-1]:
        model.AddImplication(used[i + 1], used[i])

    for i in colors:
        others = [j for j in colors if (j > i if ordered else j != i)]
        for j in others:
            for (u, v) in pairs:
                model.AddBoolOr(
                    [x[((u, v), j)].Not(), y[(u, i)].Not(), y[(v, i)].Not()]
                )

    canon = set(canonical_matching(r))
    for p in pairs:
        if p in canon:
            model.Add(x[(p, 1)] == 1)

    model.Maximize(sum(used[i] for i in colors))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time_s
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)
    if status != cp_model.OPTIMAL:
        return UNKNOWN, None
    val = int(round(solver.ObjectiveValue()))
    decomposition: Decomposition = []
    for i in colors:
        if solver.Value(used[i]) == 1:
            decomposition.append(sorted(p for p in pairs if solver.Value(x[(p, i)]) == 1))
    return val, decomposition
