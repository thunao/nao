#encoding=utf8

import posture

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
	l = line.strip()
	target = l.split()
	m.walkToPosition((target[0], target[1]))

