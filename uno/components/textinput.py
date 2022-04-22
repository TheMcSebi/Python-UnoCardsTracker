from __future__ import annotations
from pygame.locals import *
from pygame.freetype import STYLE_UNDERLINE, SysFont
from pygame import Rect, Surface

# slightly modified example code from
# https://github.com/pygame/pygame/blob/main/examples/textinput.py

class TextInput:
    """
    A simple TextInput class that allows you to receive inputs in pygame.
    """

    # Add font name for each language,
    # otherwise some text can't be correctly displayed.
    FONT_NAMES = [
        "notosanscjktcregular",
        "notosansmonocjktcregular",
        "notosansregular,",
        "microsoftjhengheimicrosoftjhengheiuilight",
        "microsoftyaheimicrosoftyaheiuilight",
        "msgothicmsuigothicmspgothic",
        "msmincho",
        "Arial",
    ]

    def __init__(
        self, promt: str, pos, screen_dimensions, print_event: bool, text_color="white", callback=None
    ) -> None:
        self.promt = promt
        self.print_event = print_event
        # position of chatlist and chatbox
        self.CHAT_LIST_POS = Rect((pos[0], pos[1] + 50), (screen_dimensions[0], 400))
        self.CHAT_BOX_POS = Rect(pos, (screen_dimensions[1], 40))
        self.CHAT_LIST_MAXSIZE = 20

        self._ime_editing = False
        self._ime_text = ""
        self._ime_text_pos = 0
        self._ime_editing_text = ""
        self._ime_editing_pos = 0
        self.chat_list = []

        # Freetype
        # The font name can be a comma separated list
        # of font names to search for.
        self.FONT_NAMES = ",".join(str(x) for x in self.FONT_NAMES)
        self.font = SysFont(self.FONT_NAMES, 24)
        self.font_small = SysFont(self.FONT_NAMES, 16)
        self.text_color = text_color

        self.callback = callback

        #print("Using font: " + self.font.name)

    def update(self, events) -> None:
        """
        Updates the text input widget
        """
        for event in events:
            if event.type == KEYDOWN:
                if self.print_event:
                    print(event)

                if self._ime_editing:
                    if len(self._ime_editing_text) == 0:
                        self._ime_editing = False
                    continue

                if event.key == K_BACKSPACE:
                    if len(self._ime_text) > 0 and self._ime_text_pos > 0:
                        self._ime_text = (
                            self._ime_text[0 : self._ime_text_pos - 1]
                            + self._ime_text[self._ime_text_pos :]
                        )
                        self._ime_text_pos = max(0, self._ime_text_pos - 1)

                elif event.key == K_DELETE:
                    self._ime_text = (
                        self._ime_text[0 : self._ime_text_pos]
                        + self._ime_text[self._ime_text_pos + 1 :]
                    )
                elif event.key == K_LEFT:
                    self._ime_text_pos = max(0, self._ime_text_pos - 1)
                elif event.key == K_RIGHT:
                    self._ime_text_pos = min(
                        len(self._ime_text), self._ime_text_pos + 1
                    )
                # Handle ENTER key
                elif event.key in [K_RETURN, K_KP_ENTER]:
                    self.callback(self._ime_text)
                    self._ime_text = ""
                    self._ime_text_pos = 0

            elif event.type == TEXTEDITING:
                if self.print_event:
                    print(event)
                self._ime_editing = True
                self._ime_editing_text = event.text
                self._ime_editing_pos = event.start

            elif event.type == TEXTINPUT:
                if self.print_event:
                    print(event)
                self._ime_editing = False
                self._ime_editing_text = ""
                self._ime_text = (
                    self._ime_text[0 : self._ime_text_pos]
                    + event.text
                    + self._ime_text[self._ime_text_pos :]
                )
                self._ime_text_pos += len(event.text)

    def draw(self, screen: Surface) -> None:
        """
        Draws the text input widget onto the provided surface
        """

        # Chat List updates
        chat_height = self.CHAT_LIST_POS.height / self.CHAT_LIST_MAXSIZE
        for i, chat in enumerate(self.chat_list):
            self.font_small.render_to(
                screen,
                (self.CHAT_LIST_POS.x, self.CHAT_LIST_POS.y + i * chat_height),
                chat,
                self.text_color,
            )

        # Chat box updates
        start_pos = self.CHAT_BOX_POS.copy()
        ime_text_l = self.promt + self._ime_text[0 : self._ime_text_pos]
        ime_text_m = (
            self._ime_editing_text[0 : self._ime_editing_pos]
            + "|"
            + self._ime_editing_text[self._ime_editing_pos :]
        )
        ime_text_r = self._ime_text[self._ime_text_pos :]

        rect_text_l = self.font.render_to(
            screen, start_pos, ime_text_l, self.text_color
        )
        start_pos.x += rect_text_l.width

        # Editing texts should be underlined
        rect_text_m = self.font.render_to(
            screen,
            start_pos,
            ime_text_m,
            self.text_color,
            None,
            STYLE_UNDERLINE,
        )
        start_pos.x += rect_text_m.width
        self.font.render_to(screen, start_pos, ime_text_r, self.text_color)