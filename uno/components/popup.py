from __future__ import annotations
from typing import TYPE_CHECKING

from pygame import Surface
from pygame.event import Event
from pygame.time import Clock, get_ticks
from pygame.locals import *
from pygame.draw import rect

from ..constants import *
from .button import Button

if TYPE_CHECKING:
    from ..uno import Uno

class Popup:
    def __init__(self, g : Uno, heading : str = None, text : str = None, buttons : list[str] = [], button_handler : function = None, is_multiline : bool = False) -> None:
        self.g = g
        self.window = g.window
        #self.pos = (self.g.h//2, self.g.w//2)
        self.heading = heading
        self.text = text
        self.buttons : list[Button] = []
        self.ticks_created = get_ticks()
        self.rect_dims = (self.g.w//2 - self.g.w//4, self.g.h//2 - self.g.h//4, self.g.w//2, self.g.h//2)
        self.is_multiline = is_multiline
        if is_multiline:
            self.font = FONT_MD
        else:
            self.font = FONT_L
        
        bsize = (150, 50)
        for i,b in enumerate(buttons):
            bpos = (
                int(self.rect_dims[2] + i*bsize[0]*1.2 - ((len(buttons)-1)*bsize[0]*1.2)/2), 
                int(self.rect_dims[3] - self.rect_dims[3]//2 + (self.rect_dims[3]//4)*3.5)
            )
            #bpos = (self.rect_dims[2], self.rect_dims[3] - self.rect_dims[3]//2 + (self.rect_dims[3]//4)*2)
            self.buttons.append(Button(self.g, b, bpos, bsize, button_handler, FONT_MD, border_size=2))

    def draw(self, window : Surface = None) -> None:
        if window is None:
            window = self.window
        
        
        rect(window, BLACK, self.rect_dims)
        rect(window, WHITE, self.rect_dims, 8)

        if self.heading is not None:
            self.g.blit_aligned(FONT_XL.render(self.heading, True, WHITE), (self.rect_dims[2], self.rect_dims[3] - self.rect_dims[3]//2 + self.rect_dims[3]//4), window)
        if self.text is not None:
            if not self.is_multiline:
                self.g.blit_aligned(self.font.render(self.text, True, WHITE), (self.rect_dims[2], self.rect_dims[3] - self.rect_dims[3]//2 + (self.rect_dims[3]//4)*2), window)
            else:
                self.render_multi_line(self.text, self.g.w//2 - self.rect_dims[0]//2, self.g.h//2 - self.rect_dims[1]//2 + 50)
        
        for b in self.buttons:
            b.draw(window)
        
    def mouse_event(self, event : Event) -> None:
        t = event.type
        p = event.pos
        #is_touch = event.touch # unused because unnecessary for functionality
        
        if t == MOUSEBUTTONUP:
            for b in self.buttons:
                if b.click(event.pos):
                    return
    
    def render_multi_line(self, text : str, x : int, y : int) -> None:
        lines = text.splitlines()
        fheight = self.font.get_height()
        for i, l in enumerate(lines):
            self.window.blit(self.font.render(l, True, WHITE), (x, y + (fheight+6)*i))