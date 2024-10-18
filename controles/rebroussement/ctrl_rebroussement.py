# coding=utf-8
import math

def rebroussement_ctrl(angle_min, longueur_min, data):
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

# rebroussement 10 0.0
# at :   ((933897.6, 6848706.7, 205.0), (933898.1, 6848708.5, -1000.0), (933897.6, 6848706.7, -1000.0))
# data : (933897.6, 6848706.7, 205.0) (933898.1, 6848708.5, -1000.0) (933897.6, 6848706.7, -1000.0)
# rebroussement 10 5.710593169199171
# at : ((934307.4, 6848677.6, 196.9), (934308.4, 6848677.7, 197.0), (934308.3, 6848677.7, 197.0), (934307.4, 6848677.6, 196.9))
# data : (934307.4, 6848677.6, 196.9) (934308.4, 6848677.7, 197.0) (934308.3, 6848677.7, 197.0)