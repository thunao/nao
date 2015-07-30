from PIL import Image,ImageFilter
import cv2
import numpy as np
from gaussianblur import MyGaussianBlur

class Ball():
    def __init__(self, list1):
        f = Image.new('RGB', (640, 480))
        width = f.size[0]
        height = f.size[1]
        for hei in range(0, height):
            for w in range(0, width):
                f.putpixel((w, hei), list1[hei * 640 + w])
        matrix = [[0 for col in range(width)] for row in range(height)]
        res = [[0 for col in range(width)] for row in range(height)]
        tv = 0
        for hei in range(0, height):
            for w in range(0, width):
                pixel = f.getpixel((w, hei))
                r = 1.0*pixel[0]/255
                g = 1.0*pixel[1]/255
                b = 1.0*pixel[2]/255
                tv += self.max3(r, g, b)
        for hei in range(0, height):
            for w in range(0, width):
                pixel = f.getpixel((w, hei))
                r = 1.0*pixel[0]/255
                g = 1.0*pixel[1]/255
                b = 1.0*pixel[2]/255
                ma = self.max3(r, g, b)
                mi = self.min3(r, g, b)
                if ma == mi:
                    h = 0
                elif ma == r and g >= b:
                    h = 60*(g-b)/(ma-mi)
                elif ma == r and g < b:
                    h = 60*(g-b)/(ma-mi)+360
                elif ma == g:
                    h = 60*(b-r)/(ma-mi)+120
                elif ma == b:
                    h = 60*(r-g)/(ma-mi)+240
                else:
                    h = 0
                v = ma
                if ma == 0:
                    s = 0
                else:
                    s = 1 - 1.0*mi/ma
                if ((h < 30 and h > 0) or (h > 355) or (h == 0 and r > g)) and s > 0.1:
                    if tv > 210000:
                        if v > 0.9:
                            matrix[hei][w] = 1
                    elif tv > 180000:
                        if v > 0.8:
                            matrix[hei][w] = 1
                    elif tv > 120000:
                        if v > 0.7:
                            matrix[hei][w] = 1
                    elif tv > 90000:
                        if v > 0.5:
                            matrix[hei][w] = 1
                    elif tv > 60000:
                        if v > 0.4:
                            matrix[hei][w] = 1
                    else:
                        if v > 0.35:
                            matrix[hei][w] = 1
        for hei in range(1, height-1):
            for w in range(1, width-1):
                count = 0
                if matrix[hei][w] == 1:
                    if matrix[hei-1][w] == 1:
                        count += 1
                    if matrix[hei-1][w-1] == 1:
                        count += 1
                    if matrix[hei-1][w+1] == 1:
                        count += 1
                    if matrix[hei][w-1] == 1:
                        count += 1
                    if matrix[hei][w+1] == 1:
                        count += 1
                    if matrix[hei+1][w] == 1:
                        count += 1
                    if matrix[hei+1][w-1] == 1:
                        count += 1
                    if matrix[hei+1][w+1] == 1:
                        count += 1
                if count >= 5:
                    res[hei][w] = 1
                    f.putpixel((w, hei), (255, 255, 255))
                else:
                    f.putpixel((w, hei), (0, 0, 0))
        f = f.filter(MyGaussianBlur(radius=10))
        fr,fg,fb = f.split()
        img = np.array(fr)
        result = img.copy()
        circles = cv2.HoughCircles(img,cv2.cv.CV_HOUGH_GRADIENT,1,5,param1=100,param2=30,minRadius=10,maxRadius=150)
        count = 0
        self.loc1 = 0
        self.loc2 = 0
        self.ra = 0
        if circles is not None:
            for i in circles[0,:]:
                count += 1
                self.loc1 += i[0]
                self.loc2 += i[1]
                self.ra += i[2]
            self.loc1 = int(self.loc1/count)
            self.loc2 = int(self.loc2/count)
            self.ra = int(self.ra/count)
            cv2.circle(result,(self.loc1,self.loc2),self.ra,(0,255,0),1)
            cv2.circle(result,(self.loc1,self.loc2),2,(0,0,255),3)

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

