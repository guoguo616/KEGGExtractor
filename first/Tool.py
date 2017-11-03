from __future__ import division
import numpy as np
from scipy import stats
import sys


class Tool:

    # caluate the area of a polygon based on four points of two lines
    def PolygonArea(self,corners):
        n = len(corners)  # of corners
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += corners[i][0] * corners[j][1]
            area -= corners[j][0] * corners[i][1]
        area = abs(area) / 2.0
        return area


    def getSlope(self,l):
        if l[0] - l[2] != 0:
            k= (l[1] - l[3]) / (l[0] - l[2])
            if abs(k) < 0.004: k = 0.0
            return k
        else:
            return False

    ''' 
        calculate the closestDistance between two line segments
        if they intersect, return back the intersect point
    
    '''
    def closestDistanceBetweenLines(self,l1,l2, clampAll=False, clampA0=False, clampA1=False, clampB0=False,
                                    clampB1=False):

        ''' Given two lines defined by numpy.array pairs (a0,a1,b0,b1)
            Return the closest points on each segment and their distance
        '''
        a1 = np.array([l1[0], l1[1], 0])
        a0 = np.array([l1[2], l1[3], 0])
        b0 = np.array([l2[0], l2[1], 0])
        b1 = np.array([l2[2], l2[3], 0])
        # If clampAll=True, set all clamps to True
        if clampAll:
            clampA0 = True
            clampA1 = True
            clampB0 = True
            clampB1 = True

        # Calculate denomitator
        A = a1 - a0
        B = b1 - b0
        magA = np.linalg.norm(A)
        magB = np.linalg.norm(B)

        _A = A / magA
        _B = B / magB

        cross = np.cross(_A, _B);
        denom = np.linalg.norm(cross) ** 2

        # If lines are parallel (denom=0) test if lines overlap.
        # If they don't overlap then there is a closest point solution.
        # If they do overlap, there are infinite closest positions, but there is a closest distance
        if not denom:
            d0 = np.dot(_A, (b0 - a0))

            # Overlap only possible with clamping
            if clampA0 or clampA1 or clampB0 or clampB1:
                d1 = np.dot(_A, (b1 - a0))

                # Is segment B before A?
                if d0 <= 0 >= d1:
                    if clampA0 and clampB1:
                        if np.absolute(d0) < np.absolute(d1):
                            return a0, b0, np.linalg.norm(a0 - b0)
                        return a0, b1, np.linalg.norm(a0 - b1)


                # Is segment B after A?
                elif d0 >= magA <= d1:
                    if clampA1 and clampB0:
                        if np.absolute(d0) < np.absolute(d1):
                            return a1, b0, np.linalg.norm(a1 - b0)
                        return a1, b1, np.linalg.norm(a1 - b1)

            # Segments overlap, return distance between parallel segments
            return None, None, np.linalg.norm(((d0 * _A) + a0) - b0)

        # Lines criss-cross: Calculate the projected closest points
        t = (b0 - a0);
        detA = np.linalg.det([t, _B, cross])
        detB = np.linalg.det([t, _A, cross])

        t0 = detA / denom;
        t1 = detB / denom;

        pA = a0 + (_A * t0)  # Projected closest point on segment A
        pB = b0 + (_B * t1)  # Projected closest point on segment B

        # Clamp projections
        if clampA0 or clampA1 or clampB0 or clampB1:
            if clampA0 and t0 < 0:
                pA = a0
            elif clampA1 and t0 > magA:
                pA = a1

            if clampB0 and t1 < 0:
                pB = b0
            elif clampB1 and t1 > magB:
                pB = b1

            # Clamp projection A
            if (clampA0 and t0 < 0) or (clampA1 and t0 > magA):
                dot = np.dot(_B, (pA - b0))
                if clampB0 and dot < 0:
                    dot = 0
                elif clampB1 and dot > magB:
                    dot = magB
                pB = b0 + (_B * dot)

            # Clamp projection B
            if (clampB0 and t1 < 0) or (clampB1 and t1 > magB):
                dot = np.dot(_A, (pB - a0))
                if clampA0 and dot < 0:
                    dot = 0
                elif clampA1 and dot > magA:
                    dot = magA
                pA = a0 + (_A * dot)

        pa_pb_dist = np.linalg.norm(pA - pB)


        if pa_pb_dist==0.0 or pa_pb_dist<0.00001:
            pa_pb_dist=0.0
        else:
        # have intersect point but distance !=0, closet to zero
            if round(pA[0])==round(pB[0]) and round(pA[1])==round(pB[1]):pa_pb_dist=-1

        return pA, pB, pa_pb_dist

    def match_line(self, l1, merge_lines):

        positionToDist=[]
        for i, mll in enumerate(merge_lines):
            dist_list = []
            for l2 in mll:

                pa,pb,mindist=self.closestDistanceBetweenLines(l1,l2,clampAll=True)
                k1 = self.getSlope(l1)
                k2 = self.getSlope(l2)
                Delta = np.math.fabs(k1 - k2)


                # mindist<=0 two lines intersect with each other
                if mindist<3 and mindist>0:

                    if (k1>0 and k2<0) or (k1<0 and k2>0) or (k1==0 and k2<>0) or (k1<>0 and k2==0):
                        pass
                    else:
                        if Delta < 0.22:
                            dist_list.append(mindist)
                elif mindist==-1:
                    if Delta<0.3011:
                        if (k1 > 0 and k2 < 0) or (k1 < 0 and k2 > 0) or (k1 == 0 and k2 <> 0) or (k1 <> 0 and k2 == 0):
                            pass
                        else:
                            dist_list.append(0)


            if len(dist_list)<>0:
                temp = sys.maxint
                for dl in dist_list:
                    if dl<temp:
                        temp=dl
                positionToDist.append((i,temp))

        if len(positionToDist)==0:
            position=-1
        else:
            position=sorted(positionToDist,key=lambda pd:pd[1])[0][0]

        return position


    def get_min_max_coor(self,x_list):
        xmin = sorted(x_list)[0]
        xmax = sorted(x_list, reverse=True)[0]
        return xmin, xmax

    def match_line1(self,l1,merge_lines):
        ls=[]
        for i, mll in enumerate(merge_lines):
            for l2 in mll:

                
                k1 = self.getSlope(l1)
                k2 = self.getSlope(l2)

                x_list=[l1[0],l1[2],l2[0],l2[2]]
                y_list=[l1[1],l1[3],l2[1],l2[3]]
                mindist = self.closestDistanceBetweenLines(l1, l2, clampAll=True)[2]
                # fit line function
                slope, intercept, r_value, p_value, std_err = stats.linregress(np.array(x_list), np.array(y_list))
                xmin, xmax = self.get_min_max_coor(x_list)
                if np.math.isnan(slope) and np.math.isnan(intercept):
                    if mindist<15:
                        ls.append((l2, i))
                        continue
                else:
                    y1 = int(round(slope * xmin + intercept))
                    y2 = int(round(slope * xmax + intercept))
                    ymin,ymax=self.get_min_max_coor([y1,y2])
                    y_min, y_max = self.get_min_max_coor(y_list)

                    corners = [(l1[0], l1[1]), (l1[2], l1[3]), (l2[0], l2[1]), (l2[2], l2[3])]
                    if abs(ymin-y_min)<3 and abs(ymax-y_max)<3 and self.PolygonArea(corners)<=20.0 and mindist<32.5 \
                            and self.pointTolineDist(((xmin+xmax)/2,(ymin+ymax)/2),k1,self.getB(l1))<3:
                            if np.math.fabs(k1 - k2)<0.2:
                                ls.append((l2,i))
                                continue


        if len(ls)==0:return -1
        ls.append((l1,-1))
        x_ls=[]
        y_ls=[]
        d_ls=[]
        for l_ in ls:
            l=l_[0]
            x_ls.append(l[0])
            x_ls.append(l[2])
            y_ls.append(l[1])
            y_ls.append(l[3])
            d_ls.append(l_[1])
        slope, intercept, r_value, p_value, std_err = stats.linregress(np.array(x_ls), np.array(y_ls))
        xmin, xmax = self.get_min_max_coor(x_ls)
        if np.math.isnan(slope) and np.math.isnan(intercept):
            ymin, ymax = self.get_min_max_coor(y_ls)
        else:
            ymin = int(round(slope * xmin + intercept))
            ymax = int(round(slope * xmax + intercept))
        return xmin,ymin,xmax,ymax,d_ls

        # return -1

    def match_line2(self,line_lists,segment_lists):
        for i, ll in enumerate(line_lists):
            merge_index_list = []
            for j, sl in enumerate(segment_lists):
                k1 = self.getK(ll)
                k2 = self.getK(sl)

                x_list1 = [ll[0], ll[2], sl[0], sl[2]]
                y_list1 = [ll[1], ll[3], sl[1], sl[3]]
                mindist = self.closestDistanceBetweenLines(ll, sl, clampAll=True)[2]
                k, b, r, p, std = stats.linregress(np.array(x_list1), np.array(y_list1))
                xmin, xmax = self.get_min_max_coor(x_list1)
                if np.math.isnan(k) and np.math.isnan(b):
                    ymin, ymax = self.get_min_max_coor(y_list1)
                    if mindist < 15:
                        line_lists[i] = (xmin, ymin, xmax, ymax)
                        merge_index_list.append(j)

                else:
                    y1 = int(round(k * xmin + b))
                    y2 = int(round(k * xmax + b))
                    ymin, ymax = self.get_min_max_coor([y1, y2])
                    y_min, y_max = self.get_min_max_coor(y_list1)
                    corners = [(ll[0], ll[1]), (ll[2], ll[3]), (sl[0], sl[1]), (sl[2], sl[3])]
                    if abs(ymin - y_min) < 1 and abs(ymax - y_max) < 1 \
                            and (k1 and k2) \
                            and abs(k1 - k2) < 0.01 \
                            and self.pointTolineDist((xmin, ymin), k1, self.getB(ll)) < 2 \
                            and self.pointTolineDist((xmax, ymax), k2, self.getB(sl)) < 2 \
                            and self.PolygonArea(corners) < 3.0:
                        line_lists[i] = (xmin, ymin, xmax, ymax)
                        merge_index_list.append(j)

            for mil in merge_index_list:
                del segment_lists[mil]
        return line_lists,segment_lists

    def fit_line(self):
        merge_lines = []
        with open('./point_info/merge_point.txt') as f:
            for k, l in enumerate(f):
                ll = l.strip().split(',')
                x1 = int(ll[0])
                y1 = int(ll[1])
                x2 = int(ll[2])
                y2 = int(ll[3])

                merge_line = []
                if len(merge_lines) == 0:
                    merge_line.append((x1, y1, x2, y2))
                    merge_lines.append(merge_line)
                else:
                    l1 = x1, y1, x2, y2
                    re = self.match_line1(l1, merge_lines)

                    if re == -1:
                        merge_line.append((x1, y1, x2, y2))
                        merge_lines.append(merge_line)
                    else:
                        for j,re_ in enumerate(re[4]):
                            if j==0:merge_lines[re_] = [(re[0], re[1], re[2], re[3])]
                            else:
                                if re_<>-1:del merge_lines[re_]


                       
        return merge_lines

    # extend a line and check whether a line cross rectangle or not
    def IsRectangleContainsLineSegment1(self, x1, y1, x2, y2, box,exDist=10):

            ls = (x1, y1, x2, y2)
           
            (minX, minY), (maxX, maxY) = self.get_min_max_point(box)[:2]
            midX = (minX + maxX) / 2
            midY = (minY + maxY) / 2

            k=self.getK(ls)

            if k or k==0:
                b = y1 - k * x1
                d = np.math.fabs(k * midX - midY + b) / np.sqrt(np.power(k, 2) + 1)
            else:
                d = np.math.fabs(x1 - midX)

            if d < 20:
                d1 = np.sqrt(np.power(midX - x1, 2) + np.power(midY - y1, 2))
                d2 = np.sqrt(np.power(midX - x2, 2) + np.power(midY - y2, 2))
                if d1 > d2:
                    for i in range(0, exDist):
                        if k or k==0:
                            if midX>x2:x2 = x2 + 1
                            elif midX<x2: x2 = x2-1

                            y2 = k * x2 + b
                        else:
                            if midY>y2:y2 = y2 + 1
                            elif midY<y2: y2 = y2 - 1

                        if self.IsRectangleContainsLineSegment(x1, y1, x2, y2, box):
                            return x1,y1,x2,int(round(y2))
                else:
                    for i in range(0, exDist):
                        if k or k==0:
                            if midX > x1:x1 = x1 + 1
                            elif midX<x1:x1=x1-1

                            y1 = k * x1 + b
                        else:
                            if midY>y1:y1 = y1 + 1
                            elif midY<y1: y1 = y1 - 1
                        if self.IsRectangleContainsLineSegment(x1, y1, x2, y2, box):
                            return x1,int(round(y1)),x2,y2
                return False

    # check whether a line cross rectangle or not

    def IsRectangleContainsLineSegment(self,x1, y1, x2, y2, box):

        ls = (x1, y1, x2, y2)
        
        (x1, y1), (x2, y2),(x3,y3),(x4,y4) = self.get_min_max_point(box)
        bl1=(x1, y1,x3,y3)
        bl2=(x1, y1,x4,y4)
        bl3=(x2, y2,x3,y3)
        bl4=(x2, y2,x4,y4)

        if self.closestDistanceBetweenLines(bl1, ls, clampAll=True)[2]==0 or self.closestDistanceBetweenLines(bl2, ls, clampAll=True)[2]==0 or self.closestDistanceBetweenLines(bl3, ls, clampAll=True)[2] == 0 or self.closestDistanceBetweenLines(bl4, ls, clampAll=True)[2] == 0:
                return True

        return False

    def getK(self, l):
        if l[0] - l[2] != 0:
            k = (l[1] - l[3]) / (l[0] - l[2])
            if abs(k) < 0.004: k = 0.0
            return k
        else:
            return None

    def getB(self,l):
        k=self.getK(l)
        if k is None:
            return None
        else:
            b=l[1]-k*l[0]

        return b

    def linearFitLine(self,x_list,y_list):
        k, b = stats.linregress(np.array(x_list), np.array(y_list))[:2]
        xmin, xmax = self.get_min_max_coor(x_list)
        ymin = int(round(k * xmin + b))
        ymax = int(round(k * xmax + b))
        return xmin,ymin,xmax,ymax


    def get_min_max_point(self,box):
        bs=[]
        for b in box:
            bs.append((np.sqrt(np.power(b[0],2)+np.power(b[1],2)),b))
        bs_sort=sorted(bs,key=lambda b:b[0])
        return bs_sort[0][1],bs_sort[3][1],bs_sort[1][1],bs_sort[2][1]

    def storeArrowList(self,arrow_list):
        f = open('./point_info/arrow_update_point.txt', 'w')
        for al in arrow_list:
            f.write(str(al).replace('(','').replace(')','')+'\n')
        f.close()

    # caculate the distance from a point to a line
    def pointTolineDist(self,p,k,b):
        return abs(k*p[0]-p[1]+b)/np.sqrt(np.power(k,2)+1)

    def match_line3(self,line_lists,segment_lists):
        for i, ll in enumerate(line_lists):

            for j, sl in enumerate(segment_lists):


                k1 = self.getK(ll)
                k2 = self.getK(sl)
                x_list = [ll[0], ll[2], sl[0], sl[2]]
                y_list = [ll[1], ll[3], sl[1], sl[3]]
                pa,pb,mindist = self.closestDistanceBetweenLines(ll, sl, clampAll=True)
                if (k1!=None and k2!=None) and (k1<>0 and k2<>0):
                    if 0<mindist<30 and pb!=None and pa!=None:
                            xi = int(round(pb[0]))
                            ysl=k2*xi+self.getB(sl)
                            yll=k1*xi+self.getB(ll)
                            if abs(ysl-yll)<3:
                                if abs(x_list[2]-xi)>=abs(x_list[3]-xi):
                                    xj=x_list[2]
                                else:
                                    xj = x_list[3]
                                ysl1 = k2 * xj + self.getB(sl)
                                yll1 = k1 * xj + self.getB(ll)
                                if abs(ysl1-yll1)<3:
                                    x_ls=[ll[0], ll[2],xi,xj]
                                    y_ls=[ll[1], ll[3],ysl,ysl1]
                                    line_lists[i] = self.linearFitLine(x_ls,y_ls)
                                    segment_lists.remove(sl)





                elif k1 is None and k2 is None: # slope is None
                    if mindist < 20:
                        # two line overlap
                        if pa is None and pb is None:
                            ymin, ymax = self.get_min_max_coor(y_list)
                        else:
                            x1=int(round(pa[0]))
                            x2 = int(round(pb[0]))
                            if abs(x1-x2)<2:
                                ymin,ymax=self.get_min_max_coor(y_list)
                        line_lists[i] = (ll[0], ymin, ll[2], ymax)
                        segment_lists.remove(sl)



        return line_lists,segment_lists

















