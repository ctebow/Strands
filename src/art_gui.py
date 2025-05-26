"""
Logic for ArtGUI. Supports cat0, cat2, cat3, and cat4 frames. 
"""
import click
import pygame
import pygame.gfxdraw
import math
import random
from ui import ArtGUIBase, GUIStub

@click.command()
@click.option("-a", "--art", required=True, help="Name of art frame to use")
@click.option("-f", "--frame", type=int, default=0)
@click.option("-w", "--width", type=int,  default=500)
@click.option("-h", "--height", type=int,  default=500)
def cmd(art: str, frame: int, width: int, height: int) -> None:
    """
    Allows for further command line argument support. Set up to take art frame, 
    frame width, width, and height arguments. 
    """
    if art:
        if art == "cat0":
            GUIStub(ArtGUI9Slice(int(frame)),
            width, height).run_event_loop()
        elif art == "cat1":
            print("This category is not supported. Input new frame")
        elif art == "cat2":
            GUIStub(ArtGUIHarlequin(int(frame)),
            width, height).run_event_loop()
        elif art == "cat3":
            GUIStub(ArtGUIHoneycomb(int(frame)),
            width, height).run_event_loop()
        elif art == "cat4":
            GUIStub(ArtGUIDrawStrands(int(frame)),
            width, height).run_event_loop()
        else:
            print("Frame type is currently not supported. Input new frame.")
    else:
        print("frame missing, input frame with <-f> or <--frame>. ")

# for Hexagons
ROOT_THREE = 1.732

# RGB tuples constant. 
COLORS = {
            "Aqua": (0, 255, 255),
            "Blue": (64, 0, 255),
            "Green": (0, 255, 64),
            "Lime": (0, 255, 64),
            "Maroon": (128, 0, 64),
            "Navy_Blue": (64, 0, 128),
            "Olive": (128, 128, 0),
            "Purple": (128, 0, 128),
            "Red": (255, 0, 0)
}

class ArtGUI9Slice(ArtGUIBase):
    """
    Art GUI implementation of a 9 slice pattern. Each slice is a different
    color. 
    """

    frame_width: int
    
    def __init__(self, frame_width: int):
        # use sys.argv[1] when calling class instance
        self.frame_width = frame_width

    def draw_background(self, surface: pygame.Surface) -> None:
        """
        Draws 9Slice background.
        Args: 
            surface: pygame.Surface, created in GUI class. 
        """
        width = surface.get_width()
        height = surface.get_height()

        # do surface math
        up_left = pygame.Rect(0, 0, self.frame_width, self.frame_width)
        up_right = pygame.Rect((width - self.frame_width, 0),
                               (self.frame_width, self.frame_width))
        down_left = pygame.Rect((0, height - self.frame_width),
                                (self.frame_width, self.frame_width))
        down_right = pygame.Rect((width - self.frame_width, 
                                  height - self.frame_width), 
                                  (self.frame_width, self.frame_width))
        left = pygame.Rect(0, self.frame_width, self.frame_width,
                            height - 2 * self.frame_width)
        right = pygame.Rect(width - self.frame_width, self.frame_width,
                            self.frame_width, height - 2 * self.frame_width)
        up = pygame.Rect(self.frame_width, 0, width - 2 * self.frame_width,
                         self.frame_width)
        down = pygame.Rect(self.frame_width, height - self.frame_width,
                           width - 2 * self.frame_width, self.frame_width)
        rects = [up_left, up_right, down_left, 
                 down_right, left, right, up, down]
        
        for rect, color in zip(rects, COLORS.values()):
            pygame.draw.rect(surface, color, rect)

