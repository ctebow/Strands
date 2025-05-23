"""
GUI Implementation for Milestone 2:
Pos, StrandFake, BoardFake, StrandsGameFake
"""
import sys
from typing import TypeAlias

import pygame

from fakes import Pos, StrandFake, BoardFake, StrandsGameFake
from ui import ArtGUIBase, ArtGUIStub
from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step
from art_gui import ArtGUI9Slice, ArtGUIHarlequin, ArtGUIHoneycomb, ArtGUIDrawStrands
Loc: TypeAlias = tuple[float, float]

FONT_SIZE = 24
LETTER_SPACER = 5
FRAME_WIDTH = 20
LINE_WIDTH = 5

class GuiStrands:
    """
    A GUI application for running a version of the NYTimes
    game Strands.

    Displays a framed board with theme and indications of the
    number of theme words found, which theme words found,
    and the hint meter current value.

    Moves from Stub to Fake implementation. Supports
    Command-Line arguments for Play and Show mode.

    Now includes interactions to select and submit
    strands via a mouse input, as well as input
    functionality for using ("h") and displaying hints.

    Pressing the "q" key at any time quits the application.
    """
    surface: pygame.Surface
    interior_hght: float
    interior_wdth: float
    row_height: float
    col_width: float
    circles: dict[Loc, float]
    temp_circles: dict[Loc, float]
    hint_circles: dict[Loc, float]
    active_hint: bool
    temp_circs_ordering: list[tuple[int, int]]
    game: StrandsGameBase
    game_mode: str
    font: pygame.font.Font

    # dictionary where key is index position of letter,
    # value is a tuple of the pixel position as well as
    # the (img_width, img_height) for that letter
    lett_locs: list[dict[tuple[int, int], tuple[Loc, tuple[int, int]]]]

    # list of active lines, a list of tuples containing start and end positions
    strd_lines: list[tuple[Loc, Loc]]

    def __init__(self) -> None:
        """
        Initializes the GUI application.
        """
        pygame.init()

        _, game_mode, brd_filename = tuple(sys.argv)
        self.game: StrandsGameBase = StrandsGameFake(brd_filename)
        board = self.game.board()

        # dynamically setting up factors for window dimensions
        grid_dim = FONT_SIZE + LETTER_SPACER

        self.font = pygame.font.Font("assets/thisprty.ttf", FONT_SIZE)
        strands_size = len(self.game.answers())
        bottom_msg = self.generate_bottom_msg(strands_size, strands_size)
        text_image = self.font.render(bottom_msg, True, (0, 0, 0))
        bottom_width = text_image.get_width() + 2 * LETTER_SPACER

        # dynamic window dimension generation
        window_width = (max(grid_dim * board.num_cols(), bottom_width)
                        + 2 * FRAME_WIDTH
                        )
        window_height = grid_dim * (board.num_rows() + 1) + 2 * FRAME_WIDTH

        if game_mode == "show":
            self.game_mode = "show"
        elif game_mode == "play":
            self.game_mode = "play"
        else:
            raise ValueError("Unsupported Play Type")

        pygame.display.set_caption(self.game.theme())

        # open application window
        self.surface = pygame.display.set_mode((window_width, window_height))

        # important interior attributes
        self.interior_hght = window_height - 2 * FRAME_WIDTH
        self.interior_wdth = window_width - 2 * FRAME_WIDTH
        self.row_height = self.interior_hght / (board.num_rows() + 1)
        self.col_width = self.interior_wdth / (board.num_cols())
        self.lett_locs = []

        # Dictionaries to store the center and radius of the circle,
        # both for the ones correponding to strands, guesses, and hints
        # the last contains index positions of ordered temp circles
        self.circles = {}
        self.temp_circles = {}
        self.temp_circs_ordering = []

        # initially no active hint
        self.hint_circles = {}
        self.active_hint = False

        # similar for lines but stores tuples of start and end tuple positions
        self.strd_lines = []

        # run event loop
        self.run_event_loop()

    def run_event_loop(self) -> None:
        """
        The event loop for our application. Inside this loop, we will
        repeatedly perform the following operations:

            1. Check for new events
            2. If there are any new events, process the events.
            3. Re-draw the window
        """
        end = 0
        while True:
            events = pygame.event.get()

            for event in events:

                if event.type == pygame.QUIT:
                    # uninitialize all Pygame modules
                    pygame.quit()

                    # and terminate the program
                    sys.exit()

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                    if (
                        self.game_mode == "play" and
                        self.lett_locs and
                        not self.game.game_over()
                        ):

                        if event.key == pygame.K_ESCAPE:
                            self.temp_circles = {}
                            self.temp_circs_ordering = []

                        elif (event.key == pygame.K_h and
                            self.game.hint_meter() >= self.game.hint_threshold()
                            ):

                            self.handle_hint_conditions()

                if (self.game_mode == "play" and
                    self.lett_locs and not
                    self.game.game_over()
                    ):
                    if event.type == pygame.MOUSEBUTTONUP:
                        x_click, y_click = event.pos
                        possible_circs = self.gen_pos_circs(self.col_width / 2)

                        for ky, val in possible_circs.items():
                            (cx, cy), rad = val
                            x_dis: float = x_click - cx
                            y_dis: float = y_click - cy
                            click_dis_sq: float = x_dis**2 + y_dis**2
                            if click_dis_sq <= rad**2:
                                strd_word = self.handle_guess_clicks(ky)

                                if (strd_word is not None and strd_word ==
                                    self.game.get_hint_word()):
                                    self.hint_circles = {}

            if self.game_mode == "show" and self.lett_locs:
                for _, show_strd in self.game.answers():
                    self.game.submit_strand(show_strd)
                    self.append_found_solutions(self.col_width / 2)

            # shows application window
            self.draw_window()

            if (self.game_mode == "play" and
                self.game.game_over() and
                end == 0
                ):
                print("The game is over! Exit anytime.")
                end += 1


    def draw_window(self) -> None:
        """
        Draws the interior and exterior frame and also
        the game board.
        """
        # fills entire background with grey
        frame: ArtGUIBase = ArtGUIHoneycomb(FRAME_WIDTH)
        frame.draw_background(self.surface)

        interior = pygame.Surface((self.interior_wdth, self.interior_hght))
        interior.fill((253, 253, 150))

        # draws the yellow interior onto grey background
        self.surface.blit(interior, (FRAME_WIDTH, FRAME_WIDTH))

        # actually drawing the lines
        for loc_1, loc_2 in self.strd_lines:
            pygame.draw.line(self.surface, color=(173, 216, 230),
                         start_pos=loc_1, end_pos=loc_2, width=LINE_WIDTH)

        # draw background circles, if applicable
        for pos_key, b_rad in self.circles.items():

            # Use pygame.draw.circle to draw a circle with its stored radius
            pygame.draw.circle(self.surface, color=(173, 216, 230),
                            center=pos_key, radius=b_rad)

        # draw temp circle lines
        for i in range(1, len(self.temp_circs_ordering)):
            cir1_ind = self.temp_circs_ordering[i - 1]
            cir2_ind = self.temp_circs_ordering[i]

            possible_circles = self.gen_pos_circs(self.col_width / 2)
            center1, _ = possible_circles[cir1_ind]
            center2, _ = possible_circles[cir2_ind]

            pygame.draw.line(self.surface, color=(128, 128, 128),
                             start_pos=center1, end_pos=center2,
                             width=LINE_WIDTH)

        # draw temp circles, if applicable
        for t_pos_key, t_rad in self.temp_circles.items():

            # Use pygame.draw.circle to draw a circle with its stored radius
            pygame.draw.circle(self.surface, color=(128, 128, 128),
                            center=t_pos_key, radius=t_rad)

        # draw hint circles, if applicable
        for ind, (h_pos_key, h_rad) in enumerate(self.hint_circles.items()):

            # Use pygame.draw.circle to draw a circle with its stored radius
            pygame.draw.circle(self.surface, color=(144, 238, 144),
                            center=h_pos_key, radius=h_rad, width=2)

            # first or last word in hint_circles
            # should just have one circle in it at a time
            if self.active_hint:
                if ind in {0, len(self.hint_circles) - 1}:
                    pygame.draw.circle(self.surface, color=(255, 71, 76),
                                center=h_pos_key, radius=h_rad, width=2)

        # showing letters and bottom
        self.display_game_board()

        # Instruct PyGame to actually refresh the window with
        # the elements we have just drawn
        pygame.display.update()

    def display_game_board(self) -> None:
        """
        Display a series of string messages that combine
        to reflect the Strands game board.
        """
        msg_color = (0, 0, 0)

        board: BoardBase = self.game.board()
        row_nums = board.num_rows()
        col_nums = board.num_cols()

        outer = []
        for r in range(row_nums):
            inner = []
            for c in range(col_nums):
                pos: PosBase = Pos(r, c)
                inner.append(board.get_letter(pos))

            outer.append(inner)

        y_counter = 1
        outer_locs = []
        for r_ind, row in enumerate(outer):
            x_counter = 1
            inner_locs = {}
            for c_ind, col in enumerate(row):
                msg = col
                txt_img: pygame.Surface = self.font.render(msg, True, msg_color)

                # methods from official Pygame documentation
                img_width = txt_img.get_width()
                img_height = txt_img.get_height()

                assert self.col_width > img_width
                x_gap = (self.col_width - img_width) / 2
                x_loc = FRAME_WIDTH + (
                    x_counter * self.col_width - (img_width + x_gap)
                )

                assert self.row_height > img_height
                y_gap = (self.row_height - img_height) / 2
                y_loc = FRAME_WIDTH + (
                    y_counter * self.row_height - (img_height + y_gap)
                )

                location = (x_loc, y_loc)
                self.surface.blit(txt_img, location)

                x_counter += 1

                # creating dictionary that assigns one location
                # uniquely to every letter
                if not self.lett_locs:
                    inner_locs[(r_ind, c_ind)] = (
                        (location, (img_width, img_height))
                    )

            y_counter += 1

            # ensures aren't building list every time
            if not self.lett_locs:
                outer_locs.append(inner_locs)

        # ensures we are not updating attribute every time
        if not self.lett_locs:
            self.lett_locs = outer_locs

        self.display_bottom(y_counter)

    def generate_bottom_msg(self, num_found: int, tot_num: int) -> str:
        """
        For the sake of determining the dynamic width and
        height of the grid, store and generate the bottom
        row message, which tracks the theme
        words found and the hint meter progress.

        Inputs:
            num_found (int): the number of strands found
            tot_num (int): the total number of strands

        Returns (str):
            The desired bottom message
        """

        bottom_msg = (
            f"Found {num_found}/{tot_num}; "
            f"Hint Once {self.game.hint_meter()}/{self.game.hint_threshold()}"
        )

        return bottom_msg

    def display_bottom(self, counter: int) -> None:
        """
        Prepare and display bottom messages, which tracks the theme
        words found and the hint meter progress.

        Inputs:
            counter (int): Standard counter to help with positioning.

        Returns:
            Nothing
        """
        num_found = len(self.game.found_strands())
        tot_num = len(self.game.answers())

        font = pygame.font.Font("assets/thisprty.ttf", FONT_SIZE)
        msg_color = (0, 0, 0)

        bottom_msg = self.generate_bottom_msg(num_found, tot_num)

        text_image: pygame.Surface = font.render(bottom_msg, True, msg_color)
        img_width = text_image.get_width()
        img_height = text_image.get_height()

        assert self.row_height > img_height
        gap = (self.row_height - img_height) / 2

        assert self.interior_wdth > img_width
        x_loc = FRAME_WIDTH + (self.interior_wdth - img_width) / 2
        y_loc = FRAME_WIDTH + counter * self.row_height - (img_height + gap)

        location = (x_loc, y_loc)
        self.surface.blit(text_image, location)

    def append_line_between(self, loc_1: Loc, loc_2: Loc) -> None:
        """
        Given two locations, save a line between these
        locations for later. This will serve to associate strands.

        Inputs:
            loc_1 (Loc): line start location
            loc_2 (Loc): line end location

        Returns:
            Nothing
        """
        self.strd_lines.append((loc_1, loc_2))

    def handle_hint_conditions(self) -> None:
        """""
        Responsible for changing attributes to
        suit appropriate hint state upon asking for a hint.

        Returns (str): the hint word, or none if active hint present
        """""

        status = self.game.use_hint()
        possible_circs = self.gen_pos_circs(self.col_width / 2)

        # condition if active hint already there
        if isinstance(status, str):
            print(status)

        elif isinstance(status, tuple):
            asw_ind, cond = status
            assert isinstance(asw_ind, int)

            _, hint_strd = self.game.answers()[asw_ind]
            # no active hint before call, outline whole word
            if cond is False:
                ind_list = []

                # appending starting position
                start_pos = hint_strd.start
                ind_list.append((start_pos.r, start_pos.c))

                # building a list of index theme word positions
                former = start_pos
                for step in hint_strd.steps:
                    next_pos = former.take_step(step)
                    ind_list.append((next_pos.r, next_pos.c))
                    former = next_pos

                # adds required circles to hint dict
                for i in ind_list:
                    center, rad = possible_circs[i]
                    self.hint_circles[center] = rad

            else:
                self.active_hint = True

    def gen_pos_circs(self, width: float) -> dict[tuple[int, int],
                                                  tuple[Loc, float]]:
        """
        For use in drawing circles and click-based
        GUI needs, generate a list of possible circles
        behind every letter in the grid.

        Inputs:
            width (float): desired length to adjust circle radius

        Returns (dict[tuple[int, int], tuple[Loc, float]]]):
            Dict to store the positions and radius of the circles,
            where the key is the index position of the circle and the
            value is a tuple of its pixel location and radius.
        """

        possible_circles = {}
        for dct in self.lett_locs:
            for pt in dct.keys():
                (x_loc, y_loc), (img_width, img_height) = dct[pt]
                x_cent = x_loc + img_width / 2
                y_cent = y_loc + img_height / 2
                center = (x_cent, y_cent)

                rad: float = width / 2
                possible_circles[pt] = (center, rad)

        return possible_circles

    def handle_guess_clicks(self, cir: tuple[int, int]) -> None | str:
        """
        Provided the index position of a cirle corresponding to a
        click, decides how to change class attributes in response.

        Inputs:
            cir (tuple[int, int]): circle index position of mentioned click

        Returns (str): the strand theme word submitted, or nothing
        """
        possible_circs = self.gen_pos_circs(self.col_width / 2)

        if cir not in possible_circs:
            raise ValueError("Invalid Click Location!")

        center, rad = possible_circs[cir]

        # in case that cir is first temp circle
        if not self.temp_circs_ordering:
            self.temp_circles = {center: rad}
            self.temp_circs_ordering = [cir]

        else:
            last_cir = self.temp_circs_ordering[-1]

            r_ind, c_ind = cir
            l_r_ind, l_c_ind = last_cir

            cir_pos = Pos(r_ind, c_ind)
            l_cir_pos = Pos(l_r_ind, l_c_ind)

            # double click last cir case
            if cir == last_cir:
                pos_lst = [Pos(r_ind, c_ind) for
                           r_ind, c_ind in self.temp_circs_ordering]
                step_lst = []
                start = pos_lst[0]

                former = start
                for i in pos_lst[1:]:
                    step_lst.append(Step(former.step_to(i)))
                    former = i

                strd: StrandBase = StrandFake(start, step_lst)

                # current output of status of strand
                msg = self.game.submit_strand(strd)
                print(msg)

                if isinstance(msg, tuple):
                    strd_word, correctness = msg
                    if correctness:
                        self.append_found_solutions(self.col_width / 2)

                        # reset after attempt
                        self.temp_circles = {}
                        self.temp_circs_ordering = []

                        if strd_word == self.game.get_hint_word():
                            self.active_hint = False

                        return strd_word

                # need to reset either way
                self.temp_circles = {}
                self.temp_circs_ordering = []

            # truncating if re-click already selected spot
            elif cir in self.temp_circs_ordering:
                l = self.temp_circs_ordering.index(cir)
                self.temp_circs_ordering = self.temp_circs_ordering[:l + 1]
                self.temp_circles = {
                    possible_circs[pt][0]: possible_circs[pt][1]
                    for pt in self.temp_circs_ordering
                    }

            # extending strand if adjacent
            elif cir_pos.is_adjacent_to(l_cir_pos):
                self.temp_circs_ordering.append(cir)
                self.temp_circles[center] = rad

            # if not adjacent then must reset
            else:
                self.temp_circs_ordering = [cir]
                self.temp_circles = {center: rad}

        return None

    def append_found_solutions(self, width: float) -> None:
        """
        Responsible for appending to the overall circle list before they
        will be drawn. Currently called once per hitting return.

        Inputs:
            width (float): desired length to adjust circle radius

        Returns:
            Nothing
        """
        # gets appended as you hit space
        found_lst = self.game.found_strands()

        # only draw if found_lst not empty
        if found_lst:
            # want newest strand appended to list
            new_strd = found_lst[-1]
            asw_locations = new_strd.positions()

            last_center = None
            pos_dct = self.gen_pos_circs(width)

            for pos in asw_locations: # could maybe draw strands here
                pt = (pos.r, pos.c)

                if pt not in pos_dct:
                    raise ValueError(f"No found center for {pt}")

                center = pos_dct[pt][0]

                if last_center is not None:
                    self.append_line_between(last_center, center)

                # changing tracking of last point always
                last_center = center

                rad: float = width / 2
                self.circles[center] = rad

if __name__ == "__main__":
    GuiStrands()
