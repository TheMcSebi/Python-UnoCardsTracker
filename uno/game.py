from __future__ import annotations
from datetime import timedelta
from random import randint

from os.path import join, dirname, realpath

from pygame.locals import *
from pygame.event import Event
from pygame.draw import line
from pygame.time import Clock, get_ticks

from .constants import *
from .components.button import Button
from .components.cards import Cards
from .components.cardstack import CardStack
from .components.particleexplosion import ParticleExplosion
from .components.popup import Popup
from .components.scrollablelist import ScrollableList

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

    #########################################################################################

    def setup(self) -> None:
        if self.g.pcount == 0:
            self.g.setstate(0)
            return
        
        self.session_start_time = get_ticks()

        self.card_padding = 30
        self.aa = True
        self.dragging_card = {}
        self.cards_gen = Cards()
        self.cards = []
        self.card_stacks = []
        self.card_pos = (0, 0)
        self.popup = None
        self.particleexplosions = []
        self.star_image = self.g.load_asset_image("star.png", 0.2)
        self.last_action_time = None
        self._update_last_action_time()
        self.popup_delay = 300_000 # 5 min
        
        #self.history_console_length = 16

        self.segwidth = self.g.w / self.g.pcount
        self.buttons = [
            Button(self.g, "Back", (100, 50), (200, 100), self.button_handler, FONT_LG),
            Button(self.g, "Undo", (300, 50), (200, 100), self.button_handler, FONT_LG),
            Button(self.g, "Stats", (500, 50), (200, 100), self.button_handler, FONT_LG),
            Button(self.g, "Pause", (700, 50), (200, 100), self.button_handler, FONT_LG),
            #Button(self.g, "Test", (900, 50), (200, 100), self.button_handler, FONT_LG),
        ]

        self.card_sec_height = self.cards_gen.h + self.card_padding*2
        
        card_y = self.g.h - self.card_sec_height/2
        for i,card in enumerate(self.cards_gen.drawing_cards):
            card_x = self.cards_gen.w//2 + self.cards_gen.w*i + self.card_padding*(i+1)
            self.cards.append({"card": card, "img": self.cards_gen.raster_playing_card(card), "pos": (card_x, card_y), "value": int(card[-1:])})

        player_sec_height = self.g.h - self.card_sec_height - 155
        self.session_stats = {}
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
            self.buttons.append(Button(self.g, f"f::crown.png::0.35::win::{p['num']}", self._get_win_button_pos(p["num"]), None, self.button_handler, FONT_LG, border_size=-1))

            # add session stats
            self.session_stats[p["name"]] = {"wins": 0, "cards": 0}
        
        # Instanciate the history console 
        self.history_console = ScrollableList(self.g, (self.g.w - 300, self.g.h - self.card_sec_height + 5))
    
    def button_handler(self, name : str) -> None:
        if name == "Back":
            self.g.setstate(0)
            return
            
        elif name == "Stats":
            self.g.setstate(3)
            return

        elif name == "Undo":
            if self.g.undo():
                self.history_console.pop()
            return

        elif name == "Pause":
            self._display_pause_popup()
            return
        
        elif name == "Test":
            self.history_console_entry("Test " + str(get_ticks()))
            return
        
        elif "::" in name:
            parts = name.split("::")
            if parts[-2] == "win":
                for p in self.g.players:
                    if int(parts[-1]) == p['num']:
                        self._player_action(p, "win")
                        self.particleexplosions.append(ParticleExplosion(self.g, self.star_image, self._get_win_button_pos(p["num"]), 240))
            return
        print(f"Unknown button: {name}")
        
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
            tpos2 = lpos - self.segwidth//2
            align = (0, 2)
            
            self.g.blit_aligned(FONT_LG.render(f"{p['name']}", self.aa, self.g.player_colors[p["num"]]), (tpos, self.g.h-self.card_sec_height-120), align=align)
            
            self.g.blit_aligned(FONT_LG.render(f"{p['cards']} cards", self.aa, self.g.player_colors[p["num"]]), (tpos, self.g.h-self.card_sec_height-80), align=align)
            self.g.blit_aligned(FONT_MD.render(f"({self.session_stats[p['name']]['cards']})", self.aa, self.g.player_colors[p["num"]]), (tpos2, self.g.h-self.card_sec_height-80), align=align)
            
            self.g.blit_aligned(FONT_LG.render(f"{p['wins']} wins", self.aa, self.g.player_colors[p["num"]]), (tpos, self.g.h-self.card_sec_height-40), align=align)
            self.g.blit_aligned(FONT_MD.render(f"({self.session_stats[p['name']]['wins']})", self.aa, self.g.player_colors[p["num"]]), (tpos2, self.g.h-self.card_sec_height-40), align=align)
        
        # hlines
        line(self.window, WHITE, (0, self.g.h - self.card_sec_height), (self.g.w, self.g.h - self.card_sec_height), 5)
        line(self.window, WHITE, (0, self.g.h - self.card_sec_height - 155), (self.g.w, self.g.h - self.card_sec_height - 155), 5)

        # game timer and session timer
        game_time = FONT_MD.render("Game time: " + str(timedelta(seconds=self.g.get_game_time()//1000)), self.aa, WHITE)
        session_time = FONT_MD.render("Session time: " + str(timedelta(seconds=(get_ticks()-self.session_start_time)//1000)), self.aa, WHITE)
        fontheight = session_time.get_size()[1] # they have the same height

        self.window.blit(game_time, (self.g.w - (game_time.get_size()[0] + 5), 5))
        self.window.blit(session_time, (self.g.w - (session_time.get_size()[0] + 5), 10 + fontheight))

        # # draw history console in the bottom right corner
        # for i,msg in enumerate(self.history_console[::-1]):
        #     txt = FONT_MD.render(msg, self.aa, WHITE)
        #     dim = txt.get_size()
        #     self.window.blit(txt, (self.g.w - 5 - dim[0], self.g.h - self.card_sec_height + (i+1)*(dim[1] + 5)))
        
        self.history_console.draw()

        # menu buttons
        for b in self.buttons:
            b.draw()
        
        for p in self.particleexplosions:
            p.loop()
            if p.finished:
                self.particleexplosions.remove(p)

        if self.dragging_card:
            self.g.blit_aligned(self.dragging_card["img"], self.card_pos)
        
        if self.popup:
            self.popup.draw()
        
        elif self.last_action_time + self.popup_delay < get_ticks():
            self._display_pause_popup() # this enables the popup
    
    def keydown(self, k : int, kmods : int) -> bool:
        if k == K_q or k == K_ESCAPE:
            self.g.setstate(0)
            return True
        return False
    
    def popup_button_handler(self, name : str) -> None:
        if name == "Yes":
            self.g.ticks_start += get_ticks() - self.popup.ticks_created
            self.popup = None
            self._update_last_action_time()
        
        elif name == "No":
            self.g.setstate(0)
    
    def mouse_event(self, event : Event) -> bool:
        if self.popup:
            self.popup.mouse_event(event)
            return True
        
        if self.history_console.mouse_event(event):
            return True
        
        t = event.type
        p = event.pos
        #is_touch = event.touch # unused because unnecessary for functionality
        
        if t == MOUSEBUTTONDOWN:
            b = event.button
            if self.dragging_card:
                return True
            for c in self.cards:
                if self.g.check_collision_center(c["pos"], c["img"].get_size(), p):
                    self.dragging_card = c
                    self.card_pos = c["pos"]
                    return True
        
        elif t == MOUSEBUTTONUP:
            self._update_last_action_time()
            b = event.button
            
            is_over_player = self._get_player_clicked(p)

            if self.dragging_card:

                if not is_over_player is None:
                    value = self.dragging_card["value"]
                    self.card_stacks[is_over_player["num"] - 1].add_cards(value)
                    self._player_action(is_over_player, "draw", value)
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
                #is_over_player = self._get_player_clicked(p)
                #if not is_over_player is None:
                #    self._player_action(is_over_player, "flash")
        
        elif t == MOUSEMOTION:
            r = event.rel
            b = event.buttons
            if self.dragging_card:
                self.card_pos = (self.card_pos[0]+r[0], self.card_pos[1]+r[1])
                return True
        return False

    def click(self, pos : tuple, btn = int) -> bool:
        return False
    
    #########################################################################################

    def _update_last_action_time(self) -> None:
        self.last_action_time = get_ticks()
    
    def _get_player_clicked(self, click_pos : tuple) -> dict:
        if click_pos[1] > self.g.h-self.card_sec_height:
            return None
        for p in self.g.players:
            lpos = self.g.w//self.g.pcount*p["num"]
            if click_pos[0] > lpos - self.segwidth and click_pos[0] < lpos:
                return p
        return None
    
    def _get_player_position(self, pnum : int) -> int:
        lpos = self.g.w//self.g.pcount*pnum
        return lpos - self.segwidth//2
    
    def _get_win_button_pos(self, pnum : int) -> tuple:
        winbtn_x = self._get_player_position(pnum) + self.segwidth//2 - 80
        winbtn_y = self.g.h - self.card_sec_height - 77
        return (winbtn_x, winbtn_y)
    
    def _player_action(self, p : dict, action : str, value : int = 1) -> None:
        if p is None:
            return

        print(f"{p['name']} {action} {value}")
        
        if action == "draw":
            p["cards"] += value
            self.history_console.add(f"{p['name']} draws {value} cards")
            self.session_stats[p["name"]]["cards"] += value
        
        elif action == "win":
            p["wins"] += value
            self.history_console.add(f"{p['name']} wins")
            self.session_stats[p["name"]]["wins"] += value
        
        self.g.playerdata_changed(p, action)
    
    def _display_pause_popup(self) -> None:
        self.popup = Popup(self.g, "Hey!", "Are you still playing?", ["Yes", "No"], self.popup_button_handler)