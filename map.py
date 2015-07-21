# encoding=utf-8

from math import cos

class NaoMap:

	def __init__(self, x0, y0, size):
		self.unknown = 0
		self.known = 1
		self.wall = 2
		self.Map = {(0, 0) : self.known}
		self.x0 = x0
		self.y0 = y0
		self.myx = 0
		self.myy = 0
		self.tuward = (0, 1)

	def robottomap(x, y):
		return ((x - self.x0) / self.size, (y - self.y0) / self.size)

	def maptorobot(x, y):
		return ((x + self.x0 + 0.5) * self.size, (y + self.y0 + 0.5) * self.size)

	def moveto(x, y):
		self.myx = x
		self.myy = y

	def turnto(x, y):
		self.toward = (x, y)
