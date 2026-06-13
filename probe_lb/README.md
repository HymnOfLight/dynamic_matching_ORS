# probe_lb — Task C1 (deterministic probe complexity + barrier)

Companion code for **Task C1** of the execution plan *"Optimal Approximation
for Fully Dynamic Matching and Ordered Ruzsa–Szemerédi Graphs"* (§6, WS-C
lower bounds; code deliverable §7, WS-D), and the **first pre-committed
fallback publishable unit** (§7.2): a SOSA-style note *"Deterministic probe
complexity of approximate matching size and a barrier for derandomizing
dynamic matching."*

It is the lower-bound counterpart to `audit_lab` (Task A0, randomness audit)
and `ors_lab` (Task B1, ORS/RS densities): `audit_lab` localizes the
pipelines' randomness to a sublinear gap-estimation oracle; `probe_lb` proves
that oracle has **no deterministic drop-in**.

## What this package proves and computes

The **gap problem** (adjacency-matrix probe model): distinguish `mu(G)=0`
from `mu(G) ≥ ⌈n/4⌉`, probing entries `Adj(u,v) ∈ {0,1}`.

1. **Lemma 3.6 (plan):** any *deterministic* adaptive algorithm needs
   `> C(⌈n/2⌉,2) − 1 = Ω(n²)` probes, vs `Õ(n)` randomized — a quadratic
   separation. The all-zeros adversary and its consistent *plant*
   `H = K_n \ P` are implemented in `probelib/model.py`.
2. **Exact deterministic complexity `D(n)`** that the adversary forces:
   `D(n) = C(n,2) − ex(n; ν ≤ ⌈n/4⌉−1)` by the Erdős–Gallai matching theorem,
   with an explicit extremal witness whose matching number is verified by an
   independent bitmask DP. `D(n) ≥ C(⌈n/2⌉,2)` always (the lemma's `1/8`
   constant is clean but ~3× loose in the computed range).
3. **Exhaustive simulation (n ≤ 12):** every deterministic probe order needs
   `≥ C(⌈n/2⌉,2)` probes and the optimal "witness" order attains exactly
   `D(n)` — including the clique-first order that probes the structure the
   proof says is required.
4. **Randomized `O(n log n)` upper bound** on the hard sparse plant: detection
   probability → 1 with zero false positives on the empty graph.
5. **Corollary 3.7 (barrier):** `D(N)` exceeds any sublinear-in-`N²` per-call
   budget (crossover at `N=16`, ≈9× by `N=256`), so the pipelines'
   sublinear oracle layer cannot be derandomized in place.

### Headline numbers (exact)

| n | gap target μ | lemma LB `C(⌈n/2⌉,2)` | exact `D(n)` |
|---|---|---|---|
| 8 | 2 | 6 | 21 |
| 12 | 3 | 15 | 45 |
| 16 | 4 | 28 | 78 |

## Layout

```
probe_lb/
├── probelib/
│   ├── matching.py      # exact bitmask-DP mu(G) + brute-force cross-check
│   ├── model.py         # adjacency-matrix probe oracle + all-zeros adversary + plant
│   ├── lemma.py         # C(⌈n/2⌉,2) bound, exact Erdős–Gallai D(n), witnesses
│   ├── algorithms.py    # deterministic probe orders + randomized O(n log n) sampler
│   ├── experiments.py   # P1 exhaustive sim, P2 complexity, P3 det-vs-rand, P4 barrier
│   └── render.py        # → LaTeX (booktabs) / Markdown
├── tests.py             # T1–T6 cross-validation suite (<1 s)
├── run_all.py           # CLI orchestrator
├── note/C1_note.{tex,pdf}
└── results/             # generated: *.json, RESULTS.md, tables, plots
```

## Reproduce

```bash
pip install matplotlib            # optional: plots only; the package is otherwise stdlib
python3 tests.py                  # 10 cross-validation checks, <1 s
python3 run_all.py --scale quick  # ~1 s
python3 run_all.py --scale full   # ~1 s; n≤12 sim, det-vs-rand at n=64, barrier to N=256
```

Everything is exact (P1/P2/P4) or seeded and reproducible (P3); no third-party
solver is required (pure standard library, `matplotlib` only for figures).

## Honesty tags (same convention as the plan)

`[V]` Erdős–Gallai cited from source; `[P]` proved in the plan and reproduced /
exhaustively certified here; `[E]` empirical/simulation-checked (the routine
lemma variants, the randomized detection curve). The deterministic complexity
`D(n)` is exact; the randomized side of Lemma 3.6 is the standard
birthday/Yao argument, illustrated (not re-proved) by P3.

## Relation to the plan and what comes next

- Packages the **L1 + L2** answer types of Problem OP-L (unconditional
  probe-model separation + architectural barrier), the SOSA-style note.
- Prior-art scoped against Assadi–Solomon (ICALP'19) and Assadi–Chen–Khanna
  (SODA'19), whose `Ω(n²)` bounds are for *finding* a maximal matching (where
  randomized is also quadratic), unlike size *estimation* here (randomized
  `Õ(n)`); see the note §6.
- Open next: the **adjacency-list** model separation (plan Task C1(b)), which
  needs a planted background graph and a derandomized congestion adversary —
  the natural follow-up package once this note is settled.