class ArtGUIHarlequin(ArtGUIBase):
    """
    GUI art class that draws a grid of regular kites. Kite width, size, and 
    spacing are easily changed through class attributes. 
    """

    KITEWIDTH = 10
    KITEHEIGHT = 20
    frame_width: int

    def __init__(self, frame_width: int):

        self.frame_width = frame_width
    
    def draw_background(self, surface: pygame.Surface) -> None:
        """
        Draws kite/harlequin background. 
        Args:
            surface: pygame.Surface, created in GUI class. 
        """

        # basic info
        width = surface.get_width()
        height = surface.get_height()
        KITEWIDTH = self.KITEWIDTH
        KITEHEIGHT = self.KITEHEIGHT

        # color randomization
        color_list = []
        for color in COLORS.values():
            color_list.append(color)

        for h in range((height // KITEHEIGHT) + 2):
            for w in range((width // KITEWIDTH) + 2):
                
                color = color_list[w % 9]

                pygame.draw.polygon(surface, color, 
                ((KITEWIDTH * (2 * w + 1) / 2, KITEHEIGHT * h), 
                (KITEWIDTH * (2 * w + 2) / 2, KITEHEIGHT * ((2 * h + 1) / 2)), 
                (KITEWIDTH * (2 * w + 1) / 2, KITEHEIGHT * (h + 1)),
                (KITEWIDTH * (2 * w) / 2, KITEHEIGHT * ((2 * h + 1) / 2))))

class ArtGUIHoneycomb(ArtGUIBase):
    """
    GUI art class that draws a grid of regular hexagons with the flat side up. 
    Hexagon size and spacing are easily changed through class attributes. 
    """

    frame_width: int
    HEX_RADIUS: int = 10
    HEX_SPACING: int = 6

    def __init__(self, frame_width: int):
        self.frame_width = frame_width

    def draw_background(self, surface: pygame.Surface) -> None:
        """
        Draws background of hexagons.
        Args:
            surface: pygame.Surface, created in GUI. 
        """
        # basic info
        RADIUS = self.HEX_RADIUS
        SPACING = self.HEX_SPACING
        frame_width = self.frame_width # keep just in case for later use
        width = surface.get_width() + RADIUS * 3 # make sure entire screen fill
        height = surface.get_height() + RADIUS * 3
    
        # calculating start positions and offset
        cx, cy = (0, 0)
        cy_odd = cy + ROOT_THREE / 2 * RADIUS + SPACING / 2
        x_offset = RADIUS * 1.5 + SPACING
        y_offset = RADIUS * ROOT_THREE + SPACING # keep just in case for later

        # for even indices (don't want to recompute odd y every time)
        for num in range(0, int(width / x_offset), 2):
            x_new = cx + x_offset * num
            self.draw_column_hex(surface, (x_new, cy), height)

        # for odd indices
        for num in range(1, int(width / x_offset), 2):
            x_new = cx + x_offset * num
            self.draw_column_hex(surface, (x_new, cy_odd), height)

    def draw_column_hex(self, surface: pygame.Surface,
                start: tuple[int | float, int | float], height: int) -> None:
        """
        Helper function to draw a column of hexagons given a starting pos 
        tuple and the height (number) of hexagons. 
        """
        cx, cy = start
        offset = self.HEX_RADIUS * ROOT_THREE + self.HEX_SPACING
        for num in range(int(height / offset)):

            vertices = self.generate_vertices((cx, cy + offset * num))
            pygame.gfxdraw.filled_polygon(surface,
                                            vertices, COLORS["Red"])

    def generate_vertices(self, 
            center: tuple[int | float, int | float]) -> list[tuple[float, float]]:
        """
        Helper function for draw_column_hex and draw_background, gives back the 
        a list of 6 vertice tuples for pygame to draw a regular hexagon. 
        """
        x, y = center
        RADIUS = self.HEX_RADIUS

        vertices = []
        for i in range(6):
            x_new = x
            y_new = y
            x_new += math.cos(math.pi / 3 * i) * RADIUS
            y_new += math.sin(math.pi / 3 * i) * RADIUS
            vertices.append((x_new, y_new))

        return vertices

class ArtGUIDrawStrands(ArtGUIBase):
    """
    GUI art class that draws "strands", represented by circles connected by
    lines. Tons of customization is possible by adding new strands to
    STRANDS_COORDS in the form of a list[str], where each string is composed of
    two numbers, the first being the row of the circle and the second the
    column. Circle and line sizes, background circle color, and normal circle
    color can all be changed by modifying class attributes. Currently this
    class only fits a 500 x 500 pixel grid, but future implementations will 
    make it fit grids of various sizes.  
    """

    frame_width: int
    circles_dict: dict[str, tuple[int, int]]

    # color, dimension, and other constants. Changing these will most likely
    # make a change to STRANDS_COORDS necessary
    RADIUS: int = 20
    SEPARATION: int = 10
    LINE_WIDTH: int = 16
    CIRCLE_COLOR: tuple[int, int, int] = (124, 209, 184) # blueish
    BACKGROUND_CIRCLE_COLOR: tuple[int, int, int] = (0, 0, 0)
    LINE_COLOR: tuple[int, int, int] = (124, 209, 184)

    # put new circle indices to draw new strands
    STRANDS_COORDS: list[list[str]] = [
        ["02", "12", "13", "14", "04"], 
        ["00", "10", "20", "30", "21"], 
        ["51", "60", "70", "80", "81", "71", "61"],
        ["90", "91", "92", "93", "94", "83", "84", "85"],
        ["96", "87", "88", "97", "98", "99", "89"],
        ["69", "59", "58", "68"],
        ["38", "48", "49", "39"],
        ["29", "18", "19", "09", "08", "17", "16", "05"]
        ]

    def __init__(self, frame_width: int):
        self.frame_width = frame_width
        self.circles_dict = {}

    def draw_background(self, surface: pygame.Surface) -> None:
        """
        Draws background using draw_background_circles, draw_strand_circles, 
        and draw_lines. 
        Args:
            surface: pygame.Surface, created in GUI. 
        """
        # change background circle color to make background circles visible. 
        self.draw_background_circles(surface)
        self.draw_strand_circles(surface)
        self.draw_lines(surface, self.STRANDS_COORDS)


    def draw_background_circles(self, surface: pygame.Surface) -> None:
        """
        Helper function for draw_background to draw the base layer of circles.
        Used mainly for adding new features to the class, since it gives a
        convenient dictionary of each circle index and its position tuple that
        makes drawing lines from circle to circle efficient. Default to 
        whatever the background color is. 
        """
        width = surface.get_width()
        height = surface.get_height()

        num_circles_x = width / (self.RADIUS * 2 + self.SEPARATION)
        num_circles_y = height / (self.RADIUS * 2 + self.SEPARATION)

        d_center_x = width / num_circles_x
        d_center_y = height / num_circles_y

        x0 = self.RADIUS + self.SEPARATION / 2
        y0 = self.RADIUS + self.SEPARATION / 2
        
        for row in range(int(num_circles_y)):
            for col in range(int(num_circles_x)):
                x, y = (int(x0 + d_center_x * col), int(y0 + d_center_y * row))
                self.circles_dict[f'{row}{col}'] = (x, y)
                pygame.gfxdraw.filled_circle(surface, x, y, self.RADIUS, 
                                             self.BACKGROUND_CIRCLE_COLOR)

    def draw_lines(self, surface: pygame.Surface, 
                   addresses: list[list[str]]) -> None:
        """
        Given a list of addresses of circle centers, draws lines connecting
        a "strand" of circles. Setup to give a gradiant of colors. 
        """
        r, g, b = self.LINE_COLOR
        for strand in addresses:
            for idx, address in enumerate(strand):

                if idx == len(strand) - 1:
                    break

                x0, y0 = self.circles_dict[address]
                x1, y1 = self.circles_dict[strand[idx + 1]]
                pygame.draw.line(surface, (r, g, b), (x0, y0), 
                                 (x1, y1), self.LINE_WIDTH)
            b += 10

    def draw_strand_circles(self, surface: pygame.Surface) -> None:
        """
        Given a list of addresses of circle centers, draws circles at each
        address. Setup to give a gradiant of colors.
        """

        r, g, b = self.CIRCLE_COLOR
        for strand in self.STRANDS_COORDS:
            for address in strand:
                x, y = self.circles_dict[address]
                pygame.gfxdraw.filled_circle(surface, x, y, 
                                             self.RADIUS, (r, g, b))
            b += 10

if __name__ == "__main__":
    cmd()
