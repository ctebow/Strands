import sys
from typing import List
from ui import ArtTUIStub, ArtTUIBase
from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step
from fakes import StrandsGameFake
from stubs import PosStub, StrandStub
from colorama import Fore, Style, init


class TUI:
    def __init__(self, game: StrandsGameBase, art: ArtTUIBase):
        self.game = game
        self.art = art

    def display(self, highlight: List[PosBase] = []) -> None:
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
        all_positions = []
        for strand in self.game.answers():
            all_positions.extend(strand.positions())
        self.display(highlight=all_positions)


def main() -> None:
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


if __name__ == "__main__":
    main()

