"""Reconstruct individual ant paths and create the E1, E2, E3... movements."""


def build_ant_paths_and_steps(time_graph, flow, ant_count, duration, source, sink):
    # ==================================================================
    # STEP 3 — TRANSFORM THE FLOW INTO A PATH FOR EACH ANT
    # ==================================================================

    remaining_flow = {}  # Creates an empty dictionary containing only edges actually used by the flow.

    for departure, destinations in flow.items():  # Goes through each departure node returned by maximum_flow.
        for arrival, quantity in destinations.items():  # Goes through each destination and the quantity sent to it.
            if quantity > 0:  # Keeps only an edge carrying at least one unit of flow.
                remaining_flow[(departure, arrival)] = quantity  # Stores how many units are still available on this edge.

    paths = []  # Creates the list that will contain the number and time path of each ant.

    for ant in range(1, ant_count + 1):  # Goes through ant identifiers 1, 2, ..., F.
        position = source  # Places the beginning of the current ant path on SOURCE.
        path = [source]  # Initializes its path with SOURCE as the first element.

        while position != sink:  # Continues while the current ant has not reached SINK.
            next_node = None  # Prepares an empty variable that will contain the next node.

            for neighbor in time_graph.successors(position):  # Goes through every node directly reachable from the current position.
                available_quantity = remaining_flow.get((position, neighbor), 0)  # Reads remaining flow on this edge, or 0 if unused.

                if available_quantity > 0:  # Checks that this edge still contains one unit that can be assigned to an ant.
                    next_node = neighbor  # Chooses this neighbor as the next position of the current path.
                    break  # Stops searching because a valid continuation has been found.

            if next_node is None:  # Detects the abnormal case where no flow path can continue to the sink.
                raise RuntimeError("Unable to reconstruct the paths.")  # Stops the program with a clear explanation.

            remaining_flow[(position, next_node)] -= 1  # Removes one unit because it has just been assigned to this ant.
            path.append(next_node)  # Adds the selected node to the end of this ant path.
            position = next_node  # Moves the cursor to this node to search for the next part of the path.

        paths.append((ant, path))  # Stores the complete path together with the corresponding ant number.

    # ==================================================================
    # STEP 4 — CREATE THE E1, E2, E3... MOVEMENTS
    # ==================================================================

    steps = []  # Creates the list that will contain all solution steps.

    for _ in range(duration):  # Repeats once for every step from 1 to the optimal duration.
        steps.append([])  # Adds an empty sub-list that will receive the movements of this step.

    for ant, path in paths:  # Goes through the time path associated with each ant.
        for node_a, node_b in zip(path, path[1:]):  # Forms every pair of consecutive nodes in the path.
            if not isinstance(node_a, tuple) or not isinstance(node_b, tuple):  # Detects SOURCE and SINK, which are strings.
                continue  # Ignores this technical pair because it is not a movement between two rooms.

            room_a, time_a, side_a = node_a  # Splits the name, time and side of the first time node.
            room_b, time_b, side_b = node_b  # Splits the name, time and side of the second time node.
            moves_forward_in_time = time_b == time_a + 1  # Checks that the transition leads to the next instant.
            changes_room = room_a != room_b  # Checks that the ant moves instead of waiting in the same room.
            crosses_a_tunnel = side_a == "exit" and side_b == "entry"  # Checks that the transition leaves an exit and reaches an entry.

            if moves_forward_in_time and changes_room and crosses_a_tunnel:  # Keeps only a real movement through a tunnel.
                movement = (ant, room_a, room_b)  # Creates the requested triplet: ant number, origin and destination.
                steps[time_b - 1].append(movement)  # Stores an arrival at t=1 in E1, at t=2 in E2, and so on.

    return paths, steps  # Returns the two objects produced by the original reconstruction blocks.
