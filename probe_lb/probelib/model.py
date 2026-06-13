"""The adjacency-matrix probe model and the all-zeros adversary.

Model (plan Def. 3.5)
---------------------
An algorithm accesses an unknown graph ``G`` on ``[n]`` only through probes
``Adj(u, v) in {0, 1}``, chosen adaptively; the cost is the number of
*distinct* pairs probed.

The gap task (plan Lemma 3.6): distinguish ``mu(G) = 0`` from
``mu(G) >= ceil(n/4)``.

All-zeros adversary
-------------------
Answer ``0`` to every probe.  After a deterministic algorithm has probed the
set ``P`` of pairs, *both* the empty graph ``G0`` (``mu = 0``) and the graph
``H = K_n \\ P`` are consistent with the all-zeros transcript.  The algorithm
can only safely answer ``mu = 0`` once ``H`` no longer has a large matching,
i.e. once ``mu(K_n \\ P) < ceil(n/4)``.  Until then the *plant* ``H`` fools
it.  This module provides exactly those primitives.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .matching import Edge, mu_complete_minus


def gap_target(n: int) -> int:
    """The ``mu >= ceil(n/4)`` side of the gap."""
    return math.ceil(n / 4)


@dataclass
class ProbeOracle:
    """Counts distinct adjacency-matrix probes against a fixed hidden graph."""

    n: int
    edges: set[Edge] = field(default_factory=set)
    _probed: set[Edge] = field(default_factory=set, init=False)

    def probe(self, u: int, v: int) -> int:
        e = (u, v) if u < v else (v, u)
        self._probed.add(e)
        return 1 if e in self.edges else 0

    @property
    def cost(self) -> int:
        return len(self._probed)


@dataclass
class AllZerosAdversary:
    """The lemma's adversary: every probe answered 0; a plant is exposed
    whenever the all-zeros transcript still admits a large matching."""

    n: int

    def answer(self, u: int, v: int) -> int:  # noqa: D401 - always 0
        return 0

    def plant_exists(self, probed: set[Edge]) -> bool:
        """Is some graph with ``mu >= ceil(n/4)`` still consistent with the
        all-zeros answers on ``probed``?  Equivalent to
        ``mu(K_n \\ probed) >= ceil(n/4)``."""
        return mu_complete_minus(self.n, probed) >= gap_target(self.n)

    def plant_matching_value(self, probed: set[Edge]) -> int:
        """``mu(K_n \\ probed)`` -- the size of the matching the plant hides."""
        return mu_complete_minus(self.n, probed)


def consistent_after(n: int, probed: set[Edge]) -> tuple[bool, int]:
    """Return ``(both_consistent, mu_of_plant)``.

    ``both_consistent`` is True iff the all-zeros transcript on ``probed``
    is consistent with both a ``mu = 0`` graph (always, the empty graph) and
    a ``mu >= ceil(n/4)`` graph (the plant), so a deterministic algorithm
    cannot yet decide."""
    mu = mu_complete_minus(n, probed)
    return mu >= gap_target(n), mu
