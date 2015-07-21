from numpy import *

def rotX(alpha):
    return mat([
        [1, 0, 0],
        [0, cos(alpha), -sin(alpha)],
        [0, sin(alpha), cos(alpha)],
    ])

def rotY(alpha):
    return mat([
        [cos(alpha), 0, sin(alpha)],
        [0, 1, 0],
        [-sin(alpha), 0, cos(alpha)],
    ])

def rotZ(alpha):
    return mat([
        [cos(alpha), -sin(alpha), 0],
        [sin(alpha), cos(alpha), 0],
        [0, 0, 1],
    ])

def matTo4D(mat):
    arr = mat.A
    return mat([
        [arr[0][0], arr[0][1], arr[0][2], 0],
        [arr[1][0], arr[1][1], arr[1][2], 0],
        [arr[2][0], arr[2][1], arr[2][2], 0],
        [0, 0, 0, 1],
    ])

def move(x, y, z):
    return mat([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1],
    ])
