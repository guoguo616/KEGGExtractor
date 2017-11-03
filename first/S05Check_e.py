import cv2
import numpy as np
from Tool import Tool
import sys

img=cv2.imread('./source/'+sys.argv[1])
src = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

char_e_list=[]
with open('./node_info/'+sys.argv[1]+'.nodes.txt') as f:
    for l in f:
        if l.startswith('char') and l.__contains__('e'):
            sp = l.split()
            if len(sp)>2:
                for hl in sp[2:len(sp)]:
                    ha=eval(hl)
                    h1=ha[0]-1
                    h2=ha[1]-1
                    count=0
                    for h1 in range(ha[0],ha[0] + 4):
                        for h2 in range(ha[1],ha[1] + 6):
                            if src[h2, h1] == 255:
                                        count = count + 1


                    if count>8 and count<=11:
                        char_e_list.append([(ha[0] - 1,ha[1] - 1),(ha[0] +4,ha[1] - 1),(ha[0] - 1,ha[1]+6),(ha[0]+4 ,ha[1]+6)])

img1 = cv2.imread('arrow.png')
gray1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray1, 45, 255, cv2.THRESH_BINARY_INV)[1]
contours,h = cv2.findContours(thresh,cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
solid_arrow_list=[]
for i,cnt in enumerate(contours):
    area = cv2.contourArea(cnt)
    if area>1000:continue
    rect = cv2.minAreaRect(cnt)
    box = cv2.cv.BoxPoints(rect)
    box = np.int0(box)

    solid_arrow_list.append([(box[0][0],box[0][1]),(box[1][0],box[1][1]),(box[2][0],box[2][1]),(box[3][0],box[3][1])])

tool=Tool()
del_list=[]
for i,e in enumerate(char_e_list):
    for sl in solid_arrow_list:

        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = tool.ori_min_max_point(e)
        el1 = (x1, y1, x3, y3)
        el2 = (x1, y1, x4, y4)
        el3 = (x2, y2, x3, y3)
        el4 = (x2, y2, x4, y4)
        if tool.IsRectangleContainsLineSegment(x1, y1, x3, y3, sl) or \
                tool.IsRectangleContainsLineSegment(x1, y1, x4, y4, sl) or \
                tool.IsRectangleContainsLineSegment(x2, y2, x3, y3, sl) or \
                tool.IsRectangleContainsLineSegment(x1, y1, x4, y4, sl):
            del_list.append(e)


del_list1=[]
[del_list1.append(i) for i in del_list if not i in del_list1]

for e in del_list1:
    char_e_list.remove(e)

cross_e_list=[]
with open('./point_info/hollow_line.txt') as f:
    for k, l in enumerate(f):
        ll = l.strip().split(',')
        x1 = int(ll[0])
        y1 = int(ll[1])
        x2 = int(ll[2])
        y2 = int(ll[3])


        arrowType = int(ll[4])
        hollow=int(ll[5])
        cross_e=0

        for e in char_e_list:
            flag = tool.IsRectangleContainsLineSegment(x1, y1, x2, y2, e)
            if flag:
                cross_e = 1
            else:
                tup = tool.IsRectangleContainsLineSegment1(x1, y1, x2, y2, e,exDist=10)
                if tup:
                    LineLoc = tup[0], tup[1], tup[2], tup[3]
                    cross_e = 1
        cross_e_list.append((x1,y1,x2,y2,arrowType,hollow,cross_e))


f1 = open('./point_info/e_cross_point.txt', 'w')
for ce in cross_e_list:
    x1 = int(ce[0])
    y1 = int(ce[1])
    x2 = int(ce[2])
    y2 = int(ce[3])
    cross_e= int(ce[6])
    if cross_e==0:
        pass
    elif cross_e==1:
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 1)
        cv2.putText(img, '*', ((x1 + x2) / 2, (y1 + y2) / 2 + 10), 0, 0.4, color=(0, 0, 255), thickness=1)
    f1.write(str(ce).replace('(','').replace(')','')+'\n')


f1.close()

cv2.imwrite('./output_img/cross_e/cross_e.png',img)


