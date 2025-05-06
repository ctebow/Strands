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

        interior_wdth = WINDOW_WIDTH - 2 * FRAME_WIDTH
        interior_hght = WINDOW_HEIGHT - 2 * FRAME_WIDTH

        interior = pygame.Surface((interior_wdth, interior_hght))
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

        outer = []
        for r in range(board.num_rows()):
            inner = []
            for c in range(board.num_cols()):
                pos: PosBase = PosStub(r, c)
                inner.append(board.get_letter(pos))

            outer.append(inner)

        counter = 1

        for row in outer:
            msg = "   ".join(row)
            text_image: pygame.Surface = font.render(msg, True, msg_color)
            img_width = text_image.get_width()
            img_height = text_image.get_height()

            assert self.interior_wdth > img_width
            x_loc = FRAME_WIDTH + (self.interior_wdth - img_width) / 2

            assert self.row_height > img_height
            gap = (self.row_height - img_height) / 2
            y_loc = FRAME_WIDTH + counter * self.row_height - (img_height + gap)

            location = (x_loc, y_loc)
            self.surface.blit(text_image, location)

            counter += 1

        self.display_bottom(game, counter)

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

if __name__ == "__main__":
    GuiStrands()
