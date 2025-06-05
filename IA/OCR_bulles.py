# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)

import cv2
import pytesseract

from transformers import pipeline

corrector = pipeline("text2text-generation", model="vennify/t5-base-grammar-correction")

def correct_text(text):
    result = corrector(text, max_new_tokens=100)[0]["generated_text"]
    return result


 # => "This is a simple text"



# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input direc

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


def get_texts(path_image, boxes, padding=0):
    # load the input image and grab the image dimensions
    image = cv2.imread(path_image)
    orig = image.copy()

    #pré-traitement
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # conversion en niveaux de gris
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]  # seuil de niveaux de gris
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(thresh, -1, kernel)  # améliorer la netteté

    (H, W) = image.shape[:2]

    # initialize the list of results
    results = []
    # loop over the bounding boxes
    for index, (centerX, centerY, width, heigth) in enumerate(boxes):
        startX, startY, endX, endY = yolo_to_pixel(centerX, centerY, width, heigth, W, H)
        # in order to obtain a better OCR of the text we can potentially
        # apply a bit of padding surrounding the bounding box -- here we
        # are computing the deltas in both the x and y directions
        dX = int((endX - startX) * padding)
        dY = int((endY - startY) * padding)
        # apply padding to each side of the bounding box, respectively
        startX = max(0, startX - dX)
        startY = max(0, startY - dY)
        endX = min(H, endX + (dX * 2))
        endY = min(W, endY + (dY * 2))
        # extract the actual padded ROI
        roi = sharpened[startY:endY, startX:endX]

        # in order to apply Tesseract v4 to OCR text we must supply
        # (1) a language, (2) an OEM flag of 1, indicating that the we
        # wish to use the LSTM neural net model for OCR, and finally
        # (3) an OEM value, in this case, 7 which implies that we are
        # treating the ROI as a single line of text
        config = ("-l eng --psm 6")
        text = pytesseract.image_to_string(roi, config=config)
        # add the bounding box coordinates and OCR'd text to the list
        # of results
        text_cleaned = "".join([c if ord(c) < 128 else "" for c in text]).strip()
        text_corrected= correct_text(text_cleaned)
        boxes[index].append(text_corrected)
    return boxes


# variables pour l'exemple
path_image = "../data/train_version_YOLO_V8/images/DS_11_jpg.rf.7dea8b7e0a5f3623f8c68550a201d943.jpg"
padding = 0
boxes = [
    [0.15, 0.80625, 0.165625, 0.0984375],
    [0.80703125, 0.1875, 0.21171875, 0.109375],
    [0.2109375, 0.184375, 0.25234375, 0.12421875],
    [0.80625, 0.51796875, 0.1921875, 0.16171875],
    [0.66640625, 0.90546875, 0.20859375, 0.11875],
    [0.84765625, 0.8328125, 0.165625, 0.115625],
    [0.2609375, 0.4546875, 0.103125, 0.090625]
]

# print(get_texts(path_image, boxes))
