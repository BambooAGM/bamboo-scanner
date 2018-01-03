import queue
import threading
from tkinter import *
from gui.widgets.grid_helpers import make_rows_responsive, make_columns_responsive
from gui.widgets.custom import TableLeftHeaders, YellowButton, GreenButton
from backend.sensors_manager import getInstantRawSensorData, openArduinoSerial, closeArduinoSerial


def get_live_sensors(widget, read_sensors, program_closed, port_closed):
    """
    Background thread to read from sensors into a queue

    :param widget: The measure_BPC Frame
    :return: None
    """
    # Wait for the previous thread to finish
    print("new thread")
    port_closed.wait()
    print("is closed")

    # open serial port
    openArduinoSerial()
    # send signal when it opens
    port_closed.clear()

    # wait for signal to read
    read_sensors.wait()

    # read signal received
    while read_sensors.is_set():
        # Fetch sensor data from arduino
        data = getInstantRawSensorData()

        # Place data in queue so widget can access it in a non-blocking way
        widget.add_to_queue(data)

        # Check if main thread has closed
        if program_closed.is_set():
            closeArduinoSerial()
            port_closed.set()
            print("program closing")
            return

    # stop reading
    closeArduinoSerial()
    port_closed.set()
    print("thread finished")


class MeasureBPC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Live Sensor Readings (cm)"
        self.queue = queue.LifoQueue()
        self.port_closed = threading.Event()
        self.port_closed.set()
        self.read_sensors = threading.Event()
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)
        self.bind("<<LeaveFrame>>", self.on_leave_frame)

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

        # Show loading message
        self.loading_text.grid()

        # open port and start reading
        self.live_thread = threading.Thread(target=get_live_sensors, name="live_sensors",
                                            args=(self, self.read_sensors, self.controller.program_closed, self.port_closed))
        self.live_thread.start()

        # send read signal
        self.read_sensors.set()

        # update GUI
        self.update_sensors()

    def update_sensors(self):
        # not closed == opened
        if not self.port_closed.is_set():
            self.loading_text.grid_remove()

        # Update from queue
        if self.read_sensors.is_set():
            try:
                while True:
                    data = self.queue.get_nowait()
                    # print(data)

                    # Update GUI with new sensor data
                    if self.read_sensors.is_set():
                        self.table.update_cells(data[0: len(data) - 1])
                        self.z_value.set("Z = " + data[len(data) - 1] + " cm")

                    self.update_idletasks()
            except queue.Empty:
                pass

            self.after(100, self.update_sensors)

    def on_leave_frame(self, event=None):
        # stop live feed and close serial port
        self.read_sensors.clear()

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
