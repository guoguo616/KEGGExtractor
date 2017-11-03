import cv2
import numpy as np
from Tool import Tool
from scipy import stats
import sys


def houghLineDetect(newIg,tool,i):

    gray = cv2.cvtColor(newIg, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
    x_list=[]
    y_list=[]

    contours, h = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        if len(cnt)<=1:continue
        for c in cnt:
            x_list.append(c[0][0])
            y_list.append(c[0][1])
            if i==18:cv2.drawContours(newIg, [cnt], 0, (0, 0, 255), 1)


    if len(x_list)==0:return 0

    slope, intercept, r_value, p_value, std_err = stats.linregress(np.array(x_list), np.array(y_list))
    xmin, xmax = tool.getCoor(x_list)
    if np.math.isnan(slope) and np.math.isnan(intercept):
        ymin, ymax = tool.getCoor(y_list)
    else:
        ymin = int(round(slope * xmin + intercept))
        ymax = int(round(slope * xmax + intercept))

    d=np.sqrt(np.power(xmin-xmax,2)+np.power(ymin-ymax,2))

    if i == 18:

        cv2.imwrite('./output_img/hollow_line/contours_detect.png', newIg)

    return d



f1 = open('./point_info/hollow_line.txt', 'w')
img=cv2.imread('./source/'+sys.argv[1])
src = cv2.imread('./output_img/final.png')
h,w,c=src.shape
tool=Tool()
with open('./point_info/arrow_update_point.txt') as f:
    for i,l in enumerate(f):

        al = l.strip().split(',')
        x1 = int(al[0])
        y1 = int(al[1])
        x2 = int(al[2])
        y2 = int(al[3])
        arrowType=int(al[4])
        Ig=np.zeros([h, w, 3], dtype=np.uint8)
        cv2.line(Ig, (x1, y1), (x2, y2), (255, 255, 255), 1)

        clean_img = cv2.bitwise_and(src,Ig)
        d=np.sqrt(np.power(x1-x2,2)+np.power(y1-y2,2))
        d1=houghLineDetect(clean_img.copy(),tool,i)
        if float(d1/d)<0.5:
            lineType=0
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(img, 'solid', ((x1 + x2) / 2, (y1 + y2) / 2 + 10), 0, 0.3, color=(0, 0, 255), thickness=1)
        else:
            lineType=1
            cv2.putText(img, 'dotted', ((x1 + x2) / 2, (y1 + y2) / 2 + 10), 0, 0.4, color=(0, 0, 255), thickness=1)
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(src, str(i + 1), ((x1+x2) / 2, (y1+y2) / 2), 0, 0.4, color=(0, 0, 255),thickness=1)
        f1.write(str(x1) + ',' + str(y1) + ',' + str(x2) + ',' + str(y2) + ',' + str(arrowType) + ',' + str(lineType) + "\n")

cv2.imwrite('./output_img/hollow_line/lineType.png', img)
f1.close()



