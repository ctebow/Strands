"""
GUI Implementation for Milestone 1:
Pos, StrandFake, BoardFake, StrandsGameFake
"""
from stubs import PosStub, StrandStub, BoardStub, StrandsGameStub
from ui import ArtGUIBase, ArtGUIStub
from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step

import pygame
import sys


WINDOW_WIDTH = 300  # need to adjust so responds dynamically to fit words
WINDOW_HEIGHT = 200 # need to adjust so responds dynamically to fit words
FRAME_WIDTH = 20

class GuiStrands:
    """
    A GUI application for running a version of the NYTimes
    game Strands.

    Displays a framed board with theme and indications of the
    number of theme words found, which theme words found,
    and the hint meter current value.

    Hitting Enter will submit a guess, whose strand is
    igored before visualizing a corresponding answer,
    in addition to previous found answers.

    Pressing Enter for a fifthm time will crash with an
    exception.

    Pressing the "q" key at any time quits the application.
    """
    surface: pygame.Surface
    interior_hght: float
    interior_wdth: float
    row_height: float
    col_width: float
    lett_locs = list[dict[str, tuple[int, int]]]

    def __init__(self) -> None:
        """
        Initializes the GUI application.
        """
        pygame.init()
        game: StrandsGameBase = StrandsGameStub("", 0)
        board = game.board()
        pygame.display.set_caption(game.theme())

        # open application window
        self.surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        # important interior attributes
        self.interior_hght = WINDOW_HEIGHT - 2 * FRAME_WIDTH
        self.interior_wdth = WINDOW_WIDTH - 2 * FRAME_WIDTH
        self.row_height = self.interior_hght / (board.num_rows() + 1)
        self.col_width = self.interior_wdth / (board.num_cols())
        self.lett_locs = []

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
        return_count = 0
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

                    elif event.key == pygame.K_RETURN:
                        if return_count == 5:
                            raise ValueError("Game is already over!")
                        
                        self.draw_found_solutions(return_count)
                        return_count += 1

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
        self.display_game_board()

        # Instruct PyGame to actually refresh the window with
        # the elements we have just drawnq
        pygame.display.update()

    def display_game_board(self) -> None:
        """
        Display a series of string messages that combine
        to reflect the Strands game board.
        """
        font: pygame.font.Font = pygame.font.Font("assets/thisprty.ttf", 24)
        msg_color = (0, 0, 0)

        game: StrandsGameBase = StrandsGameStub("", 0)
        board = game.board()
        row_nums = board.num_rows()
        col_nums = board.num_cols()

        outer = []
        for r in range(row_nums):
            inner = []
            for c in range(col_nums):
                pos: PosBase = PosStub(r, c)
                inner.append(board.get_letter(pos))

            outer.append(inner)

        y_counter = 1
        outer_locs = []
        lett_track = {}
        for row in outer:
            x_counter = 1
            inner_locs = {}
            for col in row:
                msg = col
                text_image: pygame.Surface = font.render(msg, True, msg_color)
                img_width = text_image.get_width()
                img_height = text_image.get_height()

                assert self.interior_wdth > img_width
                x_gap = (self.col_width - img_width) / 2
                x_loc = FRAME_WIDTH + x_counter * self.col_width - (img_width + x_gap)

                assert self.row_height > img_height
                y_gap = (self.row_height - img_height) / 2
                y_loc = FRAME_WIDTH + y_counter * self.row_height - (img_height + y_gap)

                location = (x_loc, y_loc)
                self.surface.blit(text_image, location)

                x_counter += 1

                # creating dictionary that assigns one location uniquely to every letter
                if self.lett_locs == []:
                    freq = lett_track.get(msg, 1)
                    ky = f"{msg}_{freq}"
                    inner_locs[ky] = location
                    lett_track[msg] = freq + 1

            y_counter += 1

            # ensures aren't building list every time
            if self.lett_locs == []:
                outer_locs.append(inner_locs)
        
        # ensures we are not updating attribute every time
        if self.lett_locs == []:
            self.lett_locs = outer_locs
        
        print(self.lett_locs)

        self.display_bottom(game, y_counter)

    def display_bottom(self, game: StrandsGameBase, counter: int) -> None:
        """
        Prepare and display bottom messages, which track the theme
        words found and the hint meter progress.
        """
        num_found = len(game.found_strands())
        tot_num = len(game.answers())

        font: pygame.font.Font = pygame.font.Font("assets/thisprty.ttf", 24)
        msg_color = (0, 0, 0)

        bottom_msg = f"Found {num_found}/{tot_num}; Hint Once {game.hint_meter()}/{game.hint_threshold()}"

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

    def draw_found_solutions(self, counter) -> None:
        """
        Responsible for drawing circles and connections between successfully
        identified key words.
        """
        new_strd = StrandStub(PosBase(0, 0), [])
        
        locations = new_strd.positions()

        for ans_pos in StrandStub.all_positions[counter]:



if __name__ == "__main__":
    GuiStrands()
