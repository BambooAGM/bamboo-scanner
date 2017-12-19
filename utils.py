import math
import numpy as np
import time


def rect_to_polar(point, center):
    (x_c, y_c) = center
    (x_o, y_o) = point
    (x_total, y_total) = (x_o - x_c, y_o - y_c)
    r = math.sqrt(float(np.square(x_total)) + float(np.square(y_total)))
    theta = math.atan2(y_total, x_total)

    return (r, theta)


# Gets current date for the generation of the text file, from the user's machine
def get_date():
    date = time.strftime("Created on %m/%d/%y %I:%M %p \n")
    return date


def resize_keep_aspect(image, w, h, max_w, max_h):
    """
    Resize an image while keeping aspect ratio.

    :param w: current width
    :param h: current height
    :param max_w: max allowed width
    :param max_h: max allowed height
    :param image: The image to resize. Must be of PIL Image format
    :return: The resized image in PIL Image format
    """
    ratio = min(max_w / w, max_h / h)
    (new_w, new_h) = (int(w * ratio), int(h * ratio))

    return image.resize((new_w, new_h))
