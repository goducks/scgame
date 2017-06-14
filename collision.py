import drawable
def checkCollision(objA, objB):
    minA = objA.sprite.y
    minB = objB.sprite.y
    maxA = objA.sprite.y
    maxB = objB.sprite.y + objB.sprite.height
    leftA = objA.sprite.x
    leftB = objB.sprite.x
    rightA = objA.sprite.x + objA.sprite.width
    rightB = objB.sprite.x + objB.sprite.width
    if isinstance(objA, drawable.Bullet):
        maxA = objA.sprite.y + (objA.sprite.height * 2)
        rightA = objA.sprite.x + (objA.sprite.width * 2)
        leftA = objA.sprite.x - objA.sprite.width
    elif isinstance(objA, drawable.EnemyBullet):
        minA = objA.sprite.y - (objA.sprite.height * 2)
    if (minA <= maxB) and (maxA >= minB) and (rightA >= leftB) and (leftA <= rightB):
        return True
    return False
