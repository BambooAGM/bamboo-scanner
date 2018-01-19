import os
import webbrowser
from tkinter import *
from tkinter import font

from PIL import Image, ImageTk

from gui.widgets.custom import GreenButton
from gui.widgets.helpers import make_columns_responsive, make_rows_responsive


class Home(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.bind("<<ShowFrame>>", self.on_show_frame)

        # Bamboo Scanner logo
        logo_image = ImageTk.PhotoImage(Image.open("assets/logo.png"))
        self.logo = Label(self, image=logo_image)
        self.logo.image = logo_image
        self.logo.grid(row=0, columnspan=2, sticky=S)

        # select a tool label
        self.select_label = Label(self, text="Select a tool:", font=self.controller.important_font, fg="grey")
        self.select_label.grid(row=1, column=0, columnspan=2, sticky=S)

        # Buttons font
        buttons_font = font.Font(family="Segoe UI Emoji", size=26)

        # BPC
        self.bpc_button = GreenButton(self, text="Pole", command=self.open_bpc, font=buttons_font)
        self.bpc_button.grid(row=2, column=0, sticky=S)

        self.bpc_description = Label(self, fg="#333333", text="Measure the external surface\n of a bamboo pole")
        self.bpc_description.grid(row=3, column=0, rowspan=2, sticky=N)

        # BSC
        self.bsc_button = GreenButton(self, text="Slice", command=self.open_bsc, font=buttons_font)
        self.bsc_button.grid(row=2, column=1, sticky=S)

        self.bsc_description = Label(self, fg="#333333",
                                     text="Measure the inner and outer\n circumferences of a\n bamboo cross section")
        self.bsc_description.grid(row=3, column=1, rowspan=3, sticky=N)

        # guide link
        self.guide_button = Button(self, text="First time? Open tutorial", relief=FLAT, command=self.open_guide,
                                   fg="blue", font=self.controller.underlined_font)
        self.guide_button.grid(row=4, columnspan=2)

        make_rows_responsive(self)
        make_columns_responsive(self)

    def on_show_frame(self, event):
        self.controller.hide_navbar()

    def open_bpc(self):
        self.controller.restore_navbar()

        # reset bpc
        self.controller.reset_BPC()

        self.controller.show_frame("ConfigBPC")

    def open_bsc(self):
        self.controller.restore_navbar()

        # reset bsc
        self.controller.reset_BSC()

        self.controller.show_frame("ConfigBSC")

    def open_guide(self):
        my_path = os.path.dirname(__file__)
        # path to pdf file
        path = os.path.join(my_path, "../assets/HOWTO.pdf")
        # open it
        webbrowser.open_new(path)
