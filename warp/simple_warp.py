import cv2
import numpy as np
import math
import random

from project import *

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


def rotate_im(h, w, cam_x, cam_y, cam_z, cam_rot_x, cam_rot_y, cam_rot_z, focal_length, sensor_size):
    H = 2160
    
    mw = w // 2
    mh = h // 2

    r = 100
    TH = h

    polygons = []
    theta = 0

    polygon_pts = []
    while TH < 2000:
        alpha, M = make_matrix(r, TH, mw, mh)
        theta += alpha
        R = rot_mat(theta)
        M_p = M.dot(R)
        polygons.append((circle_norm(theta), M_p, M_p[0][-1]))
        polygon_pts.append(M_p)
        
        n_iter = int(2*np.pi / alpha) - 1
        TH += h / n_iter 
        r += 10 / (n_iter)
        
    canvas = np.ones((H, 1000, 3), np.uint8) * 200
    canvas_top = canvas.copy()
    canvas_cam = canvas.copy()
    

    H, W = canvas.shape[:2]

    HI = 50
    WI = W // 2

    deg2rad = lambda x: x * np.pi / 180
    camera_pos = np.array((cam_x, cam_y, cam_z))
    camera_rot = [deg2rad(x) for x in [cam_rot_x, cam_rot_y, cam_rot_z]]
    polygon_pts = np.array(polygon_pts)
    polygon_pts = project_from_world(camera_pos, camera_rot, polygon_pts)
    #polygon_pts = polygon_pts.reshape(-1, 4, 1, 2).astype(np.int32)
    #print(polygon_pts.shape)
    #polygon_pts = [ p for p in polygon_pts]
    #cv2.drawContours(canvas_cam, polygon_pts, -1, (20, 20, 140), -1)
    #print(len(polygons))

    polygons.sort(key=lambda k: k[2])


    canvas_r = np.ones((H*2, W*2, 3), np.uint8) * 200
    canvas_r[:H,:W] = canvas
    canvas_r[:H,W:] = canvas_top
    canvas_r[H:,:W] = canvas_cam
    
    for i, (theta, polygon, _) in enumerate(polygons):
        if abs(theta - np.pi) <= np.pi/2:
            c = (40, 40, 40)
        else:
            c = [random.randint(0, 255) for _ in range(3)]
            
        pts = list(map(lambda pt: (WI + pt[0], HI + pt[1]), polygon))
        pts = np.array(pts, np.int32).reshape((-1, 1, 2))
        
        cv2.drawContours(canvas, [pts], 0, c, -1)

        tr, tl = list(map(lambda pt: (WI + int(pt[0]), WI + int(pt[2])), polygon[:2]))
        cv2.line(canvas_top, tr, tl, c, 2)

        polygon = polygon_pts[i]
        pts = list(map(lambda pt: (WI + pt[0], (H // 2) + pt[1]), polygon))
        pts = np.array(pts, np.int32).reshape((-1, 1, 2))
        
        cv2.drawContours(canvas_cam, [pts], 0, c, -1)

        canvas_r[:H,:W] = canvas
        canvas_r[:H,W:] = canvas_top
        canvas_r[H:,:W] = canvas_cam

        yield canvas_r

def create_demo():
    import gradio as gr
    demo = gr.Interface(rotate_im, [gr.Slider(minimum = 0, maximum = 400, value=400),
                                    gr.Slider(minimum = 0, maximum = 200, value=80),
                                    gr.Slider(minimum = 0, maximum = 2000, value=500),
                                    gr.Slider(minimum = 0, maximum = 2000, value=500),
                                    gr.Slider(minimum = 0, maximum = 2000, value=1000),
                                    gr.Slider(minimum = 0, maximum = 360, value=0),
                                    gr.Slider(minimum = 0, maximum = 360, value=0),
                                    gr.Slider(minimum = 0, maximum = 360, value=0),
                                    gr.Slider(minimum = 0, maximum = 20, value=2),
                                    gr.Slider(minimum = 0, maximum = 100, value=30),
                                    ], gr.Image())
    demo.queue()
    demo.launch()
    
if __name__ == "__main__":
    demo = create_demo()
