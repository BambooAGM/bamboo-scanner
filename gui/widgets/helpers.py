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


def resize_keep_aspect(image, max_w, max_h):
    """
    Resize an image while keeping aspect ratio.

    :param image: The image to resize. Must be of PIL Image format
    :param max_w: max allowed width
    :param max_h: max allowed height
    :return: The resized image in PIL Image format
    """
    w = image.width
    h = image.height

    ratio = min(max_w / w, max_h / h)
    (new_w, new_h) = (int(w * ratio), int(h * ratio))

    return image.resize((new_w, new_h))
