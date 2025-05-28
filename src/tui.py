# src/tui.py
import sys
import os
import random
from typing import List
import click
from colorama import Fore, Style, init

from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step
from ui import ArtTUIStub, ArtTUIBase
from fakes import StrandsGameFake
from stubs import PosStub, StrandStub
from strands import StrandsGame
from art_tui import ART_FRAMES  # Art frame classes keyed by name


class TUI:
    """
    Text User Interface for playing Strands game.
    Shows the board, accepts user input, and displays feedback.
    """
    def __init__(self, game: StrandsGameBase, art: ArtTUIBase):
        self.game = game
        self.art = art

    def display(self, highlight: List[PosBase] = []) -> None:
        # Clear the terminal screen
        print("\033c", end="")

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

        board = self.game.board()
        num_rows = board.num_rows()
        num_cols = board.num_cols()

        found_positions = []
        for strand in self.game.found_strands():
            found_positions.extend(strand.positions())

        hint_positions = []
        if self.game.hint_meter() >= self.game.hint_threshold():
            self.game.use_hint()
            hint_positions = self.game.found_strands()[-1].positions()

        for r in range(num_rows):
            self.art.print_left_bar()
            for c in range(num_cols):
                pos = PosStub(r, c)
                ch = board.get_letter(pos)

                if pos in found_positions:
                    print(Fore.GREEN + ch + Style.RESET_ALL, end="  ")
                elif pos in highlight:
                    print(Fore.YELLOW + ch + Style.RESET_ALL, end="  ")
                elif pos in hint_positions:
                    print(Fore.MAGENTA + ch + Style.RESET_ALL, end="  ")
                else:
                    print(ch, end="  ")
            self.art.print_right_bar()

        self.art.print_bottom_edge()

    def run_play_mode(self) -> None:
        """
        Runs interactive mode where player can submit strands, request hints, or quit.
        """
        self.display()
        while True:
            print("\n[Enter] to submit a strand, [h] for hint, [q] to quit")
            command = input("Command or strand (e.g. 0,0 0,1 0,2): ").strip().lower()

            if command == "q":
                print("Goodbye.")
                break
            elif command == "h":
                if self.game.hint_meter() >= self.game.hint_threshold():
                    self.game.use_hint()
                    print(Fore.MAGENTA + "Hint used!" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "Hint not ready." + Style.RESET_ALL)
                self.display()
            elif command == "":
                continue
            else:
                try:
                    coords = command.split()
                    if len(coords) < 2:
                        raise ValueError("Must enter at least 2 positions.")

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

                    self.display(pos_objs)
                    self.game.submit_strand(strand)
                    print(Fore.CYAN + "Strand submitted!" + Style.RESET_ALL)
                    self.display()
                except Exception as e:
                    print(Fore.RED + f"Invalid input: {e}" + Style.RESET_ALL)

    def run_show_mode(self) -> None:
        """
        Shows the board with all answers highlighted.
        """
        all_positions = []
        for strand in self.game.answers():
            all_positions.extend(strand.positions())
        self.display(highlight=all_positions)


def old_main() -> None:
    """
    The original main() you had that runs TUI in play or show mode,
    taking mode and board filename from sys.argv.
    """
    init(autoreset=True)
    if len(sys.argv) != 3:
        print("Usage: python3 src/tui.py [play|show] boards/<file>.txt")
        sys.exit(1)

    mode = sys.argv[1].lower()
    filename = sys.argv[2]

    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            theme = lines[0].strip()
            board_lines = [line.strip() for line in lines[1:] if line.strip()]
    except Exception as e:
        print(f"Error reading game file: {e}")
        sys.exit(1)

    # Using the fake game class here as in your original
    game = StrandsGameFake(theme, board_lines)
    art = ArtTUIStub(frame_width=2, interior_width=40)
    tui = TUI(game, art)

    if mode == "play":
        tui.run_play_mode()
    elif mode == "show":
        tui.run_show_mode()
    else:
        print("Invalid mode. Use 'play' or 'show'.")
        sys.exit(1)


# === Assignment’s required CLI launcher using click ===

@click.command()
@click.option('--show', is_flag=True, help="Start the game in show mode (answers revealed).")
@click.option('-g', '--game', type=str, help="Pick a specific board to play (just the name, no .txt).")
@click.option('-h', '--hint', 'hint_threshold', type=int, default=3, help="How many correct strands before a hint becomes available.")
@click.option('-a', '--art', 'art_frame_name', type=str, default=None, help="Which art frame to use (e.g., cat1, cat4, trees).")
@click.option('-f', '--frame', 'frame_width', type=int, default=None, help="How thick the border/frame should be.")
@click.option('-w', '--width', 'interior_width', type=int, default=None, help="How wide the inside of the game area should be.")
@click.option('-e', '--height', 'interior_height', type=int, default=None, help="How tall the inside of the game area should be.")
def main(show: bool, game: str, hint_threshold: int, art_frame_name: str,
         frame_width: int, interior_width: int, interior_height: int) -> None:
    """
    The new main() function that the assignment wants:
    - Picks board randomly or by name
    - Loads real StrandsGame (not fake)
    - Allows setting hint threshold, art frames, size params
    - Starts TUI and runs it
    """
    init(autoreset=True)  # For colorama

    board_dir = "boards"
    # Pick a board file:
    if game is None:
        game_files = [f for f in os.listdir(board_dir) if f.endswith(".txt")]
        if not game_files:
            print("Error: No game boards found in the boards directory.")
            return
        game_file = os.path.join(board_dir, random.choice(game_files))
    else:
        game_file = os.path.join(board_dir, f"{game}.txt")
        if not os.path.exists(game_file):
            print(f"Error: Game file '{game_file}' does not exist.")
            return

    # Try loading the real game with the hint threshold
    try:
        game_instance = StrandsGame(game_file, hint_threshold=hint_threshold)
    except Exception as e:
        print(f"Error loading game: {e}")
        return

    # Pick art frame class, default to stub
    art_cls = ArtTUIStub
    if art_frame_name is not None:
        art_cls = ART_FRAMES.get(art_frame_name)
        if art_cls is None:
            print(f"Error: Art frame '{art_frame_name}' is not supported.")
            return

    try:
        if art_frame_name == "cat4":
            # Special fixed size for cat4
            interior_width = 8
            interior_height = 6
            frame_width = 2 if frame_width is None else frame_width
        else:
            # Use defaults if user didn’t specify
            interior_width = interior_width or 24
            interior_height = interior_height or 14
            frame_width = frame_width or 2

        art_instance = art_cls(interior_width=interior_width,
                               interior_height=interior_height,
                               frame_width=frame_width)
    except Exception as e:
        print(f"Error initializing art frame: {e}")
        return

    tui = TUI(game_instance, art_instance)
    if show:
        tui.run_show_mode()
    else:
        tui.run_play_mode()


if __name__ == "__main__":
    # By default, run the new CLI main function.
    main()
