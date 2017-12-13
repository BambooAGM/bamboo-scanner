import numpy as np
import cv2
from PIL import Image, ImageTk


# private variables
# the __ notation causes 'name mangling' on these identifiers
__output_image = None
__circumferences = None


def get_output_image():
    return __output_image


def get_circumferences():
    return __circumferences


def reset_backend():
    global __output_image, __circumferences
    __output_image = None
    __circumferences = None


def convert_cv_to_tk(image):
    # swap color channels: BGR -> RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # convert the image to PIL format
    image = Image.fromarray(image)

    # then to ImageTk format
    return ImageTk.PhotoImage(image)


def process_image(image_path):
    """
    Processes image in order to find both the inner and outer circumference.

    :param str image_path: Path to source image file
    :return status message
    """
    global __output_image, __circumferences

    # load image from given path
    __output_image = cv2.imread(image_path)
    # convert to grayscale
    gray = cv2.cvtColor(__output_image, cv2.COLOR_BGR2GRAY)

    # detect circles in the image
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)

    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        __circumferences = circles

        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(__output_image, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(__output_image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

        # convert output image to ImageTk to display it in the GUI
        __output_image = convert_cv_to_tk(__output_image)
        return "ok"

    else:
        return "error"

def generateFile():
    return
