import cv2


def rotate_image(img, angle):
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)
    return rotated

def crop_image(img, start_y, end_y, start_x, end_x):
    return img[start_y:end_y, start_x:end_x]