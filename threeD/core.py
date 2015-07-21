import cv2
from config import camera, headJoint, matM, matMt, matMi, matMit, sift_threshole, threeD_threshole
import threeD
from numpy import *

class HeadLoc:
    def __init__(self, left = 0, down = 0):
        self.left = left
        self.down = down

#Transform from A to B
def rotAB(A, B):
    return threeD.rotZ(B.left - A.left) * threeD.rotY(B.down - A.down)

#Transform from A to B
def transAB(A, B):
    cameraA = rotAB(HeadLoc(), A) * camera
    cameraB = rotAB(LeadLoc(), B) * camera
    return retAB(A, HeadLoc()) * (cameraB - cameraA)

def transMatAB(A, B):
    t = transAB(A, B).A
    x = t[0][0]
    y = t[0][1]
    z = t[0][2]
    return mat([
        [0, -z, y],
        [z, 0, -x],
        [-y, x, 0],
    ])

def MatFAB(A, B):
    S = transMatAB(A, B)
    R = rotAB(A, B)
    return matMit * R * S * matMi

class Distance:
    def __init__(self, A, B):
        self.F = MatFAB(A, B)

    def dist(self, X, Y):
        d = (X.T * self.F * Y).A[0][0]
        return d / X.A[2][0] / Y.A[2][0]

class LineGen:
    def __init__(self, A):
        self.rot = RotAB(A, HeadLoc())
        self.loc = RotAB(HeadLoc(), A) * camera + headJoint

    def gen(self, x, y):
        P = mat([[x],[y],[1]])
        return [self.loc, self.rot * (matMi * p)]

def vec2lst(x):
    arr = x.tolist()
    return [arr[0][0], arr[1][0], arr[2][0]]

def lineCross2(a, b):
    p1 = a[0].A
    v1 = a[1].A
    p2 = b[0].A
    v2 = b[1].A
    y = (p1 - p2) / v1
    x = v2 / v1
    y = y.T[0]
    x = x.T[0]
    z = polyfit(x, y, 1)
    t2 = z[0]
    t1 = -z[1]
    return mat((p1 + v1 * t1 + p2 + v2 * t2) / 2)

def lineCross(lst):
    last = lst[-1]
    r = mat([[0], [0], [0]])
    for cur in lst:
        r += lineCross2(last, cur)
        last = cur
    return r / len(lst)


sift = cv2.SIFT()

def matchPoint(img1, img2, dist):
    ret = []
    def toVec3(pt):
        return mat(pt[0], pt[1], 1)
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)

    # BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1,des2, k=2)

    # Apply ratio test
    for m,n in matches:
        if m.distance < sift_threshole * n.distance:
            ret.append([toVec3(kp1[m.queryIdx].pt), 
                toVec3(kp2[m.trainIdx].pt), 
                ])

    # check threeD filter
    return [item for item in ret
        if dist.dist(item[0], item[1]) < threeD_threshole]
