# encoding=utf-8

__author__ = 'cty'
__version__ = '0.1'
__contact__ = 'chentianyu@outlook.com'

import sys, time, random, numpy
from naoqi import ALProxy
import vision_definitions

class HeadLoc:
    def __init__(self, left=0, down=0):
        self.left = left
        self.down = down

class Motion:

    # constructor
    def __init__(self, ip='127.0.0.1', port=9559):
        self.motionProxy = ALProxy('ALMotion', ip, port)
        self.postureProxy = ALProxy('ALRobotPosture', ip, port)
        self.camProxy = ALProxy('ALVideoDevice', ip, port)
        self.compassProxy = ALProxy('ALVisualCompass', ip, port)
        self.navi = ALProxy('ALNavigation', ip, port)

        resolution = vision_definitions.kVGA
        colorSpace = vision_definitions.kRGBColorSpace
        self.fps = 15
        self.videoClient = self.camProxy.subscribeCamera('python_client', 0, resolution, colorSpace, self.fps)
        # print self.videoClient
        # in case of camera subscribe overflow
        assert self.videoClient is not None
        # wake up nao
        self.motionProxy.wakeUp()
        # stand init
        self.postureProxy.goToPosture("StandInit", 0.5)
        # move init
        self.motionProxy.moveInit()

        # get the origin
        self.__origin = tuple(self.motionProxy.getRobotPosition(False))
        self.__origin_grid = (0, 0, 0)
        self.__position_grid = list(self.__origin_grid)

    # destructor
    def __del__(self):
        self.camProxy.unsubscribe(self.videoClient)
        self.camProxy.setAllParametersToDefault(0)
        # rest, set all stiffness to 0
        self.motionProxy.rest()

    def xiapao(self, x, y):
        print self.navi.navigateTo(x, y)

    # 瞎 jb 看
    def __look(self):
        ret = dict()

        pitch = self.motionProxy.getAngles('HeadPitch', False)[0]
        yaw = self.motionProxy.getAngles('HeadYaw', False)[0]
        print 'taking picture'
        img = self.__takePicture()
        ret[HeadLoc(left=yaw, down=pitch)] = img

        # 随便转转头
        self.motionProxy.setAngles('HeadPitch', random.uniform(-0.1, 0.1), 0.1)
        self.motionProxy.setAngles('HeadYaw', random.uniform(-0.1, 0.1), 0.1)
        time.sleep(2.0)

        pitch = self.motionProxy.getAngles('HeadPitch', False)[0]
        yaw = self.motionProxy.getAngles('HeadYaw', False)[0]
        print 'taking picture'
        img = self.__takePicture()
        ret[HeadLoc(left=yaw, down=pitch)] = img

        self.motionProxy.setAngles('HeadPitch', 0.0, 0.1)
        self.motionProxy.setAngles('HeadYaw', 0.0, 0.1)

        return ret

    def lookAround(self):
        print 'looking around... '

        ret = dict()
        angle = numpy.pi / 4

        ret[0.0] = self.__look()

        self.turn(angle)

        ret[angle] = self.__look()

        self.turn(- 2 * angle)

        ret[2 * numpy.pi - angle] = self.__look()

        self.turn(angle)

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
        print 'turning radius %f. ' %(rad)

        self.motionProxy.moveTo(0.0, 0.0, rad)
        # blocking
        self.motionProxy.waitUntilMoveIsFinished()
        self.__position_grid[2] = (self.__position_grid[2] + rad) % numpy.pi

    # (x, y, rad)
    def getPosition(self):
        return tuple(self.__position_grid)

    # robot moves to a certain grid
    def walkToPosition(self, new_position):
        # for debug
        print 'walk. '

        # x changes
        if new_position[0] != self.__position_grid[0]:
            if new_position[1] != self.__position_grid[1]:
                raise Exception('wrong target position. ')
            # make sure x changes and y does not
            dist = abs(new_position[0] - self.__position_grid[0]) * 0.05

            if new_position[0] > self.__position_grid[0]:
                if self.__position_grid[2] == 0:
                    # wont turn
                    pass
                elif self.__position_grid[2] == numpy.pi / 2:
                    # right turn pi / 2
                    self.turn(- numpy.pi / 2)
                elif self.__position_grid[2] == numpy.pi:
                    self.turn(- numpy.pi)
                elif self.__position_grid[2] == numpy.pi * 3 / 2:
                    self.turn(numpy.pi / 2)
                else:
                    raise ValueError
            else:
                if self.__position_grid[2] == 0:
                    self.turn(- numpy.pi)
                elif self.__position_grid[2] == numpy.pi / 2:
                    self.turn(numpy.pi / 2)
                elif self.__position_grid[2] == numpy.pi:
                    # wont turn
                    pass
                elif self.__position_grid[2] == numpy.pi * 3 / 2:
                    self.turn(- numpy.pi / 2)
                else:
                    raise ValueError
        # y changes
        else:
            if new_position[1] == self.__position_grid[1]:
                raise Exception('wrong target position. ')
            # make sure x does not change while y does
            dist = abs(new_position[1] - self.__position_grid[1]) * 0.05

            if new_position[1] > self.__position_grid[1]:
                if self.__position_grid[2] == 0:
                    self.turn(numpy.pi / 2)
                elif self.__position_grid[2] == numpy.pi / 2:
                    pass
                elif self.__position_grid[2] == numpy.pi:
                    self.turn(- numpy.pi / 2)
                elif self.__position_grid[2] == numpy.pi * 3 / 2:
                    self.turn(- numpy.pi)
                else:
                    raise ValueError
            else:
                if self.__position_grid[2] == 0:
                    self.turn(- numpy.pi / 2)
                elif self.__position_grid[2] == numpy.pi / 2:
                    self.turn(- numpy.pi)
                elif self.__position_grid[2] == numpy.pi:
                    self.turn(numpy.pi / 2)
                elif self.__position_grid[2] == numpy.pi * 3 / 2:
                    pass
                else:
                    raise ValueError

        #self.motionProxy.moveTo(dist, 0, 0)
        #self.motionProxy.waitUntilMoveIsFinished()
        self.compassProxy.moveTo(dist, 0, 0)
        self.compassProxy.waitUntilTargetReached()
        print 'position: ', tuple(self.motionProxy.getRobotPosition(False))
        self.__position_grid[0] = new_position[0]
        self.__position_grid[1] = new_position[1]
