import queue
import threading
from tkinter import messagebox
from tkinter import *
from gui.widgets.grid_helpers import make_rows_responsive, make_columns_responsive
from gui.widgets.custom import TableLeftHeaders, YellowButton, GreenButton
from backend.sensors_manager import getInstantRawSensorData, openArduinoSerial, closeArduinoSerial
from serial import SerialException


def get_live_sensors(widget, read_sensors, main_quit, no_arduino, disconnected, port_lock):
    """
    Runs in a separate thread to retrieve live sensor data and display it without blocking the GUI.

    :param widget: The widget whose queue we are populating (MeasureBPC Frame)
    :param read_sensors: controls when it should read from the serial port
    :param main_quit: signals the main thread has ended, and so shall the threads
    :param no_arduino: event when arduino is not found
    :param disconnected: event when not able to read from serial
    :param port_lock: semaphore to avoid race on serial port
    :return: None
    """
    # Semaphore lock to guarantee only 1 thread at a time
    with port_lock:
        print("new thread")

        # open serial port
        try:
            openArduinoSerial()
        except IOError:
            no_arduino.set()
            print("no arduino found")
            return

        # Notify we are reading
        read_sensors.set()

        # Keep reading sensors
        while read_sensors.is_set():
            try:
                # Fetch sensor data from arduino
                data = getInstantRawSensorData()
            except SerialException:
                disconnected.set()
                read_sensors.clear()
                print("arduino disconnected")
                return

            # Place data in queue so widget can access it in a non-blocking way
            widget.add_to_queue(data)

            # Check if main thread has closed
            if main_quit.is_set():
                read_sensors.clear()
                closeArduinoSerial()
                print("program closing")
                return

        # read_sensors was cleared; stop reading
        closeArduinoSerial()
        print("thread finished")


class MeasureBPC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Live Sensor Readings (cm)"
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)
        self.bind("<<LeaveFrame>>", self.on_leave_frame)

        # Live feed threading
        self.queue = queue.LifoQueue()
        self.port_lock = threading.Semaphore()

        # Signals we are reading
        self.read_sensors = threading.Event()
        # Error flags
        self.no_arduino = threading.Event()
        self.disconnected = threading.Event()

    def add_to_queue(self, data):
        self.queue.put(data)

    def initialize_widgets(self):
        # Watchers
        # Update captured count
        self.count_str = StringVar()
        self.count_number = IntVar()
        self.count_number.trace("w", self.update_count_label)
        self.count_number.set(0)

        # Loading message
        self.loading_text = Label(self, text="One moment please... Initializing sensors.")
        self.loading_text.grid(row=0, column=0, columnspan=2)

        # 12 IR sensors
        sensor_headers = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12"]
        self.table = TableLeftHeaders(self, rows=len(sensor_headers), columns=1, header_values=sensor_headers)
        self.table.grid(row=1, column=0, rowspan=4)

        # Sensor Z
        self.z_value = StringVar()
        self.z_label = Label(self, textvariable=self.z_value, font=self.controller.important_font)
        self.z_label.grid(row=1, column=1, sticky=S)

        # captured count
        self.captured_count = Label(self, textvariable=self.count_str, font=self.controller.bold_font)
        self.captured_count.grid(row=2, column=1, sticky=S, pady=5)

        # capture button
        self.capture_button = YellowButton(self, text="CAPTURE", command=self.capture)
        self.capture_button.grid(row=3, column=1, sticky=N)

        # view results button
        self.results_button = GreenButton(self, text="View Results", command=self.view_results,
                                          image=self.controller.arrow_right, compound=RIGHT)
        self.results_button.grid(row=4, column=1)

        make_rows_responsive(self)
        make_columns_responsive(self)

    def on_show_frame(self, event=None):
        #TODO update count label
        # bpc.get_number_captured()
        self.update_results_button()

        # Controls update callback
        self.do_update = True
        # Flag to only update buttons and message when necessary
        self.loading_set = False
        # update GUI
        self.update_sensors()

        # Open port and start reading
        self.run_live_thread()

    def run_live_thread(self):
        self.live_thread = threading.Thread(target=get_live_sensors, name="live_sensors",
                                            args=(self, self.read_sensors, self.controller.main_quit,
                                                  self.no_arduino, self.disconnected, self.port_lock))
        self.live_thread.start()

    def update_sensors(self):
        # No Arduino found alert
        if self.no_arduino.is_set():
            self.no_arduino.clear()

            result = messagebox.askretrycancel("Error opening serial port",
                                               "Make sure the Arduino is properly connected, and try again.",
                                               icon="error")
            # Retry
            if result:
                # open new thread
                self.run_live_thread()
            else:
                self.controller.show_frame("ConfigBPC")
                return

        # Arduino disconnected alert
        if self.disconnected.is_set():
            self.disconnected.clear()

            result = messagebox.askretrycancel("Error reading from Arduino",
                                               "Make sure the Arduino is properly connected, and try again.",
                                               icon="error")
            # Retry
            if result:
                # open new thread
                self.run_live_thread()
            else:
                self.controller.show_frame("ConfigBPC")
                return

        # Update from queue
        if self.read_sensors.is_set():
            try:
                while True:
                    data = self.queue.get_nowait()
                    # print(data)

                    # Update GUI with new sensor data
                    self.table.update_cells(data[0: len(data) - 1])
                    self.z_value.set("Z = " + data[len(data) - 1] + " cm")

                    if self.loading_set:
                        # Hide loading message
                        self.loading_text.grid_remove()
                        # Restore buttons
                        self.capture_button.configure(state=NORMAL)
                        self.results_button.configure(state=NORMAL)
                        self.loading_set = False

                    self.update_idletasks()
            except queue.Empty:
                pass

        # Sensors are still initializing
        elif not self.read_sensors.is_set() and self.do_update:
            if not self.loading_set:
                # Show loading message
                self.loading_text.grid()
                # Disable buttons
                self.capture_button.configure(state=DISABLED)
                self.results_button.configure(state=DISABLED)
                self.loading_set = True

        # Keep updating until exit signal is received or we leave this frame
        if not self.controller.main_quit.is_set() and self.do_update:
            self.after(100, self.update_sensors)

    def on_leave_frame(self, event=None):
        # stop live feed and close serial port
        self.read_sensors.clear()
        self.do_update = False

    def capture(self):
        # TODO
        # bpc.save_measurements()
        # update captured count label
        self.count_number.set(self.count_number.get() + 1)

        # enable view results button after the 1st capture
        if self.count_number.get() == 1:
            self.update_results_button()
        print("captured")

    def update_results_button(self):
        if self.count_number.get():
            self.results_button.grid()
        else:
            self.results_button.grid_remove()

    def update_count_label(self, *args):
        self.count_str.set(str(self.count_number.get()) + " measurements captured")

    def view_results(self):
        self.controller.show_frame("ResultsBPC")

    def reset(self):
        # reset captured count
        self.count_number.set(0)
