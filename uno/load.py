from __future__ import annotations
from re import I
from pygame import Color
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
        self.maybe_dragging = False
        self.dragging = False

    #########################################################################################
    
    def setup(self) -> None:
        self.saves = self.g.get_saves_info()
        self.bw = self.g.w - self.g.w//8
        self.bh = self.g.h//8

        self.buttons = []
        for i, s in enumerate(self.saves):
            btncol = Color(0, 0, 0)
            btncol.hsva = (i*(360/len(self.saves)), 100, 100, 100)
            self.buttons.append(Button(
                self.g, 
                name=s["title"], 
                pos=(self.g.w//2, self.g.h//12 + i*self.bh), 
                size=(self.bw, self.bh), 
                handler=self.button_handler, 
                font=FONT_L, 
                subtext=", ".join(s["players"]), 
                font_subtext=FONT_MD, 
                color=btncol,
                tag=s["filename"]
                #color=self.g.player_colors[len(s["players"])-2]
            ))

        self.buttons.append(Button(self.g, name="Back", pos=(100, 50), size=(200, 100), handler=self.button_handler, font=FONT_LG))
    
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
        if event.touch:
            if event.type == MOUSEBUTTONDOWN:
                self.maybe_dragging = True
                return True
            if event.type == MOUSEMOTION:
                if self.maybe_dragging:
                    self.dragging = True
                    self.maybe_dragging = False
                if self.dragging:
                    for b in self.buttons:
                        if not b.name == "Back":
                            b.pos = (b.pos[0], b.pos[1]+event.rel[1])
            if event.type == MOUSEBUTTONUP:
                self.maybe_dragging = False
                if self.dragging:
                    self.dragging = False
                    return True
        
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
        
        elif btn == BUTTON_LEFT: # needs to be here for the scroll events to take precedence
            for b in self.buttons:
                if b.click(pos):
                    return True
            pass

        return False

    #########################################################################################