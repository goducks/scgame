import sdl2
import sdl2.ext

def checkCollision(objA, objB):
    minA = objA.sprite.y
    minB = objB.sprite.y
    maxA = objA.sprite.y + objA.sprite.height
    maxB = objB.sprite.y + objB.sprite.height
    leftA = objA.sprite.x
    leftB = objB.sprite.x
    rightA = objA.sprite.x + objA.sprite.width
    rightB = objB.sprite.x + objB.sprite.width
    if (minA <= maxB) and (maxA >= minB) and (rightA >= leftB) and (leftA <= rightB):
        return True
    return False
