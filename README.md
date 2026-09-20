# Une vie de fourmi

Python / NetworkX project that computes the minimum number of steps required to move all ants from `Sv` to `Sd` while respecting room capacities.

## Repository structure

```text
uneviedefourmi/
├── fourmilieres/
│   ├── La_hormiguera_de_la_muerte.txt
│   ├── fourmiliere_3D.txt
│   ├── fourmiliere_cinq.txt
│   ├── fourmiliere_deux.txt
│   ├── fourmiliere_quatre.txt
│   ├── fourmiliere_trois.txt
│   ├── fourmiliere_un.txt
│   ├── fourmiliere_zero.txt
│   └── salle_d_at-ant.txt
├── resultats/
├── .gitignore
├── README.md
├── ants.py
├── main.py
├── requirements.txt
└── visualisation.py
```

## How the solver works

1. The selected ant hill is converted into an undirected NetworkX graph.
2. The shortest path from `Sv` to `Sd` gives the first duration worth testing.
3. For each tested duration `T`, the program creates a time-expanded directed graph.
4. Each room is split into `entry` and `exit`, and the edge between them carries the room capacity.
5. Waiting and tunnel movements connect instant `t` to instant `t + 1`.
6. `nx.maximum_flow()` checks whether all `F` ants can reach the sink at time `T`.
7. The first successful duration is the minimum duration.
8. The returned global flow is consumed one unit at a time to reconstruct one path per ant.
9. Technical nodes and waiting transitions are filtered to produce the required `E1`, `E2`, `E3...` output.
10. Matplotlib replays the solution on the physical graph.

## Install

```bash
pip install -r requirements.txt
```

## Run

Choose the desired dataset in `main.py`:

```python
ant_hill_name = "zero"
```

Available values:

`zero`, `un`, `deux`, `trois`, `quatre`, `cinq`, `3D`, `mort`, `at-ant`

Then run:

```bash
python main.py
```

## Verified minimum durations

| Ant hill | Minimum duration |
|---|---:|
| zero | 2 |
| un | 7 |
| deux | 1 |
| trois | 7 |
| quatre | 9 |
| cinq | 11 |
| 3D | 14 |
| mort | 9 |
| at-ant | 15 |

## File roles

- `ants.py`: graph construction, time-expanded network, maximum flow, path reconstruction and E1/E2/E3 generation.
- `main.py`: embedded exercise data, ant-hill selection, solver launch and terminal output.
- `visualisation.py`: graphical replay of the ant movements.
- `fourmilieres/`: readable mirrors of the nine dictionary datasets.
- `resultats/`: generated terminal results for the nine ant hills.
