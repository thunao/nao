import cv2, numpy
from posture import Motion

IP = '101.5.221.178'
PORT = 9559

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

# init a Motion instance
motion = Motion(IP, PORT)

# init window
windowName = "Chessboard"
cv2.namedWindow(windowName, 1)
delay = 1000 / motion.fps

# capture images
while cv2.waitKey(delay) < 0:
	imgstr, shape = motion.takePicture()
	image = str2array(imgstr, shape)
	cv2.imshow(windowName, image)

cv2.destroyAllWindows()
del motion
