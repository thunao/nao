# encoding=utf-8

__author__  = 'cty'
__version__ = '0.1'
__contact__ = 'chentianyu@outlook.com'

import sys, time, random, numpy
from naoqi import ALProxy
import vision_definitions

class HeadLoc:
    def __init__(self, left = 0, down = 0):
        self.left = left
        self.down = down

class Motion:

	# constructor
	def __init__(self, ip='127.0.0.1', port=9559):
		self.motionProxy = ALProxy('ALMotion', ip, port)
		self.postureProxy = ALProxy('ALRobotPosture', ip, port)
		self.camProxy = ALProxy('ALVideoDevice', ip, port)
		resolution = vision_definitions.kQVGA
		colorSpace = vision_definitions.kRGBColorSpace
		self.fps = 15
		self.videoClient = self.camProxy.subscribeCamera('python_client', 0, resolution, colorSpace, self.fps)
		# print self.videoClient
		# in case of camera subscribe overflow
		assert not self.videoClient == None
		# wake up nao
		self.motionProxy.wakeUp()
		# stand init
		self.postureProxy.goToPosture("StandInit", 0.5)
		# move init
		self.motionProxy.moveInit()

		# get the origin
		self.__origin = tuple(self.motionProxy.getRobotPosition(False))

	# destructor
	def __del__(self):
		self.camProxy.unsubscribe(self.videoClient)
		self.camProxy.setAllParametersToDefault(0)
		# rest, set all stiffness to 0
		self.motionProxy.rest()

	# 瞎 jb 看
	def lookAround(self):
		print 'wow i\'m looking around... '

		ret = dict()

		pitch = self.motionProxy.getAngles('HeadPitch', False)
		yaw = self.motionProxy.getAngles('HeadYaw', False)
		print 'taking picture'
		img = self.__takePicture()
		ret[HeadLoc(left = yaw, down = pitch)] = img

		# 随便转转头
		self.motionProxy.setAngles('HeadPitch', random.uniform(0.5, 0.5), 0.1)
		self.motionProxy.setAngles('HeadYaw', random.uniform(0.5, 0.5), 0.1)

		pitch = self.motionProxy.getAngles('HeadPitch', False)
		yaw = self.motionProxy.getAngles('HeadYaw', False)
		print 'taking picture'
		img = self.__takePicture()
		ret[HeadLoc(left = yaw, down = pitch)] = img

		self.motionProxy.setAngles('HeadPitch', 0.0, 0.1)
		self.motionProxy.setAngles('HeadYaw', 0.0, 0.1)

		return ret

	# take a picture
	def __takePicture(self):
		# for debug
		print "takePicture"

		naoImage = self.camProxy.getImageRemote(self.videoClient)

		width = naoImage[0]; height = naoImage[1]
		nchanels = naoImage[2]; array = naoImage[6]

		return self.__str2array(array, (height, width, nchanels))

	def __str2array(self, string, shape):
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

	# turn left or turn right
	# 原地转圈
	def turn(self, rad):
		# for debug
		print 'turning radius %f. ' %(direction, rad)

		self.motionProxy.moveTo(0.0, 0.0, rad)

	# robot walk, for a period of time
 	# XXX TO DO
	def walkStraight(self):
		# for debug
		print 'walk. '

		print 'position: ', self.motionProxy.getRobotPosition(False)
		# self.motionProxy.moveToward(1.0, 0.0, 0.0)
		# time.sleep(t)
		# self.motionProxy.stopMove()
		print 'position after move: ', self.motionProxy.getRobotPosition(False)
