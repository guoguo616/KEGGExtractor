import cv2
import numpy as np
from Tool import Tool
import sys

src = cv2.imread('./source/'+sys.argv[1])
src1=src.copy()

hollow_arrow_list=[]
with open('./node_info/'+sys.argv[1]+'.nodes.txt') as f:
    for l in f:
        if l.__contains__('hollow_arrow'):
            sp = l.split()
            if len(sp)>2:
                for hl in sp[2:len(sp)]:
                    ha=eval(hl)
                    cv2.rectangle(src1, (ha[0], ha[1]), (ha[0]+10, ha[1]+8),color=(0,0,255), thickness=1)
                    ll=[(ha[0], ha[1]), (ha[0] + 10, ha[1]), (ha[0], ha[1] + 8), (ha[0] + 10, ha[1] + 8)]
                    if hollow_arrow_list.__contains__(ll):
                        pass
                    else:
                        hollow_arrow_list.append(ll)

tool=Tool()
arrow_list=[]
# with open('./point_info/all_Line.txt') as f:
with open('./point_info/merge_point1.txt') as f:
    for k, l in enumerate(f):
        ll = l.strip().split(',')
        x1 = int(ll[0])
        y1 = int(ll[1])
        x2 = int(ll[2])
        y2 = int(ll[3])

        arrowType=0
        LineLoc=x1,y1,x2,y2

        for bs in hollow_arrow_list:
            flag= tool.IsRectangleContainsLineSegment(x1,y1,x2,y2,bs)
            if flag:

                arrowType = 1
                cv2.line(src1, (x1, y1), (x2, y2), (0, 0, 255), 2)
            else:
                tup=tool.IsRectangleContainsLineSegment1(x1,y1,x2,y2,bs)
                if tup:
                    LineLoc=tup[0],tup[1],tup[2],tup[3]
                    arrowType = 1
                    cv2.line(src1, (tup[0], tup[1]), (tup[2], tup[3]), (0, 0, 255), 2)


        arrow_list.append((LineLoc, arrowType))

tool.storeArrowList(arrow_list)




img = cv2.imread('arrow.png')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 45, 255, cv2.THRESH_BINARY_INV)[1]
contours,h = cv2.findContours(thresh,cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
solid_arrow_list=[]
for i,cnt in enumerate(contours):
    area = cv2.contourArea(cnt)
    if area>1000:continue
    rect = cv2.minAreaRect(cnt)
    box = cv2.cv.BoxPoints(rect)
    box = np.int0(box)

    solid_arrow_list.append([(box[0][0],box[0][1]),(box[1][0],box[1][1]),(box[2][0],box[2][1]),(box[3][0],box[3][1])])


arrow_list=[]
src2=src.copy()
with open('./point_info/arrow_update_point.txt') as f:
    for k, l in enumerate(f):
        ll = l.strip().split(',')
        x1 = int(ll[0])
        y1 = int(ll[1])
        x2 = int(ll[2])
        y2 = int(ll[3])
        arrowType= int(ll[4])

        LineLoc = x1, y1, x2, y2

        for bs in solid_arrow_list:


            flag= tool.IsRectangleContainsLineSegment(x1,y1,x2,y2,bs)
            if flag:
                arrowType=2
                cv2.line(src2, (x1, y1), (x2, y2), (0, 0, 255), 2)
            else:
                tup = tool.IsRectangleContainsLineSegment1(x1, y1, x2, y2, bs)
                if tup:
                    LineLoc = tup[0], tup[1], tup[2], tup[3]
                    arrowType = 2
                    cv2.line(src2, (x1, y1), (x2, y2), (0, 0, 255), 2)
        arrow_list.append((LineLoc, arrowType))

tool.storeArrowList(arrow_list)
cv2.imwrite('solid_arrow.png',src2)

with open('./point_info/arrow_update_point.txt') as f:
    for ll in f:
        al = ll.strip().split(',')
        x1 = int(al[0])
        y1 = int(al[1])
        x2 = int(al[2])
        y2 = int(al[3])
        arrowType = int(al[4])
        if arrowType==0:
            cv2.line(src, (x1, y1), (x2, y2), (0, 0, 255), 2)
        elif arrowType==1:

            cv2.line(src, (x1, y1), (x2, y2), (0, 255, 0), 2)
        elif arrowType==2:

            cv2.line(src, (x1, y1), (x2, y2), (255, 0, 0), 2)
cv2.imwrite('./output_img/arrow_line/solid_hollow_arrow.png',src)




