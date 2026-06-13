"""Core definitions for ordered / classical Ruzsa--Szemeredi graphs.

This module is the *trust anchor* of ``ors_lab``: it fixes the exact
combinatorial definitions used everywhere else and provides a single,
deliberately naive, **independent** certificate verifier.  Every value
that any solver backend (search / SAT / CP-SAT) produces is accepted only
after its witness passes :func:`verify_decomposition`, which shares no
code path with the solvers.

Definitions (matching plan Def. 2.3 = Behnezhad--Ghafari 2024)
--------------------------------------------------------------
Let ``M_1, ..., M_t`` be pairwise edge-disjoint matchings on ``[n]``,
each of size exactly ``r``, and let ``G = M_1 cup ... cup M_t`` be their
union.  Write ``V(M_i)`` for the set of vertices saturated by ``M_i``.

* ``M_1, ..., M_t`` is an **RS decomposition** (parameters ``(r, t)``) if
  every ``M_i`` is an *induced* matching of ``G``: no edge of ``G`` has
  both endpoints in ``V(M_i)`` other than the edges of ``M_i`` itself.
  Equivalently, for all ``i != j`` no edge of ``M_j`` lies inside
  ``V(M_i)``.

* The same sequence is an **ORS decomposition** if every ``M_i`` is
  induced in the *suffix* union ``M_i cup M_{i+1} cup ... cup M_t``:
  for all ``j > i`` no edge of ``M_j`` lies inside ``V(M_i)``.  Edges of
  *earlier* matchings are allowed to lie inside ``V(M_i)``.

The maxima over all graphs / orderings are
``RS_r(n) = max t`` (RS) and ``ORS_r(n) = max t`` (ORS).  Every RS
decomposition is an ORS decomposition under any order, so
``ORS_r(n) >= RS_r(n)`` always.

Representation
--------------
A decomposition is a ``list`` of matchings; a matching is a ``list`` of
edges ``(u, v)`` with ``u < v``.  The list order *is* the ORS order.
"""

from __future__ import annotations

from dataclasses import dataclass

Edge = tuple[int, int]
Matching = list[Edge]
Decomposition = list[Matching]


def norm_edge(u: int, v: int) -> Edge:
    """Return the edge ``(u, v)`` in canonical ``u < v`` orientation."""
    return (u, v) if u < v else (v, u)


def saturated_vertices(matching: Matching) -> set[int]:
    """Vertex set ``V(M)`` saturated by ``matching``."""
    vs: set[int] = set()
    for u, v in matching:
        vs.add(u)
        vs.add(v)
    return vs


@dataclass(frozen=True)
class VerificationResult:
    ok: bool
    reason: str = ""

    def __bool__(self) -> bool:  # allow ``if verify(...):``
        return self.ok


def verify_decomposition(
    n: int,
    r: int,
    decomposition: Decomposition,
    *,
    ordered: bool,
) -> VerificationResult:
    """Independently verify an (O)RS decomposition.

    Checks, in order: vertex range and ``u < v`` orientation; each ``M_i``
    is a matching of size exactly ``r``; pairwise edge-disjointness; and
    the (ordered) induced-matching condition.  Runs in ``O(t^2 r)`` time,
    which is ``O(t * n^2)`` since ``t*r <= binom(n,2)``.

    This routine never trusts a solver: it recomputes ``V(M_i)`` and the
    forbidden-pair condition from scratch.
    """
    t = len(decomposition)

    # 1. structural validity of each matching
    seen_edges: dict[Edge, int] = {}
    for i, m in enumerate(decomposition):
        if len(m) != r:
            return VerificationResult(False, f"M_{i} has size {len(m)} != r={r}")
        touched: set[int] = set()
        for (u, v) in m:
            if not (0 <= u < n and 0 <= v < n):
                return VerificationResult(False, f"M_{i} edge ({u},{v}) out of [0,{n})")
            if u >= v:
                return VerificationResult(False, f"M_{i} edge ({u},{v}) not oriented u<v")
            if u in touched or v in touched:
                return VerificationResult(False, f"M_{i} is not a matching at ({u},{v})")
            touched.add(u)
            touched.add(v)
            # 2. pairwise edge-disjointness across the whole decomposition
            if (u, v) in seen_edges:
                return VerificationResult(
                    False, f"edge ({u},{v}) shared by M_{seen_edges[(u, v)]} and M_{i}"
                )
            seen_edges[(u, v)] = i

    # 3. induced condition
    vsets = [saturated_vertices(m) for m in decomposition]
    for i in range(t):
        Vi = vsets[i]
        own = {(u, v) for (u, v) in decomposition[i]}
        # which other classes must avoid lying inside V(M_i)?
        others = range(i + 1, t) if ordered else range(t)
        for j in others:
            if j == i:
                continue
            for (u, v) in decomposition[j]:
                if u in Vi and v in Vi and (u, v) not in own:
                    kind = "ORS (suffix)" if ordered else "RS"
                    return VerificationResult(
                        False,
                        f"{kind} induced condition violated: edge ({u},{v}) of "
                        f"M_{j} lies inside V(M_{i})",
                    )
    return VerificationResult(True, "ok")


def union_graph_edges(decomposition: Decomposition) -> set[Edge]:
    """Edge set of ``G = union of all matchings``."""
    out: set[Edge] = set()
    for m in decomposition:
        out.update(m)
    return out


def max_r(n: int) -> int:
    """Largest matching size on ``n`` vertices, ``floor(n/2)``."""
    return n // 2
