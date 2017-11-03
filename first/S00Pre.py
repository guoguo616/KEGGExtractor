# coding=utf-8
from numpy import *
import cv2
import numpy as np
import sys
from RemoveRect import RemoveRect


def write(image):

    cv2.imwrite('./output_img/clean_img.png',image)

def pre_process(image):
    black = cv2.inRange(image, np.array([0, 0, 0]), np.array([0, 0, 0]))
    red = cv2.inRange(image, np.array([0, 0, 255]), np.array([0, 0, 255]))
    black_and_red = cv2.bitwise_or(black, red)
    H, W = black_and_red.shape
    # clean up boarder areas.
    for i in range(W):
        black_and_red[0][i] = 0
        black_and_red[H - 1][i] = 0
    for i in range(H):
        black_and_red[i][0] = 0
        black_and_red[i][W - 1] = 0
    cv2.rectangle(black_and_red, (0, H - 30), (140, H), color=0, thickness=-1)
    return black_and_red


def del_rectangles(image, rects):
    """Delete a rectangle from image."""
    for r in rects:
        cv2.rectangle(image,
                      (r.x, r.y),
                      (r.x + r.w - 1, r.y + r.h - 1),
                      color=0,
                      thickness=-1)

def load_letter_pixels(path):
    all_letters = {}
    letter = None
    with open(path) as f:
        for l in f:
            if l.startswith('#'):
                continue
            if l.startswith('>'):
                if letter:
                    letter.width = max(len(r) for r in letter.pixels)
                    letter.height = len(letter.pixels)
                letter_name = l[1:].split('#')[0].strip()
                if letter_name == 'EOF':
                    break
                letter = Letter(letter_name, [])
                all_letters.update({letter_name: letter})
                continue
            if l.strip('\n'):
                letter.pixels.append(l.strip('\n'))
    return all_letters


class Letter():
    def __init__(self, name, pixels):
        self.pixels = pixels
        self.name = name
        self.found_at = []
        self.width = None
        self.height = None

    def delete_letter(self, image):
        for x, y in self.found_at:
            if self.confirm_delete(x, y):
                for r in range(len(self.pixels)):
                    for c, p in enumerate(self.pixels[r]):
                        if p == 'o':
                            image[y + r, x + c] = 0

    def confirm_delete(self, x, y):
        global ARROW_HEADS, ARROW_H, ARROW_W
        # for ax, ay in ARROW_HEADS:
        #     if abs(x - ax) <= (self.width + ARROW_W) / 2 and abs(y-ay) <= (self.height+ARROW_H):
        #         return False
        # TODO:
        return True


class Rect():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

def read_found_nodes(path, letters):
    rects = []
    with open(path) as f:
        for l in f:
            if not l.strip():
                continue
            if l.startswith('rect'):
                sp = l.split()
                rects.append(Rect(*map(int, sp[1].split(',') + sp[2:4])))
            elif l.startswith('char'):
                sp = l.split()
                name = sp[1]
                for t in sp[2:]:
                    coord = tuple(map(int, t.split(',')))
                    letters[name].found_at.append(coord)

    return rects


ARROW_HEADS = []
ARROW_H = None
ARROW_W = None

# preserve rectangle contours
def contours(clean_img):
    _, contours, h = cv2.findContours(clean_img.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    rect_lists=[]
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
        if len(approx) == 4:
            if abs(cv2.contourArea(approx, True)) > 20.0:
                M = cv2.moments(cnt)
                cX = ((M["m10"] / M["m00"]))
                cY = int((M["m01"] / M["m00"]))
                (x, y, w, h) = cv2.boundingRect(approx)
                if abs(cX - (2 * x + w) / 2) < 0.8 or abs(cY - (2 * y + h) / 2) < 0.8 or abs(
                        cv2.contourArea(approx, True)) == 4321.0:

                    rect_lists.append(cnt)
    return rect_lists


def findSolidArrows(clean_img, shut_up=True):
    cv2.imwrite('clean.png', clean_img)
    ## 2017.7.2 +++ Try erode first and dilate back +++++++++++
    solid_arrow_img = cv2.erode(clean_img, None, iterations=1)
    cv2.imwrite('erode.png', solid_arrow_img)
    tmp_img, contours, hierarchy = cv2.findContours(solid_arrow_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    cv2.imwrite('arrow_contour.png', tmp_img)
    # delete bad contour
    for contour in contours:
        [x, y, w, h] = cv2.boundingRect(contour)
        if w > 20 and h > 20:
            pass
        elif w <= 3 or h <= 3:
            # Must not be a arrow head
            cv2.drawContours(solid_arrow_img, contour, -1, (0, 0, 0), 1)
        else:
            pass

    solid_arrow_img = cv2.dilate(solid_arrow_img, None, iterations=2)
    cv2.imwrite('arrow.png', solid_arrow_img)
    clean_img = cv2.subtract(clean_img, solid_arrow_img)
    cv2.imwrite('clean_noarrow.png', clean_img)

    return clean_img

def main(pic_name):
    # ========= Read & pre-process image ==========
    png_name = pic_name+''
    img = cv2.imread('./source/' + png_name)
    # Extract black and red, clear border, remove lower-left info box
    clean_img = pre_process(img)
    clean_img = findSolidArrows(clean_img)

    rect_lists=contours(clean_img)

    letters = load_letter_pixels('./letters_by_pixel.txt')
    # ========= Load nodes and letters detected by C++ ==
    rects_found = read_found_nodes('./node_info/' + png_name + '.nodes.txt', letters)

    del_rectangles(clean_img, rects_found)
    global ARROW_HEADS, ARROW_H, ARROW_W
    arrow = letters['arrowhead']
    ARROW_HEADS = arrow.found_at
    ARROW_H = arrow.height
    ARROW_W = arrow.width

    """Below part tries to delete letters from the image.
        There are some problem with the arrow.
    """
    for le in letters.values():
        if le.name != 'arrowhead':
            le.delete_letter(clean_img)

    write(cv2.bitwise_not(clean_img))
    fp=RemoveRect()
    fp.clean('./output_img/clean_img.png',rect_lists)


main(sys.argv[1])