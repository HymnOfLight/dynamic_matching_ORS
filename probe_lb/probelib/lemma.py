"""Quantities and witnesses for the probe lower bound (plan Lemma 3.6).

* :func:`lemma_lower_bound` -- the clean threshold ``C(ceil(n/2), 2)`` that
  the plan proves: any deterministic algorithm distinguishing ``mu = 0`` from
  ``mu >= ceil(n/4)`` makes ``> C(ceil(n/2),2) - 1`` probes.

* :func:`det_complexity` -- the *exact* number of probes the all-zeros
  adversary forces, ``D(n) = min{ |P| : mu(K_n \\ P) < ceil(n/4) }``.  By the
  Erdos--Gallai matching theorem this equals
  ``C(n,2) - ex(n; nu <= ceil(n/4)-1)``, with an explicit extremal witness
  ``P`` whose complement we verify has the right matching number.

Both are ``Theta(n^2)``; ``D(n) >= lemma_lower_bound(n)`` always (the plan's
constant ``1/8`` is a clean but non-tight lower bound on the true ``D(n)``).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .matching import Edge, max_matching
from .model import gap_target


def lemma_lower_bound(n: int) -> int:
    """``C(ceil(n/2), 2)`` -- the plan's proven probe lower bound."""
    return math.comb(math.ceil(n / 2), 2)


def erdos_gallai_max_edges(n: int, k: int) -> tuple[int, str]:
    """Max edges of an ``n``-vertex graph with matching number ``nu <= k``
    (Erdos--Gallai 1959), and which extremal family attains it.

    ``ex(n; nu<=k) = max( C(2k+1, 2),  C(k,2) + k*(n-k) )``.
    """
    if k <= 0:
        return 0, "empty"
    clique = math.comb(2 * k + 1, 2) if 2 * k + 1 <= n else -1
    split = math.comb(k, 2) + k * (n - k)
    if clique >= split:
        return clique, "clique"
    return split, "split"


def _clique_graph(n: int, k: int) -> list[Edge]:
    """Clique on ``{0..2k}`` (matching number ``k``), rest isolated."""
    verts = list(range(min(2 * k + 1, n)))
    return [(u, v) for i, u in enumerate(verts) for v in verts[i + 1:]]


def _split_graph(n: int, k: int) -> list[Edge]:
    """``k`` dominating vertices ``{0..k-1}`` joined to everything
    (a clique on them plus all edges to the other ``n-k`` vertices);
    matching number ``k``."""
    dom = list(range(k))
    edges: list[Edge] = []
    for i, u in enumerate(dom):
        for v in dom[i + 1:]:
            edges.append((u, v))
        for v in range(k, n):
            edges.append((u, v))
    return edges


def det_value(n: int) -> dict:
    """Pure-formula deterministic complexity (no graph built, no matching DP).

    Safe for large ``n``; returns ``D(n)``, the Erdos--Gallai extremal edge
    count, and the clean lemma lower bound."""
    target = gap_target(n)
    k = target - 1
    max_edges, family = erdos_gallai_max_edges(n, k)
    return {
        "n": n, "target": target, "k": k, "max_kept_edges": max_edges,
        "value": math.comb(n, 2) - max_edges, "family": family,
        "lemma_lb": lemma_lower_bound(n),
    }


@dataclass
class DetComplexity:
    n: int
    target: int            # ceil(n/4): mu >= target is the YES side
    k: int                 # target - 1: the matching number the plant must stay <=
    max_kept_edges: int    # ex(n; nu <= k)
    value: int             # D(n) = C(n,2) - max_kept_edges
    family: str            # which extremal graph realises it
    lemma_lb: int          # C(ceil(n/2),2)
    witness_kept: list     # extremal kept graph (complement of the probe set)
    verified_mu: int       # mu of the kept graph, must equal k < target


def det_complexity(n: int) -> DetComplexity:
    target = gap_target(n)
    k = target - 1
    max_edges, family = erdos_gallai_max_edges(n, k)
    kept = _clique_graph(n, k) if family == "clique" else (
        _split_graph(n, k) if family == "split" else []
    )
    mu_kept = max_matching(n, kept)
    return DetComplexity(
        n=n, target=target, k=k, max_kept_edges=max_edges,
        value=math.comb(n, 2) - max_edges, family=family,
        lemma_lb=lemma_lower_bound(n),
        witness_kept=kept, verified_mu=mu_kept,
    )


def clique_in_probeset(n: int, probed: set[Edge]) -> int:
    """Largest clique size in the probe graph (small ``n`` only).

    The proof of Lemma 3.6 shows ``mu(K_n \\ P) < ceil(n/4)`` forces ``P`` to
    contain a clique on ``ceil(n/2)`` vertices.  This helper lets the tests
    confirm that direction directly."""
    adj = [set() for _ in range(n)]
    for (u, v) in probed:
        adj[u].add(v)
        adj[v].add(u)
    best = 0

    def extend(cand: list[int], cur: int) -> None:
        nonlocal best
        best = max(best, cur)
        for idx, w in enumerate(cand):
            newcand = [x for x in cand[idx + 1:] if x in adj[w]]
            extend(newcand, cur + 1)

    extend(list(range(n)), 0)
    return best
