import sys
from collections import deque
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            for word in self.domains[var].copy():
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        i, j = self.crossword.overlaps[x, y]
        for x_word in self.domains[x].copy():
            has_overlap = False
            for y_word in self.domains[y]:
                # See if an x_word matches with a y_word at the overlap
                if x_word[i] == y_word[j]:
                    has_overlap = True

            if not has_overlap:
                self.domains[x].remove(x_word)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Build a list of arcs to queue
        arcs = list()
        for var in self.crossword.variables:
            for neighbor in self.crossword.neighbors(var):
                arcs.append((var, neighbor))

        # I'm using the built-in deque to avoid writing an extra class
        arc_queue = deque(arcs)
        # Follows the structure of the pseudocode provided in lecture
        while len(arc_queue) != 0:
            x, y = arc_queue.popleft()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                neighbors = self.crossword.neighbors(x)
                for z in neighbors:
                    # Update the other arcs with new info
                    if (z, x) not in arc_queue:
                        arc_queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Check if all variables are in assignment
        all_vars = (len(assignment) == len(self.crossword.variables))
        for var in assignment:
            # Ensure any var in assignment has a word
            if assignment[var] is None:
                return False
        # Otherwise, return if assignment is complete
        return all_vars

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # We can already assume that each node is node consistent
        for x_var in assignment:
            for y_var in self.crossword.neighbors(x_var):
                if y_var not in assignment:
                    continue

                x_assignment_null = assignment[x_var] is None
                y_assignment_null = assignment[y_var] is None
                if x_assignment_null or y_assignment_null:
                    # Avoid using NoneType object
                    continue

                i, j = self.crossword.overlaps[x_var, y_var]

                if assignment[x_var][i] != assignment[y_var][j]:
                    # Not arc consistent
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # elim_count is the number of options a word eliminates
        # for neighboring vars
        elim_count = {
            word: 0 for word in self.domains[var]
            # Ignore assigned words
            if word not in assignment.values()
        }

        for y_var in self.crossword.neighbors(var):
            i, j = self.crossword.overlaps[var, y_var]
            """
            Alternatively, I could've grouped words with
            the same character positions for each iteration,
            but it became a bunch of list management which
            seemed convoluted and memory inefficient
            """
            for x_word in elim_count:
                for y_word in self.domains[y_var]:
                    if x_word[i] != y_word[j]:
                        elim_count[x_word] += 1

        # This function will return a list of words sorted
        # based on their elimination count
        return sorted(elim_count, key=lambda x: elim_count[x])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        chosen = None
        for var in self.crossword.variables:
            if var in assignment:
                # We don't want to choose vars already assignmed
                continue

            if chosen is None:
                # The default for the first iteration
                chosen = var

            if len(self.domains[var]) < len(self.domains[chosen]):
                # Choose the var with less words in domain
                chosen = var

            if len(self.domains[var]) == len(self.domains[chosen]):
                chosen_neighbors = len(self.crossword.neighbors(chosen))
                # Choose the var with more neighbors
                if len(self.crossword.neighbors(var)) > chosen_neighbors:
                    chosen = var

        return chosen

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            # Put value in before consistence check to see if
            # value is consistent with whole assignment
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            # Otherwise, remove
            assignment[var] = None
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
