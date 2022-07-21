from __future__ import annotations
from typing import TYPE_CHECKING

from pygame import Surface
from pygame.event import Event
from pygame.time import Clock, get_ticks
from pygame.locals import *
from pygame.draw import rect
from pygame.font import Font

from ..constants import *
from .button import Button

if TYPE_CHECKING:
    from ..uno import Uno

class ScrollableList:
    def __init__(self, g : Uno, pos : tuple, size : tuple = (300, 300), font : Font = FONT_MD, direction : str = "toplast", yspacing : int = None) -> None:
        self.g = g
        self.window = g.window
        self.pos = pos
        self.size = size
        self.direction = -1 if direction == "toplast" else 1
        self.lines = []
        self.maxlen = 200
        self.font = font
        self.fontheight = self.font.get_height()
        self.is_moving = False
        self.yspacing = self.fontheight//6 if yspacing is None else yspacing
        self.last_vel = 0
        self.yoffset = 0

    def draw(self, window : Surface = None) -> None:
        if window is None:
            window = self.window
        
        if self.last_vel != 0 and not self.is_moving:
            self.yoffset = self.yoffset + self.last_vel
            self.last_vel *= 0.95
            if -1 < self.last_vel < 1:
                self.last_vel = 0
            if self.yoffset > 0:
                self.yoffset = 0
            
        
        # draw history console in the bottom right corner
        for i,msg in enumerate(self.lines[::self.direction]):
            txt = self.font.render(msg, True, WHITE)
            dim = txt.get_size()
            
            pos = (self.pos[0], self.pos[1] + (i+1)*(self.fontheight + self.yspacing) + self.yoffset)
            if pos[1] > self.pos[1]: # dont render the ones outside the top of their box
                self.window.blit(txt, pos)

    def mouse_event(self, event : Event) -> bool:
        t = event.type
        p = event.pos
        #is_touch = event.touch # unused because unnecessary for functionality
        
        if t == MOUSEBUTTONUP:
            btn = event.button
            if btn == BUTTON_WHEELDOWN:
                self.yoffset = self.yoffset + 10
                return True
            if btn == BUTTON_WHEELUP:
                self.yoffset = self.yoffset - 10
                return True
            if self.is_moving:
                self.is_moving = False
                return True
        elif t == MOUSEBUTTONDOWN:
            if p[0] > self.pos[0] and p[1] > self.pos[1]:
                self.is_moving = True
                return True
        elif t == MOUSEMOTION:
            if self.is_moving:
                #self.pos += event.delta
                self.yoffset = self.yoffset + event.rel[1]
                self.last_vel = event.rel[1]
                return True
        
        return False

    def add(self, msg : str) -> None:
        self.yoffset = 0
        self.lines.append(msg)
        if len(self.lines) > self.maxlen:
            self.lines.pop(0)
    
    def pop(self) -> None:
        self.yoffset = 0
        if len(self.lines) > 0:
            self.lines.pop()