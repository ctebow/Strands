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

class Solver:

    game_file: str | list[str]
    #board: Board
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
            word_dictionary = [line.strip() for line in f.readlines()]

        self.dictionary = word_dictionary
        self.board_lst = board_lst
      #  self.board = Board(board_lst)
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
    
    def can_place(self, strand: Strand, marked) -> bool:
        """
        Helper function for place_words, checks if a strand can be placed on
        the board.
        """

        positions = strand.positions()
        for pos in positions:
            r = pos.r
            c = pos.c
            if marked[r][c]:
                return False
        return True
    
    def place(self, strand: Strand, marked) -> int:
        """
        Helper function for place_words, places a strand on the marked board.
        """
        positions = strand.positions()
        for pos in positions:
            r = pos.r
            c = pos.c
            marked[r][c] = True

        return len(positions)

    def remove(self, strand: Strand, marked) -> None:
        """
        Helper function for place_words, removes a strand on the marked board.
        """
        positions = strand.positions()
        for pos in positions:
            r = pos.r
            c = pos.c
            marked[r][c] = False

    
    def place_words(self, words: dict[tuple[int, int], tuple[any]]) -> set[str]:
        """
        Given a list of all the words possible in a board, figure out which 
        words are the strands. Words must be at least four letters long.
        """

        # convert all words into strands
        all_strands = []
        for word in words.values():
            start, steps = word
            r, c = start
            all_strands.append(Strand(Pos(r, c), list(steps)))
        
        # remove invalid strands
        filtered = list(filter(lambda x: not (x.is_cyclic() or x.is_folded()),
                                all_strands))
        # obtain markers
        marked = [[False] * self.cols for _ in range(self.rows)]
        solutions = []

        # main checking loop:
        for idx, strand in enumerate(filtered):
            placed = []
            coverage = 0
            if self.can_place(strand, marked):
                coverage += self.place(strand, marked)
                placed.append(strand)

            for strand_new in filtered[idx+1:]:
                if strand == strand_new:
                    continue
                if self.can_place(strand_new, marked): # catches case where two are the same
                    coverage += self.place(strand_new, marked)
                    placed.append(strand_new)
            
            if coverage == self.board_size:
                solutions.append(placed)
            for strand in placed:
                self.remove(strand, marked)

        return solutions

# Place words not right, need a recursive approach. Will do later

solved = Solver("boards/grrr.txt")
words = solved.all_words()
answer = solved.place_words(words)
print(answer)
