#encoding=utf8

from movedetermine import MoveDetermine
from posture import Motion
from ball import Ball
from path.astar import astar
from stereo_calibration.detect_obstacle import detect_obstacle

import sys
import getopt
from math

#现在只是伪代码，基本不能跑

ip = ""
threshold = 10

motion = Motion(ip = ip)
movedetermine = MoveDetermine()

while True:
	vote = {}
	points = list()
	pics = motion.lookaround()
	(x, y, toward) = motion.getposition()
	myposition = (x, y)
	movedetermine.mymap.moveto(x, y)
	movedetermine.mymap.turnto(sin(toward), cos(toward))

	#points = kan.shibie(position, pics)
	for i in pics.keys():
		findflag = False
		 pics[i].keys():
			find = Ball(pics[i][j].tolist())
			if not find.getR() == 0:

	# 
	for i in points:
		p = movedetermine.mymap.maptorobot(i[0], i[1])
		tmp = (0, 0)
		if i in vote.keys():
			tmp = vote[p]
		if i[2] > 5:
			tmp[1] += 1
		else:
			tmp[0] += 1
		vote[p] = tmp

	for i in vote.keys():
		tmp = vote[i]
		if tmp[1] > threshold:
			movedetermine.mymap.addpoint(i[0], i[1], 2)
		elif tmp[0] > threshold:
			movedetermine.mymap.addpoint(i[0], i[1], 1)

	if not _isnear(target, position):
		target = move.pointtogo()
	pathfind = astar(move.mymap.Map, myposition, target)
	nextstep = pathfind.get_result
	if nextstep == myposition:
		print "pathfind.get_result Error! myposition is ", myposition, ", target is "\
			, target
		break

	try:
		motion.walkToPosition(nextstep)
	except:
		print "motion.walkToPosition Error! nextstep is ", nextstep
		break

def _isnear(p1, p2, t = 5):
	if math.abs(p1[0]-p2[0]) + math.abs(p1[1]-p2[1]) > t:
		return True
	return False

