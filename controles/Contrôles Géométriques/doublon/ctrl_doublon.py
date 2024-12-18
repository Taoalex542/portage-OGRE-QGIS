# coding=utf-8
import math
import numpy as np
def ctrl_doublon(param, data, otherdata):
    controles = []
    for i in range(len(data) - 1):
        for j in range(len(otherdata) - 1):
            point = seg_intersect(data[i],data[i + 1], otherdata[j], otherdata[j + 1])
            if (point != None and point not in controles):
                controles.append(point)
    return controles


# calcul mathématique pour vérifier si une intersection existe entre deux segments 
def seg_intersect(p1, p2, p3, p4):
    x1,y1 = p1[0],p1[1]
    x2,y2 = p2[0],p2[1]
    x3,y3 = p3[0],p3[1]
    x4,y4 = p4[0],p4[1]
    s1degree = math.atan2(y1 - y2, x1 - x2) 
    s1degree = np.degrees(s1degree)
    s2degree = math.atan2(y3 - y4, x3 - x4) 
    s2degree = np.degrees(s2degree)
    if (round(s1degree, 2) == round(s2degree, 2)): # parallel
        if ((x2 >= x4 and x2 <= x3) or (x2 >= x3 and x2 <= x4) or 
            (x1 >= x4 and x1 <= x3) or (x1 >= x3 and x1 <= x4) or
            (x4 >= x2 and x4 <= x1) or (x4 >= x1 and x4 <= x2) or 
            (x3 >= x2 and x3 <= x1) or (x3 >= x1 and x3 <= x2)):
            
            if ((x1 >= x3 and x1 <= x4) and (x2 >= x3 and x2 <= x4) or
                (x2 >= x4 and x2 <= x3) and (x1 >= x4 and x1 <= x3)):
                if x1 > x2:
                    x = (x1 - x2) / 2 + x2
                else:
                    x = (x2 - x1) / 2 + x1
                    
            if ((x3 >= x1 and x3 <= x2) or (x3 >= x2 and x3 <= x1) and
                (x4 >= x2 and x4 <= x1) or (x4 >= x1 and x4 <= x2)):
                if x3 > x4:
                    x = (x3 - x4) / 2 + x4
                else:
                    x = (x4 - x3) / 2 + x3
                
        if ((y2 >= y4 and y2 <= y3) or (y2 >= y3 and y2 <= y4) or 
            (y1 >= y4 and y1 <= y3) or (y1 >= y3 and y1 <= y4) or
            (y4 >= y2 and y4 <= y1) or (y4 >= y1 and y4 <= y2) or 
            (y3 >= y2 and y3 <= y1) or (y3 >= y1 and y3 <= y2)):
            
            if ((y1 >= y3 and y1 <= y4) and (y2 >= y3 and y2 <= y4) or
                (y2 >= y4 and y2 <= y3) and (y1 >= y4 and y1 <= y3)):
                if y1 > y2:
                    y = (y1 - y2) / 2 + y2
                else:
                    y = (y2 - y1) / 2 + y1
                    
            if ((y3 >= y1 and y3 <= y2) or (y3 >= y2 and y3 <= y1) and
                (y4 >= y2 and y4 <= y1) or (y4 >= y1 and y4 <= y2)):
                if y3 > y4:
                    y = (y3 - y4) / 2 + y4
                else:
                    y = (y4 - y3) / 2 + y3
        return (x,y)
    return None
