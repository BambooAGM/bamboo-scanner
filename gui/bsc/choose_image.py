from tkinter import *
from tkinter import filedialog, messagebox

from backend.bsc import *
from gui.widgets.custom import YellowButton, GreenButton, ResponsiveImage
from gui.widgets.helpers import make_rows_responsive, make_columns_responsive


class ConfigBSC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Select a bamboo slice image"
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def initialize_widgets(self):
        # Watchers

        # on image path change
        self.image_path = StringVar()
        self.image_path.trace("w", self.on_image_path_change)

        # responsive image container
        self.placeholder_image = Image.open("assets/placeholder_image.png")
        self.responsive_image = ResponsiveImage(self, self.placeholder_image)
        self.responsive_image.grid(row=0, column=0, rowspan=4)

        # choose image button
        self.choose_button = GreenButton(self, text="Choose an image", command=self.load_image)
        self.choose_button.grid(row=0, column=1, sticky=S)

        # selected image path
        self.path_entry = Entry(self, textvariable=self.image_path, state="readonly")
        self.path_entry.grid(row=1, column=1, sticky=EW, padx=20)

        # status message in row 2
        self.message_var = StringVar()
        self.message = Label(self, textvariable=self.message_var, font=self.controller.header_font)

        # begin button
        self.begin_button = YellowButton(self, text="BEGIN", command=self.begin, image=self.controller.arrow_right, compound=RIGHT)
        self.begin_button.grid(row=3, column=1, sticky=SE, padx=20, pady=20)

        # Update widgets
        self.on_image_path_change()

        # visited flag
        self.visit_counter = 0

        make_rows_responsive(self)
        make_columns_responsive(self)

    def load_image(self):
        # open a file chooser dialog and allow the user to select a source image
        temp_path = filedialog.askopenfilename(title="Select an image to process",
                                               filetypes=(("JPG", "*.jpg"),
                                                          ("JPEG", "*.jpeg"),
                                                          ("PNG", "*.png"),
                                                          ("TIF", "*.tif"),
                                                          ("TIFF", "*.tiff"),
                                                          ("Windows bitmaps", "*.bmp")))

        # ensure a file path was selected
        if len(temp_path) > 0:
            # disable button before processing
            self.begin_button.configure(state=DISABLED, cursor="wait")

            # Process image
            self.circumferences_found = process_image(temp_path)

            # update image path, message, and begin button
            self.image_path.set(temp_path)

            # image not found
            if self.circumferences_found is None:
                # show error message
                messagebox.showerror("Could not process image", "The image may have been moved or renamed, or you may not have access to it.")

            else:
                # Not a fresh session
                if self.visit_counter > 1:
                    # reset the BSC GUI except this frame
                    self.controller.reset_BSC_GUI(ignored=[type(self)])

                    # make this the 1st visit
                    self.visit_counter = 1

                # user image with all detected circumferences outlined
                image = get_config_image()

                # make it responsive
                self.responsive_image.destroy()
                self.responsive_image = ResponsiveImage(self, image)
                self.responsive_image.grid(row=0, column=0, rowspan=4, sticky=NSEW, pady=20)

    def on_image_path_change(self, *args):
        # image is selected
        if self.image_path.get():

            # show image path
            self.path_entry.grid()
            self.choose_button.configure(text="Change image")

            # error processing image or none found
            if self.circumferences_found is None or self.circumferences_found == 0:
                # disable begin button
                self.begin_button.configure(state=DISABLED, cursor="arrow")

                # make message red
                self.message.configure(fg="red")

                # error processing image
                if self.circumferences_found is None:
                    self.message_var.set("Error processing selected image")

                    # show placeholder image
                    self.set_placeholder_image()

                # none found
                else:
                    self.message_var.set(str(self.circumferences_found) + " circumference(s) found.\n Choose another image.")

            # some where found
            else:
                # enable begin button
                self.begin_button.configure(state=NORMAL, cursor="hand2")

                # make message green
                self.message.configure(fg="#35AD35")

                # 1 or 2 found
                if self.circumferences_found <= 2:
                    self.message_var.set("Bamboo slice detected!\n No need to choose circumferences.")

                # more than 2 found
                else:
                    self.message_var.set(str(self.circumferences_found) + " circumferences found.\n You must choose two of them.")

            # show the message
            self.message.grid(row=2, column=1, padx=20)

        # not selected
        else:
            self.begin_button.configure(state=DISABLED, cursor="arrow")
            self.path_entry.grid_remove()
            self.choose_button.configure(text="Choose an image")

            # hide the message
            self.message.grid_remove()

    def begin(self):
        # Go to pick circumferences if found more than 2
        if get_number_original_circumferences() > 2:
            self.controller.show_frame("PickCircumferencesBSC")

        # Go to configure scale
        else:
            self.controller.show_frame("RefObjectBSC")

    def on_show_frame(self, event=None):
        self.visit_counter += 1

    def set_placeholder_image(self):
        self.responsive_image.destroy()
        self.responsive_image = ResponsiveImage(self, self.placeholder_image)
        self.responsive_image.grid(row=0, column=0, rowspan=4)

    def reset(self):
        # reset to placeholder image
        self.set_placeholder_image()

        # Clear image path
        self.image_path.set("")

        # visited flag
        self.visit_counter = 0
