import cv2, math
from cv2 import Mat
import numpy as np
from random import randint

from pygame.image import frombuffer
from pygame.surfarray import make_surface, blit_array
from pygame import Surface
from os.path import join, dirname, realpath

pygame_surface_cache = {}

class Cards:
    def __init__(self, opencv_mode : bool = False) -> None:
        self.warp_matrix = Cards._calculate_warp_matrix([-0.60, 0.0, 0], (966, 968, 4)) # generate large warp matrix for card transformation
        self.h = 362
        self.w = 242
        
        self.set_cards = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "skip", "reverse", "draw2"]
        self.set_colors = ["red", "yellow", "green", "blue"]
        self.special_cards = ["wild", "wildplus4"]

        self.drawing_cards = ["wildplus4", "red_8", "red_draw2", "red_1"]
        #for c in self.set_colors:
        #    self.drawing_cards.append(f"{c}_draw2")

        self.image_path = join(dirname(realpath(__file__)), "../../cards")
        self.opencv_mode = opencv_mode
        self.debug = False
        #self.upscale = True
        
    
    def get_random_cards(self, n : int = 1) -> list:
        cards = []
        for i in range(n):
            cards.append(self.get_random_card())
        return cards
    
    def get_random_card(self) -> str:
        num = randint(0, len(self.set_cards)-4)
        col = randint(0, len(self.set_colors)-1)
        return f"{self.set_colors[col]}_{self.set_cards[num]}"

    def raster_playing_card(self, name : str, rotation : int = None) -> Surface:
        """
        name: e.g. "red_0"
        rotation: -90 - 90 degrees
        """
        im =  cv2.imread(f"{self.image_path}/{name}.png", cv2.IMREAD_UNCHANGED)

        if rotation is None:
            if self.opencv_mode:
                return im
            return Cards._to_pygame_surface(im)
        
        # resize image (TODO: fix this)
        #im = cv2.resize(im, (int(im.shape[1] * 1.3), int(im.shape[0] * 1.3)), interpolation = cv2.INTER_AREA)
