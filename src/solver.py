"""
Solver for StrandsGame. This file contains a working solver, that when given a 
game board and strings for answers, returns the strand object with starting
positions and steps for each answer. 

This file also contains a partially complete general solver, which when given
only a game board, returns all answer strands.

To run the working solver, run "src/solver.py -g boards/BOARDNAME.txt"

To see the progress on the general solver, run "src/solver.py --type general"

Resources Consulted: (for general solver)
https://polaris000.medium.com/understanding-prefix-trees-13da74b3cafb
https://stackoverflow.com/questions/8508799/bit-masking-in-python


For the Solver given answer strings:
- Use a Trie object to efficiently compare all possible word combinations in 
board with all dictionary words, return all the matches.
- Convert each possible word into a strand
- Compare with answer strings and find matching strands to solve the board. 

For the general solver:

- Generate a list of all possible words in the given board.
    - Do this using a Trie data structure to efficiently add words

- Filter these words based on how common they are, a theme score, and length,
then sort based on size.
    - Theme score is hard to do reasonably, can import some stuff for it for
different semantic vectors but may not be worth it currently. 

- Take an arbitrary number of the sorted words (I have it set at 50), and
then generate all possible board layouts with the largest number of these
strands possible. Currently im able to get this from on the order of 10 - 100 
different combos.
    - This is starting to become too computationally expensive, takes over 10
    seconds for some boards with a lot of possible words. 
    - Use bitwise Mask data structure for efficient checking in the recursion

- Using this list, try and fill in the rest of the words from the unsorted list
until I can get full coverage. If I get multiple full coverage words I can 
eliminate based on theme score.
    
- Notes: 
    - Might need to use semantic vectors to narrow word choices down, I am
currently struggling with getting rid of "good" words that aren't actually 
theme words.
    - I also should recurse more efficiently when placing the top 50 words.
"""
import click
import spacy
from strands import Pos, Board, Strand, Step
from typing import Optional, List, Dict, Set

@click.command()
@click.option("-t", "--type", required=False, help="Use General Solver")
@click.option("-g", "--game", required=True, help="Input game board name")
def cmd(type: str, game: str) -> None:
    """
    Sets up command line arguments. 
    """
    if type:
        if type == "general":
            solver = Solver(game)
            solutions = solver.show_general_result()
            print("")
            if solutions:
                print("Found a solution!")
                for i, sol in enumerate(solutions):
                    print(f"--- Solution {i+1} --- ")
                    for word in sol:
                        print(word)
                    print()
            else:
                print("No exact cover solution found.")

        else:
            print("Specify <general> to run general")
            
    else:
        solver = Solver(game)
        answers = solver.show_answers_given_result()
        solver.update_board_with_answers(answers)
        print("")
        print("ANSWERS WITH POSITIONS")
        print(answers)
        print("")

# for navigating around the gameboard and building strands
PERMS = {(-1, -1): Step.NW, 
        (-1, 0): Step.N, 
        (-1, 1): Step.NE, 
        (0, -1): Step.W,
        (0, 1): Step.E,
        (1, -1): Step.SW, 
        (1, 0): Step.S, 
        (1, 1): Step.SE}

class TrieNode:
    """
    Node for Trie class. Stores a character and all unique characters that come
    after the character in a set of words. 
    """
    children: dict[str, "TrieNode"]
    char: Optional[str]
    is_end: bool

    def __init__(self, char: Optional[str]=None):
        self.children = {}
        self.char = char
        self.is_end = False

class Trie:
    """
    Root of the Trie. Stores tree nodes that describe the words in a certain set
    of words. Each node has a unique character and a dictionary of unique 
    characters that may come after it in any given word. 
    """

    root: TrieNode

    def __init__(self) -> None:
        self.root = TrieNode()

    def add(self, word: str) -> None:
        """
        Add a word to the Trie. 
        """
        node = self.root

        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode(char)
            node = node.children[char]
        
        node.is_end = True    
            
class Mask:
    """
    FOR GENERAL SOLVER. Integer mask intended to represent a typical strands 
    gameboard. More efficient than using a list of bools to keep track 
    of positions.
    """
   
    mask: int
    rows: int
    cols: int

    def __init__(self, rows: int, cols: int):
        self.mask = 0
        self.rows = rows
        self.cols = cols
    
    def get_mask(self) -> int:
        """
        Get the mask. 
        """
        return self.mask

    def set_val(self, r: int, c: int) -> None:
        """
        Set a bit value at index r, c in the bitmask. 
        """
        # bitwise shift to index
        mask = self.mask
        self.mask = mask | (1 << (r * self.cols + c)) 

    def clear_val(self, r: int, c: int) -> None:
        """
        Clear a bit value at index r, c in the bitmask.
        """
        mask = self.mask
        self.mask = mask & ~(1 << (r * self.cols + c))
    
    def is_val(self, r: int, c: int) -> int:
        """
        Check if a certain position in the mask is set to true. 
        """
        return self.mask >> (r * self.cols + c) & 1
    
    def reset(self) -> None:
        """
        Reset the mask
        """
        self.mask = 0

    def is_full(self) -> bool:
        """
        Checks if mask is full (all cells True).
        """
        return self.mask == (1 << (self.rows * self.cols)) - 1
    
    def copy(self) -> "Mask":
        """
        Return a copy of the mask at its current state.
        """
        new_mask = Mask(self.rows, self.cols)
        new_mask.mask = self.mask
        return new_mask


