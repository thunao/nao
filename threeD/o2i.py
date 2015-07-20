# import numpy as np

def o2i(point):
	assert len(point) == 3
	cx = 320; cy = 240
	k = float(550) / point[0]
	return (cx - k * point[1], cy - k * point[2])

if __name__ == '__main__':
	print o2i((100, 10, 10))