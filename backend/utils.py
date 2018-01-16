import math
import time

import numpy as np


def midpoint(pt_a, pt_b):
    # (x1 + x2) / 2 , (y1 + y2) / 2
    return (pt_a[0] + pt_b[0]) * 0.5, (pt_a[1] + pt_b[1]) * 0.5


def rect_to_polar(point, center, inverted_y=False):
    (x_o, y_o) = point
    (x_c, y_c) = center
    x_total = x_o - x_c
    y_total = y_o - y_c

    # if y axis is inverted, adjust y_total
    if inverted_y:
        y_total = y_total * -1.0

    r = math.sqrt(float(np.square(x_total)) + float(np.square(y_total)))
    theta = math.atan2(y_total, x_total)

    return (r, theta)


def get_timestamp():
    """
    Timestamp used during text file generation.

    :return: string with timestamp of the instant the method is called.
    """
    return time.strftime("Created on %m/%d/%y %I:%M %p \n")
