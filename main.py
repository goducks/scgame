import sys
import sdl2.ext

def runLoop():
    # out main game loop 

    # read remote inputs 
    # ...

    # read local inputs & events
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            return False
        else:
            print "sdl event type: %s" % event.type
   
    # update game state
    # ...

    # send local state to remotes    

    # render or whatever

    return True

def main():
    print "--begin game--"

    RESOURCES = sdl2.ext.Resources(__file__, "resources")
    sdl2.ext.init()

    # load a sprite directly from image, note: can also manually 
    # create one, but this factory will do heavy lifting for now
    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    # debug check of supported image formats
    # formats = sdl2.ext.get_image_formats()
    # print formats
    sprite = factory.from_image(RESOURCES.get_path("IMG_0013.bmp"))

    # create window based on image size(tuple)
    width = sprite.size[0]
    height = sprite.size[1]
    window = sdl2.ext.Window("Hello World!", size=(width, height))
    window.show()

    # create a sprite renderer
    spriterenderer = factory.create_sprite_render_system(window)
    spriterenderer.render(sprite)

    running = True
    while running:
        running = runLoop()

    # cleanup
    sdl2.ext.quit()

    print "--end game--"

if __name__ == "__main__":
    main()
