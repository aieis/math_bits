import numpy as np

def rot_matrix_from_angles(x, y, z):
    C = np.cos
    S = np.sin

    Rx     = [      
        [1     , 0,     0     ], 
        [0     , C(x),  -S(x) ], 
        [0     , S(x),  C(x) ]]

    Ry     = [      
        [C(y)  , 0,     S(y)  ], 
        [0     , 1,     0     ], 
        [-S(y) , 0,     C(y)    ]]

    Rz     = [      
        [C(z)  , -S(z), 0     ], 
        [S(z)  , C(z),  0     ], 
        [0     , 0,     1     ]]


    Rx = np.array(Rx)
    Ry = np.array(Ry)
    Rz = np.array(Rz)

    final_rot = Rx.dot(Ry).dot(Rz)
    return final_rot

def project_from_world(camera_pos, camera_rot, pts):
    shape = pts.shape
    npts = pts.reshape((-1, 3)).copy()

    npts = npts - camera_pos
    R = rot_matrix_from_angles(*camera_rot)
    npts = npts.dot(R)
    
    return npts.reshape(shape)
    

if __name__ == "__main__":
    import cv2
    
    camera_pos = np.array([100, 100, 100])
    camera_rot = [np.pi/4, np.pi/4, np.pi/4]
    
    focal_length = 1
    sensor_size = 100
    
    canvas = np.ones((200, 200, 3), np.uint8) * 70

    contours = np.array([[50, 50, 100], [50, 100, 100], [100,100, 100],[100, 50, 100]])
    contours_proj = project_from_world(camera_pos, camera_rot, contours)
    print(contours)
    print(contours_proj)
    pts = contours[:, [0,1]].astype(np.int32)
    pts_proj = contours_proj[:,[0,1]].astype(np.int32)

    print(pts_proj)


    canvas_cam = np.ones((200, 200, 3), np.uint8) * 200
    
    pts = pts.reshape(-1, 1, 2)
    pts_proj = pts_proj.reshape(-1, 1, 2) + np.array([100, 100])

    
    cv2.drawContours(canvas, [pts], -1, (20, 20, 200), -1)
    cv2.drawContours(canvas_cam, [pts_proj], -1, (200, 20, 20), -1)
    
    cv2.imshow("canvas", np.hstack((canvas, canvas_cam)))
    cv2.waitKey(0)
    
