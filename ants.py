"""Core solver for the ant-hill project."""

import networkx as nx


def build_graph(data):
    """Build the physical ant-hill graph from one dataset."""
    graph = nx.Graph()  # Creates an undirected graph because tunnels can be used in both directions.

    for room, capacity in data["capacities"].items():  # Goes through every room and its capacity.
        graph.add_node(room, capacity=capacity)  # Adds the room and stores its capacity.

    graph.add_edges_from(data["tunnels"])  # Adds all tunnels.

    return graph


def solve_ant_hill(data):
    """Find the minimum duration and the movement list E1, E2, E3..."""
    ant_count = data["ants"]  # Reads the total number F of ants.
    graph = build_graph(data)  # Builds the physical graph.

    # ======================================================================
    # STEP 1 — TEST DURATIONS WITH A TIME-EXPANDED GRAPH
    # ======================================================================

    start_duration = nx.shortest_path_length(graph, "Sv", "Sd")  # Lower bound for one ant.
    steps = None  # No solution has been found yet.
    optimal_duration = None  # No optimal duration has been found yet.

    for duration in range(start_duration, start_duration + ant_count):  # Tests T in increasing order.
        time_graph = nx.DiGraph()  # Creates the directed time-expanded graph.
        source = "SOURCE"  # Technical node where the flow starts.
        sink = "SINK"  # Technical node where the flow ends.

        for time in range(duration + 1):  # Creates each instant from 0 to T.
            for room in graph.nodes:  # Copies each room at this instant.
                capacity = graph.nodes[room]["capacity"]  # Reads the room capacity.
                entry = (room, time, "entry")  # Entry side of the room.
                exit_node = (room, time, "exit")  # Exit side of the room.
                time_graph.add_edge(entry, exit_node, capacity=capacity)  # Enforces room capacity.

        for time in range(duration):  # Creates every transition from t to t+1.
            for room in graph.nodes:  # Allows an ant to wait.
                wait_departure = (room, time, "exit")  # Position before waiting.
                wait_arrival = (room, time + 1, "entry")  # Same room at the next instant.
                time_graph.add_edge(wait_departure, wait_arrival, capacity=ant_count)  # Adds waiting.

            for room_a, room_b in graph.edges:  # Goes through all tunnels.
                departure_a = (room_a, time, "exit")  # Departure from A.
                arrival_b = (room_b, time + 1, "entry")  # Arrival in B.
                departure_b = (room_b, time, "exit")  # Departure from B.
                arrival_a = (room_a, time + 1, "entry")  # Arrival in A.
                time_graph.add_edge(departure_a, arrival_b, capacity=ant_count)  # A to B.
                time_graph.add_edge(departure_b, arrival_a, capacity=ant_count)  # B to A.

        general_departure = ("Sv", 0, "entry")  # Initial vestibule entry.
        general_arrival = ("Sd", duration, "exit")  # Dormitory exit at tested time T.
        time_graph.add_edge(source, general_departure, capacity=ant_count)  # Injects F units.
        time_graph.add_edge(general_arrival, sink, capacity=ant_count)  # Collects F arrivals.

        flow_value, flow = nx.maximum_flow(time_graph, source, sink)  # Computes arrivals and global flow.

        if flow_value < ant_count:  # Checks whether all ants can arrive.
            continue  # Tests the next duration.

        optimal_duration = duration  # The first successful duration is minimal.

        # ==================================================================
        # STEP 2 — TRANSFORM GLOBAL FLOW INTO ONE PATH PER ANT
        # ==================================================================

        remaining_flow = {}  # Stores only edges that actually carry flow.

        for departure, destinations in flow.items():  # Goes through each flow departure node.
            for arrival, quantity in destinations.items():  # Goes through each destination and quantity.
                if quantity > 0:  # Keeps only used edges.
                    remaining_flow[(departure, arrival)] = quantity  # Stores available units.

        paths = []  # Will contain one reconstructed path per ant.

        for ant in range(1, ant_count + 1):  # Builds a path for ant 1 through ant F.
            position = source  # Starts at SOURCE.
            path = [source]  # Starts the path.

            while position != sink:  # Continues until SINK is reached.
                next_position = None  # Will store the next node.

                for neighbor in time_graph.successors(position):  # Goes through directly reachable nodes.
                    available_quantity = remaining_flow.get((position, neighbor), 0)  # Reads remaining flow.

                    if available_quantity > 0:  # Checks whether this edge can still be used.
                        next_position = neighbor  # Selects the neighbor.
                        break  # Stops searching after finding a valid continuation.

                if next_position is None:  # Detects an impossible reconstruction.
                    raise RuntimeError("Unable to reconstruct ant paths.")

                remaining_flow[(position, next_position)] -= 1  # Consumes one flow unit.
                path.append(next_position)  # Adds the selected node to the path.
                position = next_position  # Continues from this node.

            paths.append((ant, path))  # Stores the complete path.

        # ==================================================================
        # STEP 3 — CREATE THE MOVEMENTS E1, E2, E3...
        # ==================================================================

        steps = []  # Will contain every solution step.

        for _ in range(duration):  # Repeats once for each step.
            steps.append([])  # Adds an empty movement list.

        for ant, path in paths:  # Goes through each ant path.
            for node_a, node_b in zip(path, path[1:]):  # Forms consecutive node pairs.
                if not isinstance(node_a, tuple) or not isinstance(node_b, tuple):  # Ignores SOURCE and SINK.
                    continue

                room_a, time_a, side_a = node_a  # Splits the first time node.
                room_b, time_b, side_b = node_b  # Splits the second time node.
                moves_forward_in_time = time_b == time_a + 1  # Checks t -> t+1.
                changes_room = room_a != room_b  # Rejects waiting.
                crosses_tunnel = side_a == "exit" and side_b == "entry"  # Keeps exit -> entry moves.

                if moves_forward_in_time and changes_room and crosses_tunnel:  # Keeps a real tunnel movement.
                    movement = (ant, room_a, room_b)  # Ant number, origin, destination.
                    steps[time_b - 1].append(movement)  # Stores the movement in E1, E2...

        break  # Stops because the first feasible duration is optimal.

    if steps is None:  # Checks that a solution was found.
        raise RuntimeError("No solution found.")

    return graph, ant_count, optimal_duration, steps
