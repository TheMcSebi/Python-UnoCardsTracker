from __future__ import annotations
from pygame.event import Event
from pygame import Surface

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..uno import Uno

class CardStack:
    def __init__(self, g : Uno, img : Surface, pos : tuple[int], size : tuple[int]) -> None:
        self.g = g
        self.window = g.window
        self.card_back_img = img
        self.pos = pos
        self.size = size
        self.v_dist = 2
        self.size = size
        self.reset()

    def reset(self) -> None:
        self.stack_img = Surface(self.size)
        self.stack_size = 0
    
    def setup(self) -> None:
        pass

    def draw(self) -> None:
        if not self.stack_img is None:
            self.g.blit_centered(self.stack_img, self.pos)
    
    def add_cards(self, num : int = 1) -> None:
        for i in range(0, num):
            rowid = (self.stack_size**1.3)//500
            x_pos = (rowid * self.size[0]) * 1.5
            y_pos = self.size[1] - 150-(rowid*60) - self.stack_size*self.v_dist
            if self.stack_size < 140:
                self.g.blit_centered(self.card_back_img, (self.size[0]//2, y_pos), self.stack_img)
            elif self.stack_size < 260:
                self.g.blit_centered(self.card_back_img, (self.size[0]//2 - 40, self.size[1] - 70 - (self.stack_size-140)*self.v_dist), self.stack_img)
            elif self.stack_size < 380:
            else:
                self.g.blit_centered(self.card_back_img, (self.size[0]//2 + 40, self.size[1] - 70 - (self.stack_size-260)*self.v_dist), self.stack_img)
            self.stack_size += 1
        