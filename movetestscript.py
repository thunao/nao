from posture import Motion
from math import pi

def test(IP='127.0.0.1', PORT=9559):

	# init a Motion instance
	motion = Motion(IP, PORT)

	motion.walkStraight((5, 0))
    motion.turn(pi / 2)
    motion.walkStraight((5, 8))
    motion.turn(- pi / 2)
    motion.walkStraight((10, 8))

	del motion

if __name__ == '__main__':
	IP = sys.argv[1]
	PORT = 9559
	test(IP, PORT)
