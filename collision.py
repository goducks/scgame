import drawable

global llAx, llAy
llAx, llAy = 0, 0
def checkCollision(objA, objB):
    global llAx, llAy
    oldllx, oldlly = llAx, llAy
    llAx, llAy = objA.sprite.x, (objA.sprite.y + objA.sprite.height)
    llBx, llBy = objB.sprite.x, (objB.sprite.y + objB.sprite.height)
    urAx, urAy = (objA.sprite.x + objA.sprite.width), objA.sprite.y
    urBx, urBy = (objB.sprite.x + objB.sprite.width), objB.sprite.y
    if isinstance(objA, drawable.Bullet):
        llAx = objA.sprite.x - objA.sprite.width
    if (urAy <= llBy) and (llAy >= urBy) and (urAx >= llBx) and (llAx <= urBx):
        return True
    return False
