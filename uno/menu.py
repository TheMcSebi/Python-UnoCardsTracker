from __future__ import annotations
from pygame import Rect
from pygame.locals import *
from pygame.event import Event
from pygame.key import start_text_input
from pygame.key import set_text_input_rect
import sys

from .components.textinput import TextInput
from .components.button import Button
from .constants import *


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .uno import Uno

class Menu:
    """
    Main menu screen
    """
    def __init__(self, game : Uno) -> None:
        self.g = game
        self.window = self.g.window

    #########################################################################################

    def name_input_callback(self, name : str) -> None:
        if len(name) > 0:
            self.temp_players.append(name)
            self.text_input.promt = f"Name Player {len(self.temp_players) + 1} > "
            if len(self.temp_players) >= 2:
                self.text_input.chat_list = ["Leave the Input field empty and press enter to start the game"]
        else:
            self.show_name_input = False
            self.g.new_game(self.temp_players)
            self.g.setstate(1)
    
    def setup(self) -> None:
        self.show_name_input = False
        self.temp_players = []
        self.bw = self.g.w//4
        self.bh = self.g.h//6
        
        self.buttons = [
            Button(self.g, "Start", (self.g.w//2, self.bh*1.1*1), (self.bw, self.bh), self.button_handler),
            Button(self.g, "Load", (self.g.w//2, self.bh*1.1*2), (self.bw, self.bh), self.button_handler),
            Button(self.g, "Stats", (self.g.w//2, self.bh*1.1*3), (self.bw, self.bh), self.button_handler),
            Button(self.g, "Quit", (self.g.w//2, self.bh*1.1*4), (self.bw, self.bh), self.button_handler),
        ]
        
        self.print_event = "showevent" in sys.argv
        self.text_input = TextInput(
            promt="",
            pos=(self.g.w//30, self.g.h//30),
            screen_dimensions=(self.g.w, self.g.h),
            print_event=self.print_event,
            text_color="green",
            callback=self.name_input_callback,
        )

        start_text_input()
        input_rect = Rect(80, 80, 320, 40)
        set_text_input_rect(input_rect)
    
    def button_handler(self, name : str) -> None:
        if name == "Start":
            self.temp_players = []
            self.text_input.promt = f"Name Player 1 > "
            self.text_input.chat_list = []
            self.show_name_input = True

        elif name == "Load":
            self.g.setstate(2)
        
        elif name == "Stats":
            self.g.setstate(4)

        elif name == "Quit":
            self.g.exit()
    
    def loop(self, events : list[Event]) -> None:
        for b in self.buttons:
            b.draw()
        if self.show_name_input:
            self.text_input.update(events)
            self.text_input.draw(self.window)

    def keydown(self, k : int, kmods : int) -> bool:
        if self.show_name_input:
            if k == K_ESCAPE:
                # hide input field
                self.show_name_input = False
            return True
        return False
        
    def mouse_event(self, event : Event) -> bool:
        if True in [b.mouse_event(event) for b in self.buttons]:
            return True
        return False
    
    def click(self, pos : tuple, btn = int) -> bool:
        return False
    
    #########################################################################################