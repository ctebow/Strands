"""
Solver for StrandsGame. Given a game file with only a board, lists the 
each answer word with the accompanying Strand class. Makes use of a Trie to 
store dictionary words for efficient searching. 

Resources Consulted:
https://polaris000.medium.com/understanding-prefix-trees-13da74b3cafb

General Idea:
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
    

"""
import copy
from strands import Pos, Board, Strand, Step
from itertools import permutations
PERMS = {(-1, -1): Step.NW, 
        (-1, 0): Step.N, 
        (-1, 1): Step.NE, 
        (0, -1): Step.W,
        (0, 1): Step.E,
        (1, -1): Step.SW, 
        (1, 0): Step.S, 
        (1, 1): Step.SE}

class TrieNode:

    children: dict["TrieNode"]
    char: str
    is_end: bool

    def __init__(self, char=None):
        self.children = {}
        self.char = char
        self.is_end = False

class Trie:

    def __init__(self):
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
    Integer mask intended to represent a typical strands gameboard. More
    efficient than using a list to keep track of positions
    """   

    def __init__(self, rows, cols):
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
    
    def is_val(self, r: int, c: int) -> bool:
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
    Child class of Pos to make it hashable. 
    """
    def __eq__(self, other):
        if not isinstance(other, Pos):
            raise NotImplementedError
        
        return other.c == self.c and other.r == self.r
    
    def __hash__(self):
        return hash((self.r, self.c))


class HashStrand(Strand):
    """
    Child class of Strand to make it hashable.
    """

    def __hash__(self):
        return hash((self.start, tuple(self.steps)))


class Solver:

    game_file: str | list[str]
    board_lst: list[list[str]]
    board: Board
    filtered: list[Strand]
    dictionary: list[str]
    cols: int
    rows: int

    def __init__(self, game_file: str | list[str]):

        # process raw txt file
        if isinstance(game_file, str):
            with open(game_file, encoding="utf-8") as f:
                lines_lst: list[str] = [line.strip() for line in f.readlines()]
        else:
            lines_lst = [line.strip() for line in game_file]

        self.game_theme = lines_lst[0]

        board_lst: list[list[str]] = []

        # assumes one space before grid in valid file
        for _, r in enumerate(lines_lst[2:]):
            alph_lst = [alph.lower() for alph in r.split()]
            if r == "":
                break
            board_lst.append(alph_lst)

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

        self.dictionary = word_dictionary
        self.frequency_chart = frequency_chart
        self.board_lst = board_lst
        self.filtered = []
        self.board = Board(board_lst)
        self.cols = len(board_lst[0])
        self.rows = len(board_lst)
        self.board_size = self.cols * self.rows


    def all_words(self) -> dict[str, tuple[tuple[int, int], Step]]:
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

        
        def all_words_dfs(r, c, node, path, start, steps) -> None:
            """
            Helper function for all_words. Recursively traverses a game board
            in the form of a list until every letter has been visited. 
            """
            # take all words > 3 len
            if node.is_end:
                if len(path) > 3:
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
                    new_steps = steps + (PERMS[(nr, nc)],) # tuple for immutability
                    all_words_dfs(r + nr, c + nc, node.children[letter], 
                                  path + letter, start, new_steps)

            # reset when moving to next word
            visited[r][c] = False

        # run dfs through each letter on board
        for r in range(self.rows):
            for c in range(self.cols):
                all_words_dfs(r, c, trie.root, "", (r, c), ())
        
        return all_words
    
    def score_word(self, word: str) -> tuple[str, int]:
        """
        Scores words based on the game theme. Useful for narrowing down 
        the list of words even further. 
        """


    
    def sort_words(self, raw_words: dict[str, tuple[tuple[int, int],
                                          tuple[Step]]]) -> list[Strand]:
        """
        Filtering function for all collected words. Uses a frequency score, 
        cuts words that are too short or too long. Then turns words into strands
        and sorts them by largest to smallest. (aim for 6-7 words present.)
        """
        # sort words that only are the top 50k in english dictionary. 
        top_50k = {}
        for word in raw_words.keys():
            if word in self.frequency_chart and self.frequency_chart[word] > 200:
                top_50k[word] = raw_words[word]
        # pop words that are too long
        for word in top_50k:
            if len(word) > 10:
                top_50k.pop(word)

        # sort and transform word list into strands
        all_strands = []
        for word in top_50k.values():
            start, steps = word
            r, c = start
            all_strands.append(HashStrand(HashPos(r, c), list(steps)))
        
        # remove invalid strands, sort largest to smallest
        filtered = list(filter(lambda x: not (x.is_cyclic() or x.is_folded()),
                                all_strands))
        filtered.sort(key=lambda x: -len(x.positions()))
        self.filtered = filtered

        return filtered
    
    

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

    def create_mask(self, board: list[Strand]) -> Mask:
        mask = Mask(self.rows, self.cols)

        for strand in board:
            for pos in strand.positions():
                r = pos.r
                c = pos.c
                mask.set_val(r, c)

        return mask


    def place_top_50(self, words: list[Strand], threshold) -> set[str]:
        """
        Given a list of probable, largest words, place the top 50 and fit from
        there. 
        """
        # after we place the top idk 50 combos of words, we can go from those
        # boards

        # I think control flow should be to try it with a high threshold and then
        # narrow down if I get zero matches. 
        mask = Mask(self.rows, self.cols)
        top_50 = words[:50]
        boards = set()
        seen = set()

        def placer_dfs(strand: Strand, placed: tuple[Strand], mask: Mask, threshold):
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
    

    def greedy_place(self, boards: frozenset[frozenset[Strand]]) -> ...:
        """
        Attempt to fit remaining strands to partial boards. Use strategy of
        placing as much of the filtered words in the board, and then check
        if board is full. If not, pop one of the original members and try 
        again. Each word that can get placed will be noted. 
        """

        all_words = self.filtered
        placeable = set()
        better_boards = []
        for board in boards:
            mask = self.create_mask(board)
            board_lst = list(board)
            for strand in all_words:
                if self.can_place(strand, mask):
                    self.place(strand, mask)
                    board_lst.append(strand)
                    placeable.add(strand)
            if mask.is_full() or len(board_lst) > 6:
                better_boards.append(board_lst)

        return placeable, better_boards, len(placeable), len(better_boards)
            





solver = Solver("boards/fore.txt")
mask = Mask(8, 6)
raw = solver.all_words()
strands = solver.sort_words(raw)
boards = solver.place_top_50(strands, 6)
tup = solver.greedy_place(boards)
p, b, lp, lb = tup
for strand in p:
    print(solver.board.evaluate_strand(strand))
