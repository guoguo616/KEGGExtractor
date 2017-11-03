import cv2
import scipy.misc as smc


class RemoveRect:

    def __init__(self):
        pass


    def clean(self,path,rect_lists):
        img = cv2.imread(path)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)[1]

        f = open('./point_info/contour_rects.txt', 'w')

        # Detect rectangel
        for c in rect_lists:
            cv2.drawContours(img, [c], 0, (179, 179, 179), -1)
            rect = cv2.boundingRect(c)
            f.write(str(rect)+'\n')

        # Detect rounded-rectangel
        _, contours,h = cv2.findContours(thresh,cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
            if len(approx) == 4:

                if abs(cv2.contourArea(approx, True)) >20.0:
                    M = cv2.moments(cnt)
                    cX = ((M["m10"] / M["m00"]))
                    cY = int((M["m01"] / M["m00"]) )
                    (x, y, w, h) = cv2.boundingRect(approx)
                    if abs(cX-(2*x+w)/2)<0.01 or abs(cY-(2*y+h)/2)<0.01 or abs(cv2.contourArea(approx, True))==4321.0:
                        cv2.drawContours(img, [cnt], 0, (179, 179, 179), -1)

            elif len(approx) >7 and len(approx) <=9:

                if abs(cv2.contourArea(approx, True)) >1800 and abs(cv2.contourArea(approx, True)) <5000:
                    cv2.drawContours(img, [cnt], 0, (179, 179, 179), -1)

                    rect = cv2.boundingRect(cnt)
                    f.write(str(rect) + '\n')

        # use color Filtering method to remove rectangele and rounded-rectangle
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        final = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)[1]

        cv2.imwrite('./output_img/pre_processing.png', final)

        # smooth the edge
        h,w,c=img.shape
        res1=smc.imresize(final,(h*2,w*2),interp='bilinear')

        blur = cv2.medianBlur(res1, 5)

        th2 = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        new = cv2.resize(th2, (0, 0), fx=0.5, fy=0.5)
        cv2.imwrite('./output_img/final.png',new)
