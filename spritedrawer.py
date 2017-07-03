import os
import sdl2
import sdl2.ext as sdl2ext
import drawable
from ctypes import c_int, pointer, cast, py_object, c_void_p
from sdl2 import (pixels, render, events as sdlevents, surface, error,
                    timer)
import sdl2.sdlimage as sdlimage

class spriteMaker(object):
    def __init__(self, renderer, image, xpos = 0, ypos = 0):
        sdl2.SDL_ClearError()
        if isinstance(renderer, sdl2ext.Renderer):
            self.renderer = renderer.renderer
        elif isinstance(renderer, render.SDL_Renderer):
            self.renderer = renderer
        else:
            raise TypeError("unsupported renderer type")

        sdlimage.IMG_Init(sdlimage.IMG_INIT_PNG)
        self.surface = sdlimage.IMG_Load(image)
        self.texture = render.SDL_CreateTextureFromSurface(self.renderer, self.surface)

        self.x = xpos
        self.y = ypos
        drawable.Drawable.drawList.append(self)
        render.SDL_DestroyTexture(self.texture)
        surface.SDL_FreeSurface(self.surface)
        sdlimage.IMG_Quit()

    def render(self, renderer):
        dst = sdl2.SDL_Rect(self.x, self.y)
        w = pointer(c_int(0))
        h = pointer(c_int(0))
        sdl2.SDL_QueryTexture(self.texture, None, None, w, h)
        dst.w = w.contents.value
        dst.h = h.contents.value
        sdl2.SDL_RenderCopy(renderer.renderer, self.texture, None, dst)

class drawPlayer(spriteMaker):
    def __init__(self, renderer):
        image = os.path.join(os.path.dirname(__file__), 'resources/images', 'ship.png')
        super(drawPlayer, self).__init__(renderer, image)

    def getTexture(self):
        return self.texture