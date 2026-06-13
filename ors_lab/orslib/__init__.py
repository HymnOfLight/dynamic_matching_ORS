"""ors_lab: exact small-n ordered / classical Ruzsa--Szemeredi densities.

Task B1 of the dynamic-matching / ORS execution plan (fallback publishable
unit #2): compute exact ``ORS_r(n)`` and ``RS_r(n)`` for small ``n`` with two
independent industrial encodings (SAT, CP-SAT) plus a dependency-free
branch-and-bound search, all cross-validated through one independent
certificate verifier, and search for small-``n`` ordered-vs-unordered
separations.
"""

from .core import (
    Decomposition,
    Matching,
    VerificationResult,
    max_r,
    saturated_vertices,
    verify_decomposition,
)
from .solve import ors_value, rs_value, solve_value, available_backends

__all__ = [
    "Decomposition",
    "Matching",
    "VerificationResult",
    "verify_decomposition",
    "saturated_vertices",
    "max_r",
    "ors_value",
    "rs_value",
    "solve_value",
    "available_backends",
]
