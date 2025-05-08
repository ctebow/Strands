# src/tui.py

import sys
from time import sleep
from typing import List
from ui import ArtTUIStub, ArtTUIBase
from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step
from stubs import PosStub, StrandStub, BoardStub, StrandsGameStub
from colorama import Fore, Style, init


class TUI:
    """
    Text-based UI for the Strands game.
    """

    def __init__(self, game: StrandsGameBase, art: ArtTUIBase):
        """
        Constructor.
        Inputs:
            game: an instance of StrandsGameBase (typically StrandsGameStub)
            art: an instance of ArtTUIBase (typically ArtTUIStub)
        """
        self.game = game
        self.art = art

    def display(self) -> None:
        """Render the entire TUI screen."""
        print("\033c", end="")  # clear screen
        self.art.print_top_edge()

        # Theme display
        self.art.print_left_bar()
        print(f"Theme: {self.game.theme()}", end="")
        self.art.print_right_bar()

        # Hint meter
        self.art.print_left_bar()
        print(f"Hint meter: {self.game.hint_threshold()}", end="")
        self.art.print_right_bar()

        # Progress
        self.art.print_left_bar()
        print(f"Found: {len(self.game.found_strands())}/{len(self.game.answers())}", end="")
        self.art.print_right_bar()

        # Blank line
        self.art.print_left_bar()
        print("", end="")
        self.art.print_right_bar()

        # Board display
        found_positions = [strand.positions() for strand in self.game.found_strands()]

        board = self.game.board()
        row_nums = board.num_rows()
        col_nums = board.num_cols()

        outer = []
        for r in range(row_nums):
            inner = []
            for c in range(col_nums):
                pos: PosBase = PosStub(r, c)
                inner.append(board.get_letter(pos))

            outer.append(inner)
        
        for row in outer:
            self.art.print_left_bar()
            for col_idx, ch in enumerate(row):
                if (outer.index(row), col_idx) in found_positions:
                    print(Fore.GREEN + ch + Style.RESET_ALL, end="  ")
                else:
                    print(ch, end="  ")
            self.art.print_right_bar()

        self.art.print_bottom_edge()

    def run(self) -> None:
        """Main loop for TUI interaction."""
        self.display()
        while True:
            key = input("Press 'Enter' to submit a guess or 'q' to quit: ").strip().lower()
            if key == "q":
                print("Quitting...")
                break
            elif key == "":
                try:
                    self.game.submit_strand(StrandStub(PosStub(0, 0), [Step("n")]))
                    self.display()
                except Exception as e:
                    print(f"\n{Fore.RED}Game crashed with exception: {e}{Style.RESET_ALL}")
                    break


def main() -> None:
    """
    Entry point for TUI program.
    """
    init(autoreset=True)  # colorama init
    game: StrandsGameBase = StrandsGameStub("", 0)
    art: ArtTUIBase = ArtTUIStub(frame_width=2, interior_width=40)
    tui = TUI(game, art)
    tui.run()


if __name__ == "__main__":
    main()
