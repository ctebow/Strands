"""
Art logic for TUI
"""


import sys
from colorama import Back, Style
from ui import ArtTUIBase, TUIStub

# setup right now for 3 colors to loop, pretty easy to change by adding more
COLORS = {0: Back.BLUE, 1: Back.RED, 2: Back.GREEN}

class ArtTUIWrappers(ArtTUIBase):

    _frame_width: int
    _interior_width: int

    def __init__(self, frame_width: int, interior_width: int):

        self._frame_width = frame_width
        self._interior_width = interior_width


    def print_top_edge(self) -> None:

        width = self._frame_width
        chunks = []
        for idx in reversed(range(width)):
            chunks.append((idx % 3))
            rest = (width * 2 + self._interior_width) - len(chunks) * 2

            for num in chunks:
                print(COLORS[num] + " ", end="")
                print(Style.RESET_ALL, end="")

            print(COLORS[idx % 3] + " " * rest, end="")
            print(Style.RESET_ALL, end="")

            for num in chunks[::-1]:
                print(COLORS[num] + " ", end="")
            print(Style.RESET_ALL)

    def print_bottom_edge(self) -> None:

        width = self._frame_width
        chunks = []
        for idx in reversed(range(width)):
            chunks.append(idx % 3)
        
        for idx in range(width):

            for num in chunks:
                print(COLORS[num] + " ", end="")
                print(Style.RESET_ALL, end="")
            rest = width * 2 + self._interior_width - len(chunks) * 2
            print(COLORS[idx % 3] + " " * rest, end="")
            print(Style.RESET_ALL, end="")
            for num in chunks[::-1]:
                print(COLORS[num] + " ", end="")
            chunks.pop()
            print(Style.RESET_ALL)

    def print_right_bar(self) -> None:
        chunks = []
        for idx in range(self._frame_width):
            chunks.append(idx % 3)
        for num in chunks:
            print(COLORS[num] + " ", end="")
            print(Style.RESET_ALL, end="")
        print()

    def print_left_bar(self) -> None:
        chunks = []
        for idx in range(self._frame_width):
            chunks.append(idx % 3)
        for num in chunks[::-1]:
            print(COLORS[num] + " ", end="")
            print(Style.RESET_ALL, end="")

TUIStub(ArtTUIWrappers(int(sys.argv[1]), int(sys.argv[2])), int(sys.argv[2]), 
        int(sys.argv[3]))
