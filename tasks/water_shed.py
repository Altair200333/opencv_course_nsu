import cv2 as cv
import numpy as np

from image_transform import *
from tools import *
from color_correction import *
from tasks.tracking_tools import *
from scipy.ndimage import label

frame_size = 600


img = cv.imread("../imgs/cards.jpg")
img = clipImg(img, frame_size)


def segment_on_dt(a, img):
    border = cv.dilate(img, None, iterations=5)
    border = border - cv.erode(border, None)

    dt = cv.distanceTransform(img, 2, 3)
    dt = ((dt - dt.min()) / (dt.max() - dt.min()) * 255).astype(np.uint8)
    _, dt = cv.threshold(dt, 180, 255, cv.THRESH_BINARY)
    lbl, ncc = label(dt)
    lbl = lbl * (255 / (ncc + 1))
    # Completing the markers now.
    lbl[border == 255] = 255

    lbl = lbl.astype(np.int32)
    cv.watershed(a, lbl)

    lbl[lbl == -1] = 0
    lbl = lbl.astype(np.uint8)
    return 255 - lbl

img_copy = img.copy()
while True:
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, img_bin = cv.threshold(img_gray, 0, 255, cv.THRESH_OTSU)

    img_bin = cv.morphologyEx(img_bin, cv.MORPH_OPEN, np.ones((3, 3), dtype=int))
    result = segment_on_dt(img, img_bin)

    result[result != 255] = 0
    result = cv.dilate(result, None)

    img_copy[result == 255] = (0, 0, 255)

    cv.imshow('res', result)
    cv.imshow('warped', img_copy)
    k = cv.waitKey(1) & 0xFF

    if k == 27:
        break
