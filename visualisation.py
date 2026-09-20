"""Graph animation for the ant-hill project."""

import matplotlib.pyplot as plt
import networkx as nx


def animate_solution(graph, ant_count, steps, ant_hill_name):
    """Display the initial state and every movement step on the physical graph."""
    ant_positions = {}  # Maps each ant number to its current room.

    for ant in range(1, ant_count + 1):  # Goes through every ant before the first movement.
        ant_positions[ant] = "Sv"  # Places every ant in the vestibule.

    room_positions = nx.spring_layout(graph, seed=42)  # Keeps room coordinates stable between frames.
    figure, axis = plt.subplots(figsize=(11, 7))  # Creates the drawing window.
    states_to_display = [[]] + steps  # Adds the initial state before E1.

    for step_number, movements in enumerate(states_to_display):  # Shows the initial state and every step.
        for ant, origin, destination in movements:  # Applies the current step movements.
            ant_positions[ant] = destination  # Updates the ant position.

        labels = {}  # Stores room labels.

        for room in graph.nodes:  # Goes through every room.
            quantity = 0  # Starts occupancy at zero.

            for position in ant_positions.values():  # Reads every ant position.
                if position == room:  # Checks whether the ant is in this room.
                    quantity += 1  # Increments room occupancy.

            labels[room] = f"{room}\n{quantity} ant(s)"  # Creates the displayed room label.

        axis.clear()  # Clears the previous frame.

        nx.draw(
            graph,
            room_positions,
            ax=axis,
            labels=labels,
            node_size=2800,
            node_color="#60e5c5",
            edge_color="#60718b",
            font_weight="bold",
        )  # Draws the graph.

        axis.set_title(f"Ant hill {ant_hill_name} — step {step_number}")  # Displays name and step.
        figure.canvas.draw_idle()  # Refreshes the drawing.
        plt.pause(1.2)  # Keeps the frame visible before the next one.

    plt.show()  # Keeps the last frame open.
