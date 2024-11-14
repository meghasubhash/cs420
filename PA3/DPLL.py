import sys

# Global counter for DPLL calls
dpll_calls = 0

def parse_cnf_file(filename):
    clauses = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            clause = [lit for lit in line.split() if lit != '0']  # Keep literals as strings
            clauses.append(clause)
    return clauses

def dpll(clauses, model):
    global dpll_calls
    dpll_calls += 1
    
    # Base case: Check if all clauses are satisfied
    if all(any(lit in model and model[lit] == 1 for lit in clause) for clause in clauses):
        return model
    
    # Check for any clause that is unsatisfied (unsatisfiable state)
    if any(all(lit in model and model[lit] == -1 for lit in clause) for clause in clauses):
        return None
    
    # Unit Clause Heuristic (UCH)
    for clause in clauses:
        unassigned = [lit for lit in clause if lit not in model]
        if len(unassigned) == 1:
            lit = unassigned[0]
            model[lit] = 1 if not lit.startswith('-') else -1  # Handle negated literals
            print(f"Assigning {lit} due to unit-clause heuristic.")
            return dpll(clauses, model)
    
    # Choose a literal to assign (choice-point)
    for clause in clauses:
        for lit in clause:
            if lit not in model:
                print(f"Choice-point assignment: {lit} = True")
                model[lit] = 1
                result = dpll(clauses, model)
                if result is not None:
                    return result
                print(f"Backtracking on {lit}")
                model[lit] = -1
                result = dpll(clauses, model)
                if result is not None:
                    return result
                del model[lit]
                return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python DPLL.py <filename> <literal>*")
        sys.exit(1)

    # Echo the command-line arguments
    print("Command-line arguments:", sys.argv)
    
    filename = sys.argv[1]
    extra_literals = sys.argv[2:]  # Keep extra literals as strings

    # Parse the input file to get clauses
    clauses = parse_cnf_file(filename)
    
    # Add extra literals as unit clauses (asserted facts)
    for lit in extra_literals:
        clauses.append([lit] if not lit.startswith('-') else [lit])

    # Initialize an empty model (truth assignment)
    model = {}

    # Run the DPLL algorithm
    result = dpll(clauses, model)
    
    if result is None:
        print("UNSATISFIABLE")
    else:
        print("SATISFIABLE")
        print("Model:", result)
    
    # Print the total number of DPLL calls
    print("Total DPLL calls:", dpll_calls)

if __name__ == "__main__":
    main()
