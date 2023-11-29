import cv2
import numpy as np
import gradio as gr

## Parameters
ROTATION_ANGLE_DEG = 45
NUMBER_OF_SQUARES = 10

Point = tuple[float, float]
Square = tuple[Point, float, float]
Line = tuple[Point, Point]

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


def savePattern():
    dtheta_deg = ROTATION_ANGLE_DEG
    n = NUMBER_OF_SQUARES
    im = drawPattern(dtheta_deg, n)
    cv2.imshow("Pattern", im)
    cv2.waitKey(0)
    cv2.imwrite("zangle.png", im)

def patternGenerator(dtheta, n):
    return drawPattern(dtheta, n)


def nextTriangle():
    s_n = 10
    dtheta = np.pi / 10

    omega = 60 * np.pi / 180

    S_omega = np.sin(omega)
    C_omega = np.cos(omega)
    T_theta = np.tan(dtheta)
    S_theta = np.sin(dtheta)
    C_theta = np.cos(dtheta)
    
    zeta = np.pi - dtheta - omega
    S_zeta = np.sin(zeta)

    z = (s_n  * S_theta) / (S_theta + S_zeta)

    
    k = z * C_omega
    h = z * S_omega

    s_n1 = h / S_theta

    
    s_n1_2 = np.sqrt((s_n - z - k)**2 + h**2)

    s_n1_3 =  z * S_omega / S_theta

    print(f"{S_omega=}, {C_omega=}, {T_theta=}, {S_theta=}, {C_theta=}, {z=}, {k=}, {h=}, {s_n1=}, {s_n1_2=}, {s_n1_3=}")
    

    
    
def webui():

    with gr.Blocks() as demo:
        im = gr.Image()
        rot = gr.Slider(0, 360, 1)
        num = gr.Slider(0, 1000, 1)

        rot.change(patternGenerator, inputs=[rot, num], outputs=im)
        num.change(patternGenerator, inputs=[rot, num], outputs=im)
        
    demo.launch()

if __name__ == "__main__":
    #savePattern()
    #webui()
    nextTriangle()
