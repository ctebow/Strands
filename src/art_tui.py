"""
Logic for ArtTUI. Contains cat0 and cat1 art classes. 
"""
import click
from colorama import Back, Style
from ui import ArtTUIBase, TUIStub

@click.command()
@click.option("-a", "--art", required=True, help="Name of art frame to use")
@click.option("-f", "--frame", type=int, default=2)
@click.option("-w", "--width", type=int,  default=6)
@click.option("-h", "--height", type=int,  default=8)
def cmd(art, frame, width, height):
    """
    Allows for further command line argument support. Set up to take art frame, 
    frame width, width, and height arguments. 
    """
    if art:
        if art == "cat0":
            TUIStub(ArtTUIWrappers(frame, width), width, height)
        elif art == "cat1":
            TUIStub(ArtTUIChecks(frame, width), width, height)
        elif art == "cat2":
            print("Frame type is currently not supported. Input new frame.")
        elif art == "cat3":
            print("Frame type is currently not supported. Input new frame.")
        elif art == "cat4":
            print("Frame type is currently not supported. Input new frame.")
        else:
            print("Frame type is currently not supported. Input new frame.")
    else:
        print("frame missing, input frame with <-f> or <--frame>. ")

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
        """
        Prints the top edge of the TUI art frame. Intended to be used within
        TUI implementation. 
        """

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
        """
        Prints the bottom edge of the TUI art frame. Intended to be used inside
        the TUI game. 
        """
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
        """
        Prints right bar of the TUI art frame. Intended to be used inside TUI
        game. 
        """

        chunks = []
        for idx in range(self._frame_width):
            chunks.append(idx % 3)
        for num in chunks:
            print(COLORS[num] + " ", end="")
            print(Style.RESET_ALL, end="")
        print()

    def print_left_bar(self) -> None:
        """
        Prints left bar of the TUI art frame. Intended to be used inside TUI
        game. 
        """
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
    The color of each box can be quickly changed. This class uses an odd/even
    index i to keep track of the starting color of each row without needing to 
    know the height of the screen. 
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
        """
        Prints top edge, updates start index. 
        """
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
        """
        Prints bottom edge.
        """
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
        """
        Prints left bar, updates start index. 
        """
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
        """
        Prints right bar, updates start index. 
        """
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
        
if __name__ == "__main__":
    cmd()
