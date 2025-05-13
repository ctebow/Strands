"""
GUI Implementation for Milestone 1:
Pos, StrandFake, BoardFake, StrandsGameFake
"""
import sys
from typing import TypeAlias

import pygame

from stubs import PosStub, StrandStub, BoardStub, StrandsGameStub
from fakes import Pos, StrandFake, BoardFake, StrandsGameFake
from ui import ArtGUIBase, ArtGUIStub
from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step

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
    circles: list[dict[Loc, float]]
    game: StrandsGameBase
    game_mode: str
    font: pygame.font.Font

    # dictionary where key is index position of letter,
    # value is a tuple of the pixel position as well as
    # the (img_width, img_height) for that letter
    lett_locs: list[dict[tuple[int, int], tuple[Loc, tuple[int, int]]]]

    # list of active lines, a list of tuples containing start and end positions
    lines: list[tuple[Loc, Loc]]

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
        window_width = max(grid_dim * board.num_cols(), bottom_width) + 2 * FRAME_WIDTH
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

        # List of dictionaries to store the positions and radius of the circle
        self.circles = []

        # similar for lines but stores tuples of start and end tuple positions
        self.lines = []

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

                    if self.game_mode == "play" and self.lett_locs:
                        pass

            if self.game_mode == "show" and self.lett_locs:
                        for _, show_strd in self.game.answers():
                            self.game.submit_strand(show_strd)
                            self.append_found_solutions(self.col_width / 2)

            # shows application window
            self.draw_window()

    def draw_window(self) -> None:
        """
        Draws the interior and exterior frame and also
        the game board.
        """
        # fills entire background with grey
        frame: ArtGUIBase = ArtGUIStub(FRAME_WIDTH)
        frame.draw_background(self.surface)

        interior = pygame.Surface((self.interior_wdth, self.interior_hght))
        interior.fill((253, 253, 150))

        # draws the yellow interior onto grey background
        self.surface.blit(interior, (FRAME_WIDTH, FRAME_WIDTH))

        # actually drawing the lines
        for loc_1, loc_2 in self.lines:
            line_color: tuple[int, int, int] = (173, 216, 230)

            pygame.draw.line(self.surface, color=line_color,
                         start_pos=loc_1, end_pos=loc_2, width=LINE_WIDTH)

        # draw background circles, if applicable
        for circle in self.circles:
            pos_key: Loc = list(circle.keys())[0]
            rad: float = circle[pos_key]

            # Choosing one new color for all circles
            color: tuple[int, int, int] = (173, 216, 230)

            # Use pygame.draw.circle to draw a circle with its stored radius
            pygame.draw.circle(self.surface, color=color,
                            center=pos_key, radius=rad)

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
                text_image: pygame.Surface = self.font.render(msg, True, msg_color)

                # methods from official Pygame documentation
                img_width = text_image.get_width()
                img_height = text_image.get_height()

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
                self.surface.blit(text_image, location)

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

    def generate_bottom_msg(self, num_found: int, tot_num: int):
        """
        For the sake of determining the dynamic width and
        height of the grid, store and generate the bottom
        row message, which tracks the theme
        words found and the hint meter progress.

        Inputs:
            num_found (int): the number of strands found
            tot_num (int): the total number of strands
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

        font: pygame.font.Font = pygame.font.Font("assets/thisprty.ttf", FONT_SIZE)
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
        self.lines.append((loc_1, loc_2))

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

        # want newest strand appended to list
        new_strd = found_lst[-1]
        asw_locations = new_strd.positions()

        last_center = None

        for pos in asw_locations: # could maybe draw strands here
            pt = (pos.r, pos.c)
            
            for dct in self.lett_locs:
                if pt in dct.keys():
                    (x_loc, y_loc), (img_width, img_height) = dct[pt]
                    x_cent = x_loc + img_width / 2
                    y_cent = y_loc + img_height / 2
                    center = (x_cent, y_cent)

                    # drawing a connection between every two points
                    # in a theme word
                    if last_center is not None:
                        self.append_line_between(last_center, center)

                    # changing tracking of last point always
                    last_center = center

                    rad: float = width / 2
                    self.circles.append({center: rad})
                    break

if __name__ == "__main__":
    GuiStrands()
