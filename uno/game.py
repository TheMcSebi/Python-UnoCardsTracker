from __future__ import annotations
from datetime import timedelta
from random import randint

from os.path import join, dirname, realpath

from pygame.locals import *
from pygame.event import Event
from pygame.draw import line

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
        #self.stack_card_distance = 10
        self.aa = True
        self.dragging_card = {}
    
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
            self.cards.append({"card": card, "img": self.cards_gen.raster_playing_card(card), "pos": (card_x, card_y), "value": int(card[-1:])})
        self.card_stacks = []
        #self.stack = []
        self.card_pos = (0, 0)
        #self.stack_base_pos = self.stack_pos
        #self.prev_stack_pos = self.stack_pos

        
        borderdist = self.card_sec_height//2
        #self.clear_img_pos = (self.g.w-borderdist, self.g.h-borderdist)

        player_sec_height = self.g.h - self.card_sec_height - 155
        
        for p in self.g.players:
            # add cardstacks for each player
            cstack = CardStack(
                g = self.g, 
                img = self.cards_gen.raster_playing_card("back", 30 - (60/(self.g.pcount - 1)*(p["num"]-1))), 
                pos = (self._get_player_position(p["num"]), self.g.h - self.card_sec_height - player_sec_height//1.4), 
                size = (self.segwidth, player_sec_height)
            )
            cstack.add_cards(p["cards"])
            self.card_stacks.append(cstack)

            # regarding win-buttons
            card_x = self._get_player_position(p["num"]) + self.segwidth//2 - 80
            card_y = self.g.h - self.card_sec_height - 77
            self.buttons.append(Button(self.g, f"f::crown.png::0.35::player{p['num']}", (card_x, card_y), None, self.button_handler, FONT_LG, border_size=-1))
    
    

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
                cstack.add_cards(p["cards"])
        else:
            for p in self.g.players:
                if name == f"f::crown.png::p{p['num']}":
                    self.player_action(p, "win")
        
    def _get_player_position(self, pnum : int) -> int:
        lpos = self.g.w//self.g.pcount*pnum
        return lpos - self.segwidth//2

    def loop(self, events : list[Event]) -> None:
        for c in self.cards:
            self.g.blit_aligned(c["img"], c["pos"])
        
        for st in self.card_stacks:
            st.draw()
        
        for p in self.g.players:
            lpos = self.g.w//self.g.pcount*p["num"]
            
            
            # vlines
            if p["num"] < self.g.pcount:
                line(self.window, WHITE, (lpos, 0), (lpos, self.g.h - self.card_sec_height), 5)
            
            # name
            tpos = lpos - self.segwidth + 20
            align = (0, 2)
            self.g.blit_aligned(FONT_LG.render(f"{p['name']}", self.aa, self.g.player_colors[p["num"]]), (tpos, self.g.h-self.card_sec_height-120), align=align)
            self.g.blit_aligned(FONT_LG.render(f"{p['cards']} Karten gezogen", self.aa, self.g.player_colors[p["num"]]), (tpos, self.g.h-self.card_sec_height-80), align=align)
            self.g.blit_aligned(FONT_LG.render(f"{p['flashes']} mal geblitzt", self.aa, self.g.player_colors[p["num"]]), (tpos, self.g.h-self.card_sec_height-40), align=align)
        
        # hlines
        line(self.window, WHITE, (0, self.g.h - self.card_sec_height), (self.g.w, self.g.h - self.card_sec_height), 5)
        line(self.window, WHITE, (0, self.g.h - self.card_sec_height - 155), (self.g.w, self.g.h - self.card_sec_height - 155), 5)

        #for i,c in enumerate(self.stack):
        #    self.g.blit_centered(c["img"], (self.stack_pos[0] + c["offset"][0], self.stack_pos[1] + c["offset"][1] - i*self.stack_card_distance))
        
        # game timer
        game_time = FONT_MD.render(str(timedelta(seconds=self.g.get_game_time()//1000)), self.aa, WHITE)
        self.window.blit(game_time, (self.g.w - game_time.get_size()[0] - 5, 5))

        if self.dragging_card:
            self.g.blit_aligned(self.dragging_card["img"], self.card_pos)
        
        # clear button image
        #self.g.blit_centered(self.clear_img, self.clear_img_pos)
        # current stack size
        #self.g.blit_centered(FONT_XL.render(f"({len(self.stack)})", self.aa, WHITE), (self.clear_img_pos[0] - (self.g.w - self.clear_img_pos[0] + 20), self.clear_img_pos[1]))

        # menu buttons
        for b in self.buttons:
            b.draw()
    
    def keydown(self, k : int, kmods : int) -> bool:
        if k > K_0 and k <= K_9:
            #num = k - K_1
            #cards = self.cards_gen.get_random_cards(num)
            #for c in cards:
                #self.stack.append({"img": self.cards_gen.raster_playing_card(c, randint(0, 180)-90), "offset": (randint(0, 20)-10, 0)})
                #self.player_action(self.g.players[num], "draw")
            return True

        elif k == K_q or k == K_ESCAPE:
            self.g.setstate(0)
            return True
        
        return False
    
    def mouse_event(self, event : Event) -> bool:
        t = event.type
        p = event.pos
        is_touch = event.touch
        
        if t == MOUSEBUTTONDOWN:
            b = event.button
            #if self.g.check_collision_center(self.stack_pos, (self.cards_gen.w, self.cards_gen.h), p):
            #    self.dragging_stack = b
            #    return True
            if self.dragging_card:
                return True
            for c in self.cards:
                if self.g.check_collision_center(c["pos"], c["img"].get_size(), p):
                    self.dragging_card = c
                    self.card_pos = c["pos"]
        elif t == MOUSEBUTTONUP:
            b = event.button
            
            is_over_player = self.get_player_clicked(p)

            if self.dragging_card:

                if not is_over_player is None:
                    value = self.dragging_card["value"]
                    #self.stack_pos = self.stack_base_pos
                    self.card_stacks[is_over_player["num"] - 1].add_cards(value)
                    self.player_action(is_over_player, "draw", value)
                    #cstack.add_cards(p["cards"])
                    #self.stack = []
                    self.dragging_card = {}
                else:
                    self.dragging_card = {}
                
                return True
            else:
                # check buttons
                if b == BUTTON_LEFT:
                    for button in self.buttons:
                        if button.click(p): 
                            return True
                # check players
                is_over_player = self.get_player_clicked(p)
                if not is_over_player is None:
                    self.player_action(is_over_player, "flash")
        elif t == MOUSEMOTION:
            r = event.rel
            b = event.buttons
            if self.dragging_card:
                self.card_pos = (self.card_pos[0]+r[0], self.card_pos[1]+r[1])
                return True
        return False

    def click(self, pos : tuple, btn = int) -> bool:
        #(x, y) = pos
        #
        #if btn == BUTTON_LEFT:
        #    for c in self.cards:
        #        if self.g.check_collision_center(c["pos"], c["img"].get_size(), pos):
        #            draw_cards = 0
        #            if c["card"] == "red_draw2":
        #                draw_cards = 2
        #            elif c["card"] == "red_8":
        #                draw_cards = 8
        #            elif c["card"] == "wildplus4":
        #                draw_cards = 4
        #            
        #            if draw_cards > 0:
        #                cards = self.cards_gen.get_random_cards(draw_cards)
        #                for c in cards:
        #                    self.stack.append({"img": self.cards_gen.raster_playing_card(c, randint(0, 180)-90), "offset": (randint(0, 20)-10, 0)})
        #            
        #            return True
        #    #if self.g.check_collision_center(self.clear_img_pos, self.clear_img.get_size(), pos):
        #    #    self.stack = []
        #    #    self.stack_pos = self.stack_base_pos
        #    #    return True
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
    
    def player_action(self, p : dict, action : str, value : int = 1) -> None:
        if p is None:
            return

        print(f"{p['name']} {action} {value}")
        
        if action == "draw":
            p["cards"] += value
        elif action == "flash":
            p["flashes"] += value
        self.g.playerdata_changed(p, action)