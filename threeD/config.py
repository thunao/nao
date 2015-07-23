import numpy
from Calibration.result import matM_raw

#raw config
camera_x = 58.71
camera_y = 461.
camera_z = 63.64
headJointHeight = 1
sift_threshole = 0.75
threeD_threshole = 1
camera_depression_angle = 1.2 / 180 * numpy.pi

camera = numpy.mat([[camera_x], [camera_y], [camera_z]])
headJoint = numpy.mat([[0], [0], [headJointHeight]])

camera_depression_angle_mat = numpy.mat([
    [numpy.cos(camera_depression_angle), 0, numpy.sin(camera_depression_angle)],
    [0, 1, 0],
    [-numpy.sin(camera_depression_angle), 0, numpy.cos(camera_depression_angle)],
    ])
matM = numpy.mat(matM_raw) * camera_depression_angle_mat
matMt = matM.T
matMi = matM.I
matMit = matMi.T
