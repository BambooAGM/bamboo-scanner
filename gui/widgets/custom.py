from tkinter import *
from tkinter import font

from PIL import ImageTk

from gui.widgets.helpers import resize_keep_aspect


class YellowButton(Button):

    def __init__(self, parent, **kwargs):
        Button.__init__(self, parent, **kwargs)
        self.configure(bg="#FF9900", relief=GROOVE, padx=10, pady=5, cursor="hand2")


class GreenButton(Button):

    def __init__(self, parent, **kwargs):
        Button.__init__(self, parent, **kwargs)
        self.configure(bg="#99CC33", relief=GROOVE, padx=10, pady=5, cursor="hand2")


class RedButton(Button):

    def __init__(self, parent, **kwargs):
        Button.__init__(self, parent, **kwargs)
        self.configure(bg="#FF3300", fg="#FFFFFF", relief=GROOVE, padx=10, pady=5, cursor="hand2")


class ScrollableTextArea(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        # Text input field
        self.text = Text(self, wrap=WORD, height=5)
        self.text.pack(side=LEFT, fill=BOTH, expand=True)

        # Vertical scroll bar
        self.scroll = Scrollbar(self)
        self.text.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side=RIGHT, fill=Y)

    def get_text(self):
        self.text.get(1.0, END)

    def clear_text(self):
        self.text.delete(1.0, END)


class VerticalTable(Frame):
    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent)

        # read keyword arguments
        self.rows = kwargs.pop("rows", 2)
        self.columns = kwargs.pop("columns", 2)

        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)

        # Variable text for each content cell
        self.cell_values = []
        for row in range(self.rows):
            temp_row = []
            for column in range(self.columns):
                temp_row.append(StringVar())
            self.cell_values.append(temp_row)

        # Make the cells of the table
        self.cells = []
        bold_font = font.Font(family="Segoe UI Emoji", size=13, weight="bold")

        for row in range(self.rows):
            temp_row = []
            for column in range(self.columns):
                cell = Label(self, textvariable=self.cell_values[row][column], borderwidth=1, width=10, relief="ridge",
                             bg="#5E5E5E", fg="#FFFFFF", font=bold_font)
                cell.grid(row=row, column=column, sticky=NSEW)
                temp_row.append(cell)
            self.cells.append(temp_row)

    def update_cells(self, new_values):
        # table has only 1 row; accept single array
        if self.rows == 1 and isinstance(new_values[0], str):
            try:
                for column in range(self.columns):
                    self.cell_values[0][column].set(new_values[column])
            except IndexError:
                print("Make sure the array contains a value for each row.")

        # has many columns; use multidimensional array
        else:
            try:
                for row in range(self.rows):
                    for column in range(self.columns):
                        self.cell_values[row][column].set(new_values[row][column])
            except IndexError:
                print("Your data does not match the dimensions of the table.")


