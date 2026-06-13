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
