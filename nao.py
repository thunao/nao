#encoding=utf8

from movedetermine import MoveDetermine
from posture import Motion
from ball import Ball
#from xunlu import xunlu 
#from tuxiangshibie import tuxiangshibie

import sys
import getopt

#现在只是伪代码，基本不能跑

ip = ""
threshold = 10

motion = Motion(ip = ip)
move = MoveDetermine()
#kan = tuxiangshibie()
#xunlu = xunlu()

while True:
	vote = {}
	pics = move.lookaround()
	#position = move.position()
	#points = kan.shibie(position, pics)
	for i in pics.keys():
		for j in pics[i].keys():
			find = Ball(pics[i][j].tolist())
			if not find.getR() == 0:

	# 
	for i in points:
		p = move.mymap.maptorobot(i[0], i[1])
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
			move.mymap.addpoint(i[0], i[1], 2)
		elif tmp[0] > threshold:
			move.mymap.addpoint(i[0], i[1], 1)

	target = move.pointtogo()
	#nextstep = xunlu.astar(target)
	#motion.moveto(nextstep)



