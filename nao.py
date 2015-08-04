#encoding=utf8

from naomap import NaoMap
from movedetermine import MoveDetermine
from posture import Motion, HeadLoc
from ball import Ball
from path.astar import astar
from stereo_calibration.detect_obstacle import detect_obstacle

import sys
import getopt
from math import sin, cos, pi
import pickle

def __isnear(p1, p2, t = 5):
	if abs(p1[0]-p2[0]) + abs(p1[1]-p2[1]) > t:
		return True
	return False

#现在只是伪代码，基本不能跑

ip = "127.0.0.1"
if len(sys.argv) == 2:
	ip = sys.argv[1]
threshold = 10
headheight = 44.7
topcarmeraheight = 6.364
topcarmeadown = 1.2 /180 * pi

motion = Motion(ip = ip)
movedetermine = MoveDetermine()
target = (0, 0)

while True:
	vote = {}
	points = list()
	pics = motion.lookAround()
	(x, y, toward) = motion.getPosition()
	(realx, realy) = movedetermine.mymap.maptorobot(x, y)
	myposition = (x, y)
	movedetermine.mymap.moveto(x, y)
	movedetermine.mymap.turnto(sin(toward), cos(toward))

	with open('pics.txt', "w") as f:
		pickle.dump(pics, f)

	print "照完相，开始看图"
	#points = kan.shibie(position, pics)
	for i in pics:
		p = pics[i].keys()
		print i
		print p[0].left, ' ', p[0].down
		#find = Ball(pics[i][j].tolist())
		l = detect_obstacle(pics[i][p[0]], pics[i][p[1]], (realx, realy, headheight + topcarmeraheight), \
							(i + p[0].left, topcarmeadown + p[0].down), -1) 
		points.extend(l)
	print "size of pointlist is ", len(points)

	with open('points.txt', "w") as ff:
		pickle.dump(points, ff)

	print "看完图了，开始标点"
	jishuqi = 0
	for i in points:
		p = movedetermine.mymap.robottomap(i[0], i[1])
		tmp = [0, 0]
		if p in vote:
			tmp = vote[p]
		if i[2] > 5:
			tmp[1] += 1
		else:
			tmp[0] += 1
		vote[p] = tmp
		jishuqi += 1
		if jishuqi % 10000 == 0:
			print jishuqi

	with open("vote.txt", "w") as fff:
		pickle.dump(vote, fff)

	print "标完点了，决定障碍物"
	for i in vote:
		tmp = vote[i]
		if tmp[1] > threshold:
			movedetermine.mymap.addpoint(i[0], i[1], 2)
		elif tmp[0] > threshold:
			movedetermine.mymap.addpoint(i[0], i[1], 1)

	with open("mymap.txt", "w") as ffff:
		pickle.dump(movedetermine.mymap, ffff)

	if __isnear(target, myposition):
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