class HashPos(Pos):
    """
    FOR GENERAL SOLVER. Child class of Pos to make it hashable. 
    """
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pos):
            raise NotImplementedError
        
        return other.c == self.c and other.r == self.r
    
    def __hash__(self) -> int:
        return hash((self.r, self.c))


class HashStrand(Strand):
    """
    FOR GENERAL SOLVER. Child class of Strand to make it hashable.
    """

    def __hash__(self) -> int:
        return hash((self.start, tuple(self.steps)))
    
class Solver:
    """
    Solver class. Supports solving any board for two cases:

    - Answer strings are given. Uses all_words, sort_words, and get_answer_words
    to return the answer strands

    - Only the board and theme are given. Uses all_words, sort_words, place_top_
    50, greedy_place, and more methods to be updated to try and fit all possible
    strands to a given game board. Incomplete, able to get three or four answers
    each time as of now. 
    """
    game_theme: str
    game_file: str
    board_lst: list[list[str]]
    answers: list[str]
    board: Board
    filtered: list[HashStrand]
    dictionary: list[str]
    cols: int
    rows: int
    nlp: spacy.Language

    def __init__(self, game_file: str):

        # process raw txt file
        if isinstance(game_file, str):
            with open(game_file, encoding="utf-8") as f:
                lines_lst: list[str] = [line.strip() for line in f.readlines()]
        else:
            lines_lst = [line.strip() for line in game_file]

        self.game_theme = lines_lst[0]

        board_lst: list[list[str]] = []

        # assumes one space before grid in valid file --> get board
        for idx, r in enumerate(lines_lst[2:]):
            alph_lst = [alph.lower() for alph in r.split()]
            if r == "":
                board_stp = idx + 3
                break
            board_lst.append(alph_lst)

        answers = []
        # get only the answer strings
        for ind, r in enumerate(lines_lst[board_stp:]):
            if r == "":
                break
        
            full = r.split()
            word = full[0].lower()
            answers.append(word)

        # get word list --> to be put in Trie. 
        with open("assets/web2.txt", encoding="utf-8") as f:
            word_dictionary = [line.strip().lower() for line in f.readlines()]

        # get frequecy chart of top 50k words
        frequency_chart = {}
        with open("assets/en_50k.txt", encoding="utf-8") as f:
            for line in f.readlines():
                lst = line.split()
                if len(lst[0]) > 3:
                    frequency_chart[lst[0]] = int(lst[1])

        self.game_file = game_file
        self.dictionary = word_dictionary
        self.frequency_chart = frequency_chart
        self.board_lst = board_lst
        self.answers = answers
        self.filtered = []
        self.board = Board(board_lst)
        self.cols = len(board_lst[0])
        self.rows = len(board_lst)
        self.board_size = self.cols * self.rows
        self.nlp = spacy.load("en_core_web_md")

    def convert_to_strand(self,
raw: dict[str, tuple[tuple[int, int], tuple[Step, ...]]]) -> list[HashStrand]:
        """
        GIven a dictionary of a word and its raw strand representation, convert
        it into a list of Strands
        """

        all_strands = []
        for word in raw.values():
            start, steps = word
            r, c = start
            all_strands.append(HashStrand(HashPos(r, c), list(steps)))

        return all_strands
    

    def all_words(self) -> dict[str, tuple[tuple[int, int], tuple[Step, ...]]]:
        """
        Given a game file, returns a list of all of the valid words found in
        the game file. Words will be represented by the Strand class. 
        """

        # for efficient sorting, we can stop when a prefix fails to match
        trie = Trie()
        for word in self.dictionary:
            trie.add(word)

        # set of all words
        all_words = {}
        # keep track of which node we have been to
        visited = [[False] * self.cols for _ in range(self.rows)]

        
        def all_words_dfs(r: int, c: int, node: TrieNode, 
            path: str, start: tuple[int, int], steps: tuple[Step, ...]) -> None:
            """
            Helper function for all_words. Recursively traverses a game board
            in the form of a list until every letter has been visited. 
            """
            # take all words > 2 len
            if node.is_end:
                if len(path) > 2:
                    if path not in all_words:
                        all_words[path] = (start, steps[:-1])

            # double check indices and if we've been here
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                return None
            if visited[r][c]:
                return None
            # assign letter, end search if not a word
            letter = self.board_lst[r][c]
            if letter not in node.children:
                return None
            # update tracker
            visited[r][c] = True
            # recurse to children, track start and steps
            for perm in PERMS.keys():
                nr, nc = perm
                if 0 <= (r + nr) < self.rows and 0 <= (c + nc) < self.cols:
                    new_steps = steps + (PERMS[(nr, nc)],) # immutable tuple
                    all_words_dfs(r + nr, c + nc, node.children[letter], 
                                  path + letter, start, new_steps)

            # reset when moving to next word
            visited[r][c] = False

        # run dfs through each letter on board
        for r in range(self.rows):
            for c in range(self.cols):
                all_words_dfs(r, c, trie.root, "", (r, c), ())
        
        return all_words

    
    def sort_words(self, raw_words: dict[str, tuple[tuple[int, int],
                                        tuple[Step, ...]]]) -> list[HashStrand]:
        """
        Filtering function for all collected words. Uses a frequency score, 
        cuts words that are too short or too long. Then turns words into strands
        and sorts them by largest to smallest. (aim for 6-7 words present.)
        """
        # sort words that only are the top 50k in english dictionary. 
        top_50k = {}
        for word in raw_words.keys():
            if word in self.frequency_chart and self.frequency_chart[word] >200:
                top_50k[word] = raw_words[word]
        # pop words that are too long
        for word in list(top_50k.keys()):
            if len(word) > 10:
                top_50k.pop(word)

        # sort and transform word list into strands
        all_strands = self.convert_to_strand(top_50k)
        
        # remove invalid strands
        filtered = list(filter(lambda x: not (x.is_cyclic() or x.is_folded()),
                                all_strands))
        
        # NEW: Sort by theme similarity and length
        filtered.sort(key=lambda s: (self.get_theme_similarity(self.board.evaluate_strand(s)), len(s.positions())), reverse=True)

        self.filtered = filtered

        return filtered
    
    def get_answer_strands(self, 
                    all_strands: list[HashStrand]) -> dict[str, HashStrand]:
        """
        For a solver implementation that assumes the solver knows each answer
        word string, but does not know it's starting position or steps.
        Takes a filtered list of all possible, valid strands on the board and
        then checks if starting position matches. Returns all matches.
        """

        answers = self.answers

        found_answers = {}
        for strand in all_strands:
            word = self.board.evaluate_strand(strand)
            if word in answers:
                found_answers[word] = strand

        return found_answers

    def show_general_result(self) -> List[Dict[str, HashStrand]]:
        """
        Function that obtains current result from using the general solver.
        """
        raw_words = self.all_words()
        sorted_strands = self.sort_words(raw_words)
        
        # Limit the number of strands to keep it manageable for DLX
        candidate_strands = sorted_strands[:200]

        solutions = self.solve_with_dlx(candidate_strands)
        
        result = []
        for sol in solutions:
            dct = {}
            for strand in sol:
                word = self.board.evaluate_strand(strand)
                dct[word] = strand
            result.append(dct)
            
        return result

    def show_answers_given_result(self) -> dict[str, 
                            tuple[tuple[int, int], list[tuple[int, int]]]]:
        """
        Returns the calculated answers for the case where the solver is given
        the game answers as strings as a nice list of strings. 
        """

        words = self.all_words()
        all_strands = self.convert_to_strand(words)
        strands = self.get_answer_strands(all_strands)

        # converting from objects to something readable
        result = {}
        for word in strands.keys():
            start = strands[word].start 
            positions = strands[word].positions()
            pos_lst = []
            for position in positions:
                r = position.r
                c = position.c
                pos_lst.append((r, c))
            r = start.r
            c = start.c
            result[word] = ((r, c), pos_lst)

        return result
    
    def update_board_with_answers(self, answers: dict[str, 
                    tuple[tuple[int, int], list[tuple[int, int]]]]) -> None:
        """
        Takes found answers and creates a new game board file with all the 
        answers placed below the game board, in their usual location. The
        start position and steps are zero-indexed. Writes the coordinates of
        each strand into a new file, which can be found in assets as
        BOARDNAME-solved.txt
        """

        assert self.game_file.endswith(".txt") and \
            self.game_file.startswith("boards/")
        splice = self.game_file[7: -4]
        outfile = "assets/" + splice + "-solved.txt"
    
        with open(self.game_file, encoding="utf-8") as old, \
            open(outfile, "w", encoding="utf-8") as new:

            old_lines = old.readlines()
            # Find the end of the board section
            board_end_index = 0
            for i, line in enumerate(old_lines):
                if line.strip() == "":
                    board_end_index = i
                    break
            
            for line in old_lines[:board_end_index+1]:
                new.write(line)

            new.write("\n")
            for key, value in answers.items():
                start_pos, steps_list = value
                r, c = start_pos
                # Convert steps back to string format
                steps_str = " ".join([s.value for s in self.get_answer_strands(self.convert_to_strand(self.all_words()))[key].steps])
                new.write(f"{key} {r+1} {c+1} {steps_str}\n")

    def find_spangrams(self, strands: List[HashStrand]) -> List[HashStrand]:
        """
        Identifies strands that are potential spangrams.
        A spangram touches two opposite edges of the board.
        """
        spangrams = []
        for strand in strands:
            positions = strand.positions()
            rows = {pos.r for pos in positions}
            cols = {pos.c for pos in positions}

            touches_top = 0 in rows
            touches_bottom = (self.rows - 1) in rows
            touches_left = 0 in cols
            touches_right = (self.cols - 1) in cols

            if (touches_top and touches_bottom) or \
               (touches_left and touches_right):
                spangrams.append(strand)
        return spangrams

    def get_theme_similarity(self, word: str) -> float:
        """
        Calculates the semantic similarity between a word and the game's theme.
        """
        theme_doc = self.nlp(self.game_theme.replace("-", " "))
        word_doc = self.nlp(word)
        if not word_doc.has_vector or not theme_doc.has_vector or word_doc.vector_norm == 0 or theme_doc.vector_norm == 0:
            return 0.0
        return theme_doc.similarity(word_doc)

    def solve_with_dlx(self, strands: List[HashStrand]) -> List[List[HashStrand]]:
        """
        Solves the exact cover problem using DLX.
        """
        universe = {(r, c) for r in range(self.rows) for c in range(self.cols)}
        subsets = {s: {(p.r, p.c) for p in s.positions()} for s in strands}

        dlx = DLX(universe, subsets)
        solutions = dlx.solve()

        return solutions


