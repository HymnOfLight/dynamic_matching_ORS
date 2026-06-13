# ors_lab run summary (Task B1)

Scale `full`; backends `['search', 'sat', 'cpsat']`; elapsed 320.9s.

Every value below is produced by CP-SAT and (for n<=8) independently by a CNF/SAT encoding and a dependency-free branch-and-bound search; every witness is checked by `orslib.core.verify_decomposition`, which shares no code with the solvers.

- grid: 24 cells, 23 exact, 1 verified lower bounds.

### Exact RS / ORS grid

Each cell is `RS_r(n) / ORS_r(n)`; `>=k` marks a verified lower bound (exact value not pinned within budget); **bold** marks an ordered-vs-unordered separation.

| n \\ r | r=2 | r=3 | r=4 |
|---|---|---|---|
| n=4 | 1 / 1 | -- | -- |
| n=5 | 1 / 1 | -- | -- |
| n=6 | 3 / 3 | 1 / 1 | -- |
| n=7 | **4 / 5** | 1 / 1 | -- |
| n=8 | **6 / 8** | 1 / 1 | 1 / 1 |
| n=9 | **9 / >=11** | 3 / 3 | 1 / 1 |

### Near-n/2 regime

Each cell is `RS_r(n) / ORS_r(n)`; `>=k` marks a verified lower bound (exact value not pinned within budget); **bold** marks an ordered-vs-unordered separation.

| n \\ r | r=2 | r=3 | r=4 | r=5 | r=6 | r=7 | r=8 | r=9 | r=10 |
|---|---|---|---|---|---|---|---|---|---|
| n=6 | 3 / 3 | 1 / 1 | -- | -- | -- | -- | -- | -- | -- |
| n=7 | **4 / 5** | 1 / 1 | -- | -- | -- | -- | -- | -- | -- |
| n=8 | **6 / 8** | 1 / 1 | 1 / 1 | -- | -- | -- | -- | -- | -- |
| n=9 | **9 / >=11** | 3 / 3 | 1 / 1 | -- | -- | -- | -- | -- | -- |
| n=10 | -- | 5 / 5 | 1 / 1 | 1 / 1 | -- | -- | -- | -- | -- |
| n=11 | -- | **5 / >=6** | 1 / 1 | 1 / 1 | -- | -- | -- | -- | -- |
| n=12 | -- | -- | 3 / 3 | 1 / 1 | 1 / 1 | -- | -- | -- | -- |
| n=13 | -- | -- | 3 / 3 | 1 / 1 | 1 / 1 | -- | -- | -- | -- |
| n=14 | -- | -- | -- | 1 / 1 | 1 / 1 | 1 / 1 | -- | -- | -- |
| n=15 | -- | -- | -- | 3 / 3 | 1 / 1 | 1 / 1 | -- | -- | -- |
| n=16 | -- | -- | -- | -- | 1 / 1 | 1 / 1 | 1 / 1 | -- | -- |
| n=17 | -- | -- | -- | -- | 1 / 1 | 1 / 1 | 1 / 1 | -- | -- |
| n=18 | -- | -- | -- | -- | -- | 1 / 1 | 1 / 1 | 1 / 1 | -- |
| n=19 | -- | -- | -- | -- | -- | 1 / 1 | 1 / 1 | 1 / 1 | -- |
| n=20 | -- | -- | -- | -- | -- | -- | 1 / 1 | 1 / 1 | 1 / 1 |

### Ordered-vs-unordered separations  `ORS_r(n) > RS_r(n)`

| n | r | RS_r(n) | ORS_r(n) | gap | status | ORS witness breaks RS? |
|---|---|---|---|---|---|---|
| 7 | 2 | 4 | 5 | 1 | proven | yes |
| 8 | 2 | 6 | 8 | 2 | proven | yes |
| 9 | 2 | 9 | >=11 | 2 | lower_bound | yes |


## Separation witnesses (verified)

- `ORS_2(7)=5 > RS_2(7)=4`; ordered decomposition (checked ordered-only): `[[(0, 1), (2, 3)], [(0, 4), (1, 5)], [(0, 6), (2, 4)], [(1, 6), (3, 5)], [(2, 5), (3, 4)]]`
- `ORS_2(8)=8 > RS_2(8)=6`; ordered decomposition (checked ordered-only): `[[(0, 1), (2, 3)], [(4, 6), (5, 7)], [(1, 6), (3, 7)], [(2, 6), (3, 5)], [(0, 7), (1, 4)], [(0, 5), (3, 4)], [(1, 5), (2, 4)], [(0, 6), (2, 7)]]`
