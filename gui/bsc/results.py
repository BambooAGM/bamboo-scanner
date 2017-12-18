from datetime import datetime
from tkinter import filedialog, messagebox
from tkinter import *
from backend.bsc import *
from gui.widgets.custom import RedButton, YellowButton
from gui.widgets.grid_helpers import make_columns_responsive


class ResultsBSC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Results"
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def initialize_widgets(self):
        # Result image
        self.image_container = Label(self, width=400, height=400)
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
        self.controller.update_page_title(self.title)

        self.image = render_final_circumferences()
        self.image_container.configure(image=self.image)

    def save(self):
        date = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        save_path = filedialog.asksaveasfilename(title="Save as", defaultextension=".txt", initialfile="BSC_" + date)

        # make sure the user didn't cancel the dialog
        if len(save_path) > 0:
            if generate_text_file(save_path):
                # all good
                messagebox.showinfo("Success!", "File was generated successfully.")
                self.restart_bsc()
            else:
                messagebox.showerror("Error generating text file", "Make sure you have access to the selected destination.")

    def discard(self):
        result = messagebox.askokcancel("Discard results?", "All progress will be lost.", default="cancel", icon="warning")
        if result:
            self.restart_bsc()

    def restart_bsc(self):
        # Clear result image
        self.image_container.configure(image=None)
        self.image = None

        # go to BSC Configuration page
        self.controller.show_frame("ConfigBSC")
