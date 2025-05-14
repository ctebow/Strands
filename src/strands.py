"""
Game logic for Milestone 2:
Pos, StrandFake, BoardFake, StrandsGameFake
"""
from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step


class Pos(PosBase):
    """
    Positions on a board, represented as pairs of 0-indexed
    row and column integers. Position (0, 0) corresponds to
    the top-left corner of a board, and row and column
    indices increase down and to the right, respectively.
    """

    def take_step(self, step: Step) -> PosBase:
        c = self.c
        r = self.r

        # value method from official python website Enum documentation
        if "w" in step.value:
            c -= 1
        if "n" in step.value:
            r -= 1
        if "s" in step.value:
            r += 1
        if "e" in step.value:
            c += 1

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
            pos = stack.pop().take_step(step)
            stack.append(pos)
            position_list.append(pos)

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
        connections: set[tuple[PosBase, PosBase]] = set()
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

class StrandsGame(StrandsGameBase):
    """
    Incomplete base class for Strands game logic.
    """

    game_theme: str
    hint_thresh: int
    shown_hint_msg: bool
    game_board: list[list[str]]
    game_answers: list[tuple[str, Strand]]

    tot_game_guesses: list[tuple[str, Strand]] # only
                                               # includes strand guesses,
                                               # since dict not implmeneted
    hint_state: None | bool
    hint_word: str
    # guesses made after hint cleared
    new_game_guesses: list[tuple[str, Strand]]

    def __init__(self, game_file: str | list[str], hint_threshold: int = 3):

        if isinstance(game_file, str):
            with open(game_file, encoding="utf-8") as f:
                lines_lst: list[str] = [line.strip() for line in f.readlines()]
        else:
            lines_lst = [line.strip() for line in game_file]

        self.game_theme = lines_lst[0]
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

        self.game_board = board_lst

        game_answers: list[tuple[str, Strand]] = []
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

        self.game_answers = game_answers
        self.tot_game_guesses = []
        self.hint_state = None
        self.hint_word = self.game_answers[0][0]
        self.new_game_guesses = []

    def theme(self) -> str:
        return self.game_theme

    def board(self) -> BoardBase:
        return Board(self.game_board)

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
        cur_theme_strds = self.found_strands()

        if self.hint_state is None:
            return None

        for ind, (word, strd) in enumerate(self.answers()):
            if strd not in cur_theme_strds:
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
        for asw_word, strd in self.answers():
            if board_word == asw_word:
                if strd not in self.found_strands():
                    self.tot_game_guesses.append((asw_word, strd))
                    # theme word is found basic imp
                    if asw_word == self.hint_word:
                        # clearing the hint
                        self.hint_state = None

                    return (asw_word, True)

                return "Already found"

        # keeping track of global and refreshed guesses
        self.tot_game_guesses.append((board_word, strand))
        self.new_game_guesses.append((board_word, strand))
        return "Not a theme word"

    def use_hint(self) -> tuple[int, bool] | str:

        if self.hint_state is None:
            # next step in active_hint
            self.hint_state = False

        elif self.hint_state is False:
            # next step in active_hint
            self.hint_state = True
        else:
            return "Use your current hint"

        # actually using the hint
        pre_status = self.hint_meter()

        # trimming hint counter as needed
        if pre_status >= self.hint_threshold():
            self.new_game_guesses = self.new_game_guesses[:-3]
        else:
            self.new_game_guesses = []

        # case where pre_status can be very large
        if pre_status - self.hint_thresh < self.hint_thresh:
            self.shown_hint_msg = False

        new_active = self.active_hint()
        assert new_active is not None
        return new_active
