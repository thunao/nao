from sys import argv
from naomap import NaoMap

def testmap(filename):
    x = -5
    y = -5
    p = list()
    f = open(filename, 'r')
    mymap = NaoMap()
    for line in f.readlines():
        # s = line.readline()
        s = line.strip()
        print s
        if (len(s) > 5):
            for i in s:
                mymap.addpoint(x, y, int(i))
                y += 1
            x += 1
        else:
            p.append(int(s))
    return (mymap, (p[0], p[1]), (p[2], p[3]))

filename = "test.txt"
if (len(argv) >= 2):
    filename = argv[1]
(mymap, start, end) = testmap(filename)
