from datetime import datetime
from tkinter import filedialog, messagebox
from tkinter import *
from backend.bsc import *
from gui.widgets.custom import RedButton, YellowButton, ResponsiveImage
from gui.widgets.grid_helpers import make_columns_responsive


class ResultsBSC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Slice Results"
        self.responsive_image = None
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def initialize_widgets(self):

        # header message
        self.result_message = Label(self, text="Final Circumferences", font=self.controller.header_font)
        self.result_message.grid(row=0, column=0, columnspan=2, pady=20)

        # Result image
        # self.image_container = Label(self)
        # self.image_container.grid(row=1, columnspan=2)

        # save hint
        self.result_message = Label(self, text="Save to see all polar coordinates.")
        self.result_message.grid(row=2, column=0, columnspan=2, pady=20)

        # Save button
        self.save_button = YellowButton(self, text="SAVE", command=self.save, image=self.controller.save_icon,
                                        compound=LEFT)
        self.save_button.grid(row=3, column=0, sticky=E, padx=5, pady=20)

        # Discard button
        self.discard_button = RedButton(self, text="DISCARD", command=self.discard)
        self.discard_button.grid(row=3, column=1, sticky=W, padx=5, pady=20)

        make_columns_responsive(self)

    def on_show_frame(self, event=None):
        # render image with all circumferences
        self.image = render_final_circumferences()
        # self.image_container.configure(image=self.image)
        self.responsive_image = ResponsiveImage(self, self.image)
        self.responsive_image.grid(row=1, columnspan=2)

    def save(self):
        date = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        save_path = filedialog.asksaveasfilename(title="Save as", defaultextension=".txt", initialfile="BSC_" + date)

        # make sure the user didn't cancel the dialog
        if len(save_path) > 0:
            if generate_text_file(save_path):
                # all good
                messagebox.showinfo("Success!", "File was generated successfully.")
                # reset BSC
                self.controller.reset_BSC()
                # go to BSC Configuration page
                self.controller.show_frame("ConfigBSC")
            else:
                messagebox.showerror("Error generating text file", "Make sure you have access to the selected destination.")

    def discard(self):
        result = messagebox.askokcancel("Discard results?", "All progress will be lost.", default="cancel", icon="warning")
        if result:
            # reset BSC
            self.controller.reset_BSC()
            # go to BSC Configuration page
            self.controller.show_frame("ConfigBSC")

    def reset(self):
        # destroy the image container
        if self.responsive_image is not None:
            self.responsive_image.destroy()
            self.responsive_image = None
            self.image = None
