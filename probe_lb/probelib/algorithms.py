"""Probe algorithms: deterministic orderings vs the randomized sampler.

Deterministic algorithms are modelled as a (fixed, input-independent) order
in which pairs are probed -- which is exactly what a deterministic algorithm
reduces to against the all-zeros adversary, whose answers carry no
information.  :func:`run_all_zeros` reports the first probe count at which the
order can correctly certify ``mu < ceil(n/4)`` (i.e. the plant disappears).

The randomized sampler is the lemma's ``O(n log n)`` upper-bound algorithm:
probe uniform random pairs until one is an edge.
"""

from __future__ import annotations

import itertools
import math
import random
from dataclasses import dataclass

from .matching import Edge, mu_complete_minus
from .model import gap_target


def all_pairs(n: int) -> list[Edge]:
    return list(itertools.combinations(range(n), 2))


# --------------------------------------------------------------------------
# deterministic probe orderings
# --------------------------------------------------------------------------

def order_row_major(n: int) -> list[Edge]:
    return all_pairs(n)


def order_diagonal(n: int) -> list[Edge]:
    """Probe by increasing gap ``v - u`` (a natural non-row-major schedule)."""
    return sorted(all_pairs(n), key=lambda e: (e[1] - e[0], e))


def order_pseudo_random(n: int, seed: int = 20260613) -> list[Edge]:
    ps = all_pairs(n)
    random.Random(seed).shuffle(ps)
    return ps


def order_clique_first(n: int) -> list[Edge]:
    """Probe all pairs inside the first ``ceil(n/2)`` vertices first.

    This is the structure the lemma says a correct algorithm is *forced* to
    cover; it is a natural attempt to be efficient, and the simulation shows
    even this does not beat ``C(ceil(n/2),2)`` probes."""
    half = math.ceil(n / 2)
    inside = [(u, v) for u, v in all_pairs(n) if u < half and v < half]
    outside = [e for e in all_pairs(n) if e not in set(inside)]
    return inside + outside


def order_witness(n: int, witness_kept: list[Edge]) -> list[Edge]:
    """Probe the optimal witness probe-set first (the complement of the
    extremal kept graph), i.e. the order achieving the exact ``D(n)``."""
    kept = set(witness_kept)
    probe_first = [e for e in all_pairs(n) if e not in kept]
    rest = [e for e in all_pairs(n) if e in kept]
    return probe_first + rest


@dataclass
class RunResult:
    n: int
    order_name: str
    probes_to_certify: int     # first k with mu(K_n \ P_k) < ceil(n/4)
    total_pairs: int
    plant_alive_until: int     # = probes_to_certify - 1
    fooled_if_stop_early: bool


def run_all_zeros(n: int, order: list[Edge], order_name: str = "") -> RunResult:
    target = gap_target(n)
    probed: set[Edge] = set()
    k_certify = len(order)
    for k, e in enumerate(order, start=1):
        probed.add(e)
        if mu_complete_minus(n, probed) < target:
            k_certify = k
            break
    return RunResult(
        n=n, order_name=order_name, probes_to_certify=k_certify,
        total_pairs=math.comb(n, 2), plant_alive_until=k_certify - 1,
        fooled_if_stop_early=True,
    )


# --------------------------------------------------------------------------
# randomized sampler (lemma's O(n log n) upper bound)
# --------------------------------------------------------------------------

def sparse_plant(n: int, rng: random.Random) -> set[Edge]:
    """A random matching of size ``ceil(n/4)`` -- the hard instance for the
    randomized side (few edges among ``C(n,2)`` pairs)."""
    target = gap_target(n)
    verts = list(range(n))
    rng.shuffle(verts)
    edges: set[Edge] = set()
    for i in range(target):
        u, v = verts[2 * i], verts[2 * i + 1]
        edges.add((u, v) if u < v else (v, u))
    return edges


def randomized_detect(n: int, edges: set[Edge], budget: int, rng: random.Random) -> bool:
    """Probe ``budget`` uniform random pairs; report whether an edge was hit."""
    pairs = all_pairs(n)
    for _ in range(budget):
        u, v = rng.choice(pairs)
        if (u, v) in edges:
            return True
    return False


def detection_probability(
    n: int, edges: set[Edge], budget: int, trials: int, rng: random.Random
) -> float:
    hits = sum(randomized_detect(n, edges, budget, rng) for _ in range(trials))
    return hits / trials
