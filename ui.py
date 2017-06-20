import os
import sdl2
import sdl2.ext
from sdl2.sdlttf import (TTF_OpenFont,
                         TTF_RenderText_Shaded,
                         TTF_GetError,
                         TTF_Init,
                         TTF_Quit
                         )

class textMaker(sdl2.ext.TextureSprite):
    def __init__(self, renderer, font = None, text = "", fontSize = 16,
                       textColor = sdl2.pixels.SDL_Color(255, 255, 255),
                       backgroundColor = sdl2.pixels.SDL_Color(0, 0, 0)):
        if isinstance(renderer, sdl2.ext.Renderer):
            self.renderer = renderer.renderer
        elif isinstance(renderer, render.SDL_Renderer):
            self.renderer = renderer
        else:
            raise TypeError("unsupported renderer type")

        # to make fonts work, create a folder in the resources folder called 'fonts'
        # this font can be downloaded from: http://www.glukfonts.pl/font.php?font=Glametrix
        #  font = os.path.join(os.path.dirname(__file__), 'fontx', 'Glametrix.otf')
        # this font is just copied from your Mac in /Library/fonts/Arial.ttf to the 'font' folder
        font = os.path.join(os.path.dirname(__file__), 'resources/fonts', 'Arial.ttf')
        if font is None:
            raise IOError("Cannot find %s" % font)

        self.font = TTF_OpenFont(font, fontSize)
        if self.font is None:
            raise TTF_GetError()
        self._text = text
        self.fontSize = fontSize
        self.textColor = textColor
        self.backgroundColor = backgroundColor
        texture = self.createTexture()

        super(textMaker, self).__init__(texture)

    def createTexture(self):
        textSurface = TTF_RenderText_Shaded(self.font, self._text, self.textColor, self.backgroundColor)
        if textSurface is None:
            raise TTF_GetError()
        texture = sdl2.render.SDL_CreateTextureFromSurface(self.renderer, textSurface)
        if texture is None:
            raise sdl2.ext.SDLError()
        sdl2.surface.SDL_FreeSurface(textSurface)
        return texture

    def updateTexture(self):
        textureToDelete = self.texture

        texture = self.createTexture()
        super(TextSprite, self).__init__(texture)

        sdl2.render.SDL_DestroyTexture(textureToDelete)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if self._text == value:
            return
        self._text = value
        self.updateTexture()
