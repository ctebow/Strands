"""
Art logic for GUI
"""

### NOTE: Would be cool to add a dynamic background that talks with GUI and
### reflects what the user is doing on screen (flashes blue when a word is
### found???)

import sys
import pygame
from ui import ArtGUIBase, GUIStub

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


GUIStub(ArtGUI9Slice(int(sys.argv[1])), int(sys.argv[2]), int(sys.argv[3])).run_event_loop()
