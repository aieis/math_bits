import cv2
import numpy as np

def draw_arc(x1, y1, x2, y2, R):
    C = ((x2 - x1) + x1**2 - x2**2 + y1**2 - y2 ** 2) / (y1 - y2)

    a = C ** 2 + 1
    b = (-2*x1 - 2*C*y1)
    c = (x1**2 + y1**2 - R**2)

    print(a, b, c, (b**2 - 4 * a * c))
    x = (-b + np.sqrt(b**2 - 4*a*c)) / (2 * a)
    y = x * C
    print(x, y)

    
    im = np.ones((1024, 1024, 3), np.uint8) * 255

    c1 = (185, 0, 0)
    c2 = (0, 0, 185)
    c3 = (185, 0, 185)

    s = 5
    th = 3

    cv2.circle(im, (x1, y1), s, c1, -1)
    cv2.circle(im, (x1, y1), R, c1, th)

    cv2.circle(im, (x2, y2), s, c2, -1)
    cv2.circle(im, (x2, y2), R, c2, th)

    x = int(x)
    y = int(y)
    cv2.circle(im, (x, y), s, c3, -1)
    cv2.circle(im, (x, y), R, c3, th)

    return im

def run():
    while cv2.waitKey(1) != ord("q"):
        im = draw_arc(200, 200, 500, 500, 300)
        cv2.imshow("circle_arcs", im)

if __name__ == "__main__":
    run()
