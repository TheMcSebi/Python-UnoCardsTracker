from __future__ import annotations

from pygame import Surface
from pygame.event import Event
from pygame.draw import rect
from random import randint

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..uno import Uno

class ParticleExplosion:
    def __init__(self, g : Uno, img : Surface, pos : tuple[int], duration : int = 250, particles : int = 50) -> None:
        self.g = g
        self.window = g.window
        self.pos = pos
        self.img = img
        #self.size = size
        self.duration = duration
        #self.time_elapsed = 0
        self.particles = []
        self.finished = False

        for i in range(0, particles):
            vel = (randint(-10, 10), randint(-10, 10))
            self.particles.append({"pos": self.pos, "vel": vel, "life": duration})

    def loop(self, window : Surface = None) -> None:
        if not self.finished:
            if window is None:
                window = self.window

            particles_left = False
            for p in self.particles:
                self.g.blit_aligned(self.img, p["pos"], window)
                p["pos"] = (p["pos"][0] + p["vel"][0], p["pos"][1] + p["vel"][1])
                p["life"] -= 1
                if p["life"] <= 0:
                    self.particles.remove(p)
                    continue
                particles_left = True
        
            if not particles_left:
                self.finished = True