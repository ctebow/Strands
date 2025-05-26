"""
Game logic for Milestone 2:
Pos, StrandFake, BoardFake, StrandsGameFake
"""
import pygame

from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step


class Pos(PosBase):
    """
    Positions on a board, represented as pairs of 0-indexed
    row and column integers. Position (0, 0) corresponds to
    the top-left corner of a board, and row and column
    indices increase down and to the right, respectively.
    """

    # may look back at this versus old version
    def take_step(self, step: Step) -> PosBase:

        c = self.c
        r = self.r


          # value method from official python website Enum documentation
        if step == step.W:
            c -= 1
        elif step == step.E:
            c += 1
        elif step == step.N:
            r -= 1
        elif step == step.S:
            r += 1
        elif step == step.NE:
            r -= 1
            c += 1
        elif step == step.NW:
            r -= 1
            c -= 1
        elif step == step.SE:
            r += 1
            c += 1
        else:
            r += 1
            c -= 1

        return Pos(r, c)

    def step_to(self, other: PosBase) -> Step:
        if self == other:
            raise ValueError

        r_dist = self.r - other.r
        c_dist = self.c - other.c

        if abs(r_dist) < 2 and abs(c_dist) < 2:
            step = ""

            if r_dist == -1:
                step += "s"
            elif r_dist == 1:
                step += "n"
            if c_dist == -1:
                step += "e"
            elif c_dist == 1:
                step += "w"

            # from official python website Enum documentation
            return Step(step)

        raise ValueError

    def is_adjacent_to(self, other: PosBase) -> bool:
        try:
            self.step_to(other)
            return True

        except ValueError:
            return False

class Strand(StrandBase):
    """
    Strands, represented as a start position
    followed by a sequence of steps.
    """
    def positions(self) -> list[PosBase]:

        stack = []
        stack.append(self.start)
        position_list = [self.start]

        for step in self.steps:
            start_pos = stack.pop()
            new_pos = start_pos.take_step(step)
            stack.append(new_pos)
            position_list.append(new_pos)

        return position_list

    def is_cyclic(self) -> bool:
        pos_lst = self.positions()
        ind_lst = []
        for pos in pos_lst:
            ind_lst.append((pos.r, pos.c))
        
        # sets guarantee unique elements
        if len(ind_lst) != len(set(ind_lst)):
            return True
        
        return False

    def is_folded(self) -> bool:
        connections: set[tuple[tuple[int, int],
                               tuple[int, int]]] = set()
        pos_lst = self.positions()

        for ind, pos in enumerate(pos_lst[:-1]):
            end = pos_lst[ind + 1]
            st = (pos.r, pos.c)
            ed = (end.r, end.c)

            connections.add((st, ed))

        for st, ed in connections:
            start = Pos(st[0], st[1])
            stop = Pos(ed[0], ed[1])
            # checking if diagonal connection
            if start.step_to(stop) in {Step.NW, Step.SW, Step.NE, Step.SE}:
                
                # two possible alternative diagonals
                d_1 = (st[0], ed[1])
                d_2 = (ed[0], st[1])

                if (d_1, d_2) in connections or (d_2, d_1) in connections:
                    return True
        
        return False

