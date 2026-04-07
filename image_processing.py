import cv2
import numpy as np


def rotate_image(img, angle):
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)
    return rotated

def crop_image(img, start_y, end_y, start_x, end_x):
    return img[start_y:end_y, start_x:end_x]

def apply_median_blur(img, ksize=5):
    return cv2.medianBlur(img, ksize)

def apply_otsu_threshold(img):
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def calculate_bone_mass(binary_img):
    white_pixels = np.sum(binary_img == 255)
    total_pixels = binary_img.size
    percentage = (white_pixels / total_pixels) * 100
    return round(percentage, 2)


def apply_canny_edge_detection(img):
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    edges = cv2.Canny(gray, 50, 150)

    return edges