import numpy as np
import cv2

def write_ply(fn, verts, colors):
    verts = verts.reshape(-1, 3)
    colors = colors.reshape(-1, 3)
    verts = np.hstack([verts, colors])
    with open(fn, 'w') as f:
        np.savetxt(f, verts, '%f %f %f %d %d %d')

def rotate(pitch, yaw, points):
    R0 = np.zeros((3, 3), np.int32)
    R0[2][1] = R0[1][0] = -1
    R0[0][2] = -1
    print R0
    Rp, J = cv2.Rodrigues(np.asarray((0, pitch, 0)))
    Ry, J = cv2.Rodrigues(np.asarray((0, 0, yaw)))
    R = np.dot(np.dot(Rp, Ry), R0)
    points = np.dot(R, points.T)
    return points.T

def stereosgbm_match(imgL, imgR, fname, Q, eps):
    # disparity range is tuned for 'aloe' image pair
    window_size = 6
    min_disp = 64
    num_disp = 112 - min_disp
    stereo = cv2.StereoSGBM_create(minDisparity = min_disp,
        numDisparities = num_disp,
        blockSize = 3,
        P1 = 8 * 3 * window_size ** 2,
        P2 = 32 * 3 * window_size ** 2,
        disp12MaxDiff = 1,
        uniquenessRatio = 10,
        speckleWindowSize = 100,
        speckleRange = 32
    )

    print 'computing disparity...'
    disp = stereo.compute(imgL, imgR).astype(np.float32) / 16
    print disp.min()

    print 'generating 3d point cloud...',
    points = cv2.reprojectImageTo3D(disp, Q)
    colors = cv2.cvtColor(imgL, cv2.COLOR_BGR2RGB)
    mask = disp > disp.min()
    points = points[mask]; colors = colors[mask]
    print colors

    print points[:3]
    points = rotate(0.04, 0.176, points)
    print points[:3]
    mask = points[:, 2] > eps
    points = points[mask]
    colors = colors[mask]

    write_ply(fname, points, colors)
    print '%s saved' % fname

    cv2.imshow('left', imgL)
    cv2.imshow('disparity', (disp - min_disp) / num_disp)
    cv2.waitKey()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    print 'loading images...'
    imgL = cv2.imread('L4.jpg')
    imgR = cv2.imread('R4.jpg')
    Q = np.float32([[1, 0, 0,  -0.5*imgL.shape[1]],
                    [0, 1, 0,  -0.5*imgL.shape[0]],
                    [0, 0, 0, imgL.shape[1] * 0.8],
                    [0, 0, 1,                   0]])
    stereosgbm_match(imgL, imgR, '3DPoints.ply', Q, 0)