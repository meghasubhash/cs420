import argparse
import heapq
import itertools
from collections import deque

# Parsing the .bwp file to get initial and goal states
def parse_bwp_file(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file]

    S, B, M = map(int, lines[0].split())
    separator_indices = [i for i, line in enumerate(lines) if line.startswith('>>>')]

    initial_state_start = separator_indices[0] + 1
    initial_state_end = separator_indices[1]
    initial_state = [list(lines[i]) for i in range(initial_state_start, initial_state_end)]

    goal_state_start = separator_indices[1] + 1
    goal_state_end = separator_indices[2] if len(separator_indices) > 2 else len(lines)
    goal_state = [list(lines[i]) for i in range(goal_state_start, goal_state_end)]

    goal_state = goal_state[:S]
    return S, B, M, initial_state, goal_state

# Class for representing a state in the Blocksworld
class State:
    def __init__(self, stacks):
        self.stacks = stacks

    def __eq__(self, other):
        return self.stacks == other.stacks

    def __hash__(self):
        return hash(tuple(tuple(stack) for stack in self.stacks))

    def __str__(self):
        return "\n".join("".join(stack) for stack in self.stacks)

    def is_goal(self, goal_state):
        return self.stacks == goal_state.stacks

    def generate_successors(self):
        successors = []
        num_stacks = len(self.stacks)
        for i in range(num_stacks):
            if not self.stacks[i]:
                continue
            block_to_move = self.stacks[i][-1]
            for j in range(num_stacks):
                if i != j:
                    new_stacks = [stack[:] for stack in self.stacks]
                    new_stacks[i].pop()
                    new_stacks[j].append(block_to_move)
                    successors.append(State(new_stacks))
        return successors

# Class for representing a node in the search tree
class Node:
    def __init__(self, state, parent=None, depth=0, cost=0):
        self.state = state
        self.parent = parent
        self.depth = depth  # g(n): path cost from start to node
        self.cost = cost    # f(n): estimated total cost (g + h)

    def print_solution_path(self):
        if self.parent:
            self.parent.print_solution_path()
        print(self.state)
        print("-----")

    def get_solution_path(self):
        path = []
        current_node = self
        while current_node:
            path.append(current_node.state)
            current_node = current_node.parent
        return list(reversed(path))

# Heuristic: Number of blocks out of place
def h1(current_state, goal_state):
    misplaced = 0
    for i in range(len(current_state.stacks)):
        for j in range(min(len(current_state.stacks[i]), len(goal_state.stacks[i]))):
            if current_state.stacks[i][j] != goal_state.stacks[i][j]:
                misplaced += 1
    return misplaced

def h0(current_state, goal_state):
    return 0  # No heuristic, equivalent to BFS


# A* search algorithm
def a_star(initial_state, goal_state, max_iters, heuristic):
    frontier = []
    # Unique counter to avoid comparing Nodes directly when f(n) values are the same
    counter = itertools.count()

    # Push initial state with f(n) = 0 + h(initial)
    heapq.heappush(frontier, (0, next(counter), Node(initial_state)))  # f(n), counter, node
    explored = set()
    iters = 0
    maxq = 1

    while frontier and iters < max_iters:
        # Pop the node with the smallest f(n)
        f_n, _, node = heapq.heappop(frontier)
        explored.add(node.state)

        # Check if we reached the goal
        if node.state.is_goal(goal_state):
            print("Solution found:")
            node.print_solution_path()
            planlen = len(node.get_solution_path()) - 1
            return {'planlen': planlen, 'iters': iters, 'maxq': maxq}

        # Generate successors and push them to the priority queue
        for successor_state in node.state.generate_successors():
            if successor_state not in explored and all(n.state != successor_state for _, _, n in frontier):
                g_n = node.depth + 1  # g(n) is the depth of the node
                h_n = heuristic(successor_state, goal_state)  # Calculate h(n) using the provided heuristic
                f_n = g_n + h_n  # f(n) = g(n) + h(n)
                successor_node = Node(successor_state, parent=node, depth=g_n)
                # Push (f(n), counter, node) into the priority queue
                heapq.heappush(frontier, (f_n, next(counter), successor_node))

        # Update iteration count and max queue size
        iters += 1
        maxq = max(maxq, len(frontier))

    # If no solution was found
    print("No solution found or max iterations reached.")
    return {'planlen': 'FAILED', 'iters': iters, 'maxq': maxq}

# Main function to handle argument parsing and execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve the Blocksworld problem with A*.")
    parser.add_argument("file", help="Path to the .bwp file")
    parser.add_argument("-H", type=str, default="H1", help="Heuristic to use (H1 or custom)")
    parser.add_argument("-MAX_ITERS", type=int, default=100000, help="Maximum number of iterations (default: 100000)")
    args = parser.parse_args()

    # Parse the input file to get the problem
    S, B, M, initial_state, goal_state = parse_bwp_file(args.file)
    
    # Create State objects for initial and goal states
    initial_state = State(initial_state)
    goal_state = State(goal_state)

    # Choose heuristic function
    if args.H == "H1":
        heuristic = h1
    else:
        raise ValueError(f"Unknown heuristic: {args.H}")

    # Run A* search
    stats = a_star(initial_state, goal_state, max_iters=args.MAX_ITERS, heuristic=heuristic)

    # Print summary statistics
    print(f"statistics: {args.file} method Astar planlen {stats['planlen']} iters {stats['iters']} maxq {stats['maxq']}")
