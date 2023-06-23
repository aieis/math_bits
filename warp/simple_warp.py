import cv2
import numpy as np
import math
import random

def rot_vec(vec, theta):
    C = np.cos(theta)
    S = np.sin(theta)

    x, y, z = vec
    xp = C*x - S*z
    zp = S*x + C*z

    return (xp, y, zp)


def rot_mat(theta):
    C = np.cos(theta)
    S = np.sin(theta)
    mat = np.array([[C  , 0, S ],
                    [0  , 1, 0 ],
                    [-S , 0, C ]])
    return mat


def circle_norm(angle):
    full = np.pi * 2
    q = angle / full
    n = math.trunc(q)
    r = q - n
    return r * full

def make_matrix(r, h, mw, mh):
    x, y, z = 0, h, r
    tr = (x+mw, y-mh, z)
    tl = (x-mw, y-mh, z)
    bl = (x-mw, y+mh, z)
    br = (x+mw, y+mh, z)

    M = np.concatenate((tr,tl, bl, br), axis=0).reshape(-1, 3)
    alpha = 2 * np.arctan((mw + 10) / r)
    return alpha, M


def rotate_im(h, w):
    H = 2160
    
    mw = w // 2
    mh = h // 2

    r = 100
    TH = h

    polygons = []
    theta = 0
    
    while TH < 2000:
        alpha, M = make_matrix(r, TH, mw, mh)
        theta += alpha
        R = rot_mat(theta)
        M_p = M.dot(R)
        polygons.append((circle_norm(theta), M_p, M_p[0][-1]))

        n_iter = int(2*np.pi / alpha) - 1
        TH += h / n_iter 
        r += 10 / (n_iter)
        
    canvas = np.ones((H, 1000, 3), np.uint8) * 200
    canvas_top = canvas.copy()

    H, W = canvas.shape[:2]

    HI = 50
    WI = W // 2

    print(len(polygons))
    polygons.sort(key=lambda k: k[2])

    
    for theta, polygon, _ in polygons:
        if abs(theta - np.pi) <= np.pi/2:
            c = (40, 40, 40)
        else:
            c = [random.randint(0, 255) for _ in range(3)]
            
        pts = list(map(lambda pt: (WI + pt[0], HI + pt[1]), polygon))
        pts = np.array(pts, np.int32).reshape((-1, 1, 2))
        cv2.drawContours(canvas, [pts], 0, c, -1)

        tr, tl = list(map(lambda pt: (WI + int(pt[0]), WI + int(pt[2])), polygon[:2]))
        cv2.line(canvas_top, tr, tl, c, 2)

        disp = cv2.resize(np.hstack((canvas, canvas_top)), None, fx=0.5, fy=0.5)
        yield disp
    #     cv2.imshow("Canvas", disp)
    #     cv2.waitKey(1)


    # disp = cv2.resize(np.hstack((canvas, canvas_top)), None, fx=0.5, fy=0.5)
    # cv2.imshow("Canvas", disp)
    # cv2.waitKey(0)


def create_demo():
    import gradio as gr
    rotate_im(80, 80)

    demo = gr.Interface(rotate_im, [gr.Slider(minimum = 0, maximum = 200, value=80), gr.Slider(minimum = 0, maximum = 200, value=80)], gr.Image())
    demo.queue()
    demo.launch()
    
if __name__ == "__main__":
    demo = create_demo()
