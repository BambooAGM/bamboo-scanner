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