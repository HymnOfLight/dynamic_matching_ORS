"""Method B: a CNF/SAT encoding solved by PySAT.

The decision ``feasible(n, r, t, ordered)`` is encoded directly in CNF and
handed to a CDCL solver (Glucose 3 by default).  This is an *independent*
formulation from the branch-and-bound search of :mod:`orslib.search` and
from the CP-SAT model of :mod:`orslib.cpsat_encode`; the three are
cross-validated against each other in ``tests.py``.

Variables
---------
* ``x[p, i]`` -- pair ``p`` (an unordered vertex pair) is an edge of colour
  ``i in {1..t}``;
* ``y[w, i]`` -- vertex ``w`` is saturated by colour ``i`` (``<->`` OR of
  the incident ``x[*, i]``).

Clauses: at-most-one colour per pair; each colour is a matching (at-most-one
incident edge per vertex); each colour has exactly ``r`` edges (PySAT
cardinality network); the ``y`` definition (both directions); and the
induced condition ``x[p,j] -> not (y[u,i] and y[v,i])`` for ``j != i`` (RS)
or ``j > i`` (ORS), where ``p = {u, v}``.  ``M_1`` is pinned to the
canonical matching as a symmetry break.
"""

from __future__ import annotations

import itertools
from typing import Optional

from .core import Decomposition, Edge
from .search import UNKNOWN, canonical_matching

try:  # pragma: no cover - import guard
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool
    from pysat.solvers import Solver

    HAVE_PYSAT = True
except Exception:  # pragma: no cover
    HAVE_PYSAT = False


def available() -> bool:
    return HAVE_PYSAT


def _all_pairs(n: int) -> list[Edge]:
    return list(itertools.combinations(range(n), 2))


def feasible(
    n: int,
    r: int,
    t: int,
    *,
    ordered: bool,
    solver_name: str = "g3",
    conf_budget: Optional[int] = None,
):
    """Return a witness ``Decomposition``, ``None`` (infeasible), or
    :data:`UNKNOWN` if PySAT is unavailable or the optional ``conf_budget``
    (max CDCL conflicts) is exhausted before a decision."""
    if not HAVE_PYSAT:
        return UNKNOWN
    if t <= 0:
        return []
    if r <= 0 or 2 * r > n:
        return None

    pairs = _all_pairs(n)
    colors = list(range(1, t + 1))
    vpool = IDPool()

    def xv(p: Edge, i: int) -> int:
        return vpool.id(("x", p, i))

    def yv(w: int, i: int) -> int:
        return vpool.id(("y", w, i))

    clauses: list[list[int]] = []

    incident: dict[int, list[Edge]] = {w: [] for w in range(n)}
    for (u, v) in pairs:
        incident[u].append((u, v))
        incident[v].append((u, v))

    # (1) at most one colour per pair
    for p in pairs:
        lits = [xv(p, i) for i in colors]
        for a in range(len(lits)):
            for b in range(a + 1, len(lits)):
                clauses.append([-lits[a], -lits[b]])

    # (2) each colour is a matching: per vertex, per colour, at most one edge
    for i in colors:
        for w in range(n):
            lits = [xv(p, i) for p in incident[w]]
            for a in range(len(lits)):
                for b in range(a + 1, len(lits)):
                    clauses.append([-lits[a], -lits[b]])

    # (3) y definition: y[w,i] <-> OR_{p incident w} x[p,i]
    for i in colors:
        for w in range(n):
            inc = [xv(p, i) for p in incident[w]]
            yw = yv(w, i)
            for lit in inc:  # x -> y
                clauses.append([-lit, yw])
            clauses.append([-yw] + inc)  # y -> OR x

    # (4) exactly r edges per colour (cardinality network over the pool)
    for i in colors:
        lits = [xv(p, i) for p in pairs]
        enc = CardEnc.equals(lits=lits, bound=r, vpool=vpool, encoding=EncType.seqcounter)
        clauses.extend(enc.clauses)

    # (5) induced condition
    for i in colors:
        others = [j for j in colors if (j > i if ordered else j != i)]
        for j in others:
            for (u, v) in pairs:
                clauses.append([-xv((u, v), j), -yv(u, i), -yv(v, i)])

    # (6) symmetry break: M_1 = canonical matching
    canon = set(canonical_matching(r))
    for p in pairs:
        if p in canon:
            clauses.append([xv(p, 1)])

    with Solver(name=solver_name, bootstrap_with=clauses, use_timer=False) as solver:
        if conf_budget is not None:
            solver.conf_budget(conf_budget)
            verdict = solver.solve_limited(expect_interrupt=False)
        else:
            verdict = solver.solve()
        if verdict is None:  # budget exhausted, undecided
            return UNKNOWN
        if not verdict:
            return None
        model = set(l for l in solver.get_model() if l > 0)

    decomposition: Decomposition = []
    for i in colors:
        m = [p for p in pairs if xv(p, i) in model]
        decomposition.append(sorted(m))
    return decomposition
