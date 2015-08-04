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
		self.minx = 0
		self.maxx = 0
		self.miny = 0
		self.maxy = 0
		self.toward = (0, 1)
		self.size = size

	def robottomap(self, x, y):
		return ((int(x) - self.x0) / self.size, (int(y) - self.y0) / self.size)

	def maptorobot(self, x, y):
		return ((x + self.x0 + 0.5) * self.size, (y + self.y0 + 0.5) * self.size)

	def moveto(self, x, y):
		self.myx = x
		self.myy = y

	def turnto(self, x, y):
		self.toward = (x, y)

	def addpoint(self, x, y, type):
		if x > self.maxx:
			self.maxx = x
		if x < self.minx:
			self.minx = x
		if y > self.maxy:
			self.maxy = y
		if y < self.miny:
			self.miny = y
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

	def printmap(self):
		for j in range(self.miny, self.maxy+1):
			for i in range(self.minx, self.maxx+1):
				if i == self.myx and j == self.myy:
					print "*", 
				elif (i, j) in self.Map:
					print self.Map[(i, j)],
				else:
					print ' ',
			print " "
