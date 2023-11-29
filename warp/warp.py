import cv2
import numpy as np

def rot_mat(theta):
    C = np.cos(theta)
    S = np.sin(theta)
    mat = np.array([[C, -S],
                    [S,  C]])
    return mat

def run():
    im = np.zeros((1400,600,3), np.uint8)
    top = np.zeros((600, 600, 3), np.uint8)

    mx = im.shape[1] // 2
    w = 128
    theta = 0
    a = 100

    point = np.array((0, 100))
    #8b = 8 * 16 + b -> 8b = 128 + 11 -> 8b = 139
    col = np.array([0, 0, 139])
    N = 30
    for i in range(N):
        a_n = a * (1 + i * 0.1)
        point_n = point * a_n / a
        rot = rot_mat(theta)
        target = rot.dot(point_n)
        z = i * 50
        x = int(target[0])
        y = int(target[1])
        head = (mx + x, z)
        orig = (mx, z)
        color = (col * (N - i) / N).astype(int).tolist()

        head_t = (mx + x, mx + y)
        orig_t= (mx, mx)

        cv2.arrowedLine(im, orig, head, color, 2)
        cv2.arrowedLine(top, orig_t, head_t, color, 2)
        cv2.imshow("im", im)
        cv2.imshow("top", top)
        cv2.waitKey(30)
                                
        theta_n = 2 * np.arcsin(w/(2*a_n))
        theta += theta_n

    cv2.waitKey(0)
    
def warp():
    im = np.zeros((1400,600,3), np.uint8)
    top = np.zeros((600, 600, 3), np.uint8)

    im_w = cv2.imread("C:/etc/smalljpg/1000.jpg")
    h, w = im_w.shape[:2]
    im_w_coords = np.array([
        (x,y) for x in range(w) for y in range(h)
    ], int)


    
    mx = im.shape[1] // 2
    w_off = w + 20
    z_off = h + 20
    theta = 0
    a = 100

    point = np.array((0, 100))
    #8b = 8 * 16 + b -> 8b = 128 + 11 -> 8b = 139
    col = np.array([0, 0, 139])
    N = 10
    for i in range(N):
        a_n = a * (1 + i * 0.1)
        
        rot = rot_mat(theta)

        n_coords = im_w_coords + np.array((0, a_n))
        n_coords = np.array([n_coords[:,0], n_coords[:,1]], int)
        n_coords = rot.dot(n_coords).astype(int)

        z = 10 + i * z_off
        for px in range(w):
            for py in range(h):
                ind = px * w + py
                nx = n_coords[0, ind]
                ny = n_coords[1, ind]
                im[ny+z,nx] = im_w[px,py]
        
        cv2.imshow("im", im)
        cv2.waitKey(30)
                                
        theta_n = 2 * np.arcsin(w_off/(2*a_n))
        theta += theta_n

    cv2.waitKey(0)
        
if __name__ == "__main__":
    warp()
