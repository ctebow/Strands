"""
Solver for StrandsGame. This file contains a working solver, that when given a 
game board and strings for answers, returns the strand object with starting
positions and steps for each answer. 

This file also contains a partially complete general solver, which when given
only a game board, returns all answer strands.

To run the working solver, run "src/solver.py"

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
from strands import Pos, Board, Strand, Step
from typing import Optional

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
            ans = solver.show_general_result()
            print("")
            print("BEST BOARDS AS OF NOW: LONGEST STRANDS PLACED + EXTRA")
            print("")
            for board in ans:
                keys = board.keys()
                print(keys)
                print("")
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
    FOR GENERAL SOLVER.Integer mask intended to represent a typical strands 
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
        for word in top_50k:
            if len(word) > 10:
                top_50k.pop(word)

        # sort and transform word list into strands
        all_strands = self.convert_to_strand(top_50k)
        
        # remove invalid strands, sort largest to smallest
        filtered = list(filter(lambda x: not (x.is_cyclic() or x.is_folded()),
                                all_strands))
        filtered.sort(key=lambda x: -len(x.positions()))
        self.filtered = filtered

        return filtered
    
    def get_answer_strands(self, 
                           all_strands: list[HashStrand]) -> dict[HashStrand]:
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



    def can_place(self, strand: Strand, mask: Mask) -> bool:
        """
        Helper function for place_words, checks if a strand can be placed on
        the board.
        """

        positions = strand.positions()
        for pos in positions:
            r = pos.r
            c = pos.c
            if mask.is_val(r, c):
                return False
        return True
    
    def place(self, strand: Strand, mask: Mask) -> int:
        """
        Helper function for place_words, places a strand on the marked board.
        """
        positions = strand.positions()
        for pos in positions:
            r = pos.r
            c = pos.c
            mask.set_val(r, c)

        return len(positions)

    def remove(self, strand: Strand, mask: Mask) -> None:
        """
        Helper function for place_words, removes a strand on the marked board.
        """
        positions = strand.positions()
        for pos in positions:
            r = pos.r
            c = pos.c
            mask.clear_val(r, c)

    def create_mask(self, board: frozenset[HashStrand]) -> Mask:
        mask = Mask(self.rows, self.cols)

        for strand in board:
            for pos in strand.positions():
                r = pos.r
                c = pos.c
                mask.set_val(r, c)

        return mask


    def place_top_50(self, words: list[HashStrand], 
                     threshold: int) -> frozenset[frozenset[HashStrand]]:
        """
        Given a list of probable, largest words, place the top 50 and fit from
        there. 
        """
        # initialize mask
        mask = Mask(self.rows, self.cols)

        # take top 50 "best" words
        top_50 = words[:50]

        # accumulate promising boards
        boards = set()


        def placer_dfs(strand: HashStrand,
            placed: tuple[HashStrand,...], mask: Mask, threshold: int) -> None:
            """
            Depth first algorithm to place top 50 strands on a board. 
            """
            # condition for successful placement
            if len(placed) > threshold and not self.can_place(strand, mask):
                boards.add(frozenset(placed))
                return

            # recurse
            if self.can_place(strand, mask):
                mask_copy = mask.copy() # don't want to mutate mask state
                self.place(strand, mask_copy)
                placed_new = placed + (strand,)
                for strand_new in top_50:
                    if strand_new in placed_new:
                        continue
                    placer_dfs(strand_new, placed_new, mask_copy, threshold)
      
        for strand in top_50:
            placer_dfs(strand, (strand,), mask, threshold)

        return frozenset(boards)
    

    def greedy_place(self, 
                     boards: frozenset[frozenset[HashStrand]]) -> list[dict[str,
                                                                HashStrand]]:
        """
        Attempt to fit remaining strands to partial boards. Use strategy of
        placing as much of the filtered words in the board, and then check
        if board is full. If not, pop one of the original members and try 
        again. Each word that can get placed will be noted. 
        """
        # set up collectors

        all_words = self.filtered
        placeable = set()
        better_boards = []

        # go through boards once, try to place words that can still be placed
        for board in boards:
            mask = self.create_mask(board)
            board_lst = list(board)
            for strand in all_words:
                if self.can_place(strand, mask):
                    self.place(strand, mask)
                    board_lst.append(strand)
                    placeable.add(strand)
            if mask.is_full() or len(board_lst) > 6: # threshold for good place
                better_boards.append(board_lst)

        # return the better boards and the other words that can be placed
        result = []
        for board in better_boards:
            dct = {}
            for strand in board:
                word = self.board.evaluate_strand(strand)
                dct[word] = strand
            result.append(dct)

        return result

    def show_general_result(self) -> list[dict[str, HashStrand]]:
        """
        Function that obtains current result from using the general solver.
        """
        raw = self.all_words()
        sorts = self.sort_words(raw)
        placed = self.place_top_50(sorts, 6)
        ans = self.greedy_place(placed)

        return ans

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
            for line in old_lines[:10]:
                new.write(line)

            new.write("\nSolved Answers:\n")
            for key in answers:
                s1 = str(answers[key][0])
                spce = 12 - len(key)

                steps = ""
                for tup in answers[key][1]:
                    steps += str(tup) + " "
                new.write(key + " " * spce + s1 +  " " + steps +"\n")

if __name__ == "__main__":
    cmd()
