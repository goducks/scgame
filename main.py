import sys
import sdl2.ext

print "--begin--"

RESOURCES = sdl2.ext.Resources(__file__, "resources")

sdl2.ext.init()

# load a sprite directly from image, note can also manually create one, but this factory will
# do heavy lifting for now
factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
# debug check of supported image formats
# formats = sdl2.ext.get_image_formats()
# print formats
sprite = factory.from_image(RESOURCES.get_path("IMG_0013.bmp"))

# create window based on image size
width = sprite.size[0]
height = sprite.size[1]
window = sdl2.ext.Window("Hello World!", size=(width, height))
window.show()

# create a renderer
spriterenderer = factory.create_sprite_render_system(window)
spriterenderer.render(sprite)

# this is a dummy even processor to keep the application running "forever" --
# here's where we'll make our own game loop even processor. for now, this runs
# forever until you hit CTRL-C in the python window or close the app window
processor = sdl2.ext.TestEventProcessor()
processor.run(window)

# cleanup
sdl2.ext.quit()

print "--end--"
