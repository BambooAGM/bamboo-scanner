from tkinter import *
from gui.widgets.grid_helpers import make_rows_responsive, make_columns_responsive
from gui.widgets.custom import TableLeftHeaders, YellowButton, GreenButton


class MeasureBPC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Live Sensor Readings (cm)"
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def initialize_widgets(self):
        # 12 IR sensors
        sensor_headers = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12"]
        self.table = TableLeftHeaders(self, rows=len(sensor_headers), columns=1, header_values=sensor_headers)
        self.table.grid(row=0, column=0, rowspan=4)

        # Sensor Z
        self.z_value = StringVar()
        self.z_label = Label(self, textvariable=self.z_value, font=self.controller.important_font)
        self.z_label.grid(row=0, column=1, sticky=S)

        # captured count
        self.count_str = StringVar()
        self.count_number = IntVar()
        self.count_number.trace("w", self.update_count_label)
        self.count_number.set(0)
        self.captured_count = Label(self, textvariable=self.count_str, font=self.controller.bold_font)
        self.captured_count.grid(row=1, column=1, sticky=S, pady=5)

        # capture button
        self.capture_button = YellowButton(self, text="CAPTURE", command=self.capture)
        self.capture_button.grid(row=2, column=1, sticky=N)

        # view results button
        self.results_button = GreenButton(self, text="VIEW RESULTS", command=self.view_results,
                                          image=self.controller.arrow_right, compound=RIGHT)
        self.results_button.grid(row=3, column=1)

        make_rows_responsive(self)
        make_columns_responsive(self)

    def on_show_frame(self, event=None):
        # update page title
        self.controller.update_page_title(self.title)
        #TODO update count label
        # self.count_number.set(0)
        self.validate_count()
        self.do_sensors_update = True
        self.update_sensors()

    def update_sensors(self):
        # TODO get data from backend
        sensors_data = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        # self.after(1000)  # simulate long process
        self.table.update_cells(sensors_data)
        self.z_value.set("Z = 20 cm")
        print("updated sensors")
        # if self.do_sensors_update:
        #     self.after(500, self.update_sensors)

    def capture(self):
        #bpc.save_measurements()
        self.count_number.set(self.count_number.get() + 1)
        # only need to validate on the first capture
        if self.count_number.get() == 1:
            self.validate_count()
        print("captured")

    def validate_count(self):
        if self.count_number.get():
            self.results_button.configure(state=NORMAL)
        else:
            self.results_button.configure(state=DISABLED)

    def update_count_label(self, *args):
        self.count_str.set(str(self.count_number.get()) + " measurements captured")

    def view_results(self):
        # TODO stop updating sensors??
        self.do_sensors_update = False
        self.controller.show_frame("ResultsBPC")
