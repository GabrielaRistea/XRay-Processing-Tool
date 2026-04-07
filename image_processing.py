import os
import cv2
import numpy as np


def create_diagnostic_video(history, original, folder="video"):
    """Transforma istoricul de procesare intr-un videoclip MP4."""
    if not history:
        return False

    if not os.path.exists(folder):
        os.makedirs(folder)

    output_path = os.path.join(folder, "workflow_summary.mp4")

    frames = [original] + history

    # Luam dimensiunile primei imagini ca referinta
    h, w = frames[0].shape[:2]

    fourcc = cv2.VideoWriter_fourcc(*'H264')
    out = cv2.VideoWriter(output_path, fourcc, 1.0, (w, h))  # 1 cadru pe secunda

    for frame in frames:
        if len(frame.shape) == 2:  # Grayscale
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        else:  # RGB
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Redimensionare obligatorie
        bgr_frame = cv2.resize(bgr_frame, (w, h))
        out.write(bgr_frame)

    out.release()
    return True

def rotate_image(img, angle):
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)
    return rotated

def crop_image(img, start_y, end_y, start_x, end_x):
    return img[start_y:end_y, start_x:end_x]


def apply_clahe(img):
    # verificam daca imaginea este color (3 canale) sau grayscale
    if len(img.shape) == 3:
        # convertim in spatiul LAB pentru a aplica CLAHE doar pe canalul de luminozitate (L)
        # astfel pastram culorile intacte daca imaginea este color
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)

        # combinam canalele inapoi
        limg = cv2.merge((cl, a, b))
        final_img = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    else:
        # daca este deja grayscale (alb-negru), aplicam direct
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        final_img = clahe.apply(img)

    return final_img


def apply_sharpening(img):
    # Unsharp Masking: Imagine originala + (Originala - Gaussian Blur) * amestec
    # un blur ușor
    gaussian_blur = cv2.GaussianBlur(img, (5, 5), 1.0)

    # imaginea originală accentuată
    sharpened = cv2.addWeighted(img, 1.5, gaussian_blur, -0.5, 0)

    return sharpened

def get_histogram_data(img):
    # daca imaginea este color, o convertim in grayscale pentru histograma de intensitate
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img

    # calculam histograma
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    return hist