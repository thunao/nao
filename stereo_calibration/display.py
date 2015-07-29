import numpy as np
import math
import cv2
from stereo_match import stereosgbm_match
from stereo_calibrate import stereo_rectify

def str2point(flines):
    points = []
    for line in flines:
        if 'inf' in line:
            continue
        elems = line.split()
        point = (float(elems[0]), float(elems[1]), float(elems[2]))
        color = (int(elems[3]), int(elems[4]), int(elems[5]))
        points.append((point, color))
    return points

def getBoundary(points):
    points = np.asarray(points)
    minX = min(points[:, 0, 0])
    minY = min(points[:, 0, 1])
    minZ = min(points[:, 0, 2])
    maxX = max(points[:, 0, 0])
    maxY = max(points[:, 0, 1])
    maxZ = max(points[:, 0, 2])
    return (minX, minY, minZ), (maxX, maxY, maxZ)

def solveEquas(A):
    s1 = A[1][0] / A[0][0]; s2 = A[2][0] / A[0][0]
    A[1, :] -= A[0, :] * s1; A[2, :] -= A[0, :] * s2
    s2 = A[2][1] / A[1][1]
    A[2, 1:] -= A[1, 1:] * s2
    z = A[2][3] / A[2][2]
    y = (A[1][3] - A[1][2] * z) / A[1][1]
    x = (A[0][3] - A[0][1] * y - A[0][2] * z) / A[0][0]
    return (x, y, z)

def project(camera, canvas, p):
    x1, y1, z1 = p
    x2, y2, z2 = camera
    a1 = z2 - z1; b1 = 0; c1 = x1 - x2; d1 = (x1 - x2) * z2 + (z2 - z1) * x2
    a2 = 0; b2 = z2 - z1; c2 = y1 - y2; d2 = (y1 - y2) * z2 + (z2 - z1) * y2
    A = np.asarray([[a1, b1, c1, d1], [a2, b2, c2, d2], canvas], np.float32)
    A[2, 3] = - A[2, 3]
    return solveEquas(A)

def project(camera, canvas_v, p, flag):
    k = (canvas_v - camera[flag]) / (p[flag] - camera[flag])
    q = (np.asarray(p) - np.asarray(camera)) * k + np.asarray(camera)
    return q

def topixel(cen_p, img_sz, q, scale):
    k = - cen_p[0] / cen_p[2]
    z0 = (q[2] - k * q[0]) / (1 + k ** 2); x0 = - k * z0
    lx = np.sqrt(sum((np.asarray((x0, q[1], z0)) - np.asarray(q)) ** 2))
    ly = np.sqrt(sum((np.asarray(cen_p) - np.asarray(q)) ** 2) - lx ** 2)
    if q[0] < cen_p[0]:
        lx = -lx
    if q[1] < cen_p[1]:
        ly = -ly
    c = lx * scale + img_sz[0] / 2
    r = ly * scale + img_sz[1] / 2
    if r >= img_sz[1] or c >= img_sz[0] or r < 0 or c < 0 or math.isnan(r) or math.isnan(c):
        return 0, 0
    return int(r), int(c)

def topixel(camera, img_sz, q, scale, flag):
    idx = [(1, 2), (2, 0), (0, 1)]
    idx = idx[flag]
    c = int((q[idx[0]] - camera[idx[0]]) * scale + img_sz[0] / 2)
    r = int(-(q[idx[1]] - camera[idx[1]]) * scale + img_sz[1] / 2)
    if r >= img_sz[1] or c >= img_sz[0]:
        return 0, 0
    return c, r

