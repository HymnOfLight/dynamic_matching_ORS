"""Method A: a dependency-free branch-and-bound decision solver.

``feasible(n, r, t, ordered)`` decides whether an (O)RS decomposition with
parameters ``(r, t)`` exists on ``n`` vertices, returning a witness when it
does.  It uses no third-party library and is therefore the backend that is
always available (CI, no-network) and the independent cross-check for the
SAT / CP-SAT encodings.

Symmetry breaking (both correctness-preserving)
-----------------------------------------------
* ``M_1`` is fixed to the canonical matching ``{(0,1),(2,3),...}``: every
  decomposition can be relabelled so its first matching is this one, and
  both the RS and ORS properties are invariant under vertex relabelling.
* For RS only, the colour classes are interchangeable, so we require the
  classes ``M_2, M_3, ...`` to have strictly increasing smallest edge.
  (Edge-disjointness makes the smallest edges distinct, so ordering by the
  smallest edge is a complete tie-free symmetry break.)  For ORS the order
  is semantic and no such constraint is imposed.

A step budget guards against blow-up; when it is exhausted the solver
returns :data:`UNKNOWN` instead of a wrong answer, and the high-level layer
falls back to an exact solver backend.
"""

from __future__ import annotations

from typing import Iterator, Optional

from .core import Decomposition, Edge, Matching

UNKNOWN = "unknown"


class _BudgetExceeded(Exception):
    pass


def canonical_matching(r: int) -> Matching:
    """The matching ``{(0,1),(2,3),...,(2r-2,2r-1)}``."""
    return [(2 * i, 2 * i + 1) for i in range(r)]


def _enumerate_matchings(
    n: int,
    r: int,
    allowed,
    first_edge_lb: Optional[Edge],
    counter: list[int],
    budget: int,
) -> Iterator[Matching]:
    """Yield every size-``r`` matching whose edges all satisfy ``allowed``.

    Edges are emitted with strictly increasing smaller endpoint, so each
    matching is produced exactly once.  ``first_edge_lb`` (if given) forces
    the lexicographically smallest edge to be ``>= first_edge_lb``.
    """
    chosen: Matching = []
    used: set[int] = set()

    def rec(start_u: int) -> Iterator[Matching]:
        counter[0] += 1
        if counter[0] > budget:
            raise _BudgetExceeded
        need = r - len(chosen)
        if need == 0:
            yield list(chosen)
            return
        # prune: not enough unused vertices left from start_u onwards
        free = sum(1 for w in range(start_u, n) if w not in used)
        if free < 2 * need:
            return
        for u in range(start_u, n):
            if u in used:
                continue
            for v in range(u + 1, n):
                if v in used:
                    continue
                e = (u, v)
                if first_edge_lb is not None and not chosen and e < first_edge_lb:
                    continue
                if not allowed(e):
                    continue
                chosen.append(e)
                used.add(u)
                used.add(v)
                yield from rec(u + 1)
                chosen.pop()
                used.discard(u)
                used.discard(v)

    yield from rec(0)


def _solve(n: int, r: int, t: int, ordered: bool, budget: int) -> Optional[Decomposition]:
    if t <= 0:
        return []
    if 2 * r > n or r <= 0:
        return None

    placed: Decomposition = [canonical_matching(r)]
    vsets: list[set[int]] = [set(range(2 * r))]
    used_edges: set[Edge] = set(placed[0])
    counter = [0]

    def search() -> Optional[Decomposition]:
        if len(placed) == t:
            return [list(m) for m in placed]
        # forward predicate: edge unused and not enclosed by any earlier V(M_i)
        def allowed(e: Edge) -> bool:
            if e in used_edges:
                return False
            u, v = e
            for Vi in vsets:
                if u in Vi and v in Vi:
                    return False
            return True

        # RS symmetry: classes >= index 2 have strictly increasing first edge
        lb: Optional[Edge] = None
        if not ordered and len(placed) >= 1:
            last_first = placed[-1][0] if placed[-1] else None
            # only enforce monotonicity among the searched (non-canonical) classes
            if len(placed) >= 1:
                lb = last_first

        for cand in _enumerate_matchings(n, r, allowed, lb, counter, budget):
            Vc = set()
            for (u, v) in cand:
                Vc.add(u)
                Vc.add(v)
            if not ordered:
                # RS back-check: no earlier edge may lie inside V(cand)
                bad = False
                for m in placed:
                    for (u, v) in m:
                        if u in Vc and v in Vc and (u, v) not in set(cand):
                            bad = True
                            break
                    if bad:
                        break
                if bad:
                    continue
            placed.append(cand)
            vsets.append(Vc)
            used_edges.update(cand)
            res = search()
            if res is not None:
                return res
            placed.pop()
            vsets.pop()
            for e in cand:
                used_edges.discard(e)
        return None

    return search()


def feasible(n: int, r: int, t: int, *, ordered: bool, budget: int = 2_000_000):
    """Return a witness ``Decomposition`` if feasible, ``None`` if infeasible,
    or :data:`UNKNOWN` if the step budget was exhausted."""
    try:
        res = _solve(n, r, t, ordered, budget)
    except _BudgetExceeded:
        return UNKNOWN
    return res


def value(n: int, r: int, *, ordered: bool, budget: int = 2_000_000):
    """Maximum ``t`` for the given ``(n, r)``; returns ``(value, witness)`` or
    ``(UNKNOWN, None)`` if the budget was exhausted before deciding."""
    if r <= 0 or 2 * r > n:
        return 0, []
    best = 0
    best_witness: Decomposition = []
    t = 1
    while True:
        res = feasible(n, r, t, ordered=ordered, budget=budget)
        if res is UNKNOWN:
            return UNKNOWN, None
        if res is None:
            return best, best_witness
        best = t
        best_witness = res
        t += 1
