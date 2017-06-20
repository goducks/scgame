import sdl2.ext
import drawable as draw
import sdl2.sdlttf as sdlttf
import os

class textMaker(sdl2.ext.TextureSprite):
    def __init__(self, renderer, text = ""):
        sdlttf.TTF_Init()
        RESOURCES = sdl2.ext.Resources(__file__, "resources")
        font = RESOURCES.get_path("Arial.ttf")
        self.font = sdlttf.TTF_OpenFont(font, 24)
        self.text = text
        self.renderer = renderer
        texture = self.createText()
        print texture
        super(textMaker, self).__init__(texture)

    def createText(self):
        surface = sdlttf.TTF_RenderText_Solid(self.font, self.text, sdl2.SDL_Color())
        texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, surface)
        # sdl2.SDL_FreeSurface(surface)
        return texture