def computeCameraPos(minP, maxP, img_sz):
    '''camera = ((minP[0] + maxP[0]) / 2,
        (minP[1] + maxP[1]) / 2, 3 * maxP[2] - 2 * minP[2])
    canvas = (0, 0, 1, - 2 * maxP[2] + minP[2])'''
    minP = np.asarray(minP); maxP = np.asarray(maxP)
    n = maxP - minP
    camera = 2 * n + minP
    canvas = np.zeros((4), np.float32)
    canvas[:3] = n; canvas[3] = -np.dot(n, n + maxP[2])

    cen_p = project(camera, canvas, np.add(canvas[:3], camera))
    scale = min(img_sz[0] / (maxP[1] - minP[1]),
        img_sz[1] / (maxP[0] - minP[0])) * 2
    return camera, canvas, cen_p, scale

def computeCameraPos(minP, maxP, img_sz, flag):
    camera = (np.asarray(minP) + np.asarray(maxP)) / 2
    assert flag in range(0, 3)
    camera[flag] = 3 * maxP[flag] - 2 * minP[flag]
    canvas_v = 2 * maxP[flag] - minP[flag]
    idx = [(1, 2), (2, 0), (0, 1)]
    idx = idx[flag]
    scale = min(img_sz[1] / (maxP[idx[0]] - minP[idx[0]]),
        img_sz[0] / (maxP[idx[1]] - minP[idx[1]])) * 2
    return camera, canvas_v, scale

def drawAxis(pic, camera, canvas_v, scale, img_sz, length, flag):
    axis = np.zeros((4, 3), np.float32)
    axis[1][0] = axis[2][1] = axis[3][2] = length
    points = []
    for p in axis:
        q = project(camera, canvas_v, p, flag)
        points.append((topixel(camera, img_sz, q, scale, flag)))
    pic = cv2.line(pic, points[0], points[1], (255, 0, 0), 1)
    pic = cv2.line(pic, points[0], points[2], (0, 255, 0), 1)
    pic = cv2.line(pic, points[0], points[3], (0, 0, 255), 1)
    pic = cv2.circle(pic, points[0], 4, (255, 255, 0), -1)
    pic = cv2.circle(pic, points[1], 3, (255, 0, 0), -1)
    pic = cv2.circle(pic, points[2], 2, (0, 255, 0), -1)
    pic = cv2.circle(pic, points[3], 1, (0, 0, 255), -1)
    return pic

def display(filename, img_sz, flag):
    f = open(filename, 'r')
    flines = f.readlines()
    f.close()
    picture = np.zeros((img_sz[1], img_sz[0], 3), np.uint8)
    points = str2point(flines)
    minP, maxP = getBoundary(points)
    print minP, maxP
    camera, canvas_v, scale = computeCameraPos(minP, maxP, img_sz, flag)
    print camera, canvas_v, scale
    for p in points:
        q = project(camera, canvas_v, p[0], flag)
        c, r = topixel(camera, img_sz, q, scale, flag)
        picture[r, c, :] = p[1]
    picture = cv2.cvtColor(picture, cv2.COLOR_RGB2BGR)

    picture = drawAxis(picture, camera, canvas_v, scale, img_sz, 50.0, flag)

    cv2.imshow('3DPicture', picture)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    #display('3DPoints.ply', (640, 480), 0)
    #display('_3DPoints.ply', (640, 480), 0)
    '''imgL = cv2.imread('L2.jpg')
    imgR = cv2.imread('R2.jpg')
    Q = np.float32([[1, 0, 0,  -0.5*imgL.shape[1]],
                    [0, 1, 0,  -0.5*imgL.shape[0]],
                    [0, 0, 0, imgL.shape[1] * 0.8],
                    [0, 0, 1,                   0]])
    for i in [3, 4, 5, 6]:
        print i
        stereosgbm_match(imgL, imgR, '3DPoints.ply', Q, i)
        display('3DPoints.ply', (640, 480), 0)'''
    imgL, imgR, Q = stereo_rectify('L4.jpg', 'R4.jpg', 'rectmap.npy', 'Q.npy')
    for h in [-24, -20, -18, -16]:
        print h, "-------------------------------------------"
        stereosgbm_match(imgL, imgR, '_3DPoints.ply', Q, h)
        display('_3DPoints.ply', (640, 480), 0)