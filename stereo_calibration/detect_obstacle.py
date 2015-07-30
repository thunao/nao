import cv2, os
import numpy as np
from stereo_match import stereosgbm_match

REMAP_FILENAME = os.path.dirname(__file__) + '/rectmap.npy'
Q_MATRIX_FILENAME = os.path.dirname(__file__) + '/Q.npy'

def display2D(points):
    points2D = np.asarray(points)[:, :2];
    boundary = ((min(points2D[:, 0]), min(points2D[:, 1])),
        (max(points2D[:, 0]) + 1, max(points2D[:, 1]) + 1))
    bitmap = np.zeros(np.asarray(boundary[1]) - np.asarray(boundary[0]), np.float32)
    for p in points2D:
        bitmap[int(p[0] - boundary[0][0])][int(p[1] - boundary[0][1])] += 1
    bitmap = np.asarray(bitmap / (bitmap.max() / 255.0), np.uint8)
    cv2.imshow('Image', bitmap)
    cv2.waitKey(0)

def stereo_rectify(img1, img2, mapfn, qfn):
    urmaps = np.load(mapfn)
    Q = np.load(qfn)
    imgL = cv2.remap(img1, urmaps[0], urmaps[1], cv2.INTER_LINEAR)
    imgR = cv2.remap(img2, urmaps[2], urmaps[3], cv2.INTER_LINEAR)
    #cv2.imshow('Image L', imgL); cv2.imshow('Image R', imgR)
    #cv2.waitKey(0)
    return imgL, imgR, Q

'''
img1:   left image, np.ndarray
img2:   right image, np.ndarray, img1.shape == img2.shape
pos:    (x, y, h); position of NAO, h represents the height of the camera
angle:  (pitch, yaw); angle between two picture should be constant(5.2 Degree recommended)
eps:    point P is a detected 3D point, we recognize P as an obstacle point if P.z > eps
return points list which shape == (N, 3) and type == np.float32
'''
def detect_obstacle(img1, img2, pos, angle, eps):
    params = (angle[0], angle[1], pos[2], pos[0], pos[1])
    imgL, imgR, Q = stereo_rectify(img1, img2, REMAP_FILENAME, Q_MATRIX_FILENAME)
    return stereosgbm_match(imgL, imgR, None, Q, params, eps)

if __name__ == '__main__':
    img1 = cv2.imread('L4.jpg')
    img2 = cv2.imread('R4.jpg')
    points = detect_obstacle(img1, img2, (0, 0, 0), (0.04, 0.176), -18)
    print points
    display2D(points)