#
        #if self.debug:
        #    cv2.imshow("im", im)
        #    cv2.waitKey(0)
        #    cv2.destroyAllWindows()

        # create blank canvas
        dim = im.shape
        blank = np.zeros((dim[0]*4, dim[1]*4, dim[2]), dtype=np.uint8)
        bdim = blank.shape

        # put image in center of blank canvas
        y_offset = bdim[0]//2-dim[0]//2
        x_offset = bdim[1]//2-dim[1]//2
        blank[y_offset:y_offset+dim[0], x_offset:x_offset+dim[1]] = im

        if self.debug:
            cv2.imshow("im", blank)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # rotate 2d
        rotated2d = Cards._rotate_image2d(blank, rotation)

        if self.debug:
            cv2.imshow("im", rotated2d)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # crop top of image to prevent distortion
        y = bdim[0]//3
        x = 0
        h = bdim[0]-y
        w = bdim[1]
        cropped = rotated2d[y:y+h, x:x+w]
        cdim = cropped.shape

        if self.debug:
            cv2.imshow("im", cropped)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # rotate 3d using pre-calculated warp matrix
        rotated3d = cv2.warpPerspective(cropped, self.warp_matrix, (cdim[1], cdim[0]), flags=cv2.INTER_LINEAR)

        if self.debug:
            cv2.imshow("im", rotated3d)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # crop surrounding
        y = cdim[0]//3
        x = cdim[1]//3
        h = int(cdim[0]-y*2.5)
        w = cdim[1]-x*2

        cropped2 = rotated3d[y:y+h, x:x+w]

        if self.debug:
            cv2.imshow("im", cropped2)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    
        ## resize 2x
        c2dim = cropped2.shape
        width = int(c2dim[1] * 1.2)
        height = int(c2dim[0] * 1.2)
        finalimg = cv2.resize(cropped2, (width, height), interpolation = cv2.INTER_AREA)
        #finalimg = cropped2

        if self.opencv_mode:
            return finalimg
        return Cards._to_pygame_surface(finalimg)

    @staticmethod
    def _to_pygame_surface(opencv_image : np.ndarray) -> Surface:
        # from: https://linuxtut.com/en/f26e2756da774c164a47/
        """
        Convert OpenCV images for Pygame.

        see https://blanktar.jp/blog/2016/01/pygame-draw-opencv-image.html
        """
        opencv_image = opencv_image[:,:,::-1]  # Since OpenCV is BGR and pygame is RGB, it is necessary to convert it.
        shape = opencv_image.shape[1::-1]  # OpenCV(height,width,Number of colors), Pygame(width, height)So this is also converted.
        pygame_image = frombuffer(opencv_image.tostring(), shape, 'ARGB')

        return pygame_image
    
    @staticmethod
    def convert_opencv_img_to_pygame_v2(opencv_image): # TODO: test, might be a bit faster
        """
        Convert OpenCV images for Pygame.

        see https://gist.github.com/radames/1e7c794842755683162b
        see https://github.com/atinfinity/lab/wiki/%5BOpenCV-Python%5D%E7%94%BB%E5%83%8F%E3%81%AE%E5%B9%85%E3%80%81%E9%AB%98%E3%81%95%E3%80%81%E3%83%81%E3%83%A3%E3%83%B3%E3%83%8D%E3%83%AB%E6%95%B0%E3%80%81depth%E5%8F%96%E5%BE%97
        """
        if len(opencv_image.shape) == 2:
            #For grayscale images
            cvt_code = cv2.COLOR_GRAY2RGB
        else:
            #In other cases:
            cvt_code = cv2.COLOR_BGR2RGB
        rgb_image = cv2.cvtColor(opencv_image, cvt_code).swapaxes(0, 1)
        #Generate a Surface for drawing images with Pygame based on OpenCV images
        pygame_image = make_surface(rgb_image)

        return pygame_image
    
    @staticmethod
    def convert_opencv_img_to_pygame_v3(opencv_image): # TODO: test, might be even more faster
        """
        Convert OpenCV images for Pygame.

        see https://gist.github.com/radames/1e7c794842755683162b
        see https://github.com/atinfinity/lab/wiki/%5BOpenCV-Python%5D%E7%94%BB%E5%83%8F%E3%81%AE%E5%B9%85%E3%80%81%E9%AB%98%E3%81%95%E3%80%81%E3%83%81%E3%83%A3%E3%83%B3%E3%83%8D%E3%83%AB%E6%95%B0%E3%80%81depth%E5%8F%96%E5%BE%97
        see https://stackoverflow.com/a/42589544/4907315
        """
        if len(opencv_image.shape) == 2:
            #For grayscale images
            cvt_code = cv2.COLOR_GRAY2RGB
        else:
            #In other cases:
            cvt_code = cv2.COLOR_BGR2RGB
        rgb_image = cv2.cvtColor(opencv_image, cvt_code).swapaxes(0, 1)

        #Get a generated Surface with the same image size from the cache
        cache_key = rgb_image.shape
        cached_surface = pygame_surface_cache.get(cache_key)

        if cached_surface is None:
            #Generate a Surface for drawing images with Pygame based on OpenCV images
            cached_surface = make_surface(rgb_image)
            #Add Surface to cache
            pygame_surface_cache[cache_key] = cached_surface
        else:
            #If you find a Surface with the same image size, reuse the already generated Surface.
            blit_array(cached_surface, rgb_image)

        return cached_surface
    
    @staticmethod
    def _rotate_image2d(image : Mat, angle : int):
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
        return result

    @staticmethod
    def _calculate_translation_matrix(dx, dy):
        return np.array(
            [1, 0, dx,
             0, 1, dy,
             0, 0, 1 ]).reshape((3,3))
    
    @staticmethod
    def _calculate_warp_matrix(angles, image_size):
        rangle = np.deg2rad(angles)
        
        t1 = Cards._calculate_translation_matrix(-image_size[1]/2, -image_size[0]/2)
        t2 = Cards._calculate_translation_matrix( image_size[1]/2, image_size[0]/2 )

        R_x = np.array([[1,         0,                   0                     ],
                        [0,         math.cos(rangle[0]),  -math.sin(rangle[0]) ],
                        [0,         math.sin(rangle[0]),  math.cos(rangle[0])  ]
                        ])

        R_y = np.array([[math.cos(rangle[1]) ,   0,      math.sin(rangle[1])   ],
                        [0                   ,   1,      0                     ],
                        [-math.sin(rangle[1]),   0,      math.cos(rangle[1])   ]
                        ])

        R_z = np.array([[math.cos(rangle[2]),    -math.sin(rangle[2]),        0],
                        [math.sin(rangle[2]),    math.cos(rangle[2]) ,        0],
                        [0                  ,    0                   ,        1]
                        ])

        R = np.dot( t2.dot(R_z.dot(t1)), np.dot( t2.dot(R_y.dot(t1)), t2.dot(R_x.dot(t1)) ) )

        return R

if __name__ == "__main__":
    cards = Cards()
    cards.opencv_mode = True
    for i, c in enumerate(cards.get_random_cards(3)):
        im = cards.raster_playing_card(c, randint(-90, 90))
        cv2.imshow(f"card-{c}", im)
    cv2.waitKey(0)