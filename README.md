<div align="center">

# 🐜 Une vie de fourmi

### Optimal ant routing with graph theory, time-expanded networks and maximum flow

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-Graph%20Algorithms-4C8CBF)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557C)
![Status](https://img.shields.io/badge/Status-Completed-success)

</div>

---

## 📌 Project overview

**Une vie de fourmi** is a Python project that solves an ant-routing optimization problem.

The objective is to move every ant from the vestibule `Sv` to the dormitory `Sd` in the **minimum number of steps**, while respecting the capacity of each room.

The project combines:

- graph modeling with **NetworkX**;
- shortest-path computation;
- a **time-expanded graph**;
- **maximum-flow** optimization;
- reconstruction of one path per ant;
- step-by-step visualization with **Matplotlib**.

---

## 🎯 Problem objective

Every ant starts in:

```text
Sv
```

and must reach:

```text
Sd
```

At each step, an ant can:

- stay in its current room;
- move through a tunnel to an adjacent room.

The solution must respect the maximum capacity of every room and minimize the total number of steps required for **all ants** to reach `Sd`.

---

## ⚙️ How the solution works

### 1 — Build the physical graph

The ant hill is represented as an undirected graph:

```python
graph = nx.Graph()

for room, capacity in data["capacities"].items():
    graph.add_node(room, capacity=capacity)

graph.add_edges_from(data["tunnels"])
```

Each:

- **room** becomes a node;
- **tunnel** becomes an edge;
- **room capacity** is stored as a node attribute.

---

### 2 — Find the first duration to test

The shortest path between `Sv` and `Sd` provides a lower bound:

```python
start_duration = nx.shortest_path_length(graph, "Sv", "Sd")
```

This value does not solve the complete problem.

It only gives the minimum number of tunnel crossings required for one ant to reach the dormitory when congestion is ignored.

---

### 3 — Build a time-expanded graph

For each tested duration, the program creates a directed graph that represents both **space and time**.

Each physical room is duplicated at every instant:

```text
(room, time, "entry")
(room, time, "exit")
```

The edge:

```text
entry ─────► exit
```

carries the capacity of the room.

This transformation makes it possible to enforce room capacities with a standard maximum-flow algorithm.

---

### 4 — Represent waiting

An ant may remain in the same room between two steps:

```text
(room, t, "exit")
        │
        ▼
(room, t+1, "entry")
```

Waiting is allowed by the algorithm but is not displayed in the final `E1`, `E2`, `E3...` output.

---

### 5 — Represent movements through tunnels

For a tunnel connecting rooms `A` and `B`, both directions are represented:

```text
(A, t, "exit") ─────► (B, t+1, "entry")

(B, t, "exit") ─────► (A, t+1, "entry")
```

This corresponds to the undirected physical tunnels of the ant hill.

---

### 6 — Compute the maximum flow

The program adds a technical `SOURCE` and `SINK`, then computes:

```python
flow_value, flow = nx.maximum_flow(
    time_graph,
    source,
    sink
)
```

`flow_value` represents the number of ants that can reach the dormitory for the tested duration.

If:

```python
flow_value < ant_count
```

the duration is too short.

If:

```python
flow_value == ant_count
```

every ant can reach `Sd`.

Because durations are tested in increasing order, the **first successful duration is the minimum duration**.

---

### 7 — Reconstruct one path per ant

The maximum-flow result describes a global flow.

The program first keeps only edges carrying positive flow:

```python
remaining_flow = {}
```

Then each ant follows one available unit of flow from `SOURCE` to `SINK`.

Every time an edge is assigned to an ant:

```python
remaining_flow[(position, next_node)] -= 1
```

one unit is removed so that the same flow unit cannot be assigned twice.

---

### 8 — Build the required movement steps

The reconstructed paths are converted into movements:

```text
+++ E1 +++
f1 - Sv - S1
f2 - Sv - S2

+++ E2 +++
f1 - S1 - Sd
f2 - S2 - Sd
```

Only real room-to-room movements are displayed.

---

## 🧠 Algorithm overview

```text
┌─────────────────────┐
│   Ant-hill data     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Physical graph    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Shortest path Sv-Sd │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Time-expanded graph │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Maximum flow     │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
Not enough      All ants
   flow          arrive
     │           │
     ▼           ▼
 Test T+1   Reconstruct paths
                 │
                 ▼
           Build E1, E2...
                 │
                 ▼
           Display solution
```

---

## 📁 Repository structure

```text
uneviedefourmi/
│
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
│
├── .gitignore
├── ants.py
├── main.py
├── README.md
└── requirements.txt
```

---

## 🧩 File responsibilities

### `main.py`

Contains the main resolution process:

- integration of the nine ant-hill datasets;
- selection of the ant hill;
- physical graph creation;
- shortest-path lower bound;
- time-expanded graph construction;
- waiting transitions;
- tunnel transitions;
- maximum-flow computation;
- search for the optimal duration;
- terminal output;
- graphical animation.

### `ants.py`

Contains the parts dedicated to individual ant movements:

- positive-flow filtering;
- remaining-flow management;
- reconstruction of one path per ant;
- conversion of paths into `E1`, `E2`, `E3`, ... movements.

### `fourmilieres/`

Contains the nine exercise datasets used by the project.

### `requirements.txt`

Project dependencies:

```text
networkx
matplotlib
```

---

## 📊 Available ant hills

| Ant hill | Ants | Optimal duration |
|:---|---:|---:|
| `zero` | 2 | 2 |
| `un` | 5 | 7 |
| `deux` | 5 | 1 |
| `trois` | 5 | 7 |
| `quatre` | 10 | 9 |
| `cinq` | 50 | 11 |
| `3D` | 50 | 14 |
| `mort` | 30 | 9 |
| `at-ant` | 100 | 15 |

---

## 🚀 Installation

### Requirements

- Python 3
- pip

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

In `main.py`, select the ant hill:

```python
name = "zero"
```

Available values:

```text
zero
un
deux
trois
quatre
cinq
3D
mort
at-ant
```

Then run:

```bash
python main.py
```

---

## 💻 Example output

For the `zero` ant hill:

```text
Ant hill: zero
Ants: 2
Rooms: 4
Tunnels: 4

Minimum duration: 2 step(s)

+++ E1 +++
f1 - Sv - S1
f2 - Sv - S2

+++ E2 +++
f1 - S1 - Sd
f2 - S2 - Sd
```

---

## 🔍 Technical choices

### Why use a time-expanded graph?

A normal graph represents the geometry of the ant hill, but not the evolution of the ants over time.

The time-expanded graph adds the temporal dimension required to model:

- simultaneous movements;
- waiting;
- room occupation at every step;
- room capacities;
- arrival at a precise final time.

### Why split each room into `entry` and `exit`?

Maximum-flow algorithms naturally apply capacities to edges.

Room capacity is therefore transformed into an edge capacity:

```text
(room, t, "entry")
        │
        │ capacity = room capacity
        ▼
(room, t, "exit")
```

### Why test durations one by one?

The shortest path gives the first possible duration.

The program then tests:

```text
T
T + 1
T + 2
...
```

The first duration for which the maximum flow is equal to the number of ants is therefore the optimal duration.

---

## 🖥️ Visualization

After the optimal movements are calculated, the physical graph is displayed with NetworkX and Matplotlib.

For every step, the visualization updates the number of ants currently located in each room.

The node positions remain fixed during the animation to make the movements easier to follow.

---

## ✅ Results

The solver successfully handles all nine provided ant hills, including:

- simple parallel paths;
- narrow corridors;
- dead-end branches;
- multiple bottlenecks;
- dense networks;
- large instances with up to **100 ants**.

The program determines the minimum duration and reconstructs the individual ant movements for each case.

---

## 🎓 Concepts used

This project applies several important computer-science concepts:

- graph theory;
- shortest paths;
- directed and undirected graphs;
- graph transformation;
- maximum flow;
- capacity constraints;
- temporal modeling;
- algorithmic optimization;
- path reconstruction;
- data visualization.

---

## 🏁 Conclusion

This project transforms a movement problem into a **maximum-flow problem on a time-expanded graph**.

The physical graph represents the structure of the ant hill, while the temporal graph represents what can happen at each step.

By combining:

```text
Shortest path
      +
Time-expanded graph
      +
Maximum flow
      +
Path reconstruction
```

the program is able to determine the **minimum number of steps** required for all ants to reach the dormitory while respecting room capacities.

---

<div align="center">

### 🐜 From `Sv` to `Sd` — one optimal step at a time.

</div>
