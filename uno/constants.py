from pygame import USEREVENT, Surface
from pygame.font import SysFont
from pygame.transform import scale

DEBUG = False

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

FONT_SM = SysFont('freesansbold', 1080//40)
FONT_MD = SysFont('freesansbold', 1080//30)
FONT_L = SysFont('freesansbold', 1080//25)
FONT_LG = SysFont('freesansbold', 1080//20)
FONT_XL = SysFont('freesansbold', 1080//10)
FONT_MONOSP_SM = SysFont('courier', 1080//42)
FONT_MONOSP = SysFont('courier', 1080//25)
FONT_MONOSP_LARGE = SysFont('courier', 1080//18)

# custom events
UPDATE_GAME_STATS = USEREVENT + 1

def rescale(img : Surface, scale_factor : float) -> Surface:
    (w, h) = img.get_size()
    return scale(img, (w*scale_factor, h*scale_factor))