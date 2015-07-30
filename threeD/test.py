import testcase
from sys import argv
import cv2
import core

casename = argv[-1]

try:
    case = testcase.__getattribute__(casename)
except:
    print "casename", casename, "not found"
    quit()

heads = [core.HeadLoc(item["left"], item["down"]) for item in case]
imgs = [cv2.imread("testcase/" + item["filename"]) for item in case]
print core.get3DPoint(heads, imgs)
