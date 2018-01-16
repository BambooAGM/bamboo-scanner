from tkinter import *

from backend.bpc import set_sampleDescription, set_calibration_settings
from gui.widgets.custom import ScrollableTextArea, YellowButton, EntryWithPlaceholder
from gui.widgets.helpers import make_columns_responsive, make_rows_responsive


class ConfigBPC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Configuration"
        self.initialize_widgets()

    def initialize_widgets(self):
        # CALIBRATION

        # Ring diameter entry value
        self.ring_diameter_var = StringVar()
        self.ring_diameter_var.trace("w", self.update_begin_button)

        # Calibration object value
        self.calibration_object_var = StringVar()
        self.calibration_object_var.trace("w", self.update_begin_button)

        # Distance to end of rail value
        self.distance_z_var = StringVar()
        self.distance_z_var.trace("w", self.update_begin_button)

        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %P = value of the entry if the edit is allowed
        # %S = the text string being inserted or deleted, if any
        validate_cmd = (self.register(self.validate_dimension), '%d', '%P', '%S')

        # Calibration settings group
        self.calibration_settings = LabelFrame(self, text="Calibration Settings", fg="grey", padx=20, pady=20,
                                               font=self.controller.header_font)
        self.calibration_settings.grid(row=0, column=0, sticky=NS+W, padx=20, pady=20)

        # Ring diameter
        self.ring_diameter_label = Label(self.calibration_settings, text="Ring structure diameter", anchor=SW,
                                         font=self.controller.bold_font)
        self.ring_diameter_label.grid(row=0, column=0, sticky=SW, padx=20)

        self.ring_diameter_entry = EntryWithPlaceholder(self.calibration_settings, text_var=self.ring_diameter_var,
                                                        placeholder_text="0.00", validatecommand=validate_cmd,
                                                        validate="key", textvariable=self.ring_diameter_var)
        self.ring_diameter_entry.grid(row=1, column=0, sticky=NW, padx=20, pady=20)

        # Calibration object
        self.calibration_object_label = Label(self.calibration_settings, text="Calibration object radius",
                                              font=self.controller.bold_font, anchor=SW)
        self.calibration_object_label.grid(row=0, column=1, sticky=SW, padx=20)

        self.calibration_object_entry = EntryWithPlaceholder(self.calibration_settings, text_var=self.calibration_object_var,
                                                             placeholder_text="0.00", validatecommand=validate_cmd,
                                                             textvariable=self.calibration_object_var, validate="key")
        self.calibration_object_entry.grid(row=1, column=1, sticky=NW, padx=20, pady=20)

        # Distance to flat surface at end of rail
        self.distance_z_label = Label(self.calibration_settings, text="Distance to the end of the rail", anchor=SW,
                                      font = self.controller.bold_font)
        self.distance_z_label.grid(row=2, column=0, sticky=SW, padx=20)

        self.distance_z_entry = EntryWithPlaceholder(self.calibration_settings, text_var=self.distance_z_var,
                                                     placeholder_text="0.00", validate="key",
                                                     validatecommand=validate_cmd, textvariable=self.distance_z_var)
        self.distance_z_entry.grid(row=3, column=0, sticky=NW, padx=20, pady=20)

        # Invalid dimension message
        self.invalid_dimension = Label(self.calibration_settings, text="Dimension must be between 1 and 28 centimeters",
                                       fg="red", anchor=W)

        # make calibration section responsive
        make_columns_responsive(self.calibration_settings)
        make_rows_responsive(self.calibration_settings)

        # description label
        self.description_label = Label(self, text="Information about the sample (optional)",
                                       font=self.controller.bold_font)
        self.description_label.grid(row=1, column=0, sticky=SW, padx=20, pady=20)

        # Description text area
        self.text_area = ScrollableTextArea(self)
        self.text_area.grid(row=2, column=0, sticky=NW, padx=20)

        # begin button
        self.begin_button = YellowButton(self, text="BEGIN", command=self.begin,
                                         image=self.controller.arrow_right, compound=RIGHT)
        self.begin_button.grid(row=3, column=0, sticky=SE, padx=20, pady=20)

        # set placeholders
        self.ring_diameter_entry.set_placeholder()
        self.calibration_object_entry.set_placeholder()
        self.distance_z_entry.set_placeholder()

        make_rows_responsive(self)
        make_columns_responsive(self)

    def validate_dimension(self, action, value_if_allowed, text):
        # only when inserting
        if (action == "1"):
            if text in "0123456789.":
                try:
                    # maximum set by size of scanner (8.5 x 11 inches)
                    if float(value_if_allowed) >= 1.0 and float(value_if_allowed) <= 28.0:
                        # remove invalid message
                        self.invalid_dimension.grid_forget()
                        return True
                    else:
                        # Make system bell sound
                        self.bell()
                        # Show invalid message
                        self.invalid_dimension.grid(row=7, column=3, sticky=NSEW, padx=60, pady=20)
                        return False
                except ValueError:
                    self.bell()
                    return False
            else:
                self.bell()
                return False
        else:
            return True

    def update_begin_button(self, *args):
        ring_diameter = self.ring_diameter_var.get()
        calibration_obj = self.calibration_object_var.get()
        distance_z = self.distance_z_var.get()

        try:
            ring_diameter_ok = ring_diameter and float(ring_diameter) >= 1.0
            calibration_object_ok = calibration_obj and float(calibration_obj) >= 1.0
            distance_z_ok = distance_z and float(distance_z) >= 1.0

            # All entries filled
            if ring_diameter_ok and calibration_object_ok and distance_z_ok:
                self.begin_button.configure(state=NORMAL, cursor="hand2")
            else:
                self.begin_button.configure(state=DISABLED, cursor="arrow")
        except ValueError:
            print("cannot cast values to float")
            self.begin_button.configure(state=DISABLED, cursor="arrow")

    def begin(self):
        # save sample description
        set_sampleDescription(self.text_area.get_text())

        # save calibration settings
        ring_diameter = float(self.ring_diameter_var.get())
        calibration_obj = float(self.calibration_object_var.get())
        distance_z = float(self.distance_z_var.get())
        set_calibration_settings(ringDiameter=ring_diameter, obj_radius=calibration_obj, distance_z=distance_z)

        # Show sensors live feed
        self.controller.show_frame("MeasureBPC")

    def reset(self):
        # reset description
        self.text_area.clear_text()
