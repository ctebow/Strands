"""
Art logic for GUI
"""

### NOTE: Would be cool to add a dynamic background that talks with GUI and
### reflects what the user is doing on screen (flashes blue when a word is
### found???)

import sys
import pygame
import pygame.gfxdraw
import math
from ui import ArtGUIBase, GUIStub

ROOT_THREE = 1.732


COLORS = {
            "Aqua": (0, 255, 255),
            "Blue": (0, 0, 255),
            "Green": (0, 128, 0),
            "Lime": (0, 255, 0),
            "Maroon": (128, 0, 0),
            "Navy_Blue": (0, 0, 128),
            "Olive": (128, 128, 0),
            "Purple": (128, 0, 128),
            "Red": (255, 0, 0),
}

class ArtGUI9Slice(ArtGUIBase):

    frame_width: int
    
    def __init__(self, frame_width: int):
        # use sys.argv[1] when calling class instance
        self.frame_width = frame_width

    def draw_background(self, surface: pygame.Surface) -> None:

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
        right = pygame.Rect(width - self.frame_width, height - self.frame_width,
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

    KITEWIDTH = 10
    KITEHEIGHT = 20
    frame_width: int

    def __init__(self, frame_width):

        self.frame_width = frame_width
    
    def draw_background(self, surface: pygame.Surface) -> None:

        # basic info
        width = surface.get_width()
        height = surface.get_height()
        KITEWIDTH = self.KITEWIDTH
        KITEHEIGHT = self.KITEHEIGHT

        # color randomization
        color_list = []
        for color in COLORS.values():
            color_list.append(color)

        for h in range(height // KITEHEIGHT):
            for w in range(width // KITEWIDTH):
                
                color = color_list[w % 9]

                pygame.draw.polygon(surface, color, 
                ((KITEWIDTH * (2 * w + 1) / 2, KITEHEIGHT * h), 
                (KITEWIDTH * (2 * w + 2) / 2, KITEHEIGHT * ((2 * h + 1) / 2)), 
                (KITEWIDTH * (2 * w + 1) / 2, KITEHEIGHT * (h + 1)),
                (KITEWIDTH * (2 * w) / 2, KITEHEIGHT * ((2 * h + 1) / 2))))

class ArtGUIHoneycomb(ArtGUIBase):
# Texture is really blurry right now, I'd need to coordinate with GUI to fix 
# this problem -> pretty easy to switch from texture to plain color regardless
# Right now this is set up to just draw a hex grid accross the entire surface
# and have the GUI overlayed on top, can be changed. 

# also pretty easy to change to have different edge colors
    frame_width: int
    HEX_RADIUS = 20
    HEX_SPACING = 12

    def __init__(self, frame_width):
        self.frame_width = frame_width

    def draw_background(self, surface: pygame.Surface) -> None:

        # basic info
        RADIUS = self.HEX_RADIUS
        SPACING = self.HEX_SPACING
        frame_width = self.frame_width
        width = surface.get_width() + RADIUS * 3 # make sure entire screen filled
        height = surface.get_height() + RADIUS * 3
        

        # calculating start positions and offset
        cx, cy = (0, 0)
        cy_odd = cy + ROOT_THREE / 2 * RADIUS + SPACING / 2
        x_offset = RADIUS * 1.5 + SPACING

        
        # for even indices (don't want to recompute odd y every time)
        for num in range(0, int(width / x_offset), 2):
            x_new = cx + x_offset * num
            self.draw_column_hex(surface, (x_new, cy), height)

        # for odd indices
        for num in range(1, int(width / x_offset), 2):
            x_new = cx + x_offset * num
            self.draw_column_hex(surface, (x_new, cy_odd), height)

    def draw_column_hex(self, surface: pygame.Surface,
                        start: tuple[int], height: int) -> None:
        """
        Helper function to draw a column of hexagons. 
        """
        cx, cy = start
        offset = self.HEX_RADIUS * ROOT_THREE + self.HEX_SPACING
        for num in range(int(height / offset)):

            vertices = self.generate_vertices((cx, cy + offset * num))
            pygame.gfxdraw.filled_polygon(surface,
                                            vertices, COLORS["Red"])

    def generate_vertices(self, center: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Helper function for draw_background, given the center of a hexagon
        returns the a list of the coordinates of its vertices.
        """
        x, y = center
        HEX_RADIUS = self.HEX_RADIUS

        little_leg = HEX_RADIUS / 2
        big_leg = HEX_RADIUS * (ROOT_THREE / 2)

        up_left = (x - little_leg, y - big_leg)
        up_right = (x + little_leg, y - big_leg)
        left = (x - HEX_RADIUS, y)
        right = (x + HEX_RADIUS, y)
        down_left = (x - little_leg, y + big_leg)
        down_right = (x + little_leg, y + big_leg)

        # order matters
        return [up_left, up_right, right, down_right, down_left, left]


class ArtGUIStrands(ArtGUIBase):

    frame_width: int

    def __init__(self, frame_width):
        self.frame_width = frame_width

    def draw_background(self, surface: pygame.Surface) -> None:
        ...




GUIStub(ArtGUIHoneycomb(int(sys.argv[1])), int(sys.argv[2]), int(sys.argv[3])).run_event_loop()
