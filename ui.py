import sdl2.ext
import drawable as draw
import sdl2.sdlttf as sdlttf
import os

class text():
    def __init__(self):
        sdlttf.TTF_Init()
        font = os.path.join(os.environ['System'], "Library", "Fonts", "Arial.ttf")
        self.font = sdlttf.TTF_OpenFont(font, 24)
        message = sdlttf.TTF_RenderText_Solid(font, "Hello World", (255, 255, 255))