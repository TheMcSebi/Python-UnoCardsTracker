from __future__ import annotations
from pygame.event import Event
from pygame import Surface

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..uno import Uno

class CardStack:
    def __init__(self, g : Uno, img : Surface, pos : tuple[int]) -> None:
        self.g = g
        self.window = g.window
        self.card_back_img = img
        self.pos = pos
        self.v_dist = 4
        self.imdim = (250, 1000)
        self.reset()

    def reset(self) -> None:
        self.stack_img = Surface(self.imdim)
        self.stack_size = 0
    
    def setup(self) -> None:
        pass

    def draw(self) -> None:
        if not self.stack_img is None:
            self.g.blit_centered(self.stack_img, self.pos)
    
    def add_cards(self, num : int = 1) -> None:
        for i in range(0, num):
            if self.stack_size < 140:
                self.g.blit_centered(self.card_back_img, (self.imdim[0]//2, self.imdim[1] - 100 - self.stack_size*self.v_dist), self.stack_img)
            elif self.stack_size < 260:
                self.g.blit_centered(self.card_back_img, (self.imdim[0]//2 - 40, self.imdim[1] - 70 - (self.stack_size-140)*self.v_dist), self.stack_img)
            else:
                self.g.blit_centered(self.card_back_img, (self.imdim[0]//2 + 40, self.imdim[1] - 70 - (self.stack_size-260)*self.v_dist), self.stack_img)
            self.stack_size += 1