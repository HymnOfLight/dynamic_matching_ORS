# probe_lb run summary (Task C1)

Scale `full`; elapsed 1.2s.

Deterministic probe complexity of approximate matching size, and the architectural barrier for derandomizing dynamic matching (plan Lemma 3.6 + Cor. 3.7). All values are exact (P1/P2/P4) or seeded and reproducible (P3).

- **P1** exhaustive simulation: all_ok = `True` (every deterministic order >= C(ceil(n/2),2); witness order = exact D(n)).

### Exhaustive adversary simulation (every deterministic order)

Probes each order needs to certify `mu<ceil(n/4)` against the all-zeros adversary; the minimum equals the exact `D(n)`, and every order is `>= C(ceil(n/2),2)`.

| n | lemma LB | exact D(n) | min over orders | witness=D(n) | all orders >= LB |
|---|---|---|---|---|---|
| 4 | 1 | 6 | 6 | yes | yes |
| 5 | 3 | 6 | 6 | yes | yes |
| 6 | 3 | 10 | 10 | yes | yes |
| 7 | 6 | 15 | 15 | yes | yes |
| 8 | 6 | 21 | 21 | yes | yes |
| 9 | 10 | 21 | 21 | yes | yes |
| 10 | 10 | 28 | 28 | yes | yes |
| 11 | 15 | 36 | 36 | yes | yes |
| 12 | 15 | 45 | 45 | yes | yes |

- **P2** all_ok = `True`.

### Deterministic probe complexity of the gap problem

`D(n)` is the exact number of probes the all-zeros adversary forces (Erdős–Gallai); `C(ceil(n/2),2)` is the plan's clean lower bound. Gap target: distinguish `mu=0` from `mu>=ceil(n/4)`.

| n | target mu | lemma LB C(ceil(n/2),2) | exact D(n) | extremal | D(n)>=LB |
|---|---|---|---|---|---|
| 4 | 1 | 1 | 6 | empty | yes |
| 5 | 2 | 3 | 6 | split | yes |
| 6 | 2 | 3 | 10 | split | yes |
| 7 | 2 | 6 | 15 | split | yes |
| 8 | 2 | 6 | 21 | split | yes |
| 9 | 3 | 10 | 21 | split | yes |
| 10 | 3 | 10 | 28 | split | yes |
| 11 | 3 | 15 | 36 | split | yes |
| 12 | 3 | 15 | 45 | split | yes |
| 13 | 4 | 21 | 45 | split | yes |
| 14 | 4 | 21 | 55 | split | yes |
| 15 | 4 | 28 | 66 | split | yes |
| 16 | 4 | 28 | 78 | split | yes |

### Randomized detection vs probe budget (n=64)

Hard instance: a planted matching of size 16 (`mu>=ceil(n/4)=16`). Deterministic certification needs `D(n)=1176` probes (lemma LB 496); randomized detection:

| budget B | B/n | detect prob (plant) | false positive (empty) |
|---|---|---|---|
| 32 | 0.5 | 0.250 | 0.000 |
| 64 | 1.0 | 0.403 | 0.000 |
| 128 | 2.0 | 0.610 | 0.000 |
| 256 | 4.0 | 0.917 | 0.000 |
| 512 | 8.0 | 0.980 | 0.000 |
| 1024 | 16.0 | 1.000 | 0.000 |
| 2048 | 32.0 | 1.000 | 0.000 |

### Corollary 3.7: no deterministic drop-in at the oracle layer

`D(N)` is the forced deterministic probe cost on an N-vertex implicit graph; the ratio to any sublinear-in-`N^2` per-call budget grows without bound.

| N | lemma LB | exact D(N) | budget N·log2 N | budget N^1.5 | D/(N log N) | D/N^1.5 |
|---|---|---|---|---|---|---|
| 8 | 6 | 21 | 24 | 22 | 0.88 | 0.95 |
| 16 | 28 | 78 | 64 | 64 | 1.22 | 1.22 |
| 32 | 120 | 300 | 160 | 181 | 1.88 | 1.66 |
| 64 | 496 | 1176 | 384 | 512 | 3.06 | 2.3 |
| 128 | 2016 | 4656 | 896 | 1448 | 5.2 | 3.22 |
| 256 | 8128 | 18528 | 2048 | 4096 | 9.05 | 4.52 |

Ratio increasing (N·logN): True; crossover N (N·logN): 16; crossover N (N^1.5): 16.

