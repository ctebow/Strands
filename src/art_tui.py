"""
Art logic for TUI
"""
import sys
from colorama import Back, Style
from ui import ArtTUIBase, TUIStub

# setup right now for 3 colors to loop, pretty easy to change by adding more
COLORS = {0: Back.BLUE, 1: Back.RED, 2: Back.GREEN}

class ArtTUIWrappers(ArtTUIBase):
    """
    Class that wraps a user text interface in successive layers of solid colors.
    Contains methods to be used by the TUI to:
    - Print the top edge
    - Print the right edge
    - Print the left edge
    - Print the bottom edge
    Currently setup to loop between three colors, the color of the frame can
    be quickly adjusted.
    """

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

    """
    Class that wraps the user text interface in a checkerbox pattern.
    Contains methods to be used by the TUI to:
    - Print the top edge
    - Print the right edge
    - Print the left edge
    - Print the bottom edge
    The color of each box can be quickly changed. Future planned implementation
    of this class involves interaction with the TUI to display a dynamic
    background once a strand is found. This class uses an odd/even index i to
    keep track of the starting color of each row without needing to know the 
    height of the screen. 
    """

    _frame_width: int
    _interior_width: int
    _left_start: int
    _right_start: int
    _bottom_start: int

    def __init__(self, frame_width: int, interior_width: int):

        self._frame_width = frame_width
        self._interior_width = interior_width

        # logic to sort out various odd/even width and height cases.
        if ((self._frame_width % 2 == 0 and self._interior_width % 2 == 0) or 
            (self._frame_width % 2 != 0 and self._interior_width % 2 != 0)):
            self._left_start = self._frame_width % 2
            self._right_start = self._frame_width % 2
            self._bottom_start = self._frame_width % 2
        else:
            self._left_start = (self._frame_width) % 2
            self._right_start = (self._frame_width + 1) % 2
            self._bottom_start = (self._frame_width) % 2

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

    def print_bottom_edge(self) -> None:

        width = self._frame_width
        i = self._bottom_start % 2
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
        i = self._left_start
        for idx in range(width):
            color = COLORS[(idx + i) % 2]
            print(color + " ", end='')
            print(Style.RESET_ALL, end="")

        if i == 0:
            self._left_start = 1
        else:
            self._left_start = 0
    
    def print_right_bar(self) -> None:

        width = self._frame_width
        i = self._right_start
        for idx in range(width):
            color = COLORS[(idx + i) % 2]
            print(color + " ", end='')
            print(Style.RESET_ALL, end="")
        print(Style.RESET_ALL)

        if i == 0:
            self._right_start = 1
        else:
            self._right_start = 0

        self._bottom_start += 1

# for grading
args = sys.argv
if len(args) == 1:
    print("not enough arguments")
elif args[1] == "wrappers":
    TUIStub(ArtTUIWrappers(int(args[2]), int(args[3])), int(args[3]), int(args[4]))
elif args[1] == "cat1":
    TUIStub(ArtTUIChecks(int(args[2]), int(args[3])), int(args[3]), int(args[4]))
elif args[1] == "cat2":
    print("cat2 pattern implemented in art_gui.py")
elif args[1] == "cat3":
    print("cat3 pattern implemented in art_gui.py")
elif args[1] == "cat4":
    print("cat4 design implemented in art_gui.py")
