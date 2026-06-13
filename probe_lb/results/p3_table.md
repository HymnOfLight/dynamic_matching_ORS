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
