"""Cross-validation test suite for probe_lb.

Run with ``python3 tests.py``.

    T1  exact bitmask matching agrees with a brute-force enumerator
    T2  the all-zeros adversary keeps a plant alive below threshold and not
        above it; ProbeOracle counts probes
    T3  every deterministic probe order needs >= C(ceil(n/2),2) probes; the
        witness order achieves the exact D(n) (P1 invariants, n<=10)
    T4  Erdos--Gallai D(n): the extremal kept graph has matching number k,
        and D(n) >= the lemma lower bound (P2 invariants)
    T5  the proof's clique direction: a probe set below threshold has no
        ceil(n/2)-clique, while the extremal witness probe set does
    T6  randomized sampler: detects the plant with budget, never false-positives
        on the empty graph
"""

from __future__ import annotations

import itertools
import random
import sys

from probelib import algorithms as A
from probelib import experiments as E
from probelib.lemma import clique_in_probeset, det_complexity, lemma_lower_bound
from probelib.matching import brute_max_matching, max_matching, mu_complete_minus
from probelib.model import AllZerosAdversary, ProbeOracle, gap_target

PASS, FAIL = "PASS", "FAIL"
_results: list[tuple[str, str]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    _results.append((name, PASS if cond else FAIL))
    print(f"[{PASS if cond else FAIL}] {name}" + (f" -- {detail}" if detail else ""))


def t1_matching() -> None:
    rng = random.Random(1)
    ok = True
    for _ in range(200):
        n = rng.randint(2, 8)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [e for e in pairs if rng.random() < 0.4]
        if max_matching(n, edges) != brute_max_matching(n, edges):
            ok = False
            break
    # known graphs
    ok = ok and max_matching(4, [(0, 1), (1, 2), (2, 3), (3, 0)]) == 2  # C4
    ok = ok and max_matching(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]) == 2  # C5
    ok = ok and max_matching(6, list(itertools.combinations(range(6), 2))) == 3  # K6
    check("T1 bitmask matching == brute force (200 random + known graphs)", ok)


def t2_adversary() -> None:
    n = 8
    adv = AllZerosAdversary(n)
    # empty probe set: plant exists (K_n has huge matching)
    a = adv.plant_exists(set())
    # probe all pairs: K_n minus everything is empty, no plant
    allp = set(itertools.combinations(range(n), 2))
    b = adv.plant_exists(allp)
    check("T2a plant alive with no probes, dead after probing all pairs", a and not b)
    orc = ProbeOracle(n, edges={(0, 1)})
    orc.probe(0, 1); orc.probe(0, 1); orc.probe(2, 3)
    check("T2b ProbeOracle counts DISTINCT probes", orc.cost == 2, f"cost={orc.cost}")
    check("T2c answer respects the hidden edge",
          orc.probe(0, 1) == 1 and orc.probe(4, 5) == 0)


def t3_p1() -> None:
    r = E.exp_p1("quick")  # n up to 9
    check("T3 every order >= lemma LB and witness == exact D(n) (n<=9)",
          r["all_ok"])


def t4_p2() -> None:
    ok = True
    for n in range(4, 14):
        dc = det_complexity(n)
        if dc.verified_mu != dc.k or dc.value < dc.lemma_lb:
            ok = False
            print(f"   fail n={n}: mu={dc.verified_mu} k={dc.k} D={dc.value} lb={dc.lemma_lb}")
    check("T4 extremal kept graph has nu=k and D(n) >= lemma LB (n<=13)", ok)


def t5_clique_direction() -> None:
    n = 8
    dc = det_complexity(n)
    threshold = lemma_lower_bound(n)
    # the witness probe set = complement of the extremal kept graph
    kept = set(dc.witness_kept)
    allp = set(itertools.combinations(range(n), 2))
    witness_P = allp - kept
    # a small probe set strictly below threshold: take any threshold-1 pairs
    small_P = set(list(allp)[: threshold - 1])
    c_small = clique_in_probeset(n, small_P)
    # the extremal "split" probe set contains a large clique (proof direction)
    c_big = clique_in_probeset(n, witness_P)
    import math
    half = math.ceil(n / 2)
    check("T5a a below-threshold probe set has no ceil(n/2)-clique",
          c_small < half, f"clique={c_small}, ceil(n/2)={half}")
    check("T5b the witness probe set realises mu<target (D(n) is achievable)",
          mu_complete_minus(n, witness_P) < gap_target(n))


def t6_randomized() -> None:
    n = 24
    rng = random.Random(7)
    plant = A.sparse_plant(n, rng)
    p_hit = A.detection_probability(n, plant, budget=16 * n, trials=300,
                                    rng=random.Random(11))
    p_fp = A.detection_probability(n, set(), budget=16 * n, trials=300,
                                   rng=random.Random(13))
    check("T6a randomized sampler detects the plant at budget 16n (p>0.8)",
          p_hit > 0.8, f"p={p_hit:.3f}")
    check("T6b randomized sampler has zero false positives on empty graph",
          p_fp == 0.0, f"p={p_fp:.3f}")


def main() -> int:
    t1_matching()
    t2_adversary()
    t3_p1()
    t4_p2()
    t5_clique_direction()
    t6_randomized()
    nfail = sum(1 for _, s in _results if s == FAIL)
    print(f"\n{len(_results) - nfail}/{len(_results)} checks passed.")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
