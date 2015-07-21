import cv2, numpy
from posture import Motion

def main(IP='127.0.0.1', PORT=9559):

	# init a Motion instance
	motion = Motion(IP, PORT)

	# init window
	windowName = "Chessboard"
	cv2.namedWindow(windowName, 1)
	delay = 1000 / motion.fps

	# capture images
	while cv2.waitKey(delay) < 0:
		image = motion.takePicture()
		cv2.imshow(windowName, image)

	cv2.destroyAllWindows()

	del motion

if __name__ == '__main__':
	IP = '101.5.221.178'
	PORT = 9559
	main(IP, PORT)
