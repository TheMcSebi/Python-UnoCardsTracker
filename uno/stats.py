from __future__ import annotations

from copy import deepcopy

from pygame import Surface
from pygame.locals import *
from pygame.event import Event
from pygame.draw import circle, line
from pygame.transform import flip

from .constants import *
from .components.button import Button

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .uno import Uno

class Stats:
    """
    Stats screen
    """
    def __init__(self, game : Uno) -> None:
        self.g = game
        self.window = self.g.window
        self.stroke_width = 2
        self.circle_radius = 4
    
    #########################################################################################
    
    def setup(self) -> None:
        self.bw = self.g.w//2
        self.bh = self.g.h//8
        self.img = Surface((int(self.g.w*0.93), int(self.g.h*0.86)))
        self.img.fill(BLACK)
        self.buttons = [Button(self.g, "Back", (100, 50), (200, 100), self.button_handler, FONT_LG)]
        self.w, self.h = self.img.get_size()
        self.bottom_margin = 50

        # find highest values
        max_time = 0
        max_cards = 0
        for p in self.g.players:
            if p["history"][-1]["time"] > max_time:
                max_time = p["history"][-1]["time"]
            if p["cards"] > max_cards:
                max_cards = p["cards"]
            
        # graph scale
        tickmult = self.w/max_time
        scoremult = (self.h-self.bottom_margin)/max_cards

        # create paths
        player_markers = []
        for p in self.g.players:
            obj = {
                "color": self.g.player_colors[p["num"]], 
                "waypoints": [
                    {
                        "pos": (0, self.h-self.bottom_margin), 
                        "action": "draw"
                    }
                ]
            }

            # create paths
            prev_pos = obj["waypoints"][0]["pos"]
            curr_cards = 0
            for h in p["history"]:
                if h["action"] == "draw":
                    curr_cards += h["value"]

                pos = (
                    int(h["time"] * tickmult), 
                    int(self.h - self.bottom_margin - curr_cards*scoremult)
                )

                obj["waypoints"].append({"pos": pos, "action": h["action"]})
                
            player_markers.append(deepcopy(obj))
        
        for m in player_markers:
            # draw all colored draw count lines
            prev_pos = m["waypoints"][0]["pos"]
            for w in m["waypoints"][1:]:
                line(self.img, m["color"], prev_pos, w["pos"], self.stroke_width)
                prev_pos = w["pos"]
            line(self.img, m["color"], prev_pos, (self.w, prev_pos[1]), self.stroke_width)

            # draw circles
            for w in m["waypoints"]:
                color = m["color"]
                cr = 1
                if w["action"] == "win":
                    color = YELLOW
                    cr = 2
                circle(self.img, color, w["pos"], self.circle_radius*cr)
                

        hstepsize = 1
        while max_cards//hstepsize > 10:
            hstepsize += 1
        print(hstepsize)

        # cards lines
        for i in range(0, max_cards, hstepsize):
            ypos = self.h-self.bottom_margin-i*scoremult
            line(self.img, WHITE, (0, ypos), (self.w, ypos), self.stroke_width//2)
            self.g.blit_aligned(FONT_MD.render(str(i*hstepsize), True, WHITE), (50, ypos-10))
        line(self.img, WHITE, (0, 0), (self.w, 0), self.stroke_width//2)

        minute_mark_interval = 30
        ticklines = 0
        while ticklines < 5:
            if minute_mark_interval > 1:
                minute_mark_interval -= 1
            else:
                minute_mark_interval /= 2
            ticklines = (self.w-50)/(minute_mark_interval*60*1000*tickmult)
        
        ticklines = int(ticklines) + 1
        for i in range(0, ticklines):
            tick = i*minute_mark_interval*60*1000
            xpos = tick*tickmult
            line(self.img, WHITE, (xpos, 0), (xpos, self.h-self.bottom_margin), self.stroke_width//2)
            if i == 0: # move first number a little to the right
                xpos += 20
            self.g.blit_aligned(FONT_MD.render(str(i*minute_mark_interval), True, WHITE), (xpos, self.h-30), self.img)
        # move last number a little to the left
        line(self.img, WHITE, (self.w-self.stroke_width//2, 0), (self.w-self.stroke_width//2, self.h-self.bottom_margin), self.stroke_width//2)
        self.g.blit_aligned(FONT_MD.render(str(round(max_time/1000/60, 1)), True, WHITE), (self.w-20, self.h-30), self.img)
        
    
    def button_handler(self, name : str) -> None:
        if name == "Back":
            self.g.setstate(1)
            return
    
    def loop(self, events : list[Event]) -> None:
        self.g.blit_aligned(self.img, (self.g.w//2, self.g.h//2))
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