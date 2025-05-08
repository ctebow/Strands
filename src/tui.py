# src/tui.py

import sys
import termios
import tty
from time import sleep
from typing import List
from ui import ArtTUIStub, ArtTUIBase
from strands import StrandsGameStub, StrandsGameBase, StrandStub
from colorama import Fore, Style, init


def getch() -> str:
    """Wait for a key press on the terminal and return a single character."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


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
        print(f"Theme: {self.game.get_theme()}", end="")
        self.art.print_right_bar()

        # Hint meter
        self.art.print_left_bar()
        print(f"Hint meter: {self.game.get_hint_meter()}", end="")
        self.art.print_right_bar()

        # Progress
        self.art.print_left_bar()
        print(f"Found: {len(self.game.get_found_strands())}/{self.game.get_theme_strands_required()}", end="")
        self.art.print_right_bar()

        # Blank line
        self.art.print_left_bar()
        print("", end="")
        self.art.print_right_bar()

        # Board display
        found_positions = {pos for strand in self.game.get_found_strands()
                           for pos in strand.get_path()}
        board = self.game.get_board()
        for row in board:
            self.art.print_left_bar()
            for col_idx, ch in enumerate(row):
                if (board.index(row), col_idx) in found_positions:
                    print(Fore.GREEN + ch + Style.RESET_ALL, end="  ")
                else:
                    print(ch, end="  ")
            self.art.print_right_bar()

        self.art.print_bottom_edge()

    def run(self) -> None:
        """Main loop for TUI interaction."""
        self.display()
        while True:
            key = getch()
            if key.lower() == "q":
                print("Quitting...")
                break
            elif key == "\n":
                try:
                    self.game.submit_guess(StrandStub())
                    self.display()
                except Exception as e:
                    print(f"\n{Fore.RED}Game crashed with exception: {e}{Style.RESET_ALL}")
                    break


def main() -> None:
    """
    Entry point for TUI program.
    """
    init(autoreset=True)  # colorama init
    game: StrandsGameBase = StrandsGameStub()
    art: ArtTUIBase = ArtTUIStub(frame_width=2, interior_width=40)
    tui = TUI(game, art)
    tui.run()


if __name__ == "__main__":
    main()
