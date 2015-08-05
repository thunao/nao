# encoding=utf-8

"""
    超声波避障模块
"""
import sys
import time
import almath            # almath.TO_RAD, 角度转弧度
import argparse            # 参数解析
import threading        # 多线程类
from naoqi import ALProxy
from random import randint, uniform
import numpy, cv2
import vision_definitions
from ball import Ball
import time
import multiprocessing as mul


def checkball(img_list):
    '''
        检测有没有球，若有返回 True
    '''
    ball_checker = Ball(img_list)
    if ball_checker.getR() != 0:
        return True
    else:
        return False

class avoidance(threading.Thread):
    '''
        创建线程类 - avoidance，实现超声波避障避障功能（线程类，可后台运行）
    '''
    def __init__(self, robot_ip, robot_port=9559):
        # 线程类初始化
        threading.Thread.__init__(self)
        # 障碍物标志
        self.obstacle_left = False         # True则左侧有障碍
        self.obstacle_right = False      # True则右侧有障碍
        self.go_back = False
        self.run_flag = False            # 避障运行标志位，为False时表示退出避障循环
        # 障碍物全局变量
        self.check_distance = 0.4    # 设置检测的安全距离
        self.too_close_distance = 0.20
        self.delay_seconds = 0.2    # 设置延时事件, 单位：秒
        self.move_speed = 0.1        # 移动速度, 单位: m/s
        self.turn_angle = 10        # 旋转角度，单位: 角度
        self.wall_angle = 45
        self.test_angle = 75
        self.walk_delay = 0.3
        self.turn_delay = 1.0
        self.test_delay = 3.0
        self.run_time = 600
        self.state = 0
        self.num = 0
        self.test_num = 0
        self.take_picture_num = 0
        self.take_picture_target = 19
        self.test_turn_right = 20
        self.turn_head_delay = 1.0
        self.avoid_hand = 0
        self.image = None
        self.last_left = 100
        self.last_right = 100
        self.delte_distance = 0.1
        # naoqi.ALProxy
        try:
            self.motion = ALProxy("ALMotion", robot_ip, robot_port)
            self.memory = ALProxy("ALMemory", robot_ip, robot_port)
            self.sonar = ALProxy("ALSonar", robot_ip, robot_port)
            self.camera = ALProxy('ALVideoDevice', robot_ip, robot_port)
        except Exception, e:
            print "Could not create proxy by ALProxy in Class avoidance"
            print "Error was: ", e

        resolution = vision_definitions.kVGA
        colorSpace = vision_definitions.kRGBColorSpace
        fps = 15
        try:
            self.video_client = self.camera.subscribeCamera('python_client', 1, resolution, colorSpace, fps)
        except Exception, e:
            print 'Subscribe error'
            print 'Error was: ', e
        # in case of camera subscribe overflow
        assert self.video_client is not None

    def __str2array(self, string, shape):
        '''
            转换图像格式
        '''
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

    def checkball(self, img_list):
        '''
            检测有没有球，若有返回 True
        '''
        # print 'len: ', len(img_list)
        # print 'len: ', len(img_list[0])
        # print type(img_list[0])
        # print img_list[0]
        ball_checker = Ball(img_list)
        if ball_checker.getR() != 0:
            return True
        else:
            return False

    def takepicture(self):
        '''
            拍照拍照搜球
        '''
        assert self.camera is not None
        assert self.video_client is not None
        image = self.camera.getImageRemote(self.video_client)

        assert image is not None

        width = image[0]; height = image[1]
        nchanels = image[2]; array = image[6]

        i = self.__str2array(array, (height, width, nchanels))
        return i

    def getflag(self):
        '''
            返回运行FLAG，为True表示正在运行, 为False表示停止工作;
        '''
        return self.run_flag

    def setflag(self, bools):
        '''
            设置运行FLAG, 从而控制避障功能的on/off;
        '''
        self.run_flag = bools
        return self.run_flag

    def run(self):
        '''
            固定间隔循环检测是否存在障碍，根据障碍物标志决定机器人的行走方向
            通过设置run_flag标志位为False来停止。
        '''
        # 初始时设置运行标志位为True
        self.setflag(True)
        # 机器人行走初始化
        self.motion.wakeUp()
        self.motion.moveInit()
        # 订阅超声波
        self.sonar.subscribe("Class_avoidance")
        while self.run_flag == True:            # 避障标识为True，则持续循环检测
            self.take_picture_num += 1
            if self.take_picture_num == self.take_picture_target:
                self.take_picture_num = 0
                self.motion_stand()
                img_1 = self.takepicture()
                self.motion_head(45)
                img_2 = self.takepicture()
                self.motion_head(- 45)
                img_3 = self.takepicture()
                self.motion_head(0)
                cv2.imwrite("img_1.png", img_1);
                cv2.imwrite("img_2.png", img_2);
                cv2.imwrite("img_3.png", img_3);
                check = mul.Pool(3).map(checkball, [img_1, img_2, img_3])
                # 0. 检测有没有球
                if check[0] or check[1] or check[2]:
                    print '****** HEY BALL! ******'
                    if check[0]:
                        self.image = img_1
                    elif check[1]:
                        self.image = img_2
                    elif check[2]:
                        self.image = img_3
                    break
                else:
                    print 'NO'
                """
                if self.checkball(img_1) or self.checkball(img_2) or self.checkball(img_3):
                    print '****** HEY BALL! ******'
                    break
                else:
                	print 'NO'
                """
            else:
                # 1. 检测障碍物
                self.avoid_check()
                # 2. 根据障碍物标志决定行走方向
                self.avoid_operation()
                # 3. 延时
                time.sleep(self.delay_seconds)
        # 直到run_flag为False才会跳出while循环;
        # 取消订阅超声波
        print 'unsubscribing...'
        self.sonar.unsubscribe("Class_avoidance")
        self.camera.unsubscribe(self.video_client)
        # 机器人复位
        self.motion.stopMove()
        self.motion.rest()
        if self.image is not None:
            cv2.imshow("FFF", self.image)
            cv2.waitKey(0)


    def stop(self):
        self.setflag(False)

    def avoid_check(self):
        '''
            检测超声波数值，设置标志位
        '''
        left_value= self.memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
        right_value= self.memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
        if left_value > self.check_distance:         # 超过安全距离，无障碍
            self.obstacle_left = False
        else:                 
            self.obstacle_left = True                # 小于安全距离，有障碍

        if right_value > self.check_distance:        # 超过安全距离，无障碍
            self.obstacle_right = False
        else:                                        # 小于安全距离，有障碍
            self.obstacle_right = True
        if self.obstacle_right == True or self.obstacle_left:
            if abs(right_value - left_value) < self.delte_distance:
                self.obstacle_left = True
                self.obstacle_right = True
        if left_value < self.too_close_distance and right_value < self.too_close_distance:
            self.go_back = True
        else:
            self.go_back = False
        print "now state is %d, left: %f, right: %f"% (self.state, left_value, right_value)

    def avoid_operation(self):
        #     left        right                operation
        #   ----------------------------------------------
        #     False        False                无障碍物，直走
        #    False        True                右侧障碍，左转
        #    True        False                左侧障碍，右转
        #    True        True                左右障碍，左转
        self.delay_seconds = self.walk_delay

        if self.go_back == True:
            self.motion_back()
            return

        if self.state == 1:
            self.num += 1
            if self.num == self.test_turn_right:
                self.state = 2
                self.motion_turn_right(self.test_angle)
                self.delay_seconds = self.test_delay
                self.num = 0
                return
        elif self.state == 2:
            if self.obstacle_left == True and self.obstacle_right == True:
                self.motion_turn_left(self.test_angle)
                self.delay_seconds = self.test_delay
                self.state = 1
            else:
                #self.motion_turn_left(self.test_angle)
                #self.delay_seconds = self.test_delay
                self.state = 1
                self.test_num = 0
            return
        elif self.state == 3:
            self.test_num += 1
            if self.test_num > self.avoid_hand:
                self.motion_turn_right(self.test_angle)
                self.delay_seconds = self.test_delay
                self.state = 1
                self.test_num = 0
                return
            elif self.obstacle_left == True and self.obstacle_right == True:
                self.motion_turn_right(self.test_angle)
                self.delay_seconds = self.test_delay
                self.state = 1
                self.test_num = 0
                return

        if self.obstacle_left == False:
            if self.obstacle_right == False:
                self.motion_go()
            else:
                self.motion_turn_left(self.turn_angle)
        else:
            if self.obstacle_right == False:
                self.motion_turn_right(self.turn_angle)
            else:
                self.state = 1
                self.num = 0
                self.delay_seconds = self.turn_delay
                self.motion_turn_left(self.wall_angle)
                return

    def motion_stand(self):
        self.motion.stopMove()

    def motion_go(self):
        self.motion.move(self.move_speed, 0, 0)

    def motion_back(self):
        self.motion.move(-1.0 * self.move_speed, 0, 0)

    def motion_turn_left(self, turn_angle):
        if not turn_angle < self.wall_angle:
            self.motion_back()
            time.sleep(self.walk_delay*2)
        self.motion.moveTo(0, 0, turn_angle * almath.TO_RAD)

    def motion_turn_right(self, turn_angle):
        if not turn_angle < self.wall_angle:
            self.motion_back()
            time.sleep(self.walk_delay*2)
        self.motion.moveTo(0, 0, -1.0 * turn_angle * almath.TO_RAD)

    def motion_head(self, angle):
        self.motion.setAngles('HeadYaw', angle * almath.TO_RAD, 0.3)
        time.sleep(self.turn_head_delay)

