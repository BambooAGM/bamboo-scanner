from tkinter import *
from backend.bsc import *
from gui.widgets.custom import YellowButton, GreenButton, ResponsiveImage
from gui.widgets.grid_helpers import make_rows_responsive, make_columns_responsive


class RefObjectBSC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Configure the reference object"
        self.responsive_image = None
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def initialize_widgets(self):
        # Watchers
        # Update state of navigation buttons
        self.current_contour_var = IntVar()
        self.current_contour_var.trace("w", self.update_navigation)

        # Switch between horizontal and vertical bisections
        self.dimension_type = StringVar()
        self.dimension_type.set("horizontal")
        self.dimension_type.trace("w", self.update_image)
        
        # Update confirm button state
        self.real_dimension_var = StringVar()
        self.real_dimension_var.trace("w", self.update_confirm_button)

        # title of ref object image
        self.ref_object_var = StringVar()
        self.ref_object_title = Label(self, textvariable=self.ref_object_var, font=self.controller.header_font)
        self.ref_object_title.grid(row=0, column=0, columnspan=2, pady=20)

        # Image
        # self.image_container = Label(self)
        # self.image_container.grid(row=1, column=0, rowspan=6, columnspan=2)

        # instructions
        instructions_text = "The reference object should be a figure for which its width or height is known.\n"
        instructions_text += "This will allow the program to calculate the real dimensions of the bamboo slice."
        self.instructions = Label(self, text=instructions_text, relief=GROOVE)
        self.instructions.grid(row=1, column=2, columnspan=2)

        # select dimension to enter for the reference object
        self.dimension_label = Label(self, text="Dimension I'm providing:", font=self.controller.header_font)
        self.dimension_label.grid(row=2, column=2)
        self.dimension_width = Radiobutton(self, text="Width", variable=self.dimension_type, value="horizontal")
        self.dimension_height = Radiobutton(self, text="Height", variable=self.dimension_type, value="vertical")
        self.dimension_width.grid(row=3, column=2)
        self.dimension_height.grid(row=4, column=2)

        # user entered dimension (for pixels-per-metric)
        self.real_dimension_label = Label(self, text="Dimension in centimeters:", font=self.controller.header_font)
        self.real_dimension_label.grid(row=5, column=2, pady=20)

        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %P = value of the entry if the edit is allowed
        # %S = the text string being inserted or deleted, if any
        validate_cmd = (self.register(self.validate_float), '%d', '%P', '%S')
        self.real_dimension = Entry(self, textvariable=self.real_dimension_var, validate="key", validatecommand=validate_cmd)
        self.real_dimension.grid(row=6, column=2)

        # Controls to navigate contours
        self.prev_button = GreenButton(self, text="Previous contour", image=self.controller.arrow_left, compound=LEFT,
                                       command=lambda: self.show_contour(self.current_contour_var.get() - 1))
        self.prev_button.grid(row=7, column=0, sticky=NE, padx=5, pady=20)

        self.next_button = GreenButton(self, text="Next contour", image=self.controller.arrow_right, compound=RIGHT,
                                       command=lambda: self.show_contour(self.current_contour_var.get() + 1))
        self.next_button.grid(row=7, column=1, sticky=NW, padx=5, pady=20)

        # confirm button
        self.confirm_button = YellowButton(self, text="CONFIRM", command=self.confirm)
        self.confirm_button.grid(row=8, column=3, sticky=E, padx=10)

        # make_rows_responsive(self)
        make_columns_responsive(self)

    def on_show_frame(self, event=None):
        # fetch 1st contour
        self.boxes_len = get_number_contours()
        self.show_contour(0)
        self.update_confirm_button()

    def show_contour(self, index):
        self.box = render_box(index)
        self.current_contour_var.set(index)
        self.update_image()

    def update_image(self, *args):
        image = self.box[self.dimension_type.get()][0]
        # update image container
        # self.image_container.configure(image=image)
        if self.responsive_image is not None:
            self.responsive_image.destroy()
        self.responsive_image = ResponsiveImage(self, image)
        self.responsive_image.grid(row=1, column=0, rowspan=6, columnspan=2)

    def update_navigation(self, *args):
        current = self.current_contour_var.get()
        # update image title
        self.ref_object_var.set("Object #" + str(current + 1))

        # toggle prev
        if current == 0:
            self.prev_button.configure(state=DISABLED)
        else:
            self.prev_button.configure(state=NORMAL)

        # toggle next
        if current == self.boxes_len - 1:
            self.next_button.configure(state=DISABLED)
        else:
            self.next_button.configure(state=NORMAL)

    def validate_float(self, action, value_if_allowed, text):
        # only when inserting
        if (action == "1"):
            if text in "0123456789.":
                try:
                    # maximum 50 centimeters
                    if float(value_if_allowed) <= 50.0:
                        return True
                    else:
                        return False
                except ValueError:
                    return False
            else:
                return False
        else:
            return True

    def update_confirm_button(self, *args):
        if self.real_dimension_var.get():
            self.confirm_button.grid()
        else:
            self.confirm_button.grid_remove()

    def confirm(self):
        # pixels per metric = distance in pixels / distance in centimeters
        ppm = self.box[self.dimension_type.get()][1] / float(self.real_dimension.get())
        set_pixels_per_metric(ppm)

        if get_number_circumferences() > 2:
            # More than 2 circumferences; must handpick
            self.controller.show_frame("PickCircumferencesBSC")
        else:
            # Show results
            self.controller.show_frame("ResultsBSC")

    def reset(self):
        # reset real dimension entry field
        self.real_dimension_var.set("")

        # destroy the image container
        if self.responsive_image is not None:
            self.responsive_image.destroy()
            self.responsive_image = None
