import threading

from serial import SerialException

from backend.bpc import save_measurements, ring_diameter, calibration_obj_radius, rail_z_distance
from backend.sensors_manager import *

# Semaphore lock to guarantee only 1 thread at a time
port_lock = threading.Semaphore()

# Signals port is open
reading_sensors = threading.Event()

# Tells the thread to capture data; cleared when data is ready
capture_now = threading.Event()
# Tell the gui to grab the captured data
capture_done = threading.Event()

# Tells the thread to calibrate sensors; cleared when done
calibrate_now = threading.Event()
# Tell the gui to grab the calibration data
calibration_done = threading.Event()

# Signal to kill thread
kill_thread = threading.Event()
# Main program was closed
main_quit = threading.Event()

# Error flags
no_arduino = threading.Event()
disconnected = threading.Event()


def get_live_sensors(widget):
    """
    Runs in a separate thread to display live sensor data, capture measurements, and calibrate sensors
     without blocking the GUI.

    :param widget: The widget whose queue we are populating (MeasureBPC Frame)
    :return: None
    """
    # Semaphore lock to guarantee only 1 thread at a time
    with port_lock:
        # open serial port
        try:
            openArduinoSerial()
        except IOError:
            no_arduino.set()
            print("no arduino found")
            return

        # Notify we are reading
        reading_sensors.set()

        # Keep reading sensors
        while not main_quit.is_set() and not kill_thread.is_set():
            try:
                # User wants to capture data
                if capture_now.is_set():
                    # do not use cache
                    clearCache()

                    # Get sensor data
                    data = getCleanSensorData()
                    print("saving", data)

                    # Save data in backend
                    save_measurements(data)

                    # signal data has been captured
                    capture_done.set()

                # User wants to calibrate sensors
                elif calibrate_now.is_set():
                    # do not use cache
                    clearCache()

                    # init sensors
                    initSensors(structureRadius=ring_diameter * 0.5)

                    # clear cache again
                    clearCache()

                    # run calibration
                    calibrateAllSensors(testRadius=calibration_obj_radius, testDistance=rail_z_distance)
                    print(sensorArray)

                    # dev angle > 4.0

                    # signal calibration is done
                    calibration_done.set()

                # Show live feed
                else:
                    data = getInstantRawSensorData()
                    # Place data in queue so widget can access it in a non-blocking way
                    widget.add_to_queue(data)

            except SerialException:
                disconnected.set()
                reading_sensors.clear()
                print("arduino disconnected")
                return

        # kill signal received or main has ended
        reading_sensors.clear()
        kill_thread.clear()
        closeArduinoSerial()
        print("thread finished")