def main(robot_IP, robot_PORT=9559):
    # ----------> avoidance <----------
    avoid = avoidance(robot_IP, robot_PORT)
    try:
        avoid.start()                    # start()只能执行一次, 会开新线程运行;
        # run()可以多次执行, 但是会在本线程运行;
        # start()开新线程, 非阻塞, 因此这里延时一段时间以执行避障;
        time.sleep(avoid.run_time)
#        avoid.setflag(False)             # 方法1: 通过设置标志位为False来停止
        avoid.stop()                    # 方法2: 通过调用stop()函数停止该线程类，其内部也是设置标志位.

        # 想要再次开启避障，需要再新建一个类对象
        # 由于线程类只能调用start开启新线程一次，因此要多次使用超声波避障，需要实例化多个类；
        # avoid2 = avoidance(robot_IP, robot_PORT)
        # avoid2.start()
        # time.sleep(10)
        # avoid2.stop()
    except KeyboardInterrupt:
        # 中断程序
        avoid.stop()
        # avoid2.stop()
        print "Interrupted by user, shutting down"
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.2.100", help="Robot ip address")
    parser.add_argument("--port", type=int, default=9559, help="Robot port number")
    args = parser.parse_args()
    # ----------> 执行main函数 <----------
    main(args.ip, args.port)
