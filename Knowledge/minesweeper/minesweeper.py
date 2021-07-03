import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()
        self.board = [[False, False, False, False, False, False, False, False], [False, False, False, False, False, True, False, False], [True, False, False, False, False, False, True, False], [False, True, False, False, False, False, False, True], [False, False, False, False, False, False, False, False], [False, False, False, False, False, False, False, False], [True, False, False, False, True, False, False, True], [False, False, False, False, False, False, False, False]]

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # We can only tell which ones are mines when every cell is a
        # mine otherwise we don't have enough information to choose any
        return self.cells if len(self.cells) == self.count else set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # We can only tell which ones are safe when we know there
        # are no mines in the sentence
        return self.cells if self.count == 0 else set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count = self.count - 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def search_cells(self, logic):
        """
        Checks if sentance gives new knowledge
        about safe and mine locations
        """
        safe_cells = logic.known_safes()
        mine_cells = logic.known_mines()
        for safe_cell in safe_cells:
            self.mark_safe(safe_cell)
        for mine_cell in mine_cells:
            self.mark_mine(mine_cell)

    def add_inference(self, inference):
        """
        Adds inference to knowledge and then calls
        update_cell_knowledge to make more inferences
        """
        if inference not in self.knowledge:
            self.knowledge.append(inference)
            #We can try making new inferences now
            self.update_cell_knowledge(inference)

    def update_cell_knowledge(self, logic):
        """
        Makes inferences from knowledge by checking
        sentances for new safe and mines locations
        and checking if one sentence is a subset of
        another to whittle down the potential locations
        of mines.
        """
        for statement in self.knowledge:
            # First, check if sentence has new information
            self.search_cells(statement)
            count_diff = abs(statement.count - logic.count)

            # Statement is a proper subset of logic
            if statement.cells < logic.cells:
                # Get the cells that aren't in the subset and makes
                # a new sentence with the the number of mines not
                # in the subset ("the subset method")
                difference = logic.cells - statement.cells
                inference = Sentence(difference, count_diff)
                self.add_inference(inference)

            # Logic is a proper subset of statement
            if logic.cells < statement.cells:
                # Uses the subset method but in with logic as the subset
                difference = statement.cells - logic.cells
                inference = Sentence(difference, count_diff)
                self.add_inference(inference)
    
    def prune_knowledge(self):
        for statement in self.knowledge.copy():
            # Removes empty sentances since they clutter set
            if len(statement.cells) == 0:
                self.knowledge.remove(statement)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)

        neighbors = set()
        # Taken from Minesweeper class
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Must ensure we avoid coords like (0,-1)
                i_bounds = i >= 0 and i < self.height
                j_bounds = j >= 0 and j < self.width
                not_in_bounds = not(i_bounds and j_bounds)
                is_cell = (i, j) == cell

                # Update the sentence with previous knowledge to
                # eliminate conflicting or misleading knowledge
                discovered = (i, j) in self.safes
                if is_cell or not_in_bounds or discovered:
                    continue
                is_mine = (i, j) in self.mines
                if is_mine:
                    count = count - 1
                    continue

                neighbors.add((i, j))
        logic = Sentence(neighbors, count)

        self.knowledge.append(logic)
        self.update_cell_knowledge(logic)
        # Reduce clutter
        self.prune_knowledge()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe_cell in self.safes:
            if safe_cell not in self.moves_made:
                return safe_cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for row in range(self.height):
            for col in range(self.width):
                new_move = (row, col) not in self.moves_made
                is_mine = (row, col) in self.mines
                if new_move and not is_mine:
                    for mine in self.mines:
                        print(mine)
                    return (row, col)
        return None
