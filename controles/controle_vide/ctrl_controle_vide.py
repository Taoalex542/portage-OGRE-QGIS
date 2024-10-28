# coding=utf-8
import math

def ctrl_controle_vide(param, data, otherdata):
    controles = []
    for i in range(len(data) - 1):
        for j in range(len(otherdata) - 1):
            point = seg_intersect(data[i],data[i + 1], otherdata[j], otherdata[j + 1])
            if (point != None):
                print(data[i],data[i + 1], otherdata[j], otherdata[j + 1])
                print("main= ",data)
                print("second= ",otherdata)
                controles.append(point)
    return controles

def seg_intersect(p1, p2, p3, p4):
    x1,y1 = p1[0],p1[1]
    x2,y2 = p2[0],p2[1]
    x3,y3 = p3[0],p3[1]
    x4,y4 = p4[0],p4[1]
    denom = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
    if denom == 0: # parallel
        return None
    ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / denom
    if ua < 0 or ua > 1: # out of range
        return None
    ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / denom
    if ub < 0 or ub > 1: # out of range
        return None
    x = x1 + ua * (x2-x1)
    y = y1 + ua * (y2-y1)
    if (p1[0] == p3[0] and p1[1] == p3[1]
        or p4[0] == p2[0] and p4[1] == p2[1]
        or p1[0] == p4[0] and p4[1] == p1[1]
        or p2[0] == p3[0] and p3[1] == p2[1]):
        return None
    return (x,y)

# (934352.3, 6849376.6, -1000.0) (934352.1, 6849364.0, -1000.0) (934346.3, 6849365.9, 199.3) (934357.5, 6849365.5, 199.2)
# main=  ((934352.3, 6849376.6, -1000.0), (934352.1, 6849364.0, -1000.0))
# second=  ((934222.9, 6849378.5, 200.0), (934232.2, 6849375.7, 200.1), (934248.9, 6849371.8, 199.7), (934265.4, 6849369.3, 199.5), (934290.3, 6849368.2, 199.4), (934297.5, 6849367.9, 199.4), (934320.5, 6849367.2, 199.4), (934327.4, 6849367.0, 199.5), (934346.3, 6849365.9, 199.3), (934357.5, 6849365.5, 199.2), (934402.2, 6849362.7, 198.7), (934409.6, 6849322.3, 198.0), (934411.2, 6849313.3, 197.9))