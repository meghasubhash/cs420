import argparse
from collections import deque

def parse_bwp_file(file_path):
    with open(file_path, 'r') as file:
        # Read all lines and strip whitespace
        lines = [line.strip() for line in file]

    # First line contains S (number of stacks), B (number of blocks), M (number of moves)
    S, B, M = map(int, lines[0].split())
    
    # Locate separator lines (>>>>>>>>>)
    separator_indices = [i for i, line in enumerate(lines) if line.startswith('>>>')]

    # Parse the initial state: Between the first and second separator
    initial_state_start = separator_indices[0] + 1
    initial_state_end = separator_indices[1]
    initial_state = [list(lines[i]) for i in range(initial_state_start, initial_state_end)]

    # Parse the goal state: Between the second and third separator
    goal_state_start = separator_indices[1] + 1
    goal_state_end = separator_indices[2] if len(separator_indices) > 2 else len(lines)
    goal_state = [list(lines[i]) for i in range(goal_state_start, goal_state_end)]

    # Trim goal_state to exactly S stacks
    goal_state = goal_state[:S]

    return S, B, M, initial_state, goal_state

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

class Node:
    def __init__(self, state, parent=None, depth=0):
        self.state = state
        self.parent = parent
        self.depth = depth

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

def bfs(initial_state, goal_state, max_iters):
    frontier = deque([Node(initial_state)])  # Initialize the queue with the root node
    explored = set()  # To keep track of explored states
    iters = 0  # Track the number of iterations
    maxq = 1  # Track the maximum queue size

    while frontier and iters < max_iters:
        node = frontier.popleft()  # Get the first node from the frontier
        explored.add(node.state)  # Mark the current state as explored

        # Goal check
        if node.state.is_goal(goal_state):
            print("Solution found:")
            node.print_solution_path()  # Print the solution path
            planlen = len(node.get_solution_path()) - 1  # Subtract 1 to count moves, not states
            return {'planlen': planlen, 'iters': iters, 'maxq': maxq}

        # Expand node: Generate successors and create new Nodes
        for successor_state in node.state.generate_successors():
            if successor_state not in explored and all(n.state != successor_state for n in frontier):
                successor_node = Node(successor_state, parent=node, depth=node.depth + 1)
                frontier.append(successor_node)

        # Update iteration count and maximum queue size
        iters += 1
        maxq = max(maxq, len(frontier))

    # If the loop exits without finding a solution, return failure
    print("No solution found or max iterations reached.")
    return {'planlen': 'FAILED', 'iters': iters, 'maxq': maxq}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve the Blocksworld problem.")
    parser.add_argument("file", help="Path to the .bwp file")
    parser.add_argument("-MAX_ITERS", type=int, default=100000, help="Maximum number of iterations (default: 100000)")
    args = parser.parse_args()

    # Call the parser function with the file path provided
    S, B, M, initial_state, goal_state = parse_bwp_file(args.file)

    # Create State objects for initial and goal states
    initial_state = State(initial_state)
    goal_state = State(goal_state)

    # Run BFS to find the solution, with iteration limit
    stats = bfs(initial_state, goal_state, max_iters=args.MAX_ITERS)

    # Print summary statistics
    print(f"statistics: {args.file} method BFS planlen {stats['planlen']} iters {stats['iters']} maxq {stats['maxq']}")
