"""
Art logic for TUI
"""

### NOTE: I think I want to switch from colorama to RGB codes,
### more annoying to type but many more colors. I also want to fix the frame to
### be the same thickness on the side as on the top and bottom.
### I also wanna think about how I can make a dynamic background that talks
### with TUI.


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



class ArtTUIChecks(ArtTUIBase):

    _frame_width: int
    _interior_width: int
    _left_side_start_idx: int | None
    _right_side_start_idx: int
    _bottom_start_idx: int | None

    def __init__(self, frame_width, interior_width):

        self._frame_width = frame_width
        self._interior_width = interior_width
        self._left_side_start_idx = None
        self._right_side_start_idx = (self._interior_width + 1) % 2
        self._bottom_start_idx = None

    def print_top_edge(self) -> None:

        width = self._frame_width
        i = 0
        for col in range(width):
            for idx in range(width * 2 + self._interior_width):
                color = COLORS[(idx + i) % 2]
                print(color + " ", end="")
                print(Style.RESET_ALL, end="")
            print(Style.RESET_ALL)
            if i == 0:
                i = 1
            else:
                i = 0
        
        if i == 0:
            self._left_side_start_idx = 0
        else:
            self._left_side_start_idx = 1

    def print_bottom_edge(self) -> None:
        width = self._frame_width
        i = self._bottom_start_idx
        for col in range(width):
            for idx in range(width * 2 + self._interior_width):
                color = COLORS[(idx + i) % 2]
                print(color + " ", end="")
                print(Style.RESET_ALL, end="")
            print(Style.RESET_ALL)
            if i == 0:
                i = 1
            else:
                i = 0

    def print_left_bar(self) -> None:
        width = self._frame_width

        i = self._left_side_start_idx
        for idx in range(width):
            color = COLORS[(idx + i) % 2]
            print(color + " ", end='')
            print(Style.RESET_ALL, end="")
        
        if i == 1:
            self._right_side_start_idx = 0
        else:
            self._right_side_start_idx = 1
    
    def print_right_bar(self) -> None:
        width = self._frame_width
        i = self._right_side_start_idx
        for idx in range(width):
            color = COLORS[(idx + i) % 2]
            print(color + " ", end='')
            print(Style.RESET_ALL, end="")
        print(Style.RESET_ALL)

        if i == 0:
            self._bottom_start_idx = 0
            self._left_side_start_idx = 0
        else:
            self._bottom_start_idx = 1
            self._left_side_start_idx = 1

TUIStub(ArtTUIChecks(4, 8), 8, 10)
