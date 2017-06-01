def NDCToSC(x, y, screenwidth, screenheight):
    assert x >= 0.0 and x <= 1.0 and y >= 0.0 and y <= 1.0, "Invalid NDCs"
    return x * screenwidth, y * screenheight

def NDCToSC_x(x, screenwidth):
    assert abs(x) >= 0.0 and abs(x) <= 1.0, "Invalid NDCs"
    return int(x * screenwidth)

def NDCToSC_y(y, screenheight):
    assert abs(y) >= 0.0 and abs(y) <= 1.0, "Invalid NDCs"
    return int(y * screenheight)