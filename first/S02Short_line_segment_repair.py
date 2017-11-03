import cv2
import numpy as np
from Tool import Tool
import sys

img=cv2.imread('./source/'+sys.argv[1])
img1=img.copy()
src = cv2.imread('./output_img/pre_processing.png')
h,w,c=src.shape
newIg=np.zeros([h, w, 3], dtype=np.uint8)


line_lists=[]
with open('./point_info/merge_point1.txt') as f:
    for i,l in enumerate(f):

        al = l.strip().split(',')
        x1 = int(al[0])
        y1 = int(al[1])
        x2 = int(al[2])
        y2 = int(al[3])
        cv2.line(newIg, (x1, y1), (x2, y2), (255, 255,255), 1)
        line_lists.append((x1, y1,x2, y2))

intermediate=cv2.bitwise_not(cv2.bitwise_xor(src,newIg))


tool=Tool()
segment_lists=[]
HoughIg=np.zeros([h, w, 1], dtype=np.uint8)
gray = cv2.cvtColor(intermediate, cv2.COLOR_BGR2GRAY)
contours, h = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
for i,cnt in enumerate(contours):
    if len(cnt)<=5:continue
    cv2.drawContours(HoughIg, [cnt], 0, (255, 255, 255), 1)



cv2.imwrite('./output_img/short_segment/houghIg.png',HoughIg)
cv2.imwrite('./output_img/short_segment/src.png',intermediate)
lines = cv2.HoughLinesP(HoughIg,rho=1,theta=np.pi/180,threshold=8,minLineLength=5,maxLineGap=5)

if lines <> None:
    for x in range(0, len(lines)):
        for x1,y1,x2,y2 in lines[x]:
            d=np.sqrt(np.power(x1-x2,2)+np.power(y1-y2,2))
            if d<=5: continue
            cv2.line(img,(x1,y1),(x2,y2),(0,0,255),1)
            segment_lists.append((x1, y1, x2, y2))

## the code above is to detect the short line segments
## the code below is to try to merge all line together

cv2.imwrite('./output_img/short_segment/short_line_segment.png',img)

print 'old:'+str(len(segment_lists))

tool.match_line2(line_lists,segment_lists)

count = 0
while (count<3):
    tool.match_line3(line_lists,segment_lists)
    count=count+1




print 'new:'+str(len(segment_lists))

ff = open('./point_info/all_Line.txt', 'w')


for nls in segment_lists:
    line_lists.append(nls)

l2 = sorted(line_lists,key = lambda x:np.sqrt(np.power(x[0]-x[2],2)+np.power(x[1]-x[3],2)))

for m,nl in enumerate(l2):
    ff.write(str(nl).replace('(', '').replace(')', '') + '\n')
    cv2.line(img1, (nl[0], nl[1]), (nl[2], nl[3]), (0, 0, 255), 1)
    cv2.putText(img1, str(m+1), (nl[0], nl[1]), 0, 0.3, color=(255, 0, 0), thickness=1)

cv2.imwrite('./output_img/short_segment/fit1.png',img1)
ff.close()








