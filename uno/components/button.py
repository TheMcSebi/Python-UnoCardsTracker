from __future__ import annotations
from pygame import Surface
from pygame.locals import *
from pygame.draw import rect
from pygame.font import Font
from pygame.image import load
from pygame.event import Event

from ..constants import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..uno import Uno
    
class Button:
    def __init__(self, game : Uno, name : str, pos : tuple, size : tuple, handler : function, font : Font = FONT_XL, subtext : str = None, font_subtext : Font = FONT_MD, border_size : int = 5, color : tuple = WHITE, tag : str = None) -> None:
        self.g = game
        self.name = name
        self.subtext = subtext
        self.pos = pos # (x, y)
        self.size = size # (w, h)
        self.handler = handler
        self.font = font
        self.font_subtext = FONT_MD
        self.border_size = border_size
        self.color = color
        self.tag = tag
        
        self.img = None
        if name.startswith("f::"):
            filedata = name.split("::")
            filename = filedata[1]
            scale = None
            if len(filedata) > 3:
                scale = float(filedata[2])
            self.img = self.g.load_asset_image(filename, scale)

            if self.size is None:
                self.size = self.img.get_size()
            return

        if not subtext is None and len(self.subtext) > 0:
            self.font = FONT_LG

    def click(self, click_pos : tuple) -> bool:
        (cx, cy) = click_pos
        (x, y) = self.pos
        (w, h) = self.size
        if cx > x-w//2 and cx < x + w//2 and cy > y-h//2 and cy < y + h//2:
            if self.tag:
                self.handler(self.tag)
                return True
            self.handler(self.name)
            return True
        return False
    
    def mouse_event(self, event : Event) -> bool:
        if event.type == MOUSEBUTTONUP:
            return self.click(event.pos)
        return False
    
    def draw(self, window : Surface = None) -> None:
        (x, y) = self.pos
        (w, h) = self.size
        if window is None:
            window = self.g.window
        
        if self.img is None:
            rect(window, color=BLACK, rect=(x-w//2, y-h//2, w, h), border_radius=10)
            rect(window, color=self.color, rect=(x-w//2, y-h//2, w, h), width=self.border_size, border_radius=10)

        else:
            self.g.blit_aligned(self.img, (x, y), window)
            return
        
        if not self.subtext is None and len(self.subtext) > 0:
            self.g.blit_aligned(self.font.render(self.name, True, self.color), (x, y - h//6), window)
            self.g.blit_aligned(self.font_subtext.render(self.subtext, True, self.color), (x, y + h/6), window)
        else:
            self.g.blit_aligned(self.font.render(self.name, True, self.color), (x, y), window)