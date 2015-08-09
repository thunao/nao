import sys
from testmap import testmap

xmax=-100
xmin=100
ymax=-100
ymin=100
start = None
end = None

def calc_G(node1, node2): # G值求取
    x1 = abs(node1.x - node2.x)
    y1 = abs(node1.y - node2.y)
    x2 = 0
    y2 = 0
    if node1.father is not None:
        x2 = abs(node1.father.x - node2.x)
        y2 = abs(node1.father.y - node2.y)
    if (x1 == 1 and y1 == 0) or (x1 == 0 and y1 == 1): # 改进策略，使得弯道尽可能少
        if x2 == 0 or y2 == 0:
            return 1
        else:
            return 1.1
    return 0

def calc_H(cur, end): # H值求取，使用曼哈顿距离
    return abs(end.x-cur.x) + abs(end.y-cur.y)

class Node: # 点，即每一个网格
    def __init__(this, father, x, y):
        if x < xmin or x > xmax or y < ymin or y > ymax:
            raise Exception("")
        this.father = father
        this.x = x
        this.y = y
        if father != None:
            G2father = calc_G(father, this)
            this.G = G2father + father.G
            this.H = calc_H(this, end)
            this.F = this.G + this.H
        else:
            this.G = 0
            this.H = 0
            this.F = 0
    def reset_father(this, father, new_G):
        if father != None:
            this.G = new_G
            this.F = this.G + this.H
        this.father = father

class astar: # 寻路算法
    def __init__(this, m, s, e):
        global start,end
        this.m = m.Map
        this.open_list={} # open表
        this.close_list={} # close表
        this.preset_map()
        start = Node(None, s[0], s[1]) # 起点
        end = Node(None, e[0], e[1]) # 终点

    def min_F_node(this):
        _min = 99999999999999999
        _k = (start.x, start.y)
        for k, v in this.open_list.items():
            if _min > v.F:
                _min = v.F
                _k = k
        return this.open_list[_k]

    def addAdjacentIntoOpen(this, node):
        this.open_list.pop((node.x, node.y))
        this.close_list[(node.x, node.y)] = node
        _adjacent = []
        try:
            _adjacent.append(Node(node, node.x, node.y-1))
        except Exception,e:
            pass
        try:
            _adjacent.append(Node(node, node.x, node.y+1))
        except Exception,e:
            pass
        try:
            _adjacent.append(Node(node, node.x-1, node.y))
        except Exception,e:
            pass
        try:
            _adjacent.append(Node(node, node.x+1, node.y))
        except Exception,e:
            pass
        for a in _adjacent:
            if (a.x, a.y) == (end.x, end.y):
                new_G = calc_G(a, node) + node.G
                end.reset_father(node, new_G)
                return True
            if (a.x, a.y) in this.close_list:
                continue
            if (a.x, a.y) not in this.open_list:
                this.open_list[(a.x, a.y)] = a
            if (a.x, a.y) in this.open_list:
                exist_node = this.open_list[(a.x, a.y)]
                new_G = calc_G(node, a) + node.G
                if new_G < exist_node.G:
                    exist_node.reset_father(node, new_G)
        return False

    def find_the_path(this, start, end):
        this.open_list[(start.x, start.y)] = start
        the_node = start
        while not this.addAdjacentIntoOpen(the_node):
            the_node = this.min_F_node()
        return True

    def mark_path(this, node):
        this.path1 = []
        this.path1.append(end)
        while node.father is not None:
            print node.x, node.y
            this.path1.append(node)
            node = node.father
        if len(this.path1) > 1:
            tm = this.path1.pop()
        else:
            return (end.x, end.y)
        if tm.x - start.x == 0:
            while len(this.path1):
                tm1 = this.path1.pop()
                if tm1.x - start.x != 0: #?
                    return (tm1.x + 1, tm1.y)
            return (end.x, end.y)
        elif tm.y - start.y == 0:
            while len(this.path1):
                tm1 = this.path1.pop()
                if tm1.y - start.y != 0: #?
                    return (tm1.x, tm1.y + 1)
            return (end.x, end.y)

    def preset_map(this):
        global xmax,xmin,ymax,ymin
        for i in this.m.keys():
            if i[0] > xmax:
                xmax = i[0]
            if i[0] < xmin:
                xmin = i[0]
            if i[1] > ymax:
                ymax = i[1]
            if i[1] < ymin:
                ymin = i[1]
        for x in range(xmin, xmax+1):
            for y in range(ymin, ymax+1):
                if not this.m.has_key((x, y)):
                    block_node = Node(None, x, y)
                    this.close_list[(block_node.x, block_node.y)] = block_node
                elif this.m[(x, y)] == 2:
                    for ro in range(-3, 4):
                        for co in range(-3, 4):
                            if x+ro >= xmin and x+ro <= xmax and y + co >=ymin and y+co<=ymax:
                                block_node = Node(None, x+ro, y+co)
                                this.close_list[(block_node.x, block_node.y)] = block_node
                elif this.m[(x, y)] == 0:
                    block_node = Node(None, x, y)
                    this.close_list[(block_node.x, block_node.y)] = block_node

if __name__=='__main__':
    testm = testmap("testmap2.txt")
    t = astar(testm[0], testm[1], testm[2])
    if t.find_the_path(start, end):
        print t.mark_path(end.father)