class DLXNode:
    "A node for the Dancing Links algorithm."
    def __init__(self, name: any = None):
        self.name = name
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.column = self

class DLX:
    "Knuth's Algorithm X solver using Dancing Links."
    def __init__(self, universe: Set, subsets: Dict[any, Set]):
        self.header = self._create_matrix(universe, subsets)
        self.solutions = []

    def _create_matrix(self, universe, subsets):
        header = DLXNode("header")
        
        columns = {}
        for item in sorted(list(universe)):
            col_node = DLXNode(item)
            col_node.right = header
            col_node.left = header.left
            header.left.right = col_node
            header.left = col_node
            columns[item] = col_node

        for subset_name, subset_items in subsets.items():
            first_node_in_row = None
            for item in sorted(list(subset_items)):
                if item in columns:
                    col_node = columns[item]
                    new_node = DLXNode(subset_name)
                    
                    new_node.down = col_node
                    new_node.up = col_node.up
                    col_node.up.down = new_node
                    col_node.up = new_node
                    new_node.column = col_node
                    
                    if first_node_in_row is None:
                        first_node_in_row = new_node
                    else:
                        new_node.right = first_node_in_row
                        new_node.left = first_node_in_row.left
                        first_node_in_row.left.right = new_node
                        first_node_in_row.left = new_node
        return header

    def solve(self) -> List[List[any]]:
        self.solutions = []
        self._search(self.header, [])
        return self.solutions

    def _search(self, header, partial_solution):
        if header.right == header:
            self.solutions.append(list(partial_solution))
            return

        c = self._choose_column(header)
        self._cover(c)

        r = c.down
        while r != c:
            partial_solution.append(r.name)
            
            j = r.right
            while j != r:
                self._cover(j.column)
                j = j.right
            
            self._search(header, partial_solution)
            
            partial_solution.pop()
            j = r.left
            while j != r:
                self._uncover(j.column)
                j = j.left
            
            r = r.down
        
        self._uncover(c)

    def _choose_column(self, header):
        min_size = float('inf')
        chosen_col = None
        c = header.right
        while c != header:
            size = 0
            r = c.down
            while r != c:
                size += 1
                r = r.down
            if size < min_size:
                min_size = size
                chosen_col = c
            c = c.right
        return chosen_col

    def _cover(self, c):
        c.right.left = c.left
        c.left.right = c.right
        i = c.down
        while i != c:
            j = i.right
            while j != i:
                j.down.up = j.up
                j.up.down = j.down
                j = j.right
            i = i.down

    def _uncover(self, c):
        i = c.up
        while i != c:
            j = i.left
            while j != i:
                j.down.up = j
                j.up.down = j
                j = j.left
            i = i.up
        c.right.left = c
        c.left.right = c

if __name__ == "__main__":
    cmd()
