import cv2
from config import camera, headJoint
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

def MatFAB(A, B, M):
    S = transMatAB(A, B)
    R = rotAB(A, B)
    return M.I * R * S * M

class Distance:
    def __init__(self, A, B, M):
        self.F = MatFAB(A, B, M)

    def dist(self, X, Y):
        d = (X.T * self.F * Y).A[0][0]
        return d / X.A[2][0] / Y.A[2][0]

class LineGen:
    def __init__(self, A, M):
        self.rot = RotAB(A, HeadLoc())
        self.loc = RotAB(HeadLoc(), A) * camera + headJoint
        self.Mt = M.T

    def gen(self, x, y):
        P = mat([[x],[y],[1]])
        return [self.loc, self.rot * (self.Mt * p)]
