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

def matchPoint(kp1, des1, kp2, des2, dist, idx1, idx2):
    ret = []

    # BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1,des2, k=2)

    # Apply ratio test
    for m,n in matches:
        if m.distance < sift_threshole * n.distance:
            ret.append((m.queryIdx, m.trainIdx))

    # check threeD filter
    result = []
    for id1, id2 in ret:
        d = dist.dist(kp1[id1], kp2[id2])
        if d < threeD_threshole:
            result.append((d, idx1, id1, idx2, id2))
    return result

def get3DPoint(heads, imgs):
    def toVec3(pt):
        return mat(pt[0], pt[1], 1)
    kps = []
    dess = []
    for img in imgs:
        kp, des = sift.detectAndCompute(img, None)
        kps.append([toVec3(item.pt) for item in kp])
        dess.append(des)
    tbl = []
    for i in range(len(img)):
        for j in range(i + 1, len(img)):
            tbl += matchPoint(kps[i], dess[i], kps[j], dess[j],
                    Distance(heads[i], heads[j]), i, j)

    tbl.sort()

    idxs = {}
    ids = {}
    for d, idx1, id1, idx2, id2 in tbl:
        in1 = (idx1, id1) in idxs
        in2 = (idx2, id2) in idxs
        if not in1 and not in2:
            idxs[(idx1, id1)] = idxs[(idx2, id2)] = [idx1, idx2]
            ids[(idx1, id1)] = ids[(idx2, id2)] = [id1, id2]
        elif not in1 and in2:
            idxs[(idx1, id1)] = idxs[(idx2, id2)]
            ids[(idx1, id1)] = ids[(idx2, id2)]
            idxs[(idx2, id2)].append(idx1)
            ids[(idx2, id2)].append(id1)
        elif in1 and not in2:
            idxs[(idx2, id2)] = idxs[(idx1, id1)]
            ids[(idx2, id2)] = ids[(idx1, id1)]
            idxs[(idx1, id1)].append(idx2)
            ids[(idx1, id1)].append(id2)
        else:
            idxs1 = idxs[(idx1, id1)]
            ids1 = ids[(idx1, id1)]
            idxs2 = idxs[(idx2, id2)]
            ids2 = ids[(idx2, id2)]
            flag = True
            for i in idxs1:
                for j in idxs2:
                    flag &= i != j
            if flag:
                for i in idxs2:
                    idxs1.append(i)
                for i in ids2:
                    ids1.append(i)
                for i in zip(idxs2, ids2):
                    idxs[i] = idxs1
                    ids[i] = ids1

    s = []
    st = set()
    for idxc, idc in zip(idxs.values(), ids.values()):
        ic = zip(idxc, idc)
        if ic[0] not in st:
            st.add(ic[0])
            s.append(ic)

    linegens = [LineGen(loc) for loc in heads]

    pt  = [lineCross(
            [linegens[idx1].gen(kp[idx1][id1]) for idx1, id1 in ic])
            for ic in s]

    print pt
    return pt
