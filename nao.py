#encoding=utf8

from movedetermine import MoveDetermine
from posture import Motion, HeadLoc
from ball import Ball
from path.astar import astar
from stereo_calibration.detect_obstacle import detect_obstacle

import sys
import getopt
import math

#现在只是伪代码，基本不能跑

ip = "127.0.0.1"
if len(sys.argv) == 2:
	ip = sys.argv[1]
threshold = 10
headheight = 44.7
topcarmeraheight = 6.364
topcarmeadown = 1.2 /180 * math.pi

motion = Motion(ip = ip)
movedetermine = MoveDetermine()

while True:
	vote = {}
	points = list()
	pics = motion.lookAround()
	(x, y, toward) = motion.getposition()
	(realx, realy) = movedetermine.mymap.maptorobot(x, y)
	myposition = (x, y)
	movedetermine.mymap.moveto(x, y)
	movedetermine.mymap.turnto(sin(toward), cos(toward))

	#points = kan.shibie(position, pics)
	for i in pics.keys():
		p = pics[i].keys():
		#find = Ball(pics[i][j].tolist())
		l = detect_obstacle(pics[i][p[0]], pics[i][p[1]], (realx, realy, headheight + topcarmeraheight), \
							(i + p.left, topcarmeadown + p.down), 10) 
		points.expend(l)

	for i in points:
		p = movedetermine.mymap.robottomap(i[0], i[1])
		tmp = (0, 0)
		if p in vote.keys():
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