class Board(BoardBase):
    """
    Boards for the Strands game, consisting of a
    rectangular grid of letters.
    """

    # accidently implemented check if letters valid
    def __init__(self, letters: list[list[str]]):

        row_size = len(letters[0])

        # works with row size check to ensure nonempty rows
        if row_size == 0:
            raise ValueError

        # check row size
        for row in letters:
            if len(row) != row_size:
                raise ValueError
            # check letter formatting
            for letter in row:
                if len(letter) != 1:
                    raise ValueError
                if not letter.isalpha() or not letter.islower():
                    raise ValueError

        self.letters = letters

    def num_rows(self) -> int:
        return len(self.letters)

    def num_cols(self) -> int:
        return len(self.letters[0])

    def get_letter(self, pos: PosBase) -> str:

        # converting to 0-indexing
        if pos.r > self.num_rows() - 1 or pos.c > self.num_cols() - 1:
            raise ValueError
        if pos.r < 0 or pos.c < 0:
            raise ValueError

        return self.letters[pos.r][pos.c]

    def evaluate_strand(self, strand: StrandBase) -> str:
        msg = ""
        pos_lst = strand.positions()

        for pos in pos_lst:
            # ValueError covered by get_letter()
            msg += self.get_letter(pos)

        return msg
    
    def find_neighbors(self, pos: PosBase) -> set[tuple[int, int]]:
        """
        Helper function for the DICTIONARY-WORDS
        game enhancement. Given a valid board PosBase,
        computes and returns neighboring position objects
        in a list. These are purposely not in PosBase form
        because this class does not support being in a set.

        Inputs:
            pos (PosBase): the board position to start

        Returns (set[tuple[int, int]]): the positions of all neighbors
        """
        pos_r_nbs = [(pos.r + 1, pos.c), (pos.r - 1, pos.c)]
        pos_c_nbs = [(pos.r, pos.c + 1), (pos.r, pos.c - 1)]
        pos_diag_nbs = [(pos.r + 1, pos.c + 1), (pos.r + 1, pos.c - 1),
                        (pos.r - 1, pos.c + 1), (pos.r - 1, pos.c - 1)]

        row_count = self.num_rows()
        col_count = self.num_cols()

        if pos.r == row_count - 1:
            del pos_r_nbs[0]
        elif pos.r == 0:
            del pos_r_nbs[1]

        if pos.c == col_count - 1:
            del pos_c_nbs[0]
        elif pos.c == 0:
            del pos_c_nbs[1]

        diags = []
        for r, c in pos_diag_nbs:
            if 0 <= r <= row_count - 1 and 0 <= c <= col_count - 1:
                diags.append((r, c))

        neighbors = set(pos_r_nbs + pos_c_nbs + diags)

        return neighbors

