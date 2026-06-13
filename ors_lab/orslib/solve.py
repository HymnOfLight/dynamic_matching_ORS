"""High-level value computation with cross-validation.

``solve_value(n, r, ordered=...)`` returns the exact value ``RS_r(n)`` or
``ORS_r(n)`` together with a *verified* witness, by running every available
backend, checking each witness with the independent
:func:`orslib.core.verify_decomposition`, and asserting that the backends
agree.  Disagreement (which would indicate a bug in an encoding) is surfaced
as an error rather than silently resolved.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from . import cpsat_encode, sat_encode, search
from .core import Decomposition, verify_decomposition

UNKNOWN = search.UNKNOWN

# backend name -> decision function with signature (n, r, t, ordered) -> witness|None|UNKNOWN
_BACKENDS = {
    "search": lambda n, r, t, ordered, **kw: search.feasible(
        n, r, t, ordered=ordered, budget=kw.get("budget", 2_000_000)
    ),
    "sat": lambda n, r, t, ordered, **kw: sat_encode.feasible(
        n, r, t, ordered=ordered, conf_budget=kw.get("conf_budget", None)
    ),
    "cpsat": lambda n, r, t, ordered, **kw: cpsat_encode.feasible(
        n, r, t, ordered=ordered, max_time_s=kw.get("max_time_s", 30.0)
    ),
}


def available_backends() -> list[str]:
    out = ["search"]
    if sat_encode.available():
        out.append("sat")
    if cpsat_encode.available():
        out.append("cpsat")
    return out


def edge_ceiling(n: int, r: int) -> int:
    """An a-priori upper bound on ``t``: edge-disjointness caps ``t*r`` at
    ``binom(n, 2)``."""
    if r <= 0:
        return 0
    return math.comb(n, 2) // r


@dataclass
class MethodResult:
    method: str
    status: str  # "exact" | "lower_bound" | "unavailable"
    value: int
    witness: Decomposition = field(default_factory=list)
    decisions: dict = field(default_factory=dict)  # t -> "sat"|"unsat"|"unknown"
    note: str = ""


@dataclass
class SolveResult:
    n: int
    r: int
    ordered: bool
    value: int            # agreed exact value, or best lower bound
    exact: bool
    witness: Decomposition
    methods: dict = field(default_factory=dict)
    agreement: bool = True
    error: str = ""


def _method_value(method: str, n: int, r: int, ordered: bool, **kw) -> MethodResult:
    fn = _BACKENDS[method]
    ceil = edge_ceiling(n, r)
    if r <= 0 or 2 * r > n or ceil == 0:
        return MethodResult(method, "exact", 0, [], {}, "trivial (no size-r matching)")

    best = 0
    best_witness: Decomposition = []
    decisions: dict = {}
    t = 1
    while t <= ceil:
        res = fn(n, r, t, ordered, **kw)
        if res is UNKNOWN:
            decisions[t] = "unknown"
            if not sat_or_cpsat_present(method):
                return MethodResult(method, "unavailable", best, best_witness, decisions)
            return MethodResult(
                method, "lower_bound", best, best_witness, decisions,
                note=f"budget/time exhausted at t={t}",
            )
        if res is None:
            decisions[t] = "unsat"
            return MethodResult(method, "exact", best, best_witness, decisions)
        # feasible: verify the witness independently
        vr = verify_decomposition(n, r, res, ordered=ordered)
        if not vr.ok:
            return MethodResult(
                method, "lower_bound", best, best_witness, decisions,
                note=f"WITNESS REJECTED at t={t}: {vr.reason}",
            )
        decisions[t] = "sat"
        best, best_witness = t, res
        t += 1
    # reached the edge ceiling while still feasible: cannot be larger
    return MethodResult(method, "exact", best, best_witness, decisions)


def sat_or_cpsat_present(method: str) -> bool:
    if method == "sat":
        return sat_encode.available()
    if method == "cpsat":
        return cpsat_encode.available()
    return True


def solve_value(
    n: int,
    r: int,
    *,
    ordered: bool,
    methods: Optional[list[str]] = None,
    **kw,
) -> SolveResult:
    methods = methods or available_backends()
    results: dict[str, MethodResult] = {}
    for m in methods:
        if not sat_or_cpsat_present(m):
            results[m] = MethodResult(m, "unavailable", 0, note="backend not installed")
            continue
        results[m] = _method_value(m, n, r, ordered, **kw)

    exact_vals = {m: mr.value for m, mr in results.items() if mr.status == "exact"}
    lower_bounds = {m: mr.value for m, mr in results.items() if mr.status == "lower_bound"}

    agreement = True
    error = ""

    # any rejected witness is a hard error
    for m, mr in results.items():
        if mr.note.startswith("WITNESS REJECTED"):
            agreement = False
            error = f"{m}: {mr.note}"

    if exact_vals:
        vals = set(exact_vals.values())
        if len(vals) > 1:
            agreement = False
            error = f"exact backends disagree: {exact_vals}"
        value = max(exact_vals.values())
        exact = True
        # lower bounds must not exceed the exact value
        for m, lb in lower_bounds.items():
            if lb > value:
                agreement = False
                error = f"{m} lower bound {lb} exceeds exact {value}"
        witness = next(
            mr.witness for mr in results.values()
            if mr.status == "exact" and mr.value == value and mr.witness
        ) if value > 0 else []
    else:
        value = max(lower_bounds.values()) if lower_bounds else 0
        exact = False
        witness = next(
            (mr.witness for mr in results.values()
             if mr.status == "lower_bound" and mr.value == value and mr.witness),
            [],
        )

    return SolveResult(
        n=n, r=r, ordered=ordered, value=value, exact=exact,
        witness=witness, methods=results, agreement=agreement, error=error,
    )


def rs_value(n: int, r: int, **kw) -> SolveResult:
    return solve_value(n, r, ordered=False, **kw)


def ors_value(n: int, r: int, **kw) -> SolveResult:
    return solve_value(n, r, ordered=True, **kw)
