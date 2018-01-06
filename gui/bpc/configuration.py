from tkinter import *
from backend.bpc import set_sampleDescription
from gui.widgets.grid_helpers import make_columns_responsive, make_rows_responsive
from gui.widgets.custom import ScrollableTextArea, YellowButton


class ConfigBPC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Calibration"
        self.initialize_widgets()

    def initialize_widgets(self):
        # text area label
        self.description_label = Label(self, text="Information about the sample", font=self.controller.bold_font)
        self.description_label.grid(row=0, column=0, sticky=SW, padx=20, pady=20)

        # text area
        self.text_area = ScrollableTextArea(self)
        self.text_area.grid(row=1, column=0, sticky=N+E+W, padx=20)

        # begin button
        self.begin_button = YellowButton(self, text="BEGIN", command=self.begin, image=self.controller.arrow_right, compound=RIGHT)
        self.begin_button.grid(row=2, column=0, sticky=SE, padx=20, pady=20)

        make_rows_responsive(self)
        make_columns_responsive(self)

    def begin(self):
        text = self.text_area.text.get(1.0, END)
        set_sampleDescription(text)
        self.controller.show_frame("MeasureBPC")

    def reset(self):
        # reset description
        self.text_area.text.delete(1.0, END)
