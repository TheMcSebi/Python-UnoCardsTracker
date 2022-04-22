from __future__ import annotations
from pygame import Surface
from pygame.locals import *
from pygame.draw import rect
from pygame.font import Font

from ..constants import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..uno import Uno
    
class Button:
    def __init__(self, game : Uno, name : str, pos : tuple, size : tuple, handler : function, font : Font = FONT_XL, subtext : str = None, font_subtext : Font = FONT_MD) -> None:
        self.g = game
        self.name = name
        self.subtext = subtext
        self.pos = pos # (x, y)
        self.size = size # (w, h)
        self.handler = handler
        self.font = font
        self.font_subtext = FONT_MD
        if not subtext is None and len(self.subtext) > 0:
            self.font = FONT_LG
    
    def click(self, click_pos : tuple) -> bool:
        (cx, cy) = click_pos
        (x, y) = self.pos
        (w, h) = self.size
        if cx > x-w//2 and cx < x + w//2 and cy > y-h//2 and cy < y + h//2:
            self.handler(self.name)
            return True
        return False
    
    def draw(self, window : Surface = None) -> None:
        (x, y) = self.pos
        (w, h) = self.size
        if window is None:
            window = self.g.window
        
        rect(window, WHITE, (x-w//2, y-h//2, w, h), 5)
        if not self.subtext is None and len(self.subtext) > 0:
            self.g.blit_centered(self.font.render(self.name, True, WHITE), (x, y - h//6), window)
            self.g.blit_centered(self.font_subtext.render(self.subtext, True, WHITE), (x, y + h/6), window)
        else:
            self.g.blit_centered(self.font.render(self.name, True, WHITE), (x, y), window)