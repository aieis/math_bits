import cv2
import numpy as np
import gradio as gr

## Parameters
ROTATION_ANGLE_DEG = 10
NUMBER_OF_POLYGONS = 2
NUMBER_OF_SIDES = 4

Point = tuple[float, float]
Line = tuple[Point, Point]

Polygon = tuple[Point, int, float, float]


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



def nextPolygon(prevPolygon : Polygon, dtheta : float) -> Polygon:
    (x, y), n, s_n, theta = prevPolygon

    omega = np.pi * (n - 2) / n
    zeta = np.pi - dtheta - omega

    S_omega = np.sin(omega)
    S_theta = np.sin(dtheta)
    S_zeta = np.sin(zeta)

    z = (s_n  * S_theta) / (S_theta + S_zeta)
    h = z * S_omega
    s_n1 = h / S_theta
    p = (z, 0)
    pn = transformPoint(p, theta, (x, y))

    return (pn, n, s_n1, theta + dtheta)


def drawPolygon(im : np.ndarray, polygon : Polygon):
    (x, y), n, r, theta = polygon
    omega =  omega = np.pi * (n - 2) / n
    omega = np.pi - omega

    sides = []

    sp = (0, 0)
    for i in range(n):
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

def initPolygon(n) -> Polygon:
    avl = 1024

    # avgw = n*L / np.pi

    L = avl * np.pi / n

    x = (avl - L)

    return ((x / 2,5), n, L, 0)

def drawPatternPolygons(number_of_sides, dtheta_deg, n):
    dtheta = dtheta_deg * np.pi / 180
    im = np.ones((1024, 1024, 3), np.uint8) * 255

    if dtheta_deg is None or number_of_sides is None or n is None:
        return im

    if number_of_sides < 3:
        return im

    polygon = initPolygon(number_of_sides)
    polygons = [polygon]
    for _ in range(n):
        polygon = nextPolygon(polygon, dtheta)
        polygons.append(polygon)



    for polygon in polygons:
        drawPolygon(im, polygon)

    return im

def savePattern():
    dtheta_deg = ROTATION_ANGLE_DEG
    n = NUMBER_OF_POLYGONS
    im = drawPatternPolygons(NUMBER_OF_SIDES, dtheta_deg, n)
    cv2.imshow("Pattern", im)
    cv2.waitKey(0)
    cv2.imwrite("zangle.png", im)


def webui():
    with gr.Blocks() as demo:
        im = gr.Image()

        sides = gr.Slider(3, 100, 3, step=1)
        rot = gr.Slider(0, 360, 10)
        num = gr.Slider(0, 1000, 10, step=1)

        sides.change(drawPatternPolygons, inputs=[sides, rot, num], outputs=im)
        rot.change(drawPatternPolygons, inputs=[sides, rot, num], outputs=im)
        num.change(drawPatternPolygons, inputs=[sides, rot, num], outputs=im)


    demo.queue().launch()

if __name__ == "__main__":
    #savePattern()
    webui()
