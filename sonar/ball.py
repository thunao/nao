from PIL import Image,ImageFilter
import cv2
import numpy as np
from gaussianblur import MyGaussianBlur
from time import time

class Ball():
    def __init__(self, list1):
        tm = time()
        width = 640
        height = 480
        matrix = [[0 for col in range(width)] for row in range(height)]
        imgX = [[[0] for col in range(width)] for row in range(height)]
        tv = 0
        hsv = cv2.cvtColor(list1, cv2.COLOR_BGR2HSV)
        hsv = hsv.tolist()
        list1 = list1.tolist()
        for hei in range(0, height):
            for w in range(0, width):
                tv += hsv[hei][w][2] / 255.
        if tv > 210000:
            threshole = 0.9
        elif tv > 150000:
            threshole = 0.75
        elif tv > 120000:
            threshole = 0.7
        elif tv > 90000:
            threshole = 0.5
        elif tv > 60000:
            threshole = 0.4
        else:
            threshole = 0.35
        for hei in range(0, height):
            for w in range(0, width):
                h, s, v = hsv[hei][w]
                b, g, r = list1[hei][w]
                h *= 2
                s /= 255.
                v /= 255.
                if ((h < 30 and h > 0) or (h > 355) or (h == 0 and r > g)) and s > 0.1:
                    if v > threshole:
                        matrix[hei][w] = 1
        for hei in range(1, height-1):
            for w in range(1, width-1):
                count = 0
                if matrix[hei][w] == 1:
                    count = (matrix[hei-1][w-1] + matrix[hei-1][w] + matrix[hei-1][w+1]
                        + matrix[hei][w-1] + matrix[hei][w+1]
                        + matrix[hei+1][w-1] + matrix[hei+1][w] + matrix[hei+1][w+1])
                imgX[hei][w][0] = 255 if count >= 5 else 0
        f = cv2.GaussianBlur(np.array(imgX, np.uint8), (11, 11), 5)
        circles = cv2.HoughCircles(f,cv2.HOUGH_GRADIENT,1,5,param1=100,param2=30,minRadius=10,maxRadius=150)
        count = 0
        self.loc1 = 0
        self.loc2 = 0
        self.ra = 0
        if circles is not None:
            #fimage.save("found.jpg")
            for i in circles[0,:]:
                count += 1
                self.loc1 += i[0]
                self.loc2 += i[1]
                self.ra += i[2]
            self.loc1 = int(self.loc1/count)
            self.loc2 = int(self.loc2/count)
            self.ra = int(self.ra/count)
            #cv2.circle(result,(self.loc1,self.loc2),self.ra,(0,255,0),1)
            #cv2.circle(result,(self.loc1,self.loc2),2,(0,0,255),3)

    def getLoc(self):
        return (self.loc1, self.loc2)

    def getR(self):
        return self.ra

    def max3(self, r, g, b):
        if r > g and r > b:
            return r;
        if g > r and g > b:
            return g;
        else:
            return b;

    def min3(self, r, g, b):
        if r < g and r < b:
            return r;
        if g < r and g < b:
            return g;
        else:
            return b;

if __name__ == "__main__":
    list1 = []
    ball = Ball(list1)
    print ball.getLoc()
    print ball.getR()

