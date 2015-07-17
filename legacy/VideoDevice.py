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

def isChessboardFound(image, board_sz):
	found, corners = cv2.findChessboardCorners(
		image, board_sz, None,
		cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_FILTER_QUADS)
	return found

# init camera
local = "127.0.0.1"
remote = "101.5.222.14"
vd = ALProxy("ALVideoDevice", local, 62501)
nameID = "VM"
cameraIdx = 0
resolution = 2 # kQQQQVGA(40*30) = 8 | kVGA(640*480) = 2
colorSpace = 11 # kRGBColorSpace (vision_definitions)
fps = 10
nameID = vd.subscribeCamera(nameID, cameraIdx, resolution, colorSpace, fps)
print 'NAME ID:', nameID
print 'Resolution:', vd.getResolution(nameID)
if not vd.isCameraOpen(cameraIdx):
	vd.openCamera(cameraIdx)

# init window
windowName = "Chessboard"
cv2.namedWindow(windowName, 1)
delay = 1000 / fps

# capture images
count = 1
key = cv2.waitKey(delay)
while not key == 27:
	imgVal = vd.getImageRemote(nameID)
	width = imgVal[0]
	height = imgVal[1]
	nchanels = imgVal[2]
	shape = (height, width, nchanels)
	image = str2array(imgVal[6], shape)
	cv2.imshow(windowName, image)
	if key == 13 or isChessboardFound(image, (5, 5)):
		cv2.imwrite('cb' + str(count) + '.jpg', image)
		print 'Picture', count
		count += 1
	key = cv2.waitKey(delay)

vd.unsubscribe(nameID)
vd.setAllParametersToDefault(cameraIdx)
cv2.destroyAllWindows()
