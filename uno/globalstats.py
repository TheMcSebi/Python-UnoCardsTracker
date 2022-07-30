from __future__ import annotations
from re import I
from tabulate import tabulate

from pygame.locals import *
from pygame.event import Event
from pygame.font import Font

from .constants import *
from .components.button import Button
from .components.scrollablelist import ScrollableList

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .uno import Uno

class GlobalStats:
    """
    Statistics screen for all saves.
    """
    def __init__(self, game : Uno) -> None:
        self.g = game
        self.window = self.g.window

    #########################################################################################
    
    def setup(self) -> None:
        self.saves = self.g.get_saves()
        self.buttons : list[Button] = []

        self._button_names = ["Back", "Table", "Graph1", "Graph2", "Graph3"]
        for i,b in enumerate(self._button_names):
            self.buttons.append(Button(self.g, b, (100+(i*200), 50), (200, 100), self.button_handler, FONT_LG))
        
        
        players = {}
        for s in self.saves:
            for p in s["data"]["players"]:
                if p["name"] not in players.keys():
                    players[p["name"]] = {"wins": 0, "cards": 0}
                if "wins" in p.keys():
                    players[p["name"]]["wins"] += p["wins"]
                if "cards" in p.keys():
                    players[p["name"]]["cards"] += p["cards"]
        
        self.players = [{"name": p, "wins": players[p]["wins"], "cards": players[p]["cards"]} for p in players.keys()]
        
        self.current_page = None
        self._display_page(0) # sets current_page
        
    def button_handler(self, name : str) -> None:
        if name == "Back":
            self.g.setstate(0)
            return
        else:
            self._display_page(self._button_names.index(name)-1)
    
    def loop(self, events : list[Event]) -> None:
        if self.display_mode == "lists":
            self.left_list.draw()
            self.list_wins.draw()
        elif self.display_mode == "chart":
            pass

        for b in self.buttons:
            b.draw()
    
    def keydown(self, k : int, kmods : int) -> bool:
        if k == K_q or k == K_ESCAPE:
            self.g.setstate(0)
            return True
        return False
    
    def mouse_event(self, event : Event) -> bool:
        if True in [b.mouse_event(event) for b in self.buttons]:
            return True
        if self.display_mode == "lists":
            if self.list_wins.mouse_event(event):
                return True
            if self.left_list.mouse_event(event):
                return True
        
        return False
    
    def click(self, pos : tuple, btn = int) -> bool:
        return False
    
    #########################################################################################

    def _display_page(self, id : int) -> None:
        self.current_page = id
        self.display_mode = None
        self.left_list = None
        self.right_list = None

        if id == 0:
            self.display_mode = "lists"
            self.left_list = ScrollableList(self.g, (50, 50), font=FONT_MONOSP, direction="bottomlast")
            self.list_wins = ScrollableList(self.g, (self.g.w//2 + 50, 50), font=FONT_MONOSP, direction="bottomlast")
            tableheader = {"name": "Name", "wins": "Wins", "cards": "Cards"}

            players_by_cards = tabulate(sorted(self.players, key=lambda x: x["cards"], reverse=True), headers=tableheader, showindex=range(1, len(self.players)+1)).split("\n")
            self.left_list.add("Players by cards:")
            for line in players_by_cards:
                self.left_list.add(line)
            
            players_by_wins = tabulate(sorted(self.players, key=lambda x: x["wins"], reverse=True), headers=tableheader, showindex=range(1, len(self.players)+1)).split("\n")
            self.list_wins.add("Players by wins:")
            for line in players_by_wins:
                #line = f"{i}. {p['name']}: {p['wins']} wins, {p['cards']} cards"
                self.list_wins.add(line)