from sys import argv
from naomap import NaoMap

def testmap(filename):
    x = -5
    y = -5
    p = list()
    f = open(filename, 'r')
    mymap = NaoMap()
    for line in f.readlines():
        s = line.strip()
        if (len(s) > 5):
            for i in s:
                if not int(i) == 0:
                    mymap.addpoint(x, y, int(i))
                y += 1
            x += 1
            y = -5
        else:
            p.append(int(s))
    return (mymap, (p[0], p[1]), (p[2], p[3]))

