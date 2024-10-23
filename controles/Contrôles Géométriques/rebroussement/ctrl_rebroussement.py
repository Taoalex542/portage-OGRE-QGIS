# coding=utf-8
import math

def ctrl_rebroussement(angle_min, longueur_min, data):
    if (len(data) < 3):
        return []
    previous = None
    middle = None
    rebroussement = []
    for points in data:
        if previous != None and middle != None and points != middle and points != previous:
            angle = math.degrees(math.atan2(previous[1]-middle[1], previous[0]-middle[0]) - math.atan2(points[1]-middle[1], points[0]-middle[0]))
            if angle < 0:
                angle += 360
            if angle_min > angle:
                rebroussement.append(middle)
        previous = middle
        middle = points
    return rebroussement
