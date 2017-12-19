from PIL import ImageTk, Image
from scipy.spatial import distance as dist
from imutils import contours, perspective, resize
from utils import rect_to_polar, get_date
import numpy as np
import cv2
import math


__image_path= None
__original_image = None
__pixels_per_metric = None
__contour_boxes = []
__circumferences = []  # list of tuples: (contour, (centroidX, centroidY))
__output_image = None


# STEP 1: find reference object
# STEP 2: find circumferences
def process_image(image_path, new_h):
    """
    Finds contours that may be possible reference objects.

    :param image_path: path to source image in filesystem.
    :param new_w: width to resize image
    :param new_h: height to resize image
    :return: Number of contour boxes, and sends the GUI the 1st box.
    """
    global __image_path, __original_image, __contour_boxes, __circumferences

    # load the image
    __original_image = cv2.imread(image_path)
    if __original_image is None:
        return "The image may have been moved or renamed, or you may not have access to it."

    # save image path
    __image_path = image_path

    # TODO needs rezise? width or height?

    # resize
    __original_image = resize(__original_image, height=new_h)

    # Reduce background noise and apply canny edge detection
    temp_image = do_pre_processing(__original_image)

    # find contours
    # mode:
    # method:
    _, cnts, _ = cv2.findContours(image=temp_image, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)
    # sort contours from left to right
    (cnts, _) = contours.sort_contours(cnts)

    last_valid_area = None

    for c in cnts:
        area = cv2.contourArea(c)

        # ignore small contours
        if area < 100:
            continue

        # skip duplicates
        if last_valid_area is not None and last_valid_area - area < 500:
            continue
        last_valid_area = area

        # compute the rotated bounding box of the contour
        box = cv2.minAreaRect(c)
        box = cv2.boxPoints(box)
        box = np.array(box, dtype="int")

        # order the points in the contour such that they appear
        # in top-left, top-right, bottom-right, and bottom-left
        # order, then draw the outline of the rotated bounding
        # box
        box = perspective.order_points(box)

        # save these boxes so we can browse them in the GUI
        __contour_boxes.append(box)

        # Look for circular objects
        perimeter = cv2.arcLength(c, closed=True)
        approx = cv2.approxPolyDP(c, epsilon=0.01 * perimeter, closed=True)

        if len(approx) > 8:
            # get centroid
            M = cv2.moments(c)
            (cx, cy) = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])

            # Save circumferences and centroids to render later
            circumference = (c, (cx, cy))
            __circumferences.append(circumference)

    if len(__circumferences) >= 2:
        return "OK"
    else:
        return "Less than 2 circumferences where found in the image."


def get_number_contours():
    global __contour_boxes
    return len(__contour_boxes)


