from naoqi import ALProxy
import cv2
import numpy

def str2array(string, shape):
	assert len(string) == shape[0] * shape[1] * shape[2], len(shape) == 3
	image = numpy.zeros(shape, numpy.uint8)
	for i in range(0, shape[0]):
		p1 = i * shape[1] * shape[2]
		for j in range(0, shape[1]):
			p2 = j * shape[2]
			for c in range(0, shape[2]):
				p3 = shape[2] - c - 1
				image[i, j, c] = ord(string[p1 + p2 + p3])
	return image

# init camera
local = "127.0.0.1"
remote = "101.5.220.247"
vd = ALProxy("ALVideoDevice", local, 9559)
nameID = "VM"
cameraIdx = 0
resolution = 2 # kQQQQVGA(40*30) = 8 | kVGA(640*480) = 2
colorSpace = 11 # kRGBColorSpace
fps = 15
nameID = vd.subscribeCamera(nameID, cameraIdx, resolution, colorSpace, fps)
print nameID
print vd.getResolution(nameID)
if not vd.isCameraOpen(cameraIdx):
	vd.openCamera(cameraIdx)

# init window
windowName = "Chessboard"
cv2.namedWindow(windowName, 1)
delay = 1000 / fps

# capture images
while cv2.waitKey(delay) < 0:
	imgVal = vd.getImageRemote(nameID)
	width = imgVal[0]
	height = imgVal[1]
	nchanels = imgVal[2]
	shape = (height, width, nchanels)
	image = str2array(imgVal[6], shape)
	cv2.imshow(windowName, image)

vd.setAllParametersToDefault(cameraIdx)
cv2.destroyAllWindows()
