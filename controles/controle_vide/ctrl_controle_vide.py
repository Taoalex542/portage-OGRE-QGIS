# coding=utf-8

# récupère les points pour la gestion des trous dans QGIS pour éviter les segments non existants entre les différentes géométries
def get_holes_in_shape(data, len_data):
    hist = []
    start_points = []
    for i in range (len_data):
        if data[i] not in hist:
            hist.append(data[i])
        else:
            start_points.append(data[i])
    return start_points

def ctrl_controle_vide(param, data, otherdata):
    controles = []
    start_points = get_holes_in_shape(otherdata, len(otherdata) - 1)
    for i in range(len(data) - 1):
        for j in range(len(otherdata) - 1):
            point = seg_intersect(data[i],data[i + 1], otherdata[j], otherdata[j + 1])
            if (point != None and point not in controles and data[i] not in start_points and data[i + 1] not in start_points and otherdata[j] not in start_points and otherdata[j + 1] not in start_points):
                controles.append(point)
    return controles

# calcul mathématique pour vérifier si une intersection existe entre deux segments 
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
