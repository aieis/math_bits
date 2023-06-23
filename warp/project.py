import numpy as np

def project_from_world(camera_pos, pts, focal_length, sensor_size):
    shape = pts.shape
    npts = pts.reshape((-1, 3)).copy()
    npts = npts - camera_pos
    
    npts[:,2] = 1 / npts[:,2]
    f = focal_length
    proj_matrix = np.array([
        [f, 0, 0],
        [0, f, 0],
        [1, 1, 0]
    ])

    npts = npts.dot(proj_matrix)
    return npts.reshape(shape)
    
