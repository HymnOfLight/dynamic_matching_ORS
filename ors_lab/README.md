# ors_lab — Task B1 (exact small-n ORS/RS densities)

Companion code for **Task B1** of the execution plan *"Optimal
Approximation for Fully Dynamic Matching and Ordered Ruzsa–Szemerédi
Graphs"* (§5, WS-B; code deliverable specified in §7, WS-D), and the second
pre-committed fallback publishable unit (§7.2): *exact small-`n` ORS/RS
tables with certificates and any ordered-vs-unordered small-`n`
separation*.

It is the combinatorics counterpart of the `audit_lab` package (Task A0):
where `audit_lab` instruments the **randomness** of the dynamic-matching
pipelines, `ors_lab` computes exact values of the **combinatorial quantity**
those pipelines reduce to — the (ordered) Ruzsa–Szemerédi density that
governs the AKK25 update time.

## What this package computes

For a graph on `n` vertices, an **RS decomposition** with parameters
`(r, t)` is a partition of its edges into `t` *induced* matchings each of
size `r`; `RS_r(n)` is the largest such `t`. An **ORS decomposition** only
asks each `M_i` to be induced in the *suffix* `M_i ∪ … ∪ M_t` for some
ordering, so `ORS_r(n) ≥ RS_r(n)` always. (Definitions: `orslib/core.py`,
matching plan Def. 2.3 = Behnezhad–Ghafari 2024.)

`ors_lab` delivers:

1. **Exact tables** of `RS_r(n)` and `ORS_r(n)` over a full `(n, r)` grid
   and over the linear / near-`n/2` regime that controls the AKK25 runtime;
2. **Certificates**: every value ships a witness decomposition checked by an
   *independent* `O(t·n²)` verifier that shares no code with the solvers;
3. A **targeted separation search** for small-`n` `ORS_r(n) > RS_r(n)`
   (Pratt SOSA 2026 shows ordered ≈ unordered *asymptotically*, so any
   small-`n` gap is genuine and informative).

### Headline findings (seed-free; exact, triple cross-validated)

| result | value | status |
|---|---|---|
| `RS_2(7)` vs `ORS_2(7)` | **4 vs 5** | proven separation, gap 1 |
| `RS_2(8)` vs `ORS_2(8)` | **6 vs 8** | proven separation, gap 2 |
| `RS_2(9)` vs `ORS_2(9)` | 9 vs ≥11 | certified lower-bound separation, gap ≥2 |
| `RS_3(11)` vs `ORS_3(11)` | 5 vs ≥6 | certified lower-bound separation |
| near-`n/2` regime | `RS=ORS=1` once `2r` is close to `n` | exact, `n ≤ 20` |

The smallest separation is at `n = 7`. The ORS witnesses are re-checked
under the unordered RS condition and **fail** it — i.e. they are genuinely
*ordered*-only decompositions, not RS decompositions in disguise.

## Three independent backends (project cross-validation methodology)

Each `(n, r)` value is computed by every backend that finishes within
budget, and they must agree on the exact value; each witness is then
verified independently.

| backend | file | paradigm | role |
|---|---|---|---|
| `search` | `orslib/search.py` | branch-and-bound, **no dependencies** | always available; CI/no-network anchor |
| `sat` | `orslib/sat_encode.py` | CNF + CDCL (PySAT/Glucose) | independent encoding #1 |
| `cpsat` | `orslib/cpsat_encode.py` | CP-SAT (OR-Tools) | independent encoding #2; the workhorse on hard cells |

All three pin `M_1` to the canonical matching `{(0,1),(2,3),…}` (a
relabelling symmetry break valid for both RS and ORS); the `search` backend
additionally exploits colour-class interchangeability for RS.

## Layout

```
ors_lab/
├── orslib/
│   ├── core.py          # definitions + independent O(t n^2) certificate verifier
│   ├── search.py        # Method A: dependency-free branch-and-bound
│   ├── sat_encode.py    # Method B: CNF/SAT via PySAT (optional)
│   ├── cpsat_encode.py  # Method C: OR-Tools CP-SAT (optional)
│   ├── solve.py         # cross-validation layer: ors_value / rs_value
│   ├── tables.py        # grid / extremal tables + separation search
│   └── render.py        # → LaTeX (booktabs) / Markdown
├── tests.py             # T1–T6 cross-validation suite (<2 s)
├── run_all.py           # CLI orchestrator
├── note/                # B1 technical note (LaTeX)
└── results/             # generated: *.json, RESULTS.md, *.tex/.md, *.png
```

## Reproduce

```bash
pip install python-sat ortools matplotlib      # optional: enables sat/cpsat + plots
python3 tests.py                               # 13 cross-validation checks, <2 s
python3 run_all.py --scale quick               # ~1 s, n ≤ 7
python3 run_all.py --scale full                # ~5 min, n ≤ 9 grid + n ≤ 20 extremal
python3 run_all.py --only separations          # just the ORS>RS hunt
```

Results are deterministic (no random seeds enter the values). Without
PySAT/OR-Tools installed the `search` backend alone still computes and
verifies the small-`n` cells; the larger/harder cells need a real solver.

## Honesty tags (same convention as the plan)

`[V]` verified definition against BG24; `[P]` proved here = exhaustively
certified by ≥2 independent solvers + verifier; `[E]` empirical/within-budget
lower bound (a verified witness exists, the exact value is not pinned within
the configured solver budget). In the tables, `>=k` is an `[E]` lower bound;
every other entry is `[P]`.

## Limitations

- Exactness is solver-bounded: the `r = 2` small-induced-matching regime is
  combinatorially hard, so for `n ≥ 9` some `ORS` cells are verified lower
  bounds (e.g. `ORS_2(9) ≥ 11`) rather than pinned values. The plan's
  aspiration of `n ≲ 40` requires an industrial portfolio (kissat / Gurobi);
  the encodings here are written so that swapping the backend suffices.
- The *linear* regime `r = Θ(n)` — the one that matters for the AKK25 update
  time — is cheap and exact even at larger `n`, because `t` is small there.
- No claim is made that small-`n` separations persist asymptotically; Pratt
  SOSA 2026 implies they do **not** at polynomial scale. Their value is as
  exact extremal data and as seeds for the WS-B construction effort.
