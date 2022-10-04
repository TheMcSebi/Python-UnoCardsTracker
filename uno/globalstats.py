from __future__ import annotations
from re import I
from matplotlib.figure import Figure
from pygame import Surface
from tabulate import tabulate
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

from pygame.locals import *
from pygame.event import Event
from pygame.font import Font
from pygame.image import fromstring

from .constants import *
from .components.button import Button
from .components.scrollablelist import ScrollableList
#from .components.helper import padline

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

        self._button_names = ["Back", "Players", "By Time", "General", "Pie Chart", "Graph3"]
        for i,b in enumerate(self._button_names):
            self.buttons.append(Button(self.g, b, (100+(i*200), 50), (200, 100), self.button_handler, FONT_LG))
        
        # get color table
        col = self.g.player_colors.copy()
        for i,c in enumerate(col): # convert and add alpha value of 1 to each color
            col[i] = (c[0]/255, c[1]/255, c[2]/255, 1.0)
        self.chart_colors = col[1:]
        
        # get player data
        players = {}
        self.total_play_time = 0
        self.total_games = 0
        cont = False
        for s in self.saves:
            if cont:
                cont = False
                continue
            for p in s["data"]["players"]:
                if p["name"] not in players.keys():
                    players[p["name"]] = {"wins": 0, "cards": 0, "playtime": 0, "games": 0}
                if not "wins" in p.keys():
                    cont = True
                    break
                players[p["name"]]["wins"] += p["wins"]
                #if "cards" in p.keys():
                players[p["name"]]["cards"] += p["cards"]
                players[p["name"]]["playtime"] += s["data"]["current_tick"]
                for p2 in s["data"]["players"]:
                    self.total_games += p2["wins"]
                    players[p["name"]]["games"] += p2["wins"]
            self.total_play_time += s["data"]["current_tick"]
            self.total_games += 1
        
        # clear 0-game players
        removed_names = []
        for p in players.keys():
            if players[p]["games"] == 0:
                removed_names.append(p)
        for r in removed_names:
            del players[r]
        
        self.players = [{"name": p, "wins": players[p]["wins"], "cards": players[p]["cards"], "playtime": players[p]["playtime"]} for p in players.keys()]
        self.players_total = [{"name": p, "wins": players[p]["wins"], "cards": players[p]["cards"]} for p in players.keys()]
        self.players_by_time = [{"name": p, "wins": players[p]["wins"]/(players[p]["playtime"]/1000/60/60), "cards": players[p]["cards"]/(players[p]["playtime"]/1000/60/60)} for p in players.keys()]
        self.players_by_games = [{"name": p, "wins": players[p]["wins"]/players[p]["games"], "cards": players[p]["cards"]/players[p]["games"]} for p in players.keys()]
        
        # get games
        self.games = []
        for s in self.saves:
            history = []
            for p in s["data"]["players"]:
                if "history" in p.keys():
                    for h in p["history"]:
                        history.append(h)
            if len(history) == 0:
                print("missing history " + s["filename"])
                continue
            if isinstance(history[0], list):
                print("wrong format " + s["filename"])
                continue

            history = sorted(history, key=lambda x: x["time"])
            
            current_cards = 0
            first_time = history[0]["time"]
            for h in history:
                if h["action"] == "draw":
                    current_cards += h["value"]
                elif h["action"] == "win":
                    self.games.append({"time": h["time"]-first_time, "cards": current_cards})
                    current_cards = 0
                    first_time = h["time"]
        
        self._display_page(0)
        
    def button_handler(self, name : str) -> None:
        if name == "Back":
            self.g.setstate(0)
            return
        else:
            self._display_page(self._button_names.index(name)-1)
    
    def loop(self, events : list[Event]) -> None:
        if self.display_mode == "list":
            self.list_left.draw()
        elif self.display_mode == "lists":
            self.list_left.draw()
            self.list_right.draw()
        elif self.display_mode == "image":
            self.g.blit_aligned(self.image, (self.g.w//2, self.g.h//2))

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
        
        if self.display_mode == "list":
            if self.list_left.mouse_event(event):
                return True
        
        elif self.display_mode == "lists":
            if self.list_right.mouse_event(event):
                return True
            if self.list_left.mouse_event(event):
                return True
        
        return False
    
    def click(self, pos : tuple, btn = int) -> bool:
        return False
    
    #########################################################################################

    def _display_page(self, id : int) -> None:
        self.current_page = id
        self.display_mode = None
        self.list_left = None
        self.right_list = None
        self.image = None

        if id == 0:
            self.display_mode = "lists"
            self.list_left = ScrollableList(self.g, (50, 50), font=FONT_MONOSP, direction="bottomlast")
            self.list_right = ScrollableList(self.g, (self.g.w//2 + 50, 50), font=FONT_MONOSP, direction="bottomlast")
            tableheader = {"name": "Name", "wins": "Wins", "cards": "Cards"}

            players_by_cards = tabulate(sorted(self.players_total, key=lambda x: x["cards"], reverse=True), headers=tableheader, showindex=range(1, len(self.players_total)+1)).split("\n")
            self.list_left.add("Players by cards:")
            for line in players_by_cards:
                self.list_left.add(line)
            
            players_by_wins = tabulate(sorted(self.players_total, key=lambda x: x["wins"], reverse=True), headers=tableheader, showindex=range(1, len(self.players_total)+1)).split("\n")
            self.list_right.add("Players by wins:")
            for line in players_by_wins:
                #line = f"{i}. {p['name']}: {p['wins']} wins, {p['cards']} cards"
                self.list_right.add(line)
        if id == 1:
            self.display_mode = "lists"
            self.list_left = ScrollableList(self.g, (50, 50), font=FONT_MONOSP, direction="bottomlast")
            self.list_right = ScrollableList(self.g, (self.g.w//2 + 50, 50), font=FONT_MONOSP, direction="bottomlast")
            tableheader = {"name": "Name", "wins": "Wins", "cards": "Cards"}

            players_by_cards = tabulate(sorted(self.players_by_time, key=lambda x: x["cards"], reverse=True), headers=tableheader, showindex=range(1, len(self.players_by_time)+1)).split("\n")
            self.list_left.add("Players by cards/h:")
            for line in players_by_cards:
                self.list_left.add(line)
            
            players_by_wins = tabulate(sorted(self.players_by_time, key=lambda x: x["wins"], reverse=True), headers=tableheader, showindex=range(1, len(self.players_by_time)+1)).split("\n")
            self.list_right.add("Players by wins/h:")
            for line in players_by_wins:
                #line = f"{i}. {p['name']}: {p['wins']} wins, {p['cards']} cards"
                self.list_right.add(line)
        elif id == 2:
            self.display_mode = "list"
            self.list_left = ScrollableList(self.g, (100, 100), font=FONT_MONOSP_LARGE, direction="bottomlast")
            padlen = 35
            
            save_count = len(self.saves)
            self.list_left.add("Saves".ljust(padlen) + str(save_count))
            
            game_count = len(self.games)
            self.list_left.add("Games".ljust(padlen) + str(game_count))
            
            player_count = len(self.players)
            self.list_left.add("Players".ljust(padlen) + str(player_count))
            
            cards = sum([p["cards"] for p in self.players])
            self.list_left.add("Cards per game".ljust(padlen) + str(cards/game_count))
            
            #cards = sum([p["cards"] for p in self.players])
            self.list_left.add("Total play time".ljust(padlen) + str(self.total_play_time/1000/60/60) + " hours")
            #self.list_left.add("Cards per game".ljust(padlen) + str(cards/game_count))
            
            #self.list_left.add("Total games".ljust(padlen) + str(self.total_games) + " hours")

            all_players_total_time = 0
            for p in self.players:
                all_players_total_time += p["playtime"]
            self.list_left.add("Total person-hours wasted".ljust(padlen) + str(int(all_players_total_time/1000/60/60)) + " hours")
            
        elif id == 3:
            temp_players = sorted(self.players, key=lambda x: x["cards"], reverse=True)
            self.display_mode = "image"
            plt.style.use('_mpl-gallery-nogrid')
            plt.rcParams["figure.figsize"] = (10,10)
            plt.rcParams["figure.dpi"] = 70
            
            pcount = len(self.players)
            pcards = [0]*pcount
            labels = [""]*pcount
            #cardstotal = 0
            #winstotal = 0
            for i in range(0, pcount):
                pcards[i] += temp_players[i]["cards"]
                labels[i] = temp_players[i]["name"]
                #cardstotal += p["cards"]
                #winstotal += temp_players[i]["wins"]

            #for i in range(0, pcount):
            #    pcards[i] = pcards[i]//winstotal
            
            

            if pcount > 6:
                rest = sum(pcards[6:])
                pcards = pcards[:6] + [rest]
                labels = labels[:6] + ["Rest"]

            # plot
            fig, ax = plt.subplots()
            ax.pie(pcards, labels=labels, colors=self.chart_colors, radius=3, center=(4, 4), wedgeprops={"linewidth": 1, "edgecolor": "white"}, frame=True)

            ax.set(xlim=(0, 8), xticks=np.arange(1, 8), ylim=(0, 8), yticks=np.arange(1, 8))
            fig = plt.gcf()
            
            self.image = GlobalStats.fig2img(fig)
            plt.close(fig)
    
    @staticmethod
    def fig2img(fig : Figure) -> Surface:
        """Convert a Matplotlib figure to a PIL Image and and then to a pygame surface return it"""
        buf = BytesIO()
        fig.savefig(buf)
        buf.seek(0)
        img = Image.open(buf)
        mode = img.mode
        size = img.size
        data = img.tobytes()
        py_image = fromstring(data, size, mode)
        return py_image