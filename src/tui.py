import sys
from time import sleep
from typing import List
from ui import ArtTUIStub, ArtTUIBase
from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step
from stubs import PosStub, StrandStub, BoardStub, StrandsGameStub
from colorama import Fore, Style, init


class TUI:
    # This is the main text-based interface for the game

    def __init__(self, game: StrandsGameBase, art: ArtTUIBase):
        # Takes in the game logic and ASCII art components
        self.game = game
        self.art = art

    def display(self, highlight: List[PosBase] = []) -> None:
        # Renders the screen with theme, hint meter, progress, and the board itself.
        # If a list of positions is given in `highlight`, those letters get shown in yellow (e.g., during play input)
        print("\033c", end="")  # clear screen
        self.art.print_top_edge()

        self.art.print_left_bar()
        print(f"Theme: {self.game.theme()}", end="")
        self.art.print_right_bar()

        self.art.print_left_bar()
        print(f"Hint meter: {self.game.hint_meter()}/{self.game.hint_threshold()}", end="")
        self.art.print_right_bar()

        self.art.print_left_bar()
        print(f"Found: {len(self.game.found_strands())}/{len(self.game.answers())}", end="")
        self.art.print_right_bar()

        self.art.print_left_bar()
        print("", end="")
        self.art.print_right_bar()

        # Build 2D board to print
        board = self.game.board()
        num_rows = board.num_rows()
        num_cols = board.num_cols()

        # Positions of all found strands so far
        found_positions = []
        for strand in self.game.found_strands():
            found_positions.extend(strand.positions())

        # Draw board with appropriate coloring
        for r in range(num_rows):
            self.art.print_left_bar()
            for c in range(num_cols):
                pos = PosStub(r, c)
                ch = board.get_letter(pos)

                # Highlight if in found strands
                if pos in found_positions:
                    print(Fore.GREEN + ch + Style.RESET_ALL, end="  ")
                # Highlight if in currently selected strand (yellow)
                elif pos in highlight:
                    print(Fore.YELLOW + ch + Style.RESET_ALL, end="  ")
                else:
                    print(ch, end="  ")
            self.art.print_right_bar()

        self.art.print_bottom_edge()

    def run(self) -> None:
        # Main loop for interacting with the game via different modes
        self.display()

        while True:
            print("\nChoose mode: [show] [play] [hint] [quit]")
            mode = input("Mode: ").strip().lower()

            if mode == "quit":
                print("Goodbye.")
                break

            elif mode == "show":
                # Just redisplay the screen
                self.display()

            elif mode == "hint":
                # Tries to use a hint if the threshold has been met
                if self.game.hint_meter() >= self.game.hint_threshold():
                    self.game.use_hint()
                    print(Fore.MAGENTA + "Hint used!" + Style.RESET_ALL)
                    self.display()
                else:
                    print(Fore.RED + "Hint not ready yet." + Style.RESET_ALL)

            elif mode == "play":
                # User enters a strand via a list of space-separated row,col positions
                coords = input("Enter positions (e.g. 0,0 0,1 0,2): ").strip().split()
                try:
                    if len(coords) < 2:
                        raise ValueError("Must enter at least 2 positions.")

                    # Parse all positions
                    pos_objs = []
                    for coord in coords:
                        row, col = map(int, coord.split(","))
                        pos_objs.append(PosStub(row, col))

                    start = pos_objs[0]
                    steps = []
                    for i in range(1, len(pos_objs)):
                        delta_row = pos_objs[i].row() - pos_objs[i - 1].row()
                        delta_col = pos_objs[i].col() - pos_objs[i - 1].col()
                        steps.append(Step((delta_row, delta_col)))

                    strand = StrandStub(start, steps)

                    # Show board with user-selected strand highlighted
                    self.display(pos_objs)

                    # Submit the guess
                    self.game.submit_strand(strand)
                    print(Fore.CYAN + "Strand submitted!" + Style.RESET_ALL)
                    self.display()

                except Exception as e:
                    print(Fore.RED + f"Invalid input or game error: {e}" + Style.RESET_ALL)
            else:
                print(Fore.RED + "Invalid mode." + Style.RESET_ALL)


def main() -> None:
    # Launches the TUI using stub components (for testing)
    init(autoreset=True)  # enables colored output
    game = StrandsGameStub("", 0)
    art = ArtTUIStub(frame_width=2, interior_width=40)
    tui = TUI(game, art)
    tui.run()


if __name__ == "__main__":
    main()
