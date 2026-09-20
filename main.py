"""Solves and animates an ant hill whose data is already prepared."""

import matplotlib.pyplot as plt  # Gives access to functions that create and update the animation window.
import networkx as nx  # Gives access to graphs, shortest paths and maximum-flow computation.

from ants import build_ant_paths_and_steps  # Imports only the original STEP 3 and STEP 4 blocks moved to ants.py.


def main():  # Groups all program instructions inside a function called main.
    # ======================================================================
    # STEP 1 — INTEGRATE THE DATA, CHOOSE AN ANT HILL AND CREATE ITS GRAPH
    # ======================================================================

    ant_hills = {
        "zero": {
            "ants": 2,
            "capacities": {"Sv": 2, "Sd": 2, "S1": 1, "S2": 1},
            "tunnels": [("Sv", "S1"), ("Sv", "S2"), ("S1", "Sd"), ("S2", "Sd")],
        },
        "un": {
            "ants": 5,
            "capacities": {"Sv": 5, "Sd": 5, "S1": 1, "S2": 1},
            "tunnels": [("Sv", "S1"), ("S1", "S2"), ("S2", "Sd")],
        },
        "deux": {
            "ants": 5,
            "capacities": {"Sv": 5, "Sd": 5, "S1": 1, "S2": 1},
            "tunnels": [("Sv", "S1"), ("S1", "S2"), ("S2", "Sd"), ("Sd", "Sv")],
        },
        "trois": {
            "ants": 5,
            "capacities": {"Sv": 5, "Sd": 5, "S1": 1, "S2": 1, "S3": 1, "S4": 1},
            "tunnels": [("Sv", "S1"), ("S1", "S2"), ("S4", "Sd"), ("S1", "S4"), ("S2", "S3")],
        },
        "quatre": {
            "ants": 10,
            "capacities": {
                "Sv": 10, "Sd": 10, "S1": 2, "S2": 1, "S3": 1,
                "S4": 2, "S5": 1, "S6": 1,
            },
            "tunnels": [
                ("S3", "S4"), ("Sv", "S1"), ("S1", "S2"),
                ("S2", "S4"), ("S4", "S5"), ("S5", "Sd"),
                ("S4", "S6"), ("S6", "Sd"), ("S1", "S3"),
            ],
        },
        "cinq": {
            "ants": 50,
            "capacities": {
                "Sv": 50, "Sd": 50, "S1": 8, "S2": 4, "S3": 2, "S4": 4,
                "S5": 2, "S6": 4, "S7": 2, "S8": 5, "S9": 1, "S10": 1,
                "S11": 1, "S12": 1, "S13": 4, "S14": 2,
            },
            "tunnels": [
                ("S1", "S2"), ("S2", "S3"), ("S3", "S4"), ("S4", "Sd"),
                ("Sv", "S1"), ("S2", "S5"), ("S5", "S4"), ("S13", "Sd"),
                ("S8", "S12"), ("S12", "S13"), ("S6", "S7"), ("S7", "S9"),
                ("S9", "S14"), ("S14", "Sd"), ("S7", "S10"), ("S10", "S14"),
                ("S1", "S6"), ("S6", "S8"), ("S8", "S11"), ("S11", "S13"),
            ],
        },
        "3D": {
            "ants": 50,
            "capacities": {
                "Sv": 50, "Sd": 50, "S1": 5, "S2": 6, "S3": 1, "S4": 3,
                "S5": 2, "S6": 4, "S7": 5, "S8": 4, "S9": 2,
            },
            "tunnels": [
                ("Sv", "S1"), ("Sv", "S2"), ("S1", "S6"), ("S1", "S8"),
                ("S2", "S7"), ("S3", "S4"), ("S3", "S5"), ("S3", "S8"),
                ("S3", "S9"), ("S4", "S5"), ("S4", "Sd"), ("S5", "S6"),
                ("S6", "S7"), ("S7", "S9"), ("S9", "Sd"),
            ],
        },
        "mort": {
            "ants": 30,
            "capacities": {
                "Sv": 30, "Sd": 30, "S1": 4, "S2": 3, "S3": 2, "S4": 3,
                "S5": 4, "S6": 2, "S7": 2, "S8": 3, "S9": 5, "S10": 5,
            },
            "tunnels": [
                ("Sv", "S1"), ("Sv", "S2"), ("Sv", "S3"), ("Sv", "S4"),
                ("Sv", "S5"), ("Sv", "S6"), ("Sv", "S7"), ("Sv", "S8"),
                ("S1", "S2"), ("S1", "S3"), ("S1", "S4"), ("S1", "S5"),
                ("S1", "S6"), ("S1", "S7"), ("S1", "S8"), ("S1", "S9"),
                ("S2", "S3"), ("S2", "S4"), ("S2", "S5"), ("S2", "S6"),
                ("S2", "S7"), ("S2", "S8"), ("S2", "S9"), ("S3", "S4"),
                ("S3", "S5"), ("S3", "S6"), ("S3", "S7"), ("S3", "S8"),
                ("S3", "S9"), ("S4", "S5"), ("S4", "S6"), ("S4", "S7"),
                ("S4", "S8"), ("S4", "S9"), ("S5", "S6"), ("S5", "S7"),
                ("S5", "S8"), ("S5", "S9"), ("S6", "S7"), ("S6", "S8"),
                ("S6", "S9"), ("S7", "S8"), ("S7", "S9"), ("S8", "S9"),
                ("S9", "S10"), ("S10", "Sd"),
            ],
        },
        "at-ant": {
            "ants": 100,
            "capacities": {
                "Sv": 100, "Sd": 100, "S1": 50, "S2": 50, "S3": 50,
                "S4": 1, "S5": 1, "S6": 3, "S7": 3, "S8": 7, "S9": 5,
                "S10": 5, "S11": 3, "S12": 3, "S13": 10, "S14": 20,
                "S15": 1, "S16": 1, "S17": 30, "S18": 10, "S19": 5,
                "S20": 5, "S21": 30,
            },
            "tunnels": [
                ("Sv", "S1"), ("S1", "S2"), ("S2", "S3"), ("S3", "S4"),
                ("S4", "S5"), ("S5", "Sd"), ("Sv", "S6"), ("S6", "S7"),
                ("S7", "S8"), ("S8", "S9"), ("S9", "S10"), ("S10", "Sd"),
                ("Sv", "S11"), ("S11", "S12"), ("S12", "S13"), ("S13", "S14"),
                ("S14", "S15"), ("S15", "Sd"), ("Sv", "S16"), ("S16", "S17"),
                ("S17", "S18"), ("S18", "S19"), ("S19", "S20"), ("S20", "Sd"),
                ("S21", "S3"), ("S21", "S8"), ("S21", "S13"), ("S21", "S18"),
            ],
        },
    }

    name = "zero"  # Chooses the ant hill stored under the key "zero"; this value can be replaced by another name.
    data = ant_hills[name]  # Retrieves the complete sub-dictionary corresponding to the selected name.
    ant_count = data["ants"]  # Reads the total number F of ants to move.

    graph = nx.Graph()  # Creates an empty undirected graph because a tunnel can be used in both directions.

    for room, capacity in data["capacities"].items():  # Goes through each room name and its capacity.
        graph.add_node(room, capacity=capacity)  # Adds this room as a node and stores its capacity.

    graph.add_edges_from(data["tunnels"])  # Adds all pairs of rooms representing the tunnels.

    print(f"Ant hill: {name}")  # Displays the selected ant hill name.
    print(f"Ants: {ant_count}")  # Displays the number of ants that must reach the dormitory.
    print(f"Rooms: {graph.number_of_nodes()}")  # Displays the number of graph nodes.
    print(f"Tunnels: {graph.number_of_edges()}")  # Displays the number of graph edges.

    # ======================================================================
    # STEP 2 — TEST DURATIONS WITH A TIME-EXPANDED GRAPH
    # ======================================================================

    start_duration = nx.shortest_path_length(graph, "Sv", "Sd")  # Computes the minimum number of tunnels one ant must cross from Sv to Sd.
    steps = None  # Indicates that no feasible movement list has been found yet.
    optimal_duration = None  # Indicates that the minimum duration has not been found yet.

    for duration in range(start_duration, start_duration + ant_count):  # Tests possible durations in increasing order from the shortest path.
        time_graph = nx.DiGraph()  # Creates a directed graph representing the rooms at each instant of this duration.
        source = "SOURCE"  # Creates the technical node from which the F flow units start.
        sink = "SINK"  # Creates the technical node into which the F flow units must arrive.

        for time in range(duration + 1):  # Goes through all available instants from t=0 to t=duration included.
            for room in graph.nodes:  # Goes through all physical rooms to copy them at the current instant.
                capacity = graph.nodes[room]["capacity"]  # Retrieves the maximum capacity stored on the physical room.
                entry = (room, time, "entry")  # Represents the moment when ants enter this room at this instant.
                exit_node = (room, time, "exit")  # Represents the moment when ants leave this room at the same instant.
                time_graph.add_edge(entry, exit_node, capacity=capacity)  # Limits entry-to-exit passage to the room capacity.

        for time in range(duration):  # Goes through every time transition from t to t+1.
            for room in graph.nodes:  # Goes through all rooms to allow ants to wait there.
                wait_departure = (room, time, "exit")  # Represents the occupied room before waiting.
                wait_arrival = (room, time + 1, "entry")  # Represents the same room at the next instant.
                time_graph.add_edge(wait_departure, wait_arrival, capacity=ant_count)  # Adds the action of staying in the same room.

            for room_a, room_b in graph.edges:  # Goes through every physical tunnel connecting rooms A and B.
                departure_a = (room_a, time, "exit")  # Represents an ant leaving A at the current instant.
                arrival_b = (room_b, time + 1, "entry")  # Represents this ant arriving in B at the next instant.
                departure_b = (room_b, time, "exit")  # Represents an ant leaving B at the current instant.
                arrival_a = (room_a, time + 1, "entry")  # Represents this ant arriving in A at the next instant.
                time_graph.add_edge(departure_a, arrival_b, capacity=ant_count)  # Allows movement through the tunnel from A to B.
                time_graph.add_edge(departure_b, arrival_a, capacity=ant_count)  # Also allows movement from B to A.

        general_departure = ("Sv", 0, "entry")  # Represents the vestibule entry at the first instant.
        general_arrival = ("Sd", duration, "exit")  # Represents the dormitory exit at the tested final instant.
        time_graph.add_edge(source, general_departure, capacity=ant_count)  # Injects at most F flow units into the initial vestibule.
        time_graph.add_edge(general_arrival, sink, capacity=ant_count)  # Allows at most F units that reached the dormitory to enter the sink.

        flow_value, flow = nx.maximum_flow(time_graph, source, sink)  # Computes how many ants can reach Sd and how the flow circulates.

        if flow_value < ant_count:  # Compares possible arrivals with the total number of ants.
            continue  # Abandons this duration because it is too short and tests the next one.

        optimal_duration = duration  # Stores the first duration capable of carrying all ants; it is therefore minimal.

        paths, steps = build_ant_paths_and_steps(
            time_graph, flow, ant_count, duration, source, sink
        )  # Runs the original path-reconstruction and E1/E2/E3 blocks, now cut into ants.py.

        break  # Leaves the duration loop because the first feasible solution is optimal.

    if steps is None:  # Checks that one tested duration actually produced a solution.
        raise RuntimeError("No solution found.")  # Stops clearly if no solution was obtained.

    # ======================================================================
    # STEP 5 — DISPLAY THE SOLUTION
    # ======================================================================

    print(f"\nMinimum duration: {optimal_duration} step(s)")  # Displays the minimum number of steps found by maximum flow.

    for number, movements in enumerate(steps, start=1):  # Goes through the sub-lists while numbering them from 1.
        print(f"+++ E{number} +++")  # Displays the step title in the format requested by the exercise.

        for ant, origin, destination in movements:  # Goes through every movement planned during this step.
            print(f"f{ant} - {origin} - {destination}")  # Displays the ant identifier, origin room and destination room.

    # ======================================================================
    # STEP 6 — SHOW THE MOVEMENT ON THE GRAPH
    # ======================================================================

    ant_positions = {}  # Creates a dictionary associating each ant number with its current room.

    for ant in range(1, ant_count + 1):  # Goes through all ants before the first movement.
        ant_positions[ant] = "Sv"  # Places every ant in the vestibule, as required by the initial state.

    room_positions = nx.spring_layout(graph, seed=42)  # Computes fixed visual positions so the drawing does not move between steps.
    figure, axis = plt.subplots(figsize=(11, 7))  # Creates an 11-by-7-inch window and gets its drawing area.
    states_to_display = [[]] + steps  # Adds an empty initial step before E1.

    for number, movements in enumerate(states_to_display):  # Goes through initial state 0 and all solution steps.
        for ant, origin, destination in movements:  # Goes through movements that must be applied to obtain the current state.
            ant_positions[ant] = destination  # Replaces the previous room of this ant with its new room.

        labels = {}  # Creates the dictionary containing the text displayed inside every node.

        for room in graph.nodes:  # Goes through all rooms to compute their current occupancy.
            quantity = 0  # Initializes the number of ants in this room to zero.

            for position in ant_positions.values():  # Goes through the room currently occupied by every ant.
                if position == room:  # Checks whether the observed ant is in the room being counted.
                    quantity += 1  # Adds one ant to this room counter.

            labels[room] = f"{room}\n{quantity} ant(s)"  # Prepares a label containing the room name and occupancy.

        axis.clear()  # Clears the previous state drawing before showing the new one.
        nx.draw(
            graph,
            room_positions,
            ax=axis,
            labels=labels,
            node_size=2800,
            node_color="#60e5c5",
            edge_color="#60718b",
            font_weight="bold",
        )
        axis.set_title(f"Ant hill {name} — step {number}")  # Displays the ant hill name and visible step above the graph.
        figure.canvas.draw_idle()  # Asks Matplotlib to refresh the image after the changes.
        plt.pause(1.2)  # Keeps this image visible for 1.2 seconds before moving to the next one.

    plt.show()  # Keeps the last state window open after the animation is complete.


if __name__ == "__main__":  # Checks that this file is executed directly and is not only imported.
    main()  # Calls main to run all program steps in order.
