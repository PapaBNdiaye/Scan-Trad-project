# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)

import cv2
import pytesseract


# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory


def yolo_to_pixel(cx_norm, cy_norm, w_norm, h_norm, img_width, img_height):
    """
    Convertit les coordonnées normalisées YOLO en coordonnées en pixels (xmin, ymin, xmax, ymax).

    Args:
        cx_norm (float): Position x du centre (normalisé)
        cy_norm (float): Position y du centre (normalisé)
        w_norm (float): Largeur de la box (normalisée)
        h_norm (float): Hauteur de la box (normalisée)
        img_width (int): Largeur de l'image
        img_height (int): Hauteur de l'image

    Returns:
        tuple: (xmin, ymin, xmax, ymax) en pixels
    """
    cx = cx_norm * img_width
    cy = cy_norm * img_height
    w = w_norm * img_width
    h = h_norm * img_height

    xmin = int(cx - w / 2)
    ymin = int(cy - h / 2)
    xmax = int(cx + w / 2)
    ymax = int(cy + h / 2)

    return xmin, ymin, xmax, ymax


def get_texts(path_image, boxes, newW, newH, padding=0):
    # load the input image and grab the image dimensions
    image = cv2.imread(path_image)
    orig = image.copy()
    (origH, origW) = image.shape[:2]
    # set the new width and height and then determine the ratio in change
    # for both the width and height
    rW = origW / float(newW)
    rH = origH / float(newH)
    # resize the image and grab the new image dimensions
    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]

    # initialize the list of results
    results = []
    # loop over the bounding boxes
    for (centerX, centerY, width, heigth) in boxes:
        startX, startY, endX, endY = yolo_to_pixel(centerX, centerY, width, heigth, newW, newH)
        # scale the bounding box coordinates based on the respective
        # ratios
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)
        # in order to obtain a better OCR of the text we can potentially
        # apply a bit of padding surrounding the bounding box -- here we
        # are computing the deltas in both the x and y directions
        dX = int((endX - startX) * padding)
        dY = int((endY - startY) * padding)
        # apply padding to each side of the bounding box, respectively
        startX = max(0, startX - dX)
        startY = max(0, startY - dY)
        endX = min(origW, endX + (dX * 2))
        endY = min(origH, endY + (dY * 2))
        # extract the actual padded ROI
        roi = orig[startY:endY, startX:endX]

        # in order to apply Tesseract v4 to OCR text we must supply
        # (1) a language, (2) an OEM flag of 1, indicating that the we
        # wish to use the LSTM neural net model for OCR, and finally
        # (3) an OEM value, in this case, 7 which implies that we are
        # treating the ROI as a single line of text
        config = ("-l eng --psm 6")
        text = pytesseract.image_to_string(roi, config=config)
        # add the bounding box coordinates and OCR'd text to the list
        # of results
        results.append([(startX, startY, endX, endY), text])

    # sort the results bounding box coordinates from top to bottom
    results = sorted(results, key=lambda r: r[0][1])
    # loop over the results
    for index, (((startX, startY, endX, endY), text)) in enumerate(results):
        boxes[index].append("".join([c if ord(c) < 128 else "" for c in text]).strip())
    return boxes


# variables pour l'exemple
path_image = "../data/train_version_YOLO_V8/images/DS_2_jpg.rf.0070a2c64c6c6389ab8bbcc4c8d0287b.jpg"
(newW, newH) = (640, 640)
padding = 0
boxes = [
    [0.44609375, 0.11484375, 0.2265625, 0.12734375],
    [0.86328125, 0.14921875, 0.225, 0.11015625],
    [0.39140625, 0.303125, 0.1828125, 0.10546875]
]

# print(get_texts(path_image,boxes, newW, newH))