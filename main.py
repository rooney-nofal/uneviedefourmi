"""Main entry point for the ant-hill project."""

from ants import solve_ant_hill
from visualisation import animate_solution


ANT_HILLS = {'zero': {'ants': 2, 'capacities': {'Sv': 2, 'Sd': 2, 'S1': 1, 'S2': 1}, 'tunnels': [('Sv', 'S1'), ('Sv', 'S2'), ('S1', 'Sd'), ('S2', 'Sd')]}, 'un': {'ants': 5, 'capacities': {'Sv': 5, 'Sd': 5, 'S1': 1, 'S2': 1}, 'tunnels': [('Sv', 'S1'), ('S1', 'S2'), ('S2', 'Sd')]}, 'deux': {'ants': 5, 'capacities': {'Sv': 5, 'Sd': 5, 'S1': 1, 'S2': 1}, 'tunnels': [('Sv', 'S1'), ('S1', 'S2'), ('S2', 'Sd'), ('Sd', 'Sv')]}, 'trois': {'ants': 5, 'capacities': {'Sv': 5, 'Sd': 5, 'S1': 1, 'S2': 1, 'S3': 1, 'S4': 1}, 'tunnels': [('Sv', 'S1'), ('S1', 'S2'), ('S4', 'Sd'), ('S1', 'S4'), ('S2', 'S3')]}, 'quatre': {'ants': 10, 'capacities': {'Sv': 10, 'Sd': 10, 'S1': 2, 'S2': 1, 'S3': 1, 'S4': 2, 'S5': 1, 'S6': 1}, 'tunnels': [('S3', 'S4'), ('Sv', 'S1'), ('S1', 'S2'), ('S2', 'S4'), ('S4', 'S5'), ('S5', 'Sd'), ('S4', 'S6'), ('S6', 'Sd'), ('S1', 'S3')]}, 'cinq': {'ants': 50, 'capacities': {'Sv': 50, 'Sd': 50, 'S1': 8, 'S2': 4, 'S3': 2, 'S4': 4, 'S5': 2, 'S6': 4, 'S7': 2, 'S8': 5, 'S9': 1, 'S10': 1, 'S11': 1, 'S12': 1, 'S13': 4, 'S14': 2}, 'tunnels': [('S1', 'S2'), ('S2', 'S3'), ('S3', 'S4'), ('S4', 'Sd'), ('Sv', 'S1'), ('S2', 'S5'), ('S5', 'S4'), ('S13', 'Sd'), ('S8', 'S12'), ('S12', 'S13'), ('S6', 'S7'), ('S7', 'S9'), ('S9', 'S14'), ('S14', 'Sd'), ('S7', 'S10'), ('S10', 'S14'), ('S1', 'S6'), ('S6', 'S8'), ('S8', 'S11'), ('S11', 'S13')]}, '3D': {'ants': 50, 'capacities': {'Sv': 50, 'Sd': 50, 'S1': 5, 'S2': 6, 'S3': 1, 'S4': 3, 'S5': 2, 'S6': 4, 'S7': 5, 'S8': 4, 'S9': 2}, 'tunnels': [('Sv', 'S1'), ('Sv', 'S2'), ('S1', 'S6'), ('S1', 'S8'), ('S2', 'S7'), ('S3', 'S4'), ('S3', 'S5'), ('S3', 'S8'), ('S3', 'S9'), ('S4', 'S5'), ('S4', 'Sd'), ('S5', 'S6'), ('S6', 'S7'), ('S7', 'S9'), ('S9', 'Sd')]}, 'mort': {'ants': 30, 'capacities': {'Sv': 30, 'Sd': 30, 'S1': 4, 'S2': 3, 'S3': 2, 'S4': 3, 'S5': 4, 'S6': 2, 'S7': 2, 'S8': 3, 'S9': 5, 'S10': 5}, 'tunnels': [('Sv', 'S1'), ('Sv', 'S2'), ('Sv', 'S3'), ('Sv', 'S4'), ('Sv', 'S5'), ('Sv', 'S6'), ('Sv', 'S7'), ('Sv', 'S8'), ('S1', 'S2'), ('S1', 'S3'), ('S1', 'S4'), ('S1', 'S5'), ('S1', 'S6'), ('S1', 'S7'), ('S1', 'S8'), ('S1', 'S9'), ('S2', 'S3'), ('S2', 'S4'), ('S2', 'S5'), ('S2', 'S6'), ('S2', 'S7'), ('S2', 'S8'), ('S2', 'S9'), ('S3', 'S4'), ('S3', 'S5'), ('S3', 'S6'), ('S3', 'S7'), ('S3', 'S8'), ('S3', 'S9'), ('S4', 'S5'), ('S4', 'S6'), ('S4', 'S7'), ('S4', 'S8'), ('S4', 'S9'), ('S5', 'S6'), ('S5', 'S7'), ('S5', 'S8'), ('S5', 'S9'), ('S6', 'S7'), ('S6', 'S8'), ('S6', 'S9'), ('S7', 'S8'), ('S7', 'S9'), ('S8', 'S9'), ('S9', 'S10'), ('S10', 'Sd')]}, 'at-ant': {'ants': 100, 'capacities': {'Sv': 100, 'Sd': 100, 'S1': 50, 'S2': 50, 'S3': 50, 'S4': 1, 'S5': 1, 'S6': 3, 'S7': 3, 'S8': 7, 'S9': 5, 'S10': 5, 'S11': 3, 'S12': 3, 'S13': 10, 'S14': 20, 'S15': 1, 'S16': 1, 'S17': 30, 'S18': 10, 'S19': 5, 'S20': 5, 'S21': 30}, 'tunnels': [('Sv', 'S1'), ('S1', 'S2'), ('S2', 'S3'), ('S3', 'S4'), ('S4', 'S5'), ('S5', 'Sd'), ('Sv', 'S6'), ('S6', 'S7'), ('S7', 'S8'), ('S8', 'S9'), ('S9', 'S10'), ('S10', 'Sd'), ('Sv', 'S11'), ('S11', 'S12'), ('S12', 'S13'), ('S13', 'S14'), ('S14', 'S15'), ('S15', 'Sd'), ('Sv', 'S16'), ('S16', 'S17'), ('S17', 'S18'), ('S18', 'S19'), ('S19', 'S20'), ('S20', 'Sd'), ('S21', 'S3'), ('S21', 'S8'), ('S21', 'S13'), ('S21', 'S18')]}}


def main():
    """Select one ant hill, solve it and display the requested movements."""
    ant_hill_name = "zero"  # Replace with: un, deux, trois, quatre, cinq, 3D, mort or at-ant.
    data = ANT_HILLS[ant_hill_name]  # Retrieves the selected dataset.

    graph, ant_count, optimal_duration, steps = solve_ant_hill(data)  # Solves the selected ant hill.

    print(f"Ant hill: {ant_hill_name}")
    print(f"Ants: {ant_count}")
    print(f"Rooms: {graph.number_of_nodes()}")
    print(f"Tunnels: {graph.number_of_edges()}")
    print(f"\nMinimum duration: {optimal_duration} step(s)")

    for step_number, movements in enumerate(steps, start=1):  # Goes through E1, E2...
        print(f"+++ E{step_number} +++")

        for ant, origin, destination in movements:  # Goes through movements of this step.
            print(f"f{ant} - {origin} - {destination}")

    animate_solution(graph, ant_count, steps, ant_hill_name)  # Displays the graph step by step.


if __name__ == "__main__":
    main()
