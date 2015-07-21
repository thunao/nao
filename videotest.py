import cv2, numpy
from posture import Motion

def main(IP='127.0.0.1', PORT=9559):

	# init a Motion instance
	motion = Motion(IP, PORT)

	# your code

	del motion

if __name__ == '__main__':
	IP = '101.5.221.178'
	PORT = 9559
	main(IP, PORT)
