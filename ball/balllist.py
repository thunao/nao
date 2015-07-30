from PIL import Image,ImageFilter
import cv2
import numpy as np
from gaussianblur import MyGaussianBlur
from ball import Ball

list1 = []
f = Image.open("bottom.jpg")
width = f.size[0]
height = f.size[1]
for hei in range(0, height):
    for w in range(0, width):
        pixel = f.getpixel((w, hei))
        list1.append(pixel)

b = Ball(list1)
print b.getLoc(), b.getR()

