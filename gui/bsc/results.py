from tkinter import messagebox
from tkinter import *
from backend.bsc import *
from gui.widgets.custom import RedButton, YellowButton
from gui.widgets.grid_helpers import make_columns_responsive


class ResultsBSC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def initialize_widgets(self):
        # Result image
        self.image_container = Label(self)
        self.image_container.grid(row=0, columnspan=2)

        # Save button
        self.save_button = YellowButton(self, text="SAVE", command=self.save, image=self.controller.save_icon,
                                        compound=LEFT)
        self.save_button.grid(row=1, column=0)

        # Discard button
        self.discard_button = RedButton(self, text="DISCARD", command=self.discard)
        self.discard_button.grid(row=1, column=1)

        make_columns_responsive(self)

    def on_show_frame(self, event=None):
        # update page title
        #self.controller.update_page_title(self.title)
        self.image_container.configure(image=get_output_image())

    def save(self):
        for (x, y, r) in get_circumferences():
            print(x, y, r)
        # TODO generate text file and show confirmation
        self.restart_bsc()

    def discard(self):
        result = messagebox.askokcancel("Discard results?", "All progress will be lost.", default="cancel", icon="warning")
        if result:
            self.restart_bsc()

    def restart_bsc(self):
        # Clear result image
        self.image_container.configure(image=None)

        # go to BSC Configuration page
        self.controller.show_frame("ConfigBSC")
