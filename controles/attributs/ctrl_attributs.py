# coding=utf-8

def ctrl_attributs(data, otherdata, id, second_id, pos, second_pos):
    controles = []
    if data == otherdata and id != second_id:
        if (pos not in controles and second_pos not in controles):
            controles.append(pos)
            controles.append(second_pos)
    return controles