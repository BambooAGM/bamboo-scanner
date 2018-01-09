def make_columns_responsive(container, **kwargs):
    """
    Make the columns of a Tk container responsive.

    :param container: Tk widget whose grid will be configured
    :param args: a list of ignored columns
    """
    ignored = kwargs.pop("ignored", [])
    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)

    # number of columns in grid
    columns = container.grid_size()[0]

    for column in range(columns):
        if column not in ignored:
            container.grid_columnconfigure(column, weight=1)


def make_rows_responsive(container, **kwargs):
    """
    Make the rows of a Tk container responsive.

    :param container: Tk widget whose grid will be configured
    :param args: a list of ignored rows
    """
    ignored = kwargs.pop("ignored", [])
    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)

    # number of rows in grid
    rows = container.grid_size()[1]

    for row in range(rows):
        if row not in ignored:
            container.grid_rowconfigure(row, weight=1)


def reset_both_responsive(container):
    columns, rows = container.grid_size()

    for column in range(columns):
        container.grid_columnconfigure(column, weight=0)

    for row in range(rows):
        container.grid_rowconfigure(row, weight=0)
