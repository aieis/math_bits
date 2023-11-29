import cv2
import numpy as np
import gradio as gr

## Parameters
ROTATION_ANGLE_DEG = 10
NUMBER_OF_SQUARES = 20

Point = tuple[float, float]
Square = tuple[Point, float, float]
Line = tuple[Point, Point]

Triangle = tuple[Point, float, float]

def transformPoint(p1 : Point, rotation : float, translation : Point) -> Point:
    px, py = p1
    tx, ty = translation

    C = np.cos(rotation)
    S = np.sin(rotation)

    pxn = px * C - py * S + tx
    pyn = px * S + py * C + ty

    return (pxn, pyn)    
    

def transformLine(line: Line, rotation: float, translation: Point):
    p1, p2 = line
    return (transformPoint(p1, rotation, translation), transformPoint(p2, rotation, translation))
    

def drawSquare(im : np.ndarray, sq : Square):
    (x, y), r, theta = sq

    bl = (0, 0)
    br = (0, r)
    tr = (r, r)
    tl = (r, 0)

    sides = [
        (bl, br),
        (br, tr),
        (tr, tl),
        (tl, bl)
    ]


    h, _ = im.shape[:2]

    nsides = [transformLine(line, theta, (x,y)) for line in sides]
    for side in nsides:
        p1, p2 = side
        fx, fy = p1
        tx, ty = p2

        fp = (int(fx), int(h - fy))
        tp = (int(tx), int(h - ty))

        cv2.line(im, fp, tp, (0, 0, 0), 2)


def nextSquare(prevSquare : Square, rat : float, dtheta : float) -> Square:
    (x, y), r, theta = prevSquare
    z = rat * r
    h = r - z
    p = (z, 0)
    pn = transformPoint(p, theta, (x, y))
    xn, yn = pn
    rn = np.sqrt(h**2 + z**2)
    return ((xn, yn), rn, theta + dtheta)


def initSquare() -> Square:
    return ((0,0), 1024, 0)

def drawPattern(dtheta_deg, n):
    dtheta = dtheta_deg * np.pi / 180
    T = np.tan(dtheta)
    T = T if T > 0 else -T
    rat = T/(1+T)

    square = initSquare()

    squares = [square]
    for _ in range(n):
        square = nextSquare(square, rat, dtheta)
        squares.append(square)

    im = np.ones((1024, 1024, 3), np.uint8) * 255
    
    for square in squares:
        drawSquare(im, square)

    return im


def patternGenerator(dtheta, n):
    return drawPattern(dtheta, n)


def nextTriangle(prevTriangle : Triangle, dtheta : float) -> Triangle:
    (x, y), s_n, theta = prevTriangle
    
    omega = np.pi / 3
    zeta = np.pi - dtheta - omega

    S_omega = np.sin(omega)
    S_theta = np.sin(dtheta)
    S_zeta = np.sin(zeta)
    
    z = (s_n  * S_theta) / (S_theta + S_zeta)
    h = z * S_omega
    s_n1 = h / S_theta
    p = (z, 0)
    pn = transformPoint(p, theta, (x, y))

    return (pn, s_n1, theta + dtheta)


def drawTriangle(im : np.ndarray, triangle : Triangle):
    (x, y), r, theta = triangle
    omega = np.pi / 3 * 2

    sides = []

    sp = (0, 0)
    for i in range(3):
        side = ((0,0), (r, 0))
        siden = transformLine(side, i * omega, sp)
        sp = siden[1]
        sides.append(siden)


    h, _ = im.shape[:2]

    nsides = [transformLine(line, theta, (x,y)) for line in sides]
    for side in nsides:
        p1, p2 = side
        fx, fy = p1
        tx, ty = p2

        fp = (int(fx), int(h - fy))
        tp = (int(tx), int(h - ty))

        cv2.line(im, fp, tp, (0, 0, 0), 2)

def initTriangle() -> Triangle:
    return ((0,0), 1024, 0)
        
def drawPatternTriangles(dtheta_deg, n):
    dtheta = dtheta_deg * np.pi / 180

    triangle = initTriangle()
    triangles = [triangle]
    for _ in range(n):
        triangle = nextTriangle(triangle, dtheta)
        triangles.append(triangle)

    im = np.ones((1024, 1024, 3), np.uint8) * 255
    
    for triangle in triangles:
        drawTriangle(im, triangle)

    return im

def savePattern():
    dtheta_deg = ROTATION_ANGLE_DEG
    n = NUMBER_OF_SQUARES
    im = drawPatternTriangles(dtheta_deg, n)
    cv2.imshow("Pattern", im)
    cv2.waitKey(0)
    cv2.imwrite("zangle.png", im)

    
def webui():

    with gr.Blocks() as demo:
        im = gr.Image()
        rot = gr.Slider(0, 360, 1)
        num = gr.Slider(0, 1000, 1)

        rot.change(drawPatternTriangles, inputs=[rot, num], outputs=im)
        num.change(drawPatternTriangles, inputs=[rot, num], outputs=im)
        
    demo.launch()

if __name__ == "__main__":
    #savePattern()
    webui()

    