def render_box(index):
    """
    Generates 2 images of the specified bounding box (with horizontal and vertical bisections)

    :param index: The bounding box to render
    :return: result = { "horizontal": (TkImage, width), "vertical": (TkImage, height) }
    """
    global __original_image, __contour_boxes

    box = __contour_boxes[index]

    # 1st of 2 output images: horizontal and vertical bisections
    orig_horizontal_line = __original_image.copy()

    # draw the actual boxes
    cv2.drawContours(orig_horizontal_line, [box.astype("int")], -1, (0, 255, 0), 2)

    # loop over the original points and draw them
    for (x, y) in box:
        cv2.circle(orig_horizontal_line, (int(x), int(y)), 5, (0, 0, 255), -1)

    # unpack the ordered bounding box, then compute the midpoint
    # between the top-left and top-right coordinates, followed by
    # the midpoint between bottom-left and bottom-right coordinates
    (tl, tr, br, bl) = box

    # Midpoints
    # Forms vertical bisection
    (tl_tr_x, tl_tr_y) = midpoint(tl, tr)  # top-left and top-right
    (bl_br_x, bl_br_y) = midpoint(bl, br)  # bottom-left and bottom-right

    # Forms horizontal bisection
    (tl_bl_x, tl_bl_y) = midpoint(tl, bl)  # top-left and bottom-left
    (tr_br_x, tr_br_y) = midpoint(tr, br)  # top-right and bottom-right

    # 2nd output image; Here is where the images deviate
    orig_vertical_line = orig_horizontal_line.copy()

    # draw the midpoints on the image
    cv2.circle(orig_vertical_line, (int(tl_tr_x), int(tl_tr_y)), 5, (255, 0, 0), -1)
    cv2.circle(orig_vertical_line, (int(bl_br_x), int(bl_br_y)), 5, (255, 0, 0), -1)
    cv2.circle(orig_horizontal_line, (int(tl_bl_x), int(tl_bl_y)), 5, (255, 0, 0), -1)
    cv2.circle(orig_horizontal_line, (int(tr_br_x), int(tr_br_y)), 5, (255, 0, 0), -1)

    # draw lines between the midpoints
    cv2.line(orig_vertical_line, (int(tl_tr_x), int(tl_tr_y)), (int(bl_br_x), int(bl_br_y)), (255, 0, 255), 2)
    cv2.line(orig_horizontal_line, (int(tl_bl_x), int(tl_bl_y)), (int(tr_br_x), int(tr_br_y)), (255, 0, 255), 2)

    # draw text on midpoint of lines
    # vertical
    (m_vertical_x, m_vertical_y) = midpoint((tl_tr_x, tl_tr_y), (bl_br_x, bl_br_y))
    cv2.putText(orig_vertical_line, "X", (int(m_vertical_x - 5), int(m_vertical_y)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)
    # horizontal
    (m_horizontal_x, m_horizontal_y) = midpoint((tl_bl_x, tl_bl_y), (tr_br_x, tr_br_y))
    cv2.putText(orig_horizontal_line, "X", (int(m_horizontal_x), int(m_horizontal_y + 5)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)

    # compute the Euclidean distance between the midpoints
    box_height = dist.euclidean((tl_tr_x, tl_tr_y), (bl_br_x, bl_br_y))
    box_width = dist.euclidean((tl_bl_x, tl_bl_y), (tr_br_x, tr_br_y))

    result = {
        "horizontal": (convert_cv_to_tk(orig_horizontal_line), box_width),
        "vertical": (convert_cv_to_tk(orig_vertical_line), box_height)
    }

    return result


def set_pixels_per_metric(value):
    global __pixels_per_metric
    __pixels_per_metric = value


def render_all_circumferences():
    circumference_images = []

    for circumference in __circumferences:
        cnt = circumference[0]
        circ_image = __original_image.copy()

        cv2.drawContours(circ_image, [cnt], 0, color=(0, 255, 0), thickness=2)

        # convert to TkImage and add to result
        circumference_images.append(convert_cv_to_tk(circ_image))

    return circumference_images


def get_number_circumferences():
    return len(__circumferences)


def set_final_circumferences(selected):
    global __circumferences

    final_circumferences = []

    for i, circumference in enumerate(__circumferences):
        if i in selected:
            final_circumferences.append(circumference)

    __circumferences = final_circumferences


def render_final_circumferences():
    global __output_image

    # Generate if we haven't yet
    if __output_image is None:
        output = __original_image.copy()
        colors = ((0, 165, 255), (255, 255, 0))

        for (circumference, color) in zip(__circumferences, colors):
            cnt = circumference[0]
            cx, cy = circumference[1]

            cv2.drawContours(output, [cnt], 0, color=color, thickness=2)
            cv2.circle(output, center=(cx, cy), radius=5, color=color, thickness=-1)

        __output_image = convert_cv_to_tk(output)

    return __output_image


def circumferences_to_polar_and_avg_diameter():
    global __pixels_per_metric

    # 2 rows for each circumference: contains (polar coords, avg diameter)
    circumferences_data = []

    for circumference in __circumferences:
        (contour, centroid) = circumference
        temp_polar_coords = []
        temp_diameters = []

        for points in contour:
            for inner in points:
                (r, theta) = rect_to_polar(point=inner, center=centroid)
                scaled_r = r / __pixels_per_metric

                # save diameter for average
                temp_diameters.append(scaled_r * 2)

                # round and save polar coord
                polar_coord = (round(scaled_r, 2), round(math.degrees(theta), 2))
                temp_polar_coords.append(polar_coord)

        # calculate average diameter
        temp_average_diameter = np.round(np.mean(temp_diameters), 2)

        # save
        circumferences_data.append((temp_polar_coords, temp_average_diameter))

    return circumferences_data


def generate_text_file(file_path):
    circumferences_data = circumferences_to_polar_and_avg_diameter()

    try:
        f = open(file_path, "w+")
        f.write("Image processed: %s\n" % __image_path)
        f.write("\n")
        f.write(get_date())
        f.write("\n")

        tags = ("Outer Circumference", "Inner Circumference")
        for ((polar_coords, avg_diameter), (contour, centroid), tag) in zip(circumferences_data, __circumferences, tags):
            cx, cy = centroid

            # Write circumference tag
            f.write("*%s*\n" % tag)

            # write polar coords
            f.write("Polar coordinates:\n")
            for (r, theta) in polar_coords:
                f.write(" (%s, %s) " % (r, theta))
            f.write("\n")

            # write centroid
            f.write("Centroid: (%s, %s)" % (cx, cy))
            f.write("\n")

            # write average diameter
            f.write("Average Diameter: %s" % avg_diameter)
            f.write("\n")

            f.write("\n")

        f.close()
        return True

    except:
        print("error generating file")
        return False


def do_pre_processing(image):
    # luminescence = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    # channels = cv2.split(luminescence)
    # channels[0] = cv2.equalizeHist(channels[0])
    # luminescence = cv2.merge(channels)
    # luminescence = cv2.cvtColor(luminescence, cv2.COLOR_YUV2BGR)

    # START PRE-PROCESSING
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # OPTION 1
    # gray = cv2.GaussianBlur(gray, ksize=(7, 7), sigmaX=0)

    # OPTION 2
    # smooth out any background noise and preserve edges
    gray = cv2.bilateralFilter(gray, d=7, sigmaColor=100, sigmaSpace=100)

    # perform edge detection, then perform a dilation + erosion to close gaps in between object edges
    # orig = 50, 100
    # test8: 50, 175 .. 100, 200
    edged = cv2.Canny(gray, threshold1=50, threshold2=100)
    edged = cv2.dilate(edged, kernel=None, iterations=1)
    edged = cv2.erode(edged, kernel=None, iterations=1)

    return edged


def convert_cv_to_tk(image):
    # swap color channels: BGR -> RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # convert the image to PIL format
    image = Image.fromarray(image)

    # then to ImageTk format
    return ImageTk.PhotoImage(image)


def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)


def reset_bsc_backend():
    global __original_image, __pixels_per_metric, __contour_boxes, __circumferences, __output_image
    __original_image = None
    __pixels_per_metric = None
    __contour_boxes = []
    __circumferences = []
    __output_image = None


if __name__ == "__main__":
    print(process_image("C:/Users/arosa/PycharmProjects/BambooScanner/test8.jpg", 800))
    set_pixels_per_metric(5.0)
    # print(circumferences_to_polar())
    # render_all_circumferences()
    generate_text_file("C:/Users/arosa/PycharmProjects/BambooScanner/BSC_test.txt")
