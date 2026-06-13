"""probe_lb: deterministic probe complexity of approximate matching size.

Task C1 of the dynamic-matching / ORS execution plan (WS-C lower bounds +
WS-D engineering; first pre-committed fallback publishable unit, plan
Sec. 7.2).  Implements the all-zeros adversary of Lemma 3.6, the exact
deterministic probe complexity it forces, the randomized O(n log n) upper
bound, and the architectural barrier of Corollary 3.7.
"""

from .lemma import det_complexity, lemma_lower_bound
from .matching import max_matching, mu_complete_minus
from .model import AllZerosAdversary, ProbeOracle, gap_target

__all__ = [
    "max_matching",
    "mu_complete_minus",
    "ProbeOracle",
    "AllZerosAdversary",
    "gap_target",
    "lemma_lower_bound",
    "det_complexity",
]
