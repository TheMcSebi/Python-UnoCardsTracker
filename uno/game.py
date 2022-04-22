from __future__ import annotations
from datetime import timedelta
from random import randint

from os.path import join, dirname, realpath

from pygame.locals import *
from pygame.event import Event
from pygame.draw import line
from pygame.image import load

from .constants import *
from .components.button import Button
from .components.cards import Cards
from .components.cardstack import CardStack
#from .components.draggablecard import DraggableCard

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .uno import Uno

class Game:
    """
    Level board screen
    """
    def __init__(self, game : Uno) -> None:
        self.g = game
        self.window = self.g.window

        self.card_padding = 30
        self.stack_card_distance = 10
        self.aa = True
        self.dragging = 0
    
    #########################################################################################

    def setup(self) -> None:
        if self.g.pcount == 0:
            self.g.setstate(0)
            return
        
        self.segwidth = self.g.w / self.g.pcount
        self.buttons = [
            Button(self.g, "Back", (100, 50), (200, 100), self.button_handler, FONT_LG),
            #Button(self.g, "Stats", (300, 50), (200, 100), self.button_handler, FONT_LG)
            Button(self.g, "Undo", (300, 50), (200, 100), self.button_handler, FONT_LG)
        ]

        self.cards_gen = Cards()
        self.card_sec_height = self.cards_gen.h + self.card_padding*2
        self.cards = []
        card_y = self.g.h - self.card_sec_height/2
        for i,card in enumerate(self.cards_gen.drawing_cards):
            card_x = self.cards_gen.w//2 + self.cards_gen.w*i + self.card_padding*(i+1)
            self.cards.append({"card": card, "img": self.cards_gen.raster_playing_card(card), "pos": (card_x, card_y)})
        
        self.stack = []
        self.stack_pos = (self.g.w//2, self.g.h - 70)
        self.stack_base_pos = self.stack_pos

        self.clear_img = load(join(self.g.assets_dir, "clear-sign.png")).convert_alpha()
        borderdist = self.card_sec_height//2
        self.clear_img_pos = (self.g.w-borderdist, self.g.h-borderdist)

        self.card_stacks = []
        for p in self.g.players:
            cstack = CardStack(self.g, self.cards_gen.raster_playing_card("back", 30 - (60/(self.g.pcount - 1)*(p["num"]-1))), (self._get_player_position(p["num"]), self.g.h-self.card_sec_height - 550))
            cstack.add_cards(p["score"])
            self.card_stacks.append(cstack)

    
    def button_handler(self, name : str) -> None:
        if name == "Back":
            self.g.setstate(0)
        elif name == "Stats":
            self.g.setstate(3)
        elif name == "Undo":
            self.g.undo()
            # stacks need to be redrawn
            for p in self.g.players:
                cstack = self.card_stacks[p["num"] - 1]
                cstack.reset()
                cstack.add_cards(p["score"])
        
    def _get_player_position(self, pnum : int) -> int:
        lpos = self.g.w//self.g.pcount*pnum
        return lpos - self.segwidth//2

    def loop(self, events : list[Event]) -> None:
        for c in self.cards:
            self.g.blit_centered(c["img"], c["pos"])
        
        for st in self.card_stacks:
            st.draw()
        
        for p in self.g.players:
            lpos = self.g.w//self.g.pcount*p["num"]
            tpos = lpos - self.segwidth//2

            color = WHITE
            
            # vlines
            if p["num"] < self.g.pcount:
                line(self.window, WHITE, (lpos, 0), (lpos, self.g.h - self.card_sec_height), 5)
            
            # name and score
            self.g.blit_centered(FONT_LG.render(p["name"], self.aa, self.g.player_colors[p["num"]]), (tpos, self.g.h-self.card_sec_height-40))
            self.g.blit_centered(FONT_XL.render(str(p["score"]), self.aa, color), (tpos, self.g.h//2))
        
        # hline
        line(self.window, WHITE, (0, self.g.h - self.card_sec_height), (self.g.w, self.g.h - self.card_sec_height), 5)

        for i,c in enumerate(self.stack):
            self.g.blit_centered(c["img"], (self.stack_pos[0] + c["offset"][0], self.stack_pos[1] + c["offset"][1] - i*self.stack_card_distance))
        
        # game timer
        game_time = FONT_MD.render(str(timedelta(seconds=self.g.get_game_time()//1000)), self.aa, WHITE)
        self.window.blit(game_time, (self.g.w - game_time.get_size()[0] - 5, 5))
        
        # clear button image
        self.g.blit_centered(self.clear_img, self.clear_img_pos)

        # menu buttons
        for b in self.buttons:
            b.draw()
    
    def keydown(self, k : int, kmods : int) -> bool:
        if k > K_0 and k <= K_9:
            num = k - K_1
            cards = self.cards_gen.get_random_cards(num)
            for c in cards:
                self.stack.append({"img": self.cards_gen.raster_playing_card(c, randint(0, 180)-90), "offset": (randint(0, 20)-10, 0)})
            return True

        elif k == K_q or k == K_ESCAPE:
            self.g.setstate(0)
            return True
        
        return False
    
    def mouse_event(self, e : Event) -> bool:
        t = e.type
        p = e.pos
        is_touch = e.touch
        
        if t == MOUSEBUTTONDOWN:
            b = e.button
            if self.dragging > 0:
                self.dragging = 0
                self.stack_pos = self.stack_base_pos
                return True
            elif self.g.check_collision_center(self.stack_pos, (self.cards_gen.w, self.cards_gen.h), p):
                self.dragging = b
                #self.stack.pop()
                return True
        elif t == MOUSEBUTTONUP:
            b = e.button
            if self.dragging == b:
                self.dragging = 0

                player_clicked = self.get_player_clicked(p)
                if not player_clicked is None:
                    self.stack_pos = self.stack_base_pos
                    #print(player_clicked)
                    self.card_stacks[player_clicked["num"] - 1].add_cards(len(self.stack))
                    self.update_score(player_clicked, len(self.stack))
                    self.stack = []
                
                return True
            elif self.g.check_collision_center(self.stack_pos, (self.cards_gen.w, self.cards_gen.h), p):
                # prevent event propagation if stack is in the way TODO: check if it works
                print("hit stack on exiting mouse click event")
                return True
        
        elif t == MOUSEMOTION:
            r = e.rel
            b = e.buttons
            if self.dragging > 0 and b[self.dragging-1] == 1:
                self.stack_pos = (self.stack_pos[0]+r[0], self.stack_pos[1]+r[1])
                return True
        return False

    def click(self, pos : tuple, btn = int) -> bool:
        (x, y) = pos
        
        if btn == BUTTON_LEFT:
            for b in self.buttons:
                if b.click(pos): 
                    return True
            
            for c in self.cards:
                if self.g.check_collision_center(c["pos"], c["img"].get_size(), pos):
                    draw_cards = 0
                    if c["card"] == "red_draw2":
                        draw_cards = 2
                    elif c["card"] == "red_8":
                        draw_cards = 8
                    elif c["card"] == "wildplus4":
                        draw_cards = 4
                    
                    if draw_cards > 0:
                        cards = self.cards_gen.get_random_cards(draw_cards)
                        for c in cards:
                            self.stack.append({"img": self.cards_gen.raster_playing_card(c, randint(0, 180)-90), "offset": (randint(0, 20)-10, 0)})
                    
                    return True
            if self.g.check_collision_center(self.clear_img_pos, self.clear_img.get_size(), pos):
                self.stack = []
                self.stack_pos = self.stack_base_pos
                return True
            ## modify player level
            #_mod = 1
            #if y > self.g.h//2:
            #    _mod = -1
            #
            #p = self.get_player_clicked(x)
            #self.update_score(p, _mod)
            return False
    
    #########################################################################################
    
    def get_player_clicked(self, click_pos : tuple) -> dict:
        if click_pos[1] > self.g.h-self.card_sec_height:
            return None
        for p in self.g.players:
            lpos = self.g.w//self.g.pcount*p["num"]
            if click_pos[0] > lpos - self.segwidth and click_pos[0] < lpos:
                return p
        return None
    
    def update_score(self, p : dict, _mod : int) -> None:
        if p is None:
            return
        p["score"] += _mod
        self.g.playerdata_changed(p)