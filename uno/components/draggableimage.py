from __future__ import annotations
from pygame.event import Event
from pygame import Surface


# TODO: move all relevant code from game.py to here

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..uno import Uno

class DraggableImage:
    def __init__(self, g : Uno, img : Surface, base_pos : tuple[int]) -> None:
        self.g = g
        self.window = g.window
        self.img = img
        self.base_pos = base_pos

    def setup(self) -> None:
        pass

    def draw(self, events : list[Event]) -> None:
        self.g.blit_aligned(self.card, self.base_pos)
        for e in events:
            print(e)