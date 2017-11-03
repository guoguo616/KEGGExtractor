import cv2
import numpy as np
import sys
from Tool import Tool
from scipy import stats

img = cv2.imread('./output_img/final.png')
merge_img=img.copy()

gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

thresh = cv2.threshold(gray,60, 255, cv2.THRESH_BINARY_INV)[1]

f = open('./point_info/point.txt', 'w')
merge_lines = []
lines = cv2.HoughLinesP(thresh,rho=1,theta=np.pi/180,threshold=12,minLineLength=10,maxLineGap=8)
tool = Tool()

for x in range(0, len(lines)):
    for x1,y1,x2,y2 in lines[x]:
        cv2.line(img,(x1,y1),(x2,y2),(0,0,255),1)
        f.write(str(x1)+','+str(y1)+','+str(x2)+','+str(y2) + "\n")
        merge_line = []
        if len(merge_lines) == 0:
            merge_line.append((x1, y1, x2, y2))
            merge_lines.append(merge_line)
        else:
            l1=x1,y1,x2,y2
            equal = tool.match_line(l1, merge_lines)

            if equal == -1:
                merge_line.append((x1, y1, x2, y2))
                merge_lines.append(merge_line)
            else:
                merge_lines[equal].append((x1, y1, x2, y2))



f = open('./point_info/merge_point.txt', 'w')

for k, ms in enumerate(merge_lines):
    x_list = []
    y_list = []
    for i, ll in enumerate(ms):
        if len(ms) > 1:
            x_list.append(ll[0])
            x_list.append(ll[2])
            y_list.append(ll[1])
            y_list.append(ll[3])
        else:
            f.write(str(ll).replace('(','').replace(')','') + "\n")
            if(k%3==0):
                col = (0, 0, 255)
            elif(k%3==1):
                col=(255,0,0)
            else:
                col=(0,255,0)
            cv2.putText(merge_img,str(k+1),((ll[0]+ll[2])/2,(ll[1]+ll[3])/2),0,0.4,color=(0,0,255),thickness=1)
            cv2.line(merge_img, (int(ll[0]), int(ll[1])), (int(ll[2]), int(ll[3])),col , 1)

    if len(ms) > 1:

        slope, intercept, r_value, p_value, std_err = stats.linregress(np.array(x_list), np.array(y_list))
        xmin, xmax = tool.getCoor(x_list)

        if np.math.isnan(slope) and np.math.isnan(intercept):
            ymin,ymax=tool.getCoor(y_list)
            cv2.line(merge_img, (xmin, ymin), (xmax, ymax), (204, 204, 255), 1)
        else:
            ymin = int(round(slope * xmin + intercept))
            ymax = int(round(slope * xmax + intercept))
            f.write(str(xmin) + ',' + str(ymin) + ',' + str(xmax) + ',' + str(ymax) + "\n")
            cv2.putText(merge_img, '***', ((xmin + xmax) / 2, (ymin + ymax) / 2), 0, 0.4,color=(0, 0, 255), thickness=1)
            cv2.line(merge_img, (xmin, ymin), (xmax, ymax), (204,204, 255), 1)

cv2.imwrite('./output_img/hough.png',img)
cv2.imwrite('./output_img/merge.png',merge_img)


final_img = cv2.imread('./source/'+sys.argv[1])
f = open('./point_info/merge_point1.txt', 'w')

for k,ms in enumerate(tool.fit_line()):
        f.write(str(ms).replace('(','').replace(')','').replace('[','').replace(']','') + "\n")
        for i,ll in enumerate(ms):
            if(k%3==0):
                col = (0, 0, 255)
            elif(k%3==1):
                col=(255,0,0)
            else:
                col=(0,255,0)

            cv2.putText(final_img,str(k+1),((ll[0]+ll[2])/2,(ll[1]+ll[3])/2),0,0.4,color=(0,0,255),thickness=1)
            cv2.line(final_img, (int(ll[0]), int(ll[1])), (int(ll[2]), int(ll[3])),col , 2)



cv2.imwrite('./output_img/fit.png',final_img)

f.close()