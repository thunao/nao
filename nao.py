#encoding=utf8

from naomap import NaoMap
from movedetermine import MoveDetermine
from posture import Motion, HeadLoc
from ball import Ball
from path.astar import astar
from stereo_calibration.detect_obstacle import detect_obstacle, display2D

import sys
import getopt
from math import sin, cos, pi
import pickle
import json

def __isnear(p1, p2, t = 5):
	if abs(p1[0]-p2[0]) + abs(p1[1]-p2[1]) > t:
		return True
	return False

#现在只是伪代码，基本不能跑

ip = "127.0.0.1"
test = False
if len(sys.argv) >= 2:
	ip = sys.argv[1]
if len(sys.argv) >= 3:
	test = True
wallthreshold = 500
floorthreshold = 50
headheight = 44.7
topcarmeraheight = 6.364
topcarmeadown = 1.2 /180 * pi

motion = Motion(ip = ip)
movedetermine = MoveDetermine()
target = (0, 0)

while True:
	vote = {}
	points = list()
	if test:
		with open('pics.txt', "r") as ff:
			pics = pickle.load(ff)
	else:
		pics = motion.lookAround()
	(x, y, toward) = motion.getPosition()
	(realx, realy) = movedetermine.mymap.maptorobot(x, y)
	myposition = (x, y)
	movedetermine.mymap.moveto(x, y)
	movedetermine.mymap.turnto(sin(toward), cos(toward))

	if not test:
		with open('pics.txt', "w") as f:
			pickle.dump(pics, f)

	print "taken pics"
	#points = kan.shibie(position, pics)
	for i in pics:
		p = pics[i].keys()
		print i
		print p[0].left, ' ', p[0].down
		#find = Ball(pics[i][j].tolist())
		l = detect_obstacle(pics[i][p[0]], pics[i][p[1]], (realx, realy, headheight + topcarmeraheight), \
							(i + p[0].left, topcarmeadown + p[0].down), -100) 
		display2D(l)
		points.extend(l)
	print "size of pointlist is ", len(points)

	#if not test:
	#	with open('points.txt', "w") as ff:
	#		pickle.dump(points, ff)

	print "add point"
	jishuqi = 0
	for i in points:
		p = movedetermine.mymap.robottomap(i[0], i[1])
		tmp = [0, 0]
		if p in vote:
			tmp = vote[p]
		if i[2] > 50:
			tmp[1] += 1
		else:
			tmp[0] += 1
		vote[p] = tmp
		jishuqi += 1
		if jishuqi % 10000 == 0:
			print jishuqi

	#with open("vote.txt", "w") as fff:
	#	json.dump(vote, fff)


	print "vote wall"
	with open("vote.txt", "w") as fff:
		for i in range(-100, 100):
			for j in range(-100, 100):
				if (i, j) in vote:
					fff.write("(%d, %d) [%d, %d]\n" % (i, j, vote[(i, j)][0], vote[(i, j)][1])) 
	for i in vote:
		tmp = vote[i]
		if tmp[1] > wallthreshold:
			movedetermine.mymap.addpoint(i[0], i[1], 2)
		elif tmp[0] > floorthreshold:
			movedetermine.mymap.addpoint(i[0], i[1], 1)

	movedetermine.mymap.printmap()
	#print movedetermine.mymap.Map
	#with open("mymap.txt", "w") as ffff:
	#	json.dump(movedetermine.mymap.Map, ffff)

	if __isnear(target, myposition):
		print "near!"
		target = move.pointtogo()
	pathfind = astar(movedetermine.mymap, myposition, target)
	nextstep = pathfind.get_result()
	if nextstep == myposition:
		print "pathfind.get_result Error! myposition is ", myposition, ", target is "\
			, target
		break

	try:
		motion.walkToPosition(nextstep)
	except:
		print "motion.walkToPosition Error! nextstep is ", nextstep
		break

