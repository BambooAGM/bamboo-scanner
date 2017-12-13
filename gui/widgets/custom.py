from tkinter import font
from tkinter import *
from gui.widgets.grid_helpers import make_columns_responsive


class YellowButton(Button):

    def __init__(self, parent, **kwargs):
        Button.__init__(self, parent, **kwargs)
        self.configure(bg="#FF9900", relief=FLAT, padx=10, pady=5, disabledforeground="#333333")


class GreenButton(Button):

    def __init__(self, parent, **kwargs):
        Button.__init__(self, parent, **kwargs)
        self.configure(bg="#99CC33", relief=FLAT, padx=10, pady=5)


class RedButton(Button):

    def __init__(self, parent, **kwargs):
        Button.__init__(self, parent, **kwargs)
        self.configure(bg="#FF3300", fg="#FFFFFF", relief=FLAT, padx=10, pady=5)


class ScrollableTextArea(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        # Text input field
        self.text = Text(self, wrap=WORD)
        self.text.pack(side=LEFT, fill=BOTH, expand=True)

        # Vertical scroll bar
        self.scroll = Scrollbar(self)
        self.text.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side=RIGHT, fill=Y)


class TableLeftHeaders(Frame):
    """
    A table with headers on the leftmost column.

    :param rows: number of rows
    :param columns: number of columns (not counting the header)
    :param header_values: the text of the headers
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
            self.delete_button = Button(self, text="Delete\n selected", state=DISABLED, relief=FLAT)
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
                checkbox = Checkbutton(self, variable=self.checkbox_values[column])
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

        # make_columns_responsive(self)

    def update_cells(self, new_values):
        # table has only 1 column; accept single array
        if self.columns == 1 and isinstance(new_values[0], str):
            try:
                for row in range(self.rows):
                    self.cell_values[row][0].set(new_values[row])
            except:
                print("Make sure the array contains a value for each row.")
        # has many columns; use multidimensional array
        else:
            try:
                for row in range(self.rows):
                    for column in range(self.columns):
                        self.cell_values[row][column].set(new_values[column][row])
            except:
                print("Your data does not match the dimensions of the table.")

    def set_headers(self, values):
        for row in range(self.rows):
            self.headers[row].configure(text=values[row])

    def update_button(self, *args):
        # if button is disabled, no checkboxes were checked, so we automatically enable
        if self.is_button_disabled:
            self.is_button_disabled = False
            self.delete_button.configure(state=NORMAL, bg="#FF3300", fg="#FFFFFF")
        # look for a selected checkbox; if non found, disable button
        else:
            for column in range(self.columns):
                if self.checkbox_values[column].get():
                    # found a box still enabled
                    return
            # all checkboxes are unselected; disable button
            self.is_button_disabled = True
            self.delete_button.configure(state=DISABLED, bg=self.disabled_background)

    def get_checked_indices(self):
        """
        Used when user presses delete button to find which are the deleted columns.

        :return: array of indices corresponding to deleted columns
        """
        result = []

        if self.can_select_columns:
            result = []
            for column in range(self.columns):
                if self.checkbox_values[column].get():
                    result.append(column)

        return result