class StrandsGame(StrandsGameBase):
    """
    Incomplete base class for Strands game logic.
    """

    game_theme: str
    hint_thresh: int
    shown_hint_msg: bool
    game_board: Board
    game_answers: list[tuple[str, StrandBase]]
    game_file: str
    show_mode: bool
    sound_mode: bool
    tot_game_guesses: list[tuple[str, StrandBase]]
    hint_state: None | bool
    hint_word: str
    # guesses made after hint cleared
    new_game_guesses: list[tuple[str, StrandBase]]
    word_dictionary: list[str]

    def __init__(self, game_file: str | list[str], hint_threshold: int = 3):

        # for relevant sound enhancements
        pygame.mixer.init()

        # process raw txt file
        if isinstance(game_file, str):
            self.game_file = game_file
            with open(game_file, encoding="utf-8") as f:
                lines_lst: list[str] = [line.strip() for line in f.readlines()]
        else:
            lines_lst = [line.strip() for line in game_file]
        
        self.game_theme = lines_lst[0]
        # check if game theme exists:
        if self.game_theme == "":
            raise ValueError
        
        self.hint_thresh = hint_threshold
        self.shown_hint_msg = False

        board_lst: list[list[str]] = []

        # assumes one space before grid in valid file
        for ind, r in enumerate(lines_lst[2:]):
            if r == "":
                board_stp = ind + 3
                break

            alph_lst = [alph.lower() for alph in r.split()]
            board_lst.append(alph_lst)

        self.game_board = Board(board_lst) # updated to be board object

        game_answers: list[tuple[str, StrandBase]] = []
        for ind, r in enumerate(lines_lst[board_stp:]):
            if r == "":
                break

            steps: list[Step] = []
            full = r.split()
            word = full[0].lower()

            # adjusting to 0-indexing
            start = Pos(int(full[1]) - 1, int(full[2]) - 1)
            steps.extend([Step(dirc.lower()) for dirc in full[3:]])

            game_answers.append((word, Strand(start, steps)))

        # game board and answer checks (board object already checks some)

        # check if no space between theme and board
        if self.game_board.letters == []:
            raise ValueError
        # check if no space between board and answers
        if game_answers == []:
            raise ValueError
        
        tot_ans_len = 0
        for answer in game_answers:
            # check answer longer than three letters
            if len(answer[0]) < 3:
                raise ValueError

            # check answers start on board and strand object actually gives word
            if answer[0] != self.game_board.evaluate_strand(answer[1]):
                raise ValueError
            
            tot_ans_len += len(answer[0])
        
        # make sure answers fill board
        if tot_ans_len != (self.game_board.num_cols() * 
                           self.game_board.num_rows()):
            print("answers do not fill board")
            raise ValueError

        # initializing word dictionary using web2.txt
        with open("assets/web2.txt", encoding="utf-8") as f:
            word_dictionary = [line.strip() for line in f.readlines()]

        # word dictionary
        self.word_dictionary = word_dictionary
        self.game_answers = game_answers
        self.tot_game_guesses = []
        self.hint_state = None
        self.hint_word = self.game_answers[0][0]
        self.new_game_guesses = []
        
        # assume in Play mode
        self.show_mode = False

        # sounds enhancement
        self.sound_mode = False

    def run_dfs(self, start: tuple[int, int], dictionary: set[str],
                partials: set[str], words_sub: set[str]) -> None:
        '''
        Part of the DICTIONARY-WORDS enhancement.
        Performs a DFS on the game_board from boards/G.txt
        to ultimately generate a new file G-with-words.txt with
        an additional section listing all words
        on the board from web2.txt.

        Inputs:
            start (tuple[int, int]): the starting position for dfs
            dictionary (set[str]): the desired source dictionary
            words_sub (set[str]): the destination word set

        Returns:
            Nothing
        '''
        srt_r, srt_c = start
        stack = [(start, [start], self.game_board.get_letter(Pos(srt_r, srt_c)))]

        while stack:
            (r, c), journey, board_wrd = stack.pop()

            if board_wrd not in partials and board_wrd not in dictionary:
                continue

            if board_wrd in dictionary and not len(board_wrd) < 3:
                words_sub.add(board_wrd)

            for w in self.game_board.find_neighbors(Pos(r, c)):
                nb_r, nb_c = w

                # prevents dfs revisiting
                if w not in journey:
                    lett = self.game_board.get_letter(Pos(nb_r, nb_c))
                    stack.append((w, journey + [w], board_wrd + lett))

    def dict_enhancement(self) -> None:
        """
        Iterates through all letters in the game_board,
        running DFS starting at each one to construct a set
        of all dictionary words in the game.
        """

        with open("assets/web2.txt", encoding="utf-8") as f:
            dictionary = set(line.strip().lower() for line in f.readlines())

        # hoping to reduce computation time with O(1) lookups
        partials = set()
        for wrd in dictionary:
            for p in range(1, len(wrd)):
                partial = wrd[:p]
                partials.add(partial)

        words_sub: set[str] = set()
        for r in range(self.game_board.num_rows()):
            for c in range(self.game_board.num_cols()):
                start = (r, c)
                self.run_dfs(start, dictionary, partials, words_sub)

        # building new file name from old
        assert self.game_file.endswith(".txt") and self.game_file.startswith("boards/")
        splice = self.game_file[7: -4]
        outfile = "assets/" + splice + "-with-words.txt"
    
        with open(self.game_file, encoding="utf-8") as old, open(outfile, "w", encoding="utf-8") as new:
            for line in old.readlines():
                new.write(line)

            new.write("\nRelevant Dictionary Words:\n")
            for word in sorted(words_sub):
                new.write(word + "\n")

    def get_hint_word(self) -> str:
        return self.hint_word

    def theme(self) -> str:
        return self.game_theme

    def board(self) -> BoardBase:
        return self.game_board

    def answers(self) -> list[tuple[str, StrandBase]]:
        return self.game_answers

    def found_strands(self) -> list[StrandBase]:

        found_strands: list[StrandBase] = []
        for gus_word, _ in self.tot_game_guesses:
            for ans_word, ans_strd in self.game_answers:
                if gus_word == ans_word:
                    # appends desired ans_strd, even if different from guess
                    found_strands.append(ans_strd)

        return found_strands

    def game_over(self) -> bool:

        if len(self.found_strands()) == len(self.answers()):
            return True

        return False

    def hint_threshold(self) -> int:
        return self.hint_thresh

    def hint_meter(self) -> int:

        level = len(self.new_game_guesses)
        if level >= self.hint_threshold() and not self.shown_hint_msg:
            # only does this once per beating the threshold
            print("You can request a hint!")
            self.shown_hint_msg = True

        return level

    def active_hint(self) -> None | tuple[int, bool]:

        # theme words found thus far
        found_theme_strds = self.found_strands()

        if self.hint_state is None:
            return None

        for ind, (word, strd) in enumerate(self.answers()):
            if strd not in found_theme_strds:
                # ith answer is 0-indexed
                i = ind
                self.hint_word = word
                return (i, self.hint_state)

        return None

    def submit_strand(self, strand: StrandBase) -> tuple[str, bool] | str:

        # ensures pos arguments of strand exist on board
        try:
            board_letters = [self.board().get_letter(pos)
                             for pos in strand.positions()]
        except ValueError:
            return "Not a theme word"

        board_word = "".join(board_letters)

        # check if too short
        if len(board_word) < 3:
            if not self.show_mode and self.sound_mode:
                error_sound = pygame.mixer.Sound("assets/error_008.ogg")
                error_sound.play()

            return "Too short"

        # check if answer/already found answer
        for asw_word, asw_strd in self.answers():
            if board_word == asw_word:
                if asw_strd not in self.found_strands():
                    self.tot_game_guesses.append((asw_word, asw_strd))
                    # theme word is found basic imp
                    if asw_word == self.hint_word:
                        # clearing the hint
                        self.hint_state = None

                    if not self.show_mode and self.sound_mode:
                        correct_sound = pygame.mixer.Sound("assets/confirmation_001.ogg")
                        correct_sound.play()
                    return (asw_word, True)

                if not self.show_mode and self.sound_mode:
                    error_sound = pygame.mixer.Sound("assets/error_008.ogg")
                    error_sound.play()

                return "Already found"

        # check if dictionary word/already found dictionary word
        if board_word in self.word_dictionary:
            # is an unfound word
            if (board_word, strand) not in self.tot_game_guesses:
                self.tot_game_guesses.append((board_word, strand))

                # hint meter updates when this is appended
                self.new_game_guesses.append((board_word, strand))
                
                if not self.show_mode and self.sound_mode:
                    dict_sound = pygame.mixer.Sound("assets/maximize_006.ogg")
                    dict_sound.play()

                return (board_word, False)
            # already found
            else:
                if not self.show_mode and self.sound_mode:
                    error_sound = pygame.mixer.Sound("assets/error_008.ogg")
                    error_sound.play()

                return "Already found"

        # word is not a valid dictionary word
        else:
            if self.sound_mode:
                error_sound = pygame.mixer.Sound("assets/error_008.ogg")
                error_sound.play()
            return "Not in word list"

    def use_hint(self) -> tuple[int, bool] | str:

        if self.sound_mode:
            hint_sound = pygame.mixer.Sound("assets/question_003.ogg")
            hint_sound.play()

        # check if we need to reset hint state to false (NEW LOGIC)
        if self.hint_word:
            for tup in self.tot_game_guesses:
                if self.hint_word == tup[0]:
                    self.hint_state = None
                    break

        hint_level = self.hint_meter()
        hint_threshold = self.hint_threshold()

        # check if we can get hint (NEW LOGIC)
        if hint_level < hint_threshold:
            return "No hint yet"

        # update hint status
        if self.hint_state is None:
            self.hint_state = False

        elif self.hint_state is False:
            self.hint_state = True
        else:
            return "Use your current hint"

        # since we used a hint, we need to trim the hint meter
        if hint_threshold == 0:
            # chosen functionality for 0 case
            self.new_game_guesses = self.new_game_guesses[1:]
        else:
            self.new_game_guesses = self.new_game_guesses[hint_threshold:]

        if hint_level - self.hint_thresh < self.hint_thresh:
            self.shown_hint_msg = False

        # with updated hint state, we can grab our hint
        new_active = self.active_hint()
        assert new_active is not None

        return new_active
