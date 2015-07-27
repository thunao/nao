# encoding=utf-8

from naomap import NaoMap
from math import pi, acos, asin, hypot

def _sign(x):
	if x == 0:
		return 0
	elif x < 0:
		return -1
	else:
		return 1

class MoveDetermine:

 	def __init__(self, x0, y0, size):
		self.mymap = NaoMap(x0, y0, size)

	def _theta(self, x1, y1, x2, y2):
		if hypot(x1, y1) == 0 or hypot(x2, y2) == 0:
			return 2 * pi
		cos1 = x1 / hypot(x1, y1)
		cos2 = x2 / hypot(x2, y2)
		theta1 = acos(cos1)
		theta2 = acos(cos2)
		if y1 < 0:
			theta1 += pi
		if y2 < 0:
			theta2 += pi
		theta = theta2 - theta1
		if theta < 0:
			theta += 2 * pi
		return theta

	def pointtogo(self):
		mintheta = 2 * pi
		x = self.mymap.myx
		y = self.mymap.myy
		rightx = self.mymap.toward[y]
		righty = -self.mymap.toward[x]
		for i in self.mymap.edge.keys():
			theta = self._theta(rightx, righty, i[0]-x, i[1]-y)
			if theta < mintheta:
				mintheta = theta
				x = i[0]
				y = i[1]
		flag = True
		while flag:
			flag = False
			for i in range(-3, 4):
				for j in range(-3, 4):
					if (x+i, y+j) in self.mymap.Map.keys():
						if self.mymap.Map[(x+i, y+j)] == self.mymap.wall:
							flag = True
							x -= _sign(i)*3-i
							y -= _sign(j)*3-j
							break
				if flag:
					break
		return (x, y)
