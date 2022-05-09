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
from pygame.image import load as load_image
from pygame.transform import scale

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
        self.save_version = None # gets set on load or new game

        self.players = []
        self.pcount = 0
        self.ticks_start = 0
        self.player_colors = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0x3f, 0xab, 0xda), (0x77, 0x00, 0xff), (255, 0, 255), (0, 255, 255)]
        
        self.w = 0
        self.h = 0
        self.bg = None
        self._screen_resolution_changed()
        self.screens[self.state].setup()
    
    @staticmethod
    def get_app_folder() -> str:
        """
        Get application storage directory
        If it doesn't exist, create it
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
                    if screen.mouse_event(e):
                        continue
                    
                    if e.type == MOUSEBUTTONUP:
                        pos = get_mouse_pos()
                        if screen.click(pos, e.button):
                            continue
                elif e.type == VIDEORESIZE:
                    self._screen_resolution_changed()
            
            self.loop(events)
            screen.loop(events)
            display_update()
    
    def undo(self) -> None:
        """
        Undo the last player action
        """
        last_value = 0
        last_time = 0
        last_index = 0
        last_player = None
        last_action = None
        for p in self.players:
            if len(p["history"]) == 0:
                continue
            htime = p["history"][-1]["time"]
            if htime > last_time:
                last_time = htime
                last_player = p
                last_action = p["history"][-1]["action"]
        if last_player:
            sum_actions = 0
            tmp = 0
            for i,h in enumerate(last_player["history"]):
                if h["action"] == last_action:
                    last_value = tmp
                    sum_actions += 1
                    tmp = h["value"]
                    last_index = i
            
            if sum_actions > 1:
                if last_action == "flash":
                    last_player["flashes"] = last_value
                elif last_action == "draw":
                    last_player["cards"] = last_value
            elif sum_actions == 1:
                if last_action == "draw":
                    last_player["cards"] = 0
                elif last_action == "flash":
                    last_player["flashes"] = 0
            last_player["history"].pop(last_index)
        else:
            print("nothing to undo")
    
    def setstate(self, num : int) -> None:
        """
        Set the screen state of the game
        :param num: screen number
        """
        self.state = num
        if self.state >= len(self.screens):
            self.state = 0
        if self.state < 0:
            self.state = len(self.screens) - 1
        self.screens[self.state].setup()
    
    def load_asset_image(self, imgname : str, rescale : float = None) -> Surface:
        """
        Load an image from the assets folder
        :param imgname: name of the image
        :param rescale: rescale the image to this size
        """
        img = load_image(join(self.assets_dir, imgname)).convert_alpha()
        
        if not rescale is None:
            imsize = img.get_size()
            img = scale(img, (int(imsize[0]*rescale), int(imsize[1]*rescale)))
        
        return img
    
    def check_collision_center(self, center_pos : tuple, area_size : tuple, touch_pos : tuple) -> bool:
        """
        Check if a point is inside a rectangle
        :param center_pos: center position of the rectangle
        :param area_size: size of the rectangle
        :param touch_pos: position of the point
        """
        return (center_pos[0] - area_size[0] / 2 <= touch_pos[0] <= center_pos[0] + area_size[0] / 2) and (center_pos[1] - area_size[1] / 2 <= touch_pos[1] <= center_pos[1] + area_size[1] / 2)

    
    #########################################################################################

    def loop(self, events : list[Event]) -> None:
        self.window.blit(self.bg, (0, 0))
    
    def keydown(self, k : int, kmods : int) -> None:
        if k == K_ESCAPE or k == K_q:
            self.exit()
    
    #########################################################################################

    def new_game(self, playernames : list) -> None:
        """
        Start a new game
        :param playernames: list of player names
        """

        if len(playernames) == 0:
            return
        self.save_version = 2
        
        self.players = []
        for i,p in enumerate(playernames, start = 1):
            self.players.append({
                "num": i,
                "name": p,
                "cards": 0,
                "flashes": 0,
                "wins": 0,
                "history": [],
            })
        self.pcount = len(self.players)
        self.ticks_start = get_ticks()
        self.playerdata_changed(None)
        
        datestr = "{:%Y_%m_%d-%H_%M_%S}".format(datetime.datetime.now())
        self.save_file_name = f"savegame_{datestr}.json"
    
    def get_saves(self):
        """
        Load all savegames from the savegame folder
        """

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
                        if not "cards" in p:
                            players.append(f"{p['name']} ({p['score']} cards)")

                        else:
                            players.append(f"{p['name']} ({p['cards']} cards/{p['flashes']} flashes)")
                    savegames.append({"filename": filename, "players": players})
            except Exception as e:
                print(f"Error loading file '{filename}': {e}")
        return savegames
        
    
    def load(self, filename) -> None:
        """
        Load a previously saved game
        :param filename: name of the savegame
        """

        self.save_file_name = filename
        with open(f"saves/{filename}", "r") as f:
            game = json.loads(f.read())
            if not "save_version" in game:
                # convert save version from 0 to 1
                self.game_version = 1
                for ip, p in enumerate(game["players"]):
                    cards = game["players"][ip]["score"]
                    game["players"][ip].pop("score", None)
                    game["players"][ip]["cards"] = cards
                    game["players"][ip]["flashes"] = 0
                    for ih, h in enumerate(p["history"]):
                        game["players"][ip]["history"][ih] = {"action": "draw", "time": h[1], "value": h[0]}
            elif game["save_version"] == 1:
                # convert to game version 2 if necessary
                # convert save version from 0 to 1
                #game["save_version"] = 2
                self.game_version = 2
                for ip, p in enumerate(game["players"]):
                    #cards = game["players"][ip]["score"]
                    
                    game["players"][ip]["wins"] = 0
                    
                    for ih, h in enumerate(p["history"]):
                        action = h["action"]
                        if h["action"] == "flash":
                            action = "win"
                        game["players"][ip]["history"][ih] = {"action": action, "time": h["time"], "value": h["value"]}
                pass

            self.players = game["players"]
            self.ticks_start = get_ticks() - game["current_tick"]
            self.pcount = len(self.players)
            self.playerdata_changed(None)
            self.setstate(1)
    
    def save(self) -> None:
        """
        Save the current game
        """
        if self.save_file_name is None:
            return
        
        game = {
            "current_tick": self.get_game_time(), 
            "players": self.players, 
            "save_version": self.save_version
        }
        
        if not os.path.isdir("saves"):
            os.mkdir("saves")
        
        with open(f"saves/{self.save_file_name}", "w") as f:
            f.write(json.dumps(game))
    
    def playerdata_changed(self, p : dict, action : str = "draw") -> None:
        """
        Appends a history entry and saves the game
        """
        if p is None:
            return

        if action == "draw":
            value = p["cards"]
        elif action == "flash":
            value = p["flashes"]
        elif action == "win":
            value = p["wins"]
        else:
            return

        p["history"].append({"action": action, "value": value, "time": self.get_game_time()})
        self.save()
    
    def blit_aligned(self, src : Surface, dest : tuple, target : Surface = None, align : tuple = (2, 2)) -> None:
        (x, y) = dest
        if target is None:
            target = self.window
        
        if not align is None:
            if align[0] != 0:
                x -= src.get_width() // align[0]
            if align[1] != 0:
                y -= src.get_height() // align[1]
        target.blit(src, (x, y))

    def get_game_time(self) -> int:
        return get_ticks() - self.ticks_start

    #########################################################################################

    def exit(self) -> None:
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
