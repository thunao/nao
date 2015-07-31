#encoding=utf8

import posture
import sys

ip = "127.0.0.1"
filename = "movetest.txt"
if len(sys.argv) >= 2:
	ip = sys.argv[1]
if len(sys.argv) >= 3:
	filename = sys.argv[2]

m = posture.Motion(ip)
f = open(filename, 'r')
line = f.readline()
while len(line) > 0:
	print line
	l = line.strip()
	target = l.split()
	m.walkToPosition((float(target[0]), float(target[1])))
	line = f.readline()

