from __future__ import annotations
from pygame.locals import *
from pygame.event import Event

from .constants import *
from .components.button import Button

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .uno import Uno

class Load:
    """
    Load screen
    """
    def __init__(self, game : Uno) -> None:
        self.g = game
        self.window = self.g.window

    #########################################################################################
    
    def setup(self) -> None:
        self.saves = self.g.get_saves()
        self.bw = self.g.w//2
        self.bh = self.g.h//8

        self.buttons = [Button(self.g, "Back", (100, 50), (200, 100), self.button_handler, FONT_LG)]
        for i, s in enumerate(self.saves):
            self.buttons.append(Button(self.g, s["filename"], (self.g.w//2, self.g.h//12 + i*self.bh), (self.bw, self.bh), self.button_handler, FONT_LG, ", ".join(s["players"]), FONT_MD))
    
    def button_handler(self, name : str) -> None:
        if name == "Back":
            self.g.setstate(0)
            return
        self.g.load(name)
    
    def loop(self, events : list[Event]) -> None:
        for b in self.buttons:
            b.draw()

    def keydown(self, k : int, kmods : int) -> bool:
        if k == K_q or k == K_ESCAPE:
            self.g.setstate(0)
            return True
        return False
    
    def mouse_event(self, event : Event) -> bool:
        return False
    
    def click(self, pos : tuple, btn = int) -> bool:
        if btn == BUTTON_WHEELDOWN:
            for b in self.buttons:
                if not b.name == "Back":
                    b.pos = (b.pos[0], b.pos[1]-self.bh//3)
        
        elif btn == BUTTON_WHEELUP:
            for b in self.buttons:
                if not b.name == "Back":
                    b.pos = (b.pos[0], b.pos[1]+self.bh//3)
        
        elif btn == BUTTON_LEFT:
            for b in self.buttons:
                if b.click(pos):
                    return True
        return False
    
    #########################################################################################