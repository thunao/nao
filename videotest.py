import cv2, numpy, sys
from posture import Motion

def test(IP='127.0.0.1', PORT=9559):

	# init a Motion instance
	motion = Motion(IP, PORT)

	# test code
	imgs = motion.lookAround()
	cnt = 0
	for key in imgs:
		print 'left: ', key.left, '; down: ', key.down
		cv2.imwrite('img' + str(cnt) + '.jpg', imgs[key])
		cnt += 1

	del motion

if __name__ == '__main__':
	IP = sys.argv[1]
	PORT = 9559
	test(IP, PORT)
