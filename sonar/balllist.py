from PIL import Image,ImageFilter
import cv2
import numpy as np
from gaussianblur import MyGaussianBlur
from ball import Ball

list1 = []
f = Image.open("L4.jpg")
width = f.size[0]
height = f.size[1]
matrix = [[0 for col in range(width)] for row in range(height)]

for hei in range(0, height):
    for w in range(0, width):
        pixel = f.getpixel((w, hei))
        matrix[hei][w]=[pixel[2], pixel[1], pixel[0]]

b = Ball(np.array(matrix, np.uint8))
print b.getLoc(), b.getR()

