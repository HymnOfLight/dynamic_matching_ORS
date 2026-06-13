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
