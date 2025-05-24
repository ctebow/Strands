"""
Solver for StrandsGame. Given a game file with only a board, lists the 
each answer word with the accompanying Strand class. Makes use of a Trie to 
store dictionary words for efficient searching. 

Resources Consulted:
https://polaris000.medium.com/understanding-prefix-trees-13da74b3cafb
"""

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

class Solver:

    game_file: str | list[str]
    board_lst = list[list[str]]
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
        self.cols = len(board_lst[0])
        self.rows = len(board_lst)
        self.board_size = self.cols * self.rows


    def all_words(self) -> set[str]:
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

        
        def dfs(r, c, node, path, start, steps) -> None:
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
                    dfs(r + nr, c + nc, node.children[letter], path + letter,
                         start, new_steps)

            # reset when moving to next word
            visited[r][c] = False

        # run dfs through each letter on board
        for r in range(self.rows):
            for c in range(self.cols):
                dfs(r, c, trie.root, "", (r, c), ())
        
        return all_words
    
    def sort_words(self, raw_words: dict[tuple[int, int],
                                          tuple[Step, ...]]) -> list[Strand]:
        """
        Filtering function for all collected words. Uses a frequency score, 
        "odd" letter combination dictionary, words that are too short or too 
        long, plural or conjugated forms. Then turns words into strands and 
        sorts them by largest to smallest. (aim for 6-7 words present.)
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
            all_strands.append(Strand(Pos(r, c), list(steps)))
        
        # remove invalid strands, sort largest to smallest
        filtered = list(filter(lambda x: not (x.is_cyclic() or x.is_folded()),
                                all_strands))
        filtered.sort(key=lambda x: -len(x.positions()))

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

    def place_top_50(self, words: list[Strand]) -> set[str]:
        """
        Given a list of probable, largest words, place the top 50 and fit from
        there. 
        """
        # after we place the top idk 50 combos of words, we can go from those
        # boards

        # represent boards bitwise.
        mask = Mask(self.rows, self.cols)
        top_50 = words[:50]
        boards = []

        def placer_dfs(strand: Strand, placed: tuple[Strand], mask: Mask):
            """
            Depth first algorithm to place top 50 strands on a board. 
            """
            if len(placed) > 5:
                boards.append(placed)
                return
            
            if self.can_place(strand, mask):
                self.place(strand, mask)
                placed_new = placed + (strand,)
                for strand_new in top_50:
                    if strand == strand_new:
                        continue
                    placer_dfs(strand_new, placed_new, mask)
                self.remove(strand, mask)
      
        for strand in top_50:
            placer_dfs(strand, (strand,), mask)

        return boards








# Place words not right, need a recursive approach. Will do later
grrr_ans = ["VEXED",
"IRKED",
"SURLY",
"CRANKY",
"GRUMPY",
"PEEVED",
"TOUCHY",
"CROSSWORD"]

solver = Solver("boards/grrr.txt")
raw = solver.all_words()
sorts = solver.sort_words(raw)
boards = solver.place_top_50(sorts)
print(boards)