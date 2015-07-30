# encoding=utf-8

from math import cos

class NaoMap:

	def __init__(self, x0 = 0, y0 = 0, size = 5):
		self.unknown = 0
		self.known = 1
		self.wall = 2
		self.Map = {(0, 0) : self.known}
		for i in range(-1, 2):
			for j in range (-1, 2):
				if (i, j) not in self.Map.keys():
					self.Map[(i, j)] = self.unknown
		self.edge = {(0, 0): 0}
		self.x0 = x0
		self.y0 = y0
		self.myx = 0
		self.myy = 0
		self.toward = (0, 1)

	def robottomap(self, x, y):
		return ((x - self.x0) / self.size, (y - self.y0) / self.size)

	def maptorobot(x, y):
		return ((x + self.x0 + 0.5) * self.size, (y + self.y0 + 0.5) * self.size)

	def moveto(self, x, y):
		self.myx = x
		self.myy = y

	def turnto(self, x, y):
		self.toward = (x, y)

	def addpoint(self, x, y, type):
		self.Map[(x, y)] = type
		flag = False
		if type == self.known:
			for i in range(-1, 2):
				for j in range(-1, 2):
					if (x+i, y+j) not in self.Map.keys():
						self.Map[(x+i, y+j)] = self.unknown
						flag = True
					elif (x+i, y+j) in self.edge.keys():
						if not self._isedge(x+i, y+j):
							self.edge.pop((x+i, y+j))
		if flag:
			self.edge[(x, y)] = 0

	def _isedge(self, x, y):
		for i in range(-1, 2):
			for j in range(-1, 2):
				if self.Map[(x+i, y+j)] == self.unknown:
					return True
		return False

