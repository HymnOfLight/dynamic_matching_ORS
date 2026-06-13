"""Build the exact small-n ORS/RS tables and the separation search.

Three deliverables (plan Task B1):

* :func:`grid_table` -- exact ``RS_r(n)`` and ``ORS_r(n)`` over a full
  ``(n, r)`` grid, each cell cross-validated by every backend that finishes
  within budget and each witness checked by the independent verifier;
* :func:`extremal_table` -- the linear / near-``n/2`` regime
  ``r = floor(n/2) - j`` across a wide ``n`` range (small ``t``, cheap and
  exact), which is the regime that controls the AKK25 update time;
* :func:`separation_search` -- the targeted hunt for small-``n``
  ``ORS_r(n) > RS_r(n)`` separations (Pratt's equivalence is asymptotic, so
  small-``n`` gaps are possible and informative).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional

from .core import Decomposition, verify_decomposition
from .solve import available_backends, solve_value


@dataclass
class Cell:
    n: int
    r: int
    ordered: bool
    value: int
    exact: bool
    verified: bool
    agreement: bool
    methods: dict = field(default_factory=dict)   # method -> {status, value}
    witness: Decomposition = field(default_factory=list)
    error: str = ""

    def to_json(self) -> dict:
        return {
            "n": self.n, "r": self.r, "ordered": self.ordered,
            "value": self.value, "exact": self.exact, "verified": self.verified,
            "agreement": self.agreement,
            "methods": self.methods, "witness": self.witness, "error": self.error,
        }


def _budgets_for(n: int) -> dict:
    """Pick per-backend budgets so slow backends bail gracefully instead of
    hanging.  Larger ``n`` -> rely more on CP-SAT, smaller search/SAT effort."""
    if n <= 8:
        return {"budget": 3_000_000, "conf_budget": 2_000_000, "max_time_s": 30.0}
    if n <= 10:
        return {"budget": 1_500_000, "conf_budget": 400_000, "max_time_s": 30.0}
    return {"budget": 300_000, "conf_budget": 120_000, "max_time_s": 20.0}


def _methods_for(n: int) -> list[str]:
    """Use all backends on small instances (triple cross-validation); drop the
    pure-Python search on large ones where CP-SAT/SAT are the workhorses."""
    avail = available_backends()
    if n <= 8:
        return avail
    return [m for m in avail if m != "search"] or avail


_CELL_CACHE: dict[tuple[int, int, bool], "Cell"] = {}


def clear_cache() -> None:
    _CELL_CACHE.clear()


def compute_cell(n: int, r: int, ordered: bool) -> Cell:
    key = (n, r, ordered)
    if key in _CELL_CACHE:
        return _CELL_CACHE[key]
    cell = _compute_cell_uncached(n, r, ordered)
    _CELL_CACHE[key] = cell
    return cell


def _compute_cell_uncached(n: int, r: int, ordered: bool) -> Cell:
    res = solve_value(
        n, r, ordered=ordered, methods=_methods_for(n), **_budgets_for(n)
    )
    verified = True
    if res.witness:
        verified = verify_decomposition(n, r, res.witness, ordered=ordered).ok
    methods = {
        m: {"status": mr.status, "value": mr.value, "note": mr.note}
        for m, mr in res.methods.items()
    }
    return Cell(
        n=n, r=r, ordered=ordered, value=res.value, exact=res.exact,
        verified=verified, agreement=res.agreement, methods=methods,
        witness=res.witness, error=res.error,
    )


def grid_table(n_max: int, r_min: int = 2) -> list[Cell]:
    cells: list[Cell] = []
    for n in range(2 * r_min, n_max + 1):
        for r in range(r_min, n // 2 + 1):
            for ordered in (False, True):
                cells.append(compute_cell(n, r, ordered))
    return cells


def extremal_table(n_max: int, n_min: int = 6, j_max: int = 2) -> list[Cell]:
    cells: list[Cell] = []
    for n in range(n_min, n_max + 1):
        for j in range(0, j_max + 1):
            r = n // 2 - j
            if r < 2:
                continue
            for ordered in (False, True):
                cells.append(compute_cell(n, r, ordered))
    return cells


@dataclass
class Separation:
    n: int
    r: int
    rs_value: int
    ors_value: int
    rs_exact: bool
    ors_exact: bool
    gap: int
    status: str               # "proven" | "lower_bound"
    ors_witness: Decomposition = field(default_factory=list)
    ors_witness_breaks_rs: bool = False


def separation_search(n_max: int, r_min: int = 2) -> list[Separation]:
    """Scan ``(n, r)`` for ``ORS_r(n) > RS_r(n)``.

    A separation is ``proven`` when both values are exact; it is a
    ``lower_bound`` separation when ``RS`` is exact and the ORS witness
    already exceeds it (so the gap is certified even if the exact ORS value
    is not pinned).  In both cases the ORS witness is re-checked under the RS
    condition to confirm it is genuinely *ordered*-only.
    """
    out: list[Separation] = []
    for n in range(2 * r_min, n_max + 1):
        for r in range(r_min, n // 2 + 1):
            rs = compute_cell(n, r, ordered=False)
            ors = compute_cell(n, r, ordered=True)
            if ors.value <= rs.value:
                continue
            if not rs.exact:
                # cannot certify a gap without an exact RS upper bound
                continue
            breaks_rs = False
            if ors.witness:
                breaks_rs = not verify_decomposition(
                    n, r, ors.witness, ordered=False
                ).ok
            status = "proven" if (rs.exact and ors.exact) else "lower_bound"
            out.append(Separation(
                n=n, r=r, rs_value=rs.value, ors_value=ors.value,
                rs_exact=rs.exact, ors_exact=ors.exact,
                gap=ors.value - rs.value, status=status,
                ors_witness=ors.witness, ors_witness_breaks_rs=breaks_rs,
            ))
    return out