class HorizontalTable(Frame):
    """
    A table with headers on the leftmost column. Data is filled column by column.

    :param rows: number of rows
    :param columns: number of columns (not counting the header)
    :param header_values: the text of the headers
    :param can_select_columns: shows checkboxes on top of table for each column, and an action button
    :param button_command: Action button's command
    """
    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent)

        # read keyword arguments
        self.rows = kwargs.pop("rows", 2)
        self.columns = kwargs.pop("columns", 2)
        self.header_values = kwargs.pop("header_values", None)
        self.can_select_columns = kwargs.pop("can_select_columns", False)
        self.button_command = kwargs.pop("button_command", None)

        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)

        if self.can_select_columns:
            # Delete button
            self.is_button_disabled = True
            self.delete_button = Button(self, text="Delete\nselected", state=DISABLED, relief=GROOVE)

            # save the original background color to restore it later
            self.disabled_background = self.delete_button.cget("background")

            # optional button callback
            if self.button_command:
                self.delete_button.configure(command=self.button_command)
            self.delete_button.grid(row=0, column=0, sticky=NSEW, pady=5)

            # Checkboxes value variable
            self.checkbox_values = []
            for column in range(self.columns):
                checkbox_value = IntVar()
                checkbox_value.trace("w", self.update_button)
                self.checkbox_values.append(checkbox_value)

            # The checkbox widgets
            self.checkboxes = []
            for column in range(self.columns):
                checkbox = Checkbutton(self, variable=self.checkbox_values[column], cursor="hand2")
                # offset by one column since delete button is in 1st column
                checkbox.grid(row=0, column=column + 1, sticky=S+E+W)
                self.checkboxes.append(checkbox)

        # Variable text for each content cell
        self.cell_values = []
        for row in range(self.rows):
            temp_row = []
            for column in range(self.columns):
                temp_row.append(StringVar())
            self.cell_values.append(temp_row)

        # Make header cells
        self.headers = []
        bold_font = font.Font(family="Segoe UI Emoji", size=13, weight="bold")
        for row in range(self.rows):
            header = Label(self, borderwidth=1, width=10, relief="ridge", bg="#C9C9C9", fg="#000000", font=bold_font)

            # add text value if provided
            if self.header_values:
                header.configure(text=self.header_values[row])

            # offset by one row since delete checkboxes are there
            header.grid(row=row + 1, column=0, sticky=NSEW)
            self.headers.append(header)

        # Make the cells of the table
        self.cells = []
        for row in range(self.rows):
            temp_row = []
            for column in range(self.columns):
                cell = Label(self, textvariable=self.cell_values[row][column], borderwidth=1, width=10, relief="ridge")
                # offset by one row and column since delete checkboxes are in the 1st row, and headers in the 1st column
                cell.grid(row=row + 1, column=column + 1, sticky=NSEW)
                temp_row.append(cell)
            self.cells.append(temp_row)

    def update_cells(self, new_values):
        # table has only 1 column; accept single array
        if self.columns == 1 and isinstance(new_values[0], str):
            try:
                for row in range(self.rows):
                    self.cell_values[row][0].set(new_values[row])
            except IndexError:
                print("Make sure the array contains a value for each row.")

        # has many columns; use multidimensional array
        else:
            try:
                for column in range(self.columns):
                    for row in range(self.rows):
                        self.cell_values[row][column].set(new_values[column][row])
            except IndexError:
                print("Your data does not match the dimensions of the table.")

    def clear_cells(self):
        for column in range(self.columns):
            for row in range(self.rows):
                self.cell_values[row][column].set("")

    def update_column(self, column, new_values):
        try:
            for row in range(self.rows):
                self.cell_values[row][column].set(new_values[row])
        except IndexError:
            print("Your data does not match the dimensions of the table.")

    def clear_column(self, column):
        for row in range(self.rows):
            self.cell_values[row][column].set("")

    def set_headers(self, values):
        for row in range(self.rows):
            self.headers[row].configure(text=values[row])

    def update_button(self, *args):
        # if button is disabled, no checkboxes were checked, so we automatically enable
        if self.is_button_disabled:
            self.is_button_disabled = False
            self.delete_button.configure(state=NORMAL, bg="#FF3300", fg="#FFFFFF", cursor="hand2")

        # look for a selected checkbox; if non found, disable button
        else:
            for column in range(self.columns):
                if self.checkbox_values[column].get():
                    # found a box still enabled
                    return
            # all checkboxes are unselected; disable button
            self.is_button_disabled = True
            self.delete_button.configure(state=DISABLED, bg=self.disabled_background, cursor="arrow")

    def get_checked_indices(self):
        """
        Used when user presses delete button to find which are the deleted columns.

        :return: array of indices corresponding to deleted columns
        """
        if self.can_select_columns:
            result = []
            for column in range(self.columns):
                if self.checkbox_values[column].get():
                    result.append(column)

            return result


class ResponsiveImage(Frame):

    def __init__(self, parent, image, tag="IMG", anchor=N):
        Frame.__init__(self, parent)

        # save image
        self.original = image
        # image tag
        self.tag = tag
        # image anchor position
        self.anchor = anchor

        # make frame responsive
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # source image in TK Image format
        self.image = ImageTk.PhotoImage(self.original)

        # create canvas and place image inside it
        self.canvas = Canvas(self, borderwidth=0, highlightthickness=0)
        self.canvas.create_image(0, 0, image=self.image, anchor=NW, tags=self.tag)
        self.canvas.grid(row=0, sticky=NSEW)

        # the magic
        self.bind("<Configure>", self.resize)

    def resize(self, event):
        # resize while keeping aspect ratio
        resized = resize_keep_aspect(image=self.original, max_w=event.width, max_h=event.height)

        # the new resized image, in TkImage format
        self.image = ImageTk.PhotoImage(resized)
        self.canvas.delete(self.tag)

        # place image top-centered in the canvas
        if self.anchor == N:
            self.canvas.create_image(event.width/2, 0, image=self.image, anchor=N, tags=self.tag)
        # only NW for now
        else:
            self.canvas.create_image(0, 0, image=self.image, anchor=NW, tags=self.tag)

    # def change_image(self, image):
    #     self.original = image
    #     self.image = ImageTk.PhotoImage(self.original)
    #     self.canvas.delete("IMG")
    #     self.canvas.create_image(0, 0, image=self.image, anchor=NW, tags="IMG")


class EntryWithPlaceholder(Entry):

    def __init__(self, parent, text_var, placeholder_text, placeholder_color="grey", **kwargs):
        Entry.__init__(self, parent, **kwargs)

        # Keep a reference of the parent to have someone to focus out onto
        self.parent = parent
        # a reference of the StringVar used for the entry's content
        self.value_var = text_var
        # the placeholder
        self.placeholder_text = placeholder_text

        # save the entry's text color
        self.text_color = self["fg"]
        # placeholder text color
        self.placeholder_color = placeholder_color

        # bind to focus in/out of entry to handle placeholder
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

    def set_placeholder(self):
        self.value_var.set(self.placeholder_text)
        self.configure(fg=self.placeholder_color)

        # force focus out
        self.parent.focus()

    def on_focus_in(self, event):
        # clear placeholder on entry focus
        if self["fg"] == self.placeholder_color:
            self.value_var.set("")
            self.configure(fg=self.text_color)

    def on_focus_out(self, event):
        # Set placeholder if entry is empty
        if not self.value_var.get():
            self.set_placeholder()
