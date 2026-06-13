"""Cross-validation test suite for ors_lab.

Run with ``python3 tests.py``.  Every test is dependency-light; the
SAT / CP-SAT specific checks self-skip if those backends are not installed,
but the dependency-free search backend and the independent verifier are
always exercised.

    T1  verifier accepts valid and rejects invalid decompositions
    T2  the three backends agree on a battery of exact (n, r) cells
    T3  ORS_r(n) >= RS_r(n) on the battery (ordering can only help)
    T4  the (7,2) ordered-vs-unordered separation reproduces and is certified
    T5  trivial / boundary identities (r=1 gives C(n,2); r=floor(n/2) gives 1)
    T6  every feasible witness from every backend passes the verifier
"""

from __future__ import annotations

import itertools
import sys

from orslib import cpsat_encode, sat_encode, search
from orslib.core import verify_decomposition
from orslib.solve import available_backends, solve_value

PASS, FAIL = "PASS", "FAIL"
_results: list[tuple[str, str, str]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    _results.append((name, PASS if cond else FAIL, detail))
    print(f"[{PASS if cond else FAIL}] {name}" + (f" -- {detail}" if detail else ""))


# ---------------------------------------------------------------- T1
def t1_verifier() -> None:
    # canonical single induced perfect-ish matching is valid (RS and ORS)
    ok = verify_decomposition(6, 2, [[(0, 1), (2, 3)]], ordered=False)
    check("T1a verifier accepts a valid 1-class decomposition", ok.ok, ok.reason)

    # the proven (7,2) ORS witness: valid as ORS, invalid as RS
    ors_w = [[(0, 1), (2, 3)], [(0, 4), (1, 5)], [(0, 6), (2, 4)],
             [(1, 6), (3, 5)], [(2, 5), (3, 4)]]
    a = verify_decomposition(7, 2, ors_w, ordered=True)
    b = verify_decomposition(7, 2, ors_w, ordered=False)
    check("T1b verifier accepts the ORS(7,2) witness as ordered", a.ok, a.reason)
    check("T1c verifier rejects the same witness as unordered RS", not b.ok, b.reason)

    # wrong size
    c = verify_decomposition(6, 2, [[(0, 1)]], ordered=False)
    check("T1d verifier rejects a wrong-size matching", not c.ok, c.reason)
    # shared edge
    d = verify_decomposition(6, 2, [[(0, 1), (2, 3)], [(0, 1), (4, 5)]], ordered=True)
    check("T1e verifier rejects a shared edge", not d.ok, d.reason)
    # non-matching (shared vertex within a class)
    e = verify_decomposition(6, 2, [[(0, 1), (1, 2)]], ordered=False)
    check("T1f verifier rejects a non-matching class", not e.ok, e.reason)


# ---------------------------------------------------------------- T2/T3/T6
BATTERY = [(4, 2), (5, 2), (6, 2), (6, 3), (7, 2), (7, 3), (8, 3), (8, 4)]


def t2_t3_t6_backends_agree() -> None:
    backends = available_backends()
    all_agree = True
    ors_ge_rs = True
    witnesses_ok = True
    for (n, r) in BATTERY:
        for ordered in (False, True):
            res = solve_value(n, r, ordered=ordered, methods=backends)
            exact_vals = {
                m: mr.value for m, mr in res.methods.items() if mr.status == "exact"
            }
            if len(set(exact_vals.values())) > 1:
                all_agree = False
                print(f"   disagreement n={n} r={r} ordered={ordered}: {exact_vals}")
            # verify every witness produced
            for m, mr in res.methods.items():
                if mr.witness:
                    vr = verify_decomposition(n, r, mr.witness, ordered=ordered)
                    if not vr.ok:
                        witnesses_ok = False
                        print(f"   bad witness {m} n={n} r={r}: {vr.reason}")
        rs = solve_value(n, r, ordered=False, methods=backends)
        ors = solve_value(n, r, ordered=True, methods=backends)
        if rs.exact and ors.exact and ors.value < rs.value:
            ors_ge_rs = False
            print(f"   ORS<RS at n={n} r={r}: RS={rs.value} ORS={ors.value}")
    check(f"T2 backends agree on the exact battery ({len(BATTERY)} cells)", all_agree)
    check("T3 ORS_r(n) >= RS_r(n) on the battery", ors_ge_rs)
    check("T6 every feasible witness passes the independent verifier", witnesses_ok)


# ---------------------------------------------------------------- T4
def t4_separation() -> None:
    rs = solve_value(7, 2, ordered=False)
    ors = solve_value(7, 2, ordered=True)
    cond = rs.exact and ors.exact and rs.value == 4 and ors.value == 5
    check("T4a RS_2(7)=4 and ORS_2(7)=5 (proven separation)", cond,
          f"RS={rs.value} ORS={ors.value}")
    breaks = ors.witness and not verify_decomposition(
        7, 2, ors.witness, ordered=False
    ).ok
    check("T4b the ORS_2(7) witness is genuinely ordered-only", bool(breaks))


# ---------------------------------------------------------------- T5
def t5_boundaries() -> None:
    # r=1: every single edge is its own induced matching -> C(n,2)
    import math
    res = solve_value(5, 1, ordered=False)
    check("T5a RS_1(5) = C(5,2) = 10", res.exact and res.value == math.comb(5, 2),
          f"value={res.value}")
    # r = floor(n/2): one class saturates (almost) everything -> exactly 1
    res2 = solve_value(8, 4, ordered=True)
    check("T5b ORS_4(8) = 1 (a second perfect matching is forbidden)",
          res2.exact and res2.value == 1, f"value={res2.value}")


def main() -> int:
    print(f"backends available: {available_backends()}\n")
    t1_verifier()
    t2_t3_t6_backends_agree()
    t4_separation()
    t5_boundaries()
    n_fail = sum(1 for _, s, _ in _results if s == FAIL)
    print(f"\n{len(_results) - n_fail}/{len(_results)} checks passed.")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
