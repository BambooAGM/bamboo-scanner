from tkinter import *

from backend.bsc import *
from gui.widgets.custom import YellowButton, GreenButton, RedButton, ResponsiveImage
from gui.widgets.helpers import make_columns_responsive, make_rows_responsive


class PickCircumferencesBSC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Select the slice's circumferences"
        self.circumferences = []
        self.selected_circumferences = []
        self.responsive_image = None
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def initialize_widgets(self):
        # Watchers

        # Update state of navigation buttons
        self.current_circumference_var = IntVar()
        self.current_circumference_var.trace("w", self.update_navigation)

        # Update count label
        self.selected_count_var = IntVar()
        self.selected_count_var.trace("w", self.update_count_text)

        # Update buttons
        self.selected_count_text = StringVar()
        self.selected_count_text.trace("w", self.update_buttons)

        # title of circumference image
        self.circumference_title_var = StringVar()
        self.circumference_title = Label(self, textvariable=self.circumference_title_var, font=self.controller.header_font)
        self.circumference_title.grid(row=0, column=0, sticky=W, padx=20, pady=20)

        # Controls to navigate contours
        self.prev_button = GreenButton(self, text="Previous", image=self.controller.arrow_left, compound=LEFT,
                                       command=lambda: self.show_circumference(self.current_circumference_var.get() - 1))
        self.prev_button.grid(row=0, column=1, sticky=SE, padx=5, pady=20)

        self.next_button = GreenButton(self, text="Next", image=self.controller.arrow_right, compound=RIGHT,
                                       command=lambda: self.show_circumference(self.current_circumference_var.get() + 1))
        self.next_button.grid(row=0, column=2, sticky=SW, pady=20)

        # image in row=1, col=0, colspan=3, rowspan=4

        # instructions
        instructions_text = "More than 2 circumferences were found.\n"
        instructions_text += "Select the inner and outer circumference of the bamboo slice."
        self.instructions = Label(self, text=instructions_text, relief=GROOVE, padx=10, pady=10)
        self.instructions.grid(row=1, column=3, padx=40)

        # remove button
        self.remove_button = RedButton(self, text="Deselect circumference", command=self.deselect)
        self.remove_button.grid(row=2, column=3)

        # select button
        self.select_button = YellowButton(self, text="Use this circumference", command=self.select)
        self.select_button.grid(row=2, column=3)

        # Selection count
        self.selected_count = Label(self, textvariable=self.selected_count_text, font=self.controller.important_font)
        self.selected_count.grid(row=3, column=3, sticky=N)

        # confirm button
        self.confirm_button = YellowButton(self, text="CONFIRM", command=self.confirm, state=DISABLED, cursor="arrow")
        self.confirm_button.grid(row=4, column=3, sticky=SE, padx=20, pady=20)

        make_columns_responsive(self, ignored=[1, 2])
        make_rows_responsive(self, ignored=[0])

    def on_show_frame(self, event=None):
        # fetch all circumferences
        self.circumferences = render_all_circumferences()

        # initialize if it's empty
        if not self.selected_circumferences:
            # generate selected flags
            self.selected_circumferences = [False] * len(self.circumferences)

        # Show the last object we were browsing, or the 1st one if this is a fresh session
        try:
            self.show_circumference(self.current_circumference_var.get())
        # In case something weird happens
        except IndexError:
            print("could not show circumference; resetting")
            self.reset()
            self.on_show_frame()

    def show_circumference(self, index):
        self.current_circumference_var.set(index)
        image = self.circumferences[index]

        if self.responsive_image is not None:
            self.responsive_image.destroy()
        self.responsive_image = ResponsiveImage(self, image)
        self.responsive_image.grid(row=1, column=0, rowspan=4, columnspan=3, sticky=NSEW, pady=20)

    def update_navigation(self, *args):
        current = self.current_circumference_var.get()
        self.circumference_title_var.set("Circumference #" + str(current + 1))

        # toggle prev
        if current == 0:
            self.prev_button.configure(state=DISABLED, cursor="arrow")
        else:
            self.prev_button.configure(state=NORMAL, cursor="hand2")

        # toggle next
        if current == len(self.circumferences) - 1:
            self.next_button.configure(state=DISABLED, cursor="arrow")
        else:
            self.next_button.configure(state=NORMAL, cursor="hand2")

        # Toggle select and remove buttons
        self.update_select_remove_buttons()

    def update_buttons(self, *args):
        self.update_select_remove_buttons()
        self.update_confirm_button()

    def update_select_remove_buttons(self):
        # only if array has been initialized
        if len(self.selected_circumferences):

            # selected
            if self.selected_circumferences[self.current_circumference_var.get()]:
                # this one is selected; show remove button
                self.select_button.grid_remove()
                self.remove_button.grid()

            # not selected
            else:
                # show select button
                self.remove_button.grid_remove()
                self.select_button.grid()

                # 2 already selected; disable select button
                if self.selected_count_var.get() == 2:
                    self.select_button.configure(state=DISABLED, cursor="arrow")
                else:
                    # still can select; re-enable button
                    self.select_button.configure(state=NORMAL, cursor="hand2")

    def update_confirm_button(self):
        # Toggle confirm button
        if self.selected_count_var.get() == 2:
            self.confirm_button.configure(state=NORMAL, cursor="hand2")
        else:
            self.confirm_button.configure(state=DISABLED, cursor="arrow")

    def update_count_text(self, *args):
        # update label text
        self.selected_count_text.set(str(self.selected_count_var.get()) + " of 2 circumferences selected")

    def deselect(self):
        # deselect
        self.selected_circumferences[self.current_circumference_var.get()] = False

        # Decrease count
        self.selected_count_var.set(self.selected_count_var.get() - 1)

    def select(self):
        # mark as selected
        self.selected_circumferences[self.current_circumference_var.get()] = True

        # Increase count
        self.selected_count_var.set(self.selected_count_var.get() + 1)

    def confirm(self):
        selected = []

        for index, selected_flag in enumerate(self.selected_circumferences):
            if selected_flag:
                selected.append(index)

        # Apply in backend
        set_final_circumferences(selected)

        # Show results
        self.controller.show_frame("RefObjectBSC")

    def reset(self):
        # destroy the image container
        if self.responsive_image is not None:
            self.responsive_image.destroy()
            self.responsive_image = None

        # clear circumferences
        self.circumferences.clear()
        self.selected_circumferences.clear()
        self.selected_count_var.set(0)

        # Start showing 1st circumference
        self.current_circumference_var.set(0)
