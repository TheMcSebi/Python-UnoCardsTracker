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
        self.stack_height = [230, 460, 680, 900, 1120, 1340, 1560, 1780, 2000]
        self.reset()

    def reset(self) -> None:
        self.stack_img = Surface(self.size)
        self.stack_size = 0
    
    def setup(self) -> None:
        pass

    def draw(self) -> None:
        if not self.stack_img is None:
            self.g.blit_aligned(self.stack_img, self.pos)
    
    def add_cards(self, num : int = 1) -> None:
        for i in range(0, num):
            #rowid = (self.stack_size**1.3)//500
            #x_pos = (rowid * self.size[0]) * 1.5
            #y_pos = self.size[1] - 50 -(rowid*60) - self.stack_size*self.v_dist

            if self.stack_size < self.stack_height[0]:
                pos = (self.size[0]//2, self.size[1] - 100 - self.stack_size*self.v_dist)
            elif self.stack_size < self.stack_height[1]:
                pos = (self.size[0]//2 - 40, self.size[1] - 70 - (self.stack_size-self.stack_height[0])*self.v_dist)
            elif self.stack_size < self.stack_height[2]:
                pos = (self.size[0]//2 + 40, self.size[1] - 70 - (self.stack_size-self.stack_height[1])*self.v_dist)
            elif self.stack_size < self.stack_height[3]:
                pos = (self.size[0]//2 - 80, self.size[1] - 35 - (self.stack_size-self.stack_height[2])*self.v_dist)
            elif self.stack_size < self.stack_height[4]:
                pos = (self.size[0]//2, self.size[1] - 35 - (self.stack_size-self.stack_height[3])*self.v_dist)
            else: #if self.stack_size < self.stack_height[5]:
                pos = (self.size[0]//2 + 80, self.size[1] - 35 - (self.stack_size-self.stack_height[4])*self.v_dist)
            
            self.g.blit_aligned(self.card_back_img, pos, self.stack_img)
            self.stack_size += 1
        