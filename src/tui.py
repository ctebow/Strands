import sys
from typing import List
from ui import ArtTUIStub, ArtTUIBase
from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step
from stubs import PosStub, StrandStub, BoardStub, StrandsGameStub
from colorama import Fore, Style, init


def step_from_char(ch: str) -> Step:
    """
    Convert a single-character direction string to a Step enum value.
    Raises ValueError if the character is invalid.

    Inputs:
        ch: single character string representing direction (e.g. 'N', 'S', 'E', 'W', etc.)

    Returns:
        Step enum corresponding to the character
    """
    ch = ch.upper()
    try:
        return Step(ch)
    except ValueError:
        raise ValueError(f"Invalid step character: {ch}")


class TUI:
    """
    Text-based UI for the Strands game.
    """

    def __init__(self, game: StrandsGameBase, art: ArtTUIBase):
        """
        Constructor.

        Inputs:
            game: instance of StrandsGameBase (e.g., StrandsGameStub)
            art: instance of ArtTUIBase (e.g., ArtTUIStub)
        """
        self.game = game
        self.art = art

    def display(self) -> None:
        """Render the entire TUI screen."""
        print("\033c", end="")  # Clear screen
        self.art.print_top_edge()

        # Theme display
        self.art.print_left_bar()
        print(f"Theme: {self.game.theme()}", end="")
        self.art.print_right_bar()

        # Hint meter display
        self.art.print_left_bar()
        print(f"Hint meter: {self.game.hint_meter()}", end="")
        self.art.print_right_bar()

        # Progress display
        self.art.print_left_bar()
        print(f"Found: {len(self.game.found_strands())}/{len(self.game.answers())}", end="")
        self.art.print_right_bar()

        # Blank line
        self.art.print_left_bar()
        print("", end="")
        self.art.print_right_bar()

        # Board display
        board = self.game.board()
        num_rows = board.num_rows()
        num_cols = board.num_cols()

        # Collect all found positions into a set for quick lookup
        found_positions = set()
        for strand in self.game.found_strands():
            for pos in strand.positions():
                found_positions.add((pos.r, pos.c))

        for r in range(num_rows):
            self.art.print_left_bar()
            for c in range(num_cols):
                pos = PosStub(r, c)
                ch = board.get_letter(pos)
                if (r, c) in found_positions:
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
                # For the stub, the submitted strand is ignored anyway,
                # so just submit any StrandStub with a valid Step list.
                try:
                    strand = StrandStub(PosStub(0, 0), [step_from_char("N")])
                    self.game.submit_strand(strand)
                    self.display()
                except Exception as e:
                    print(f"\n{Fore.RED}Game crashed with exception: {e}{Style.RESET_ALL}")
                    break


def main() -> None:
    """
    Entry point for TUI program.
    """
    init(autoreset=True)  # Initialize colorama
    game: StrandsGameBase = StrandsGameStub("", 0)
    art: ArtTUIBase = ArtTUIStub(frame_width=2, interior_width=40)
    tui = TUI(game, art)
    tui.run()


if __name__ == "__main__":
    main()
