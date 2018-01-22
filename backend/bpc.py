import numpy as np

from backend.sensors_manager import distToPointSingleIRSensor, sensorArray
from backend.utils import get_timestamp, twoPointDistance

sample_description = ""
saved_measurement = []

# calibration settings
ring_diameter = 0.0
calibration_obj_diameter = 0.0
rail_z_distance = 0.0


# Resets all global variables in case of a discard or return home
def reset_bpc_backend():
    global sample_description, saved_measurement, ring_diameter, calibration_obj_diameter, rail_z_distance
    sample_description = ""
    saved_measurement.clear()

    ring_diameter = 0.0
    calibration_obj_diameter = 0.0
    rail_z_distance = 0.0


def get_calibration_settings():
    return ring_diameter, calibration_obj_diameter, rail_z_distance


def set_calibration_settings(ringDiameter, obj_diameter, distance_z):
    global ring_diameter, calibration_obj_diameter, rail_z_distance

    ring_diameter = ringDiameter
    calibration_obj_diameter = obj_diameter
    rail_z_distance = distance_z


# Sample Description, user input
def set_sampleDescription(description):
    global sample_description

    sample_description = description


def save_measurements(array):
    global saved_measurement

    saved_measurement.append(array)


# Sorts the measurements list for preview display and text file generation.
def sort_ByZeta(array):
    if not array:
        print("Array must not be empty")

    array.sort(key=lambda x: x[len(array) - 1])

    return array


def delete_measurement(array):
    """
    Deletes any number of saved measurements.

    :param array: Deleted indices from saved measurements.
    """
    global saved_measurement

    if not array:
        return saved_measurement

    adjust = 0
    for i in range(0, len(array)):
        del saved_measurement[array[i] - adjust]
        adjust += 1

    return saved_measurement


def extract_data_from_saved_measurements():
    """
    Translates recorded distances into rectangular coordinates.

    :return: x, y, z coordinates for each snapshot, along with its centroid and average diameter
    return format = ((xS, yS, zS), (centroid_xS, centroid_yS, centroid_zS), avg_diameters)
    """
    # surface coordinates
    temp_xS = []
    temp_yS = []
    temp_zS = []

    # centroid coordinates
    temp_centroid_xS = []
    temp_centroid_yS = []
    temp_centroid_zS = []

    # average diameters; correspond to the centroid zS
    temp_average_diameters = []

    # convert captured measurements into rectangular coordinates
    for sensor_data in saved_measurement:
        # reading from sensor Z * applied calibration factor
        z = sensor_data[-1] * sensorArray[-1].factor

        # store diameters here to calculate average
        temp_diameters = []

        # convert IR sensor readings to x, y
        for i in range(len(sensor_data) - 1):
            (x, y) = distToPointSingleIRSensor(s=sensorArray[i], distanceMeasured=sensor_data[i])

            # radius
            r = twoPointDistance((x, y), (0.0, 0.0))

            # save diameter for average
            temp_diameters.append(r * 2.0)

            # save them separately
            temp_xS.append(x)
            temp_yS.append(y)
            temp_zS.append(z)

        # calculate centroid for this group of sensor data
        centroid_x = np.mean(temp_xS)
        centroid_y = np.mean(temp_yS)

        # save them separately
        temp_centroid_xS.append(centroid_x)
        temp_centroid_yS.append(centroid_y)
        temp_centroid_zS.append(z)

        # calculate average diameter
        average_diameter = np.mean(temp_diameters)
        temp_average_diameters.append(average_diameter)

    return ((temp_xS, temp_yS, temp_zS), (temp_centroid_xS, temp_centroid_yS, temp_centroid_zS), temp_average_diameters)


def generate_text_file(file_path):
    global sample_description

    ((xS, yS, zS), (centroid_xS, centroid_yS, centroid_zS), avg_diameters) = extract_data_from_saved_measurements()

    try:
        f = open(file_path, "w+")
        f.write(get_timestamp())
        f.write("\n")

        # write sample description
        f.write("Bamboo sample description:\n")
        f.write("%s\n" % sample_description)
        f.write("\n")

        # write x, y, z coordinates
        f.write("Rectangular coordinates: (%s different Zs)\n" % len(avg_diameters))
        f.write("x, y, z\n")
        for (x, y, z) in zip(xS, yS, zS):
            f.write("%s, %s, %s\n" % (x, y, z))
        f.write("\n")

        # write centroids
        f.write("Centroids:\n")
        f.write("x, y, z\n")
        for (x, y, z) in zip(centroid_xS, centroid_yS, centroid_zS):
            f.write("%s, %s, %s\n" % (x, y, z))
        f.write("\n")

        # write average diameter
        f.write("Average Diameters:\n")
        f.write("z, avg diameter\n")
        for (z, avg_diameter) in zip(centroid_zS, avg_diameters):
            f.write("%s, %s\n" % (z, avg_diameter))
        f.write("\n")

        f.close()
        return True

    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
        return False
