from __future__ import annotations
import json, os, datetime
from random import seed
from time import time
from os.path import join, dirname, realpath
import ctypes
from tkinter.messagebox import NO
from pygame import Surface, quit as pygame_quit, init as pygame_init
from pygame.display import set_mode, set_caption, get_surface, update as display_update
from pygame.event import Event, get as get_events
from pygame.font import SysFont, init as font_init
from pygame.mixer import init as mixer_init, Sound
from pygame.time import Clock, get_ticks

from pygame.mouse import get_pos as get_mouse_pos
from pygame.key import get_mods as get_key_mods
from pygame.locals import *

ctypes.windll.user32.SetProcessDPIAware()

pygame_init()
mixer_init()
font_init()

from .menu import Menu
from .game import Game
from .load import Load
from .stats import Stats
from .constants import *

class Uno:
    """
    Load Screen
    """
    def __init__(self, fullscreen : bool = False) -> None:
        seed(int(time()))
        self.true_res = Uno._os_get_screen_resolution()
        flags = 0
        if fullscreen:
            flags = FULLSCREEN
        self.window = set_mode(self.true_res, flags)
        set_caption("Uno Level Tracker")

        self.appfolder = Uno.get_app_folder()
        self.assets_dir = join(dirname(realpath(__file__)), "../assets")

        self.screens = [Menu(self), Game(self), Load(self), Stats(self)]

        # init vars
        self.fps = 60
        self.clock = Clock()
        self.state = 0
        self.save_file_name = None

        self.players = []
        self.pcount = 0
        self.ticks_start = 0
        self.player_colors = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        
        self.w = 0
        self.h = 0
        self.bg = None
        self._screen_resolution_changed()
        self.screens[self.state].setup()
    
    @staticmethod
    def get_app_folder() -> str:
        """
        Get application folder and create it if it doesn't exist
        """
        # on windows return %APPDATA%\Uno
        # on linux return ~/.uno
        # on mac return ~/Library/Application Support/Uno
        if os.name == "nt":
            path = os.path.join(os.environ["APPDATA"], "Uno")
        elif os.name == "posix":
            path = os.path.join(os.environ["HOME"], ".uno")
        else:
            path = os.path.join(os.environ["HOME"], "Library", "Application Support", "Uno")
        
        if not os.path.exists(path):
            os.makedirs(path)
        os.chdir(path)
        return path

    def main_loop(self):
        self.run = True
        while self.run:
            self.clock.tick(self.fps)
            screen = self.screens[self.state]
            events = get_events()
            for e in events:
                # event handler
                if e.type == QUIT:
                    self.exit()
                elif e.type == KEYDOWN:
                    kmods = get_key_mods()
                    if not screen.keydown(e.key, kmods):
                        self.keydown(e.key, kmods)
                elif e.type in [MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION]:
                    if not screen.mouse_event(e):
                        self.mouse_event(e)
                    if e.type == MOUSEBUTTONUP:
                        pos = get_mouse_pos()
                        if not screen.click(pos, e.button):
                            self.click(pos, e.button)
                elif e.type == VIDEORESIZE:
                    self._screen_resolution_changed()
            
            self.loop(events)
            screen.loop(events)
            display_update()
    
    def undo(self) -> None:
        latest_action = 0
        latest_action_player = None
        for p in self.players:
            action_time = p["history"][-1][1]
            if action_time > latest_action:
                latest_action = action_time
                latest_action_player = p
        if latest_action_player:
            action = latest_action_player["history"][-2]
            latest_action_player["score"] = action[0]
            latest_action_player["history"].pop()
        else:
            print("nothing to undo")
    
    def setstate(self, num : int) -> None:
        self.state = num
        if self.state >= len(self.screens):
            self.state = 0
        if self.state < 0:
            self.state = len(self.screens) - 1
        self.screens[self.state].setup()
    
    def check_collision_center(self, center_pos : tuple, area_size : tuple, touch_pos : tuple) -> bool:
        return (center_pos[0] - area_size[0] / 2 <= touch_pos[0] <= center_pos[0] + area_size[0] / 2) and (center_pos[1] - area_size[1] / 2 <= touch_pos[1] <= center_pos[1] + area_size[1] / 2)

    
    #########################################################################################

    def loop(self, events : list[Event]) -> None:
        self.window.blit(self.bg, (0, 0))
    
    def keydown(self, k : int, kmods : int) -> None:
        if k == K_ESCAPE or k == K_q:
            self.exit()
            
    def mouse_event(self, event : Event) -> None:
        pass
    
    def click(self, pos : tuple, btn = int) -> None:
        pass
    
    #########################################################################################

    def new_game(self, playernames : list) -> None:
        if len(playernames) == 0:
            return
        
        self.players = []
        for i,p in enumerate(playernames, start = 1):
            self.players.append({
                "num": i,
                "name": p,
                "score": 0,
                "history": [],
            })
        self.pcount = len(self.players)
        self.ticks_start = get_ticks()
        self.playerdata_changed(None)
        
        datestr = "{:%Y_%m_%d-%H_%M_%S}".format(datetime.datetime.now())
        self.save_file_name = f"savegame_{datestr}.json"
    
    def get_saves(self):
        if not os.path.isdir("saves"):
            return []
        
        savefiles = sorted(os.listdir("saves"), reverse = True)
        savegames = []
        for filename in savefiles:
            if not filename.endswith(".json"):
                continue
            try:
                with open(f"saves/{filename}", "r") as f:
                    game = json.loads(f.read())
                    players = []
                    for p in game["players"]:
                        players.append(f"{p['name']} ({p['score']})")
                    savegames.append({"filename": filename, "players": players})
            except Exception as e:
                print(f"Error loading file '{filename}': {e}")
        return savegames
        
    
    def load(self, filename) -> None:
        self.save_file_name = filename
        with open(f"saves/{filename}", "r") as f:
            game = json.loads(f.read())
            self.players = game["players"]
            self.ticks_start = get_ticks() - game["current_tick"]
            self.pcount = len(self.players)
            self.playerdata_changed(None)
            self.setstate(1)
    
    def save(self) -> None:
        if self.save_file_name is None:
            return
        
        game = {"current_tick": self.get_game_time(), "players": self.players}
        
        if not os.path.isdir("saves"):
            os.mkdir("saves")
        
        with open(f"saves/{self.save_file_name}", "w") as f:
            f.write(json.dumps(game))
    
    def playerdata_changed(self, p : dict) -> None:
        if not p is None:
            p["history"].append((p["score"], self.get_game_time()))
            self.save()
        
        #self.players_by_score = sorted(self.players, key = lambda x: x["score"], reverse = True)
        
    def blit_centered(self, src : Surface, dest : tuple, target : Surface = None) -> None:
        (x, y) = dest
        if target is None:
            target = self.window
        target.blit(src, (x - src.get_width() / 2, y - src.get_height() / 2))
    
    def get_game_time(self) -> int:
        return get_ticks() - self.ticks_start
    
    #########################################################################################

    def exit(self) -> None:
        self.save()
        self.run = False
        pygame_quit()
        raise SystemExit()

    def _screen_resolution_changed(self) -> None:
        global FONT_SM, FONT_MD, FONT_LG, FONT_XL
        self.true_res = Uno._os_get_screen_resolution()
        print(f"screen resolution is {self.true_res}")
        self.w, self.h = get_surface().get_size()

        smaller_dim = min(self.w, self.h)
        FONT_SM = SysFont('calibri', smaller_dim//40)
        FONT_MD = SysFont('calibri', smaller_dim//30)
        FONT_LG = SysFont('calibri', smaller_dim//20)
        FONT_XL = SysFont('calibri', smaller_dim//10)
        
        self.bg = Surface((self.w, self.h))
    
    @staticmethod
    def _os_get_screen_resolution() -> tuple:
        return (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1) - 100)
        


#########################################################################################


if __name__ == "__main__":
    Uno().main_loop()
