from __future__ import annotations
from typing import TYPE_CHECKING

from pygame import Surface
from pygame.event import Event
from pygame.time import Clock, get_ticks
from pygame.locals import *

from ..constants import *
from .button import Button

if TYPE_CHECKING:
    from ..uno import Uno

class Popup:
    def __init__(self, g : Uno, heading : str = None, text : str = None, buttons : list[Button] = [], button_handler = None) -> None:
        self.g = g
        self.window = g.window
        self.pos = (self.g.h/2, self.g.w/2)
        self.heading = None
        self.heading = heading
        self.text = text
        self.buttons = []
        self.ticks_created = get_ticks()
        for b in buttons:
            bpos = self.pos
            bsize = (200, 50)
            self.buttons.append(Button(self.g, b, bpos, bsize, button_handler, FONT_MD, border_size=2))

    def draw(self) -> None:
        self.g.blit_aligned(self.stack_img, self.pos)
        for b in self.buttons:
            b.draw(self.window)
    def mouse_event(self, event : Event) -> None:
        for b in self.buttons:
            if b.click(event.pos):
                return