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
        self.buttons = [Button(self.g, "Back", (100, 50), (200, 100), self.button_handler, FONT_LG)]
        self.list_cards = ScrollableList(self.g, (50, 50), font=FONT_MONOSP, direction="bottomlast")
        self.list_wins = ScrollableList(self.g, (self.g.w//2 + 50, 50), font=FONT_MONOSP, direction="bottomlast")
        players = {}
        for s in self.saves:
            for p in s["data"]["players"]:
                if p["name"] not in players.keys():
                    players[p["name"]] = {"wins": 0, "cards": 0}
                if "wins" in p.keys():
                    players[p["name"]]["wins"] += p["wins"]
                players[p["name"]]["cards"] += p["cards"]
        
        players = [{"name": p, "wins": players[p]["wins"], "cards": players[p]["cards"]} for p in players.keys()]
        
        tableheader = {"name": "Name", "wins": "Wins", "cards": "Cards"}
        
        players_by_cards = tabulate(sorted(players, key=lambda x: x["cards"], reverse=True), headers=tableheader, showindex=range(1, len(players)+1)).split("\n")
        self.list_cards.add("Players by cards:")
        for line in players_by_cards:
            self.list_cards.add(line)
        
        
        
        players_by_wins = tabulate(sorted(players, key=lambda x: x["wins"], reverse=True), headers=tableheader, showindex=range(1, len(players)+1)).split("\n")
        self.list_wins.add("Players by wins:")
        for line in players_by_wins:
            #line = f"{i}. {p['name']}: {p['wins']} wins, {p['cards']} cards"
            self.list_wins.add(line)
        
    def button_handler(self, name : str) -> None:
        if name == "Back":
            self.g.setstate(0)
            return
    
    def loop(self, events : list[Event]) -> None:
        self.list_cards.draw()
        self.list_wins.draw()

    def keydown(self, k : int, kmods : int) -> bool:
        if k == K_q or k == K_ESCAPE:
            self.g.setstate(0)
            return True
        return False
    
    def mouse_event(self, event : Event) -> bool:
        if not self.list_wins.mouse_event(event):
            if self.list_cards.mouse_event(event):
                return True
        else:
            return True
        
        return False
    
    def click(self, pos : tuple, btn = int) -> bool:
        return False
    
    #########################################################################################