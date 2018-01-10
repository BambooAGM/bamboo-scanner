import math
import time

import numpy as np


def rect_to_polar(point, center):
    (x_o, y_o) = point
    (x_c, y_c) = center
    (x_total, y_total) = (x_o - x_c, y_o - y_c)
    r = math.sqrt(float(np.square(x_total)) + float(np.square(y_total)))
    theta = math.atan2(y_total, x_total)

    return (r, theta)


def get_timestamp():
    """
    Timestamp used during text file generation.

    :return: string with timestamp of the instant the method is called.
    """
    return time.strftime("Created on %m/%d/%y %I:%M %p \n")
