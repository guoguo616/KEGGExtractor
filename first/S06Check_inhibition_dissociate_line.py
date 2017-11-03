import numpy as np
import cv2
import sys
from Tool import tool
import math


def ang(lineA, lineB):
    vA = [(lineA[0]-lineA[2]), (lineA[1]-lineA[3])]
    vB = [(lineB[0]-lineB[2]), (lineB[1]-lineB[3])]
    vA_angle=math.atan2(vA[1],vA[0])*180/math.pi
    vB_angle=math.atan2(vB[1],vB[0])*180/math.pi

    if vA_angle==180.0:vA_angle=0.0
    if vB_angle==180.0:vB_angle=0.0


    return abs(vA_angle-vB_angle)


def LocateAtTheEndOfLight(line1,pa):
    if (abs(line1[0]-pa[0])<2 and abs(line1[1]-pa[1])<2) or (abs(line1[2]-pa[0])<2 and abs(line1[3]-pa[1])<2):
        return True
    else:
        return False




img=cv2.imread('./source/'+sys.argv[1])

all_Line=[]

segment_list=[]
with open('./point_info/e_cross_point.txt') as f:
    for l in f:
        ll = l.strip().split(',')
        x1 = int(ll[0])
        y1 = int(ll[1])
        x2 = int(ll[2])
        y2 = int(ll[3])

        all_Line.append((x1,y1,x2,y2))

        d=np.sqrt(np.power(x1 - x2, 2) + np.power(y1 - y2, 2))
        if d>5 and d<20:
            segment_list.append((x1,y1,x2,y2))
            # cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

tool=tool()
for k,al in enumerate(all_Line):

    isShortLine=[]
    for sl in segment_list:

        x1 = int(sl[0])
        y1 = int(sl[1])
        x2 = int(sl[2])
        y2 = int(sl[3])
        pa, pb, mindist = tool.closestDistanceBetweenLines(al, sl, clampAll=True)
        if  mindist<=0 and pa<>None and pb<>None and ang>30:
            if LocateAtTheEndOfLight(al,pa):
                # cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                isShortLine.append(1)
            else:
                isShortLine.append(2)
        else:
            isShortLine.append(3)




    x_1 = int(al[0])
    y_1 = int(al[1])
    x_2 = int(al[2])
    y_2 = int(al[3])
    # # cv2.line(img, (x_1, y_1), (x_2, y_2), (255, 0, 0), 1)
    # cv2.putText(img, str(k + 1), (int((x_1+x_2)/2), int((y_1+y_2)/2)), 0, 0.3, color=(255, 0, 0), thickness=1)
    if isShortLine.__contains__(0):
        continue
    if isShortLine.__contains__(1) and isShortLine.__contains__(2):
        cv2.line(img, (x_1, y_1), (x_2, y_2), (0, 255, 255), 2)
        continue
    if isShortLine.__contains__(1):cv2.line(img, (x_1, y_1), (x_2, y_2), (0, 0, 255), 2)
    elif isShortLine.__contains__(2):cv2.line(img, (x_1, y_1), (x_2, y_2), (0, 255, 0), 2)



cv2.imwrite('./output_img/dissociation/dis.png',img)