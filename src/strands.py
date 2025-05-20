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
    game_board: Board
    game_answers: list[tuple[str, Strand]]

    tot_game_guesses: list[tuple[str, Strand]] # only
                                               # includes strand guesses,
                                               # since dict not implmeneted
    hint_state: None | bool
    hint_word: str
    # guesses made after hint cleared
    new_game_guesses: list[tuple[str, Strand]]
    word_dictionary: list[str]

    def __init__(self, game_file: str | list[str], hint_threshold: int = 3):

        # process raw txt file
        if isinstance(game_file, str):
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
        if len(board_word) < 4:
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


                    return (asw_word, True)

                return "Already found"

        # check if dictionary word/already found dictionary word
        if board_word in self.word_dictionary:
            # is an unfound word
            if (board_word, strand) not in self.tot_game_guesses:
                self.tot_game_guesses.append((board_word, strand))

                # hint meter updates when this is appended
                self.new_game_guesses.append((board_word, strand))

                return (board_word, False)
            # already found
            else:
                return "Already found"

        # word is not a valid dictionary word
        else:
            return "Not in word list"

    def use_hint(self) -> tuple[int, bool] | str:


        hint_level = self.hint_meter()
        hint_threshold = self.hint_threshold()

        # check if we can get hint
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
        num_new_hints = (len(self.new_game_guesses)
                        - hint_threshold)
        self.new_game_guesses = self.new_game_guesses[:-num_new_hints]

        if hint_level - self.hint_thresh < self.hint_thresh:
            self.shown_hint_msg = False

        # with updated hint state, we can grab our hint
        new_active = self.active_hint()
        assert new_active is not None

        return new_active
