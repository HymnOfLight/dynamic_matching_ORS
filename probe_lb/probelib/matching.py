"""Exact maximum matching for small graphs.

The probe-lower-bound arguments need the maximum matching size ``mu(G)`` of
graphs ``G = K_n \\ P`` repeatedly as the probe set ``P`` grows.  We use an
exact bitmask DP, ``O(n * 2^n)``, which is comfortable for the ``n <= ~20``
regime of this package.  ``tests.py`` cross-validates it against a
brute-force matching enumerator on tiny graphs (no shared code path).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable

Edge = tuple[int, int]


def adjmasks(n: int, edges: Iterable[Edge]) -> list[int]:
    """Per-vertex neighbour bitmasks."""
    adj = [0] * n
    for (u, v) in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def max_matching_from_adj(n: int, adj: list[int]) -> int:
    """Maximum matching size via subset DP.

    ``f[S]`` = max matching within the induced subgraph on vertex set ``S``.
    Processing ``S`` in increasing integer order is valid because every term
    on the right removes bits (a strictly smaller integer).
    """
    size = 1 << n
    f = [0] * size
    for S in range(1, size):
        i = (S & -S).bit_length() - 1  # lowest set vertex
        rest = S ^ (1 << i)
        best = f[rest]  # leave i unmatched
        nbrs = adj[i] & rest
        m = nbrs
        while m:
            j = (m & -m).bit_length() - 1
            cand = 1 + f[rest ^ (1 << j)]
            if cand > best:
                best = cand
            m &= m - 1
        f[S] = best
    return f[size - 1]


def max_matching(n: int, edges: Iterable[Edge]) -> int:
    return max_matching_from_adj(n, adjmasks(n, list(edges)))


def complete_minus(n: int, removed: set[Edge]) -> list[Edge]:
    """Edges of ``K_n \\ removed`` (edges given as ``(u, v)`` with ``u < v``)."""
    out: list[Edge] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in removed:
                out.append((u, v))
    return out


def mu_complete_minus(n: int, removed: set[Edge]) -> int:
    """``mu(K_n \\ removed)`` without materialising all edges."""
    adj = [((1 << n) - 1) ^ (1 << i) for i in range(n)]  # K_n adjacency
    for (u, v) in removed:
        adj[u] &= ~(1 << v)
        adj[v] &= ~(1 << u)
    return max_matching_from_adj(n, adj)


def brute_max_matching(n: int, edges: Iterable[Edge]) -> int:
    """Reference matching number by recursive enumeration (tests only)."""
    elist = list(edges)

    @lru_cache(maxsize=None)
    def rec(used: int, start: int) -> int:
        best = 0
        for k in range(start, len(elist)):
            u, v = elist[k]
            bit = (1 << u) | (1 << v)
            if used & bit:
                continue
            best = max(best, 1 + rec(used | bit, k + 1))
        return best

    return rec(0, 0)
