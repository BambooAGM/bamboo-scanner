from PIL import ImageTk, Image
from scipy.spatial import distance as dist
from imutils import contours, perspective, resize
from utils import rect_to_polar, get_date
import numpy as np
import cv2
import math


__image_path = None
__original_image = None
__pixels_per_metric = None
__contour_boxes = []
__circumferences = []  # list of tuples: (contour, (centroidX, centroidY))
__output_image = None


def get_image_path():
    return __image_path


def get_number_boxes():
    return len(__contour_boxes)


# STEP 1: find reference object
# STEP 2: find circumferences
def process_image(image_path):
    """
    Finds contours that may be possible reference objects.

    :param image_path: path to source image in filesystem.
    :return: Status message
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
    # __original_image = resize(__original_image, height=new_h)

    # Reduce background noise and apply canny edge detection
    temp_image = do_pre_processing(__original_image)

    # find contours
    # mode:
    # method:
    _, cnts, _ = cv2.findContours(image=temp_image, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_NONE)
    # sort contours from left to right
    # (cnts, _) = contours.sort_contours(cnts)

    counter = 1
    for c in cnts:
        area = cv2.contourArea(c)

        # ignore small contours
        if area < 10000:
            continue

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

        perimeter = cv2.arcLength(c, closed=True)
        approx = cv2.approxPolyDP(c, epsilon=0.01 * perimeter, closed=True)

        # Look for circular objects
        if len(approx) > 10 and len(approx) < 20:
            # filter with contour properties

            # BOUNDING RECTANGLE
            x, y, w, h = cv2.boundingRect(c)

            # aspect ratio
            aspect_ratio = float(w) / h

            # extent
            rect_area = w * h
            extent = float(area) / rect_area

            # solidity
            hull = cv2.convexHull(c)
            hull_area = cv2.contourArea(hull)
            solidity = float(area) / hull_area

            # valid properties
            size_ok = w > 25 and h > 25
            solidity_ok = solidity > 0.9
            aspect_ratio_ok = aspect_ratio >= 0.8 and aspect_ratio <= 1.2

            if size_ok and solidity_ok and aspect_ratio_ok:
                # print("Object", counter)
                # counter += 1
                # print("aspect ratio", aspect_ratio)
                # print("extent", extent)
                # print("solidity", solidity)

                # get centroid
                M = cv2.moments(c)
                (cx, cy) = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])

                # get real points
                # mask = np.zeros(temp_image.shape, np.uint8)
                # cv2.drawContours(mask, [c], 0, 255, -1)
                # # pixelpoints = np.transpose(np.nonzero(mask))
                # pixelpoints = cv2.findNonZero(mask)
                # print("pixelpoints", len(pixelpoints))
                # print("contour", len(c))

                # Save circumference, centroid, and hull
                circumference = (c, (cx, cy))
                __circumferences.append(circumference)

                # test_image = __original_image.copy()
                # cv2.drawContours(test_image, [c], 0, (200, 0, 0), 2)
                # # cv2.drawContours(test_image, [hull], 0, (0, 200, 0), 2)
                # cv2.imshow("indi", test_image)
                # cv2.waitKey(0)


    print("# of circumferences:", len(__circumferences))

    if len(__circumferences) >= 2:
        return "OK"
    else:
        # reset
        reset_bsc_backend()
        return "Less than 2 circumferences where found in the image."


def render_boxes():
    """
    Generates images of each contour's bounding box (with horizontal and vertical bisections)

    :return: a list of bounding boxes in the following format: { "horizontal": (TkImage, width), "vertical": (TkImage, height) }
    """
    global __original_image, __contour_boxes

    boxes = []

    for box in __contour_boxes:

        # 1st of 2 output images: horizontal and vertical bisections
        orig_horizontal_line = __original_image.copy()

        # draw the actual boxes
        cv2.drawContours(orig_horizontal_line, [box.astype("int")], -1, color=(0, 255, 0), thickness=5)

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
        cv2.line(orig_vertical_line, (int(tl_tr_x), int(tl_tr_y)), (int(bl_br_x), int(bl_br_y)), (255, 0, 255), thickness=5)
        cv2.line(orig_horizontal_line, (int(tl_bl_x), int(tl_bl_y)), (int(tr_br_x), int(tr_br_y)), (255, 0, 255), thickness=5)

        # draw text on midpoint of lines
        # vertical
        (m_vertical_x, m_vertical_y) = midpoint((tl_tr_x, tl_tr_y), (bl_br_x, bl_br_y))
        cv2.putText(orig_vertical_line, "cm?", (int(m_vertical_x + 10), int(m_vertical_y)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), thickness=3)
        # horizontal
        (m_horizontal_x, m_horizontal_y) = midpoint((tl_bl_x, tl_bl_y), (tr_br_x, tr_br_y))
        cv2.putText(orig_horizontal_line, "cm?", (int(m_horizontal_x), int(m_horizontal_y + 40)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), thickness=3)

        # compute the Euclidean distance between the midpoints
        box_height = dist.euclidean((tl_tr_x, tl_tr_y), (bl_br_x, bl_br_y))
        box_width = dist.euclidean((tl_bl_x, tl_bl_y), (tr_br_x, tr_br_y))

        contour_box = {
            "horizontal": (convert_cv_to_pil(orig_horizontal_line), box_width),
            "vertical": (convert_cv_to_pil(orig_vertical_line), box_height)
        }

        boxes.append(contour_box)

    return boxes


def set_pixels_per_metric(value):
    global __pixels_per_metric
    __pixels_per_metric = value


def render_all_circumferences():
    circumference_images = []

    for circumference in __circumferences:
        cnt = circumference[0]
        circ_image = __original_image.copy()

        cv2.drawContours(circ_image, [cnt], 0, color=(0, 255, 0), thickness=3)

        # convert to PIL and add to result
        circumference_images.append(convert_cv_to_pil(circ_image))

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


def sort_circumferences():
    # get a reference of each circumference tuple (contour, centroid, hull)
    circumference_1 = __circumferences[0]
    circumference_2 = __circumferences[1]

    # find out which is bigger
    area_1 = len(circumference_1[0])
    area_2 = len(circumference_2[0])

    # outer circumference should come first
    if area_2 > area_1:
        __circumferences.reverse()
        print("order reversed")


def apply_hull_to_outer():
    outer = __circumferences[0]

    hull = outer[2]
    original_contour = outer[0]

    print("hull", len(hull))
    print("original", len(original_contour))


def render_final_circumferences():
    global __output_image

    output = __original_image.copy()
    # red, cyan
    colors = ((0, 0, 255), (255, 255, 0))

    sort_circumferences()
    # apply_hull_to_outer()

    for (circumference, color) in zip(__circumferences, colors):
        cnt = circumference[0]
        cx, cy = circumference[1]

        cv2.drawContours(output, [cnt], 0, color=color, thickness=3)
        cv2.circle(output, center=(cx, cy), radius=5, color=color, thickness=-1)

    __output_image = convert_cv_to_pil(output)

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
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # OPTION 1
    gray = cv2.GaussianBlur(gray, ksize=(5, 5), sigmaX=0)

    # OPTION 2
    # smooth out any background noise and preserve edges
    # gray = cv2.bilateralFilter(gray, d=5, sigmaColor=75, sigmaSpace=50)

    # perform edge detection, then perform a dilation + erosion to close gaps in between object edges
    # orig = 50, 100
    # test8: 50, 175 .. 100, 200... 22, 66
    edged = cv2.Canny(gray, threshold1=0, threshold2=60)
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


def convert_cv_to_pil(image):
    # swap color channels: BGR -> RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # convert the image to PIL format
    return Image.fromarray(image)


def midpoint(pt_a, pt_b):
    return (pt_a[0] + pt_b[0]) * 0.5, (pt_a[1] + pt_b[1]) * 0.5


def reset_bsc_backend():
    global __original_image, __pixels_per_metric, __contour_boxes, __circumferences, __output_image
    __original_image = None
    __pixels_per_metric = None
    __contour_boxes.clear()
    __circumferences.clear()
    __output_image = None


if __name__ == "__main__":
    print(process_image("C:/Users/arosa/PycharmProjects/BambooScanner/test3a.jpg"))
    set_pixels_per_metric(5.0)
    # print(circumferences_to_polar())
    # render_all_circumferences()
    # generate_text_file("C:/Users/arosa/PycharmProjects/BambooScanner/BSC_test.txt")
