

GAP_BETWEEN_CATEGORIES = 0.5  # How much extra space should be between different categories
BOX_PLOT_STEP = 0.7  # How much to increment x for each box plot. Boxplots have a default width of 0.5
CATEGORY_LABEL_POSITION = 0.35  # How much, relative to the height of the whole figure, should the category label be below the x-axis

FONT_SIZE_AXIS_LABEL = 20
FONT_SIZE_TITLE = 20
FONT_SIZE_X_TICK = 12

PLOT_DEFAULT_WIDTH = 2  # Approximate width (in inches) of an empty plot
BOX_PLOT_WIDTH = 1  # Approximate width (in inches) that the plot grows when a boxplot is added

# Custom adjustment of column labels. column_name_in_dataframe => new_column_name
COLUMN_LABEL_MAPPING = {
    "party status: other": "other"
}


def compute_dataframe_grouping(_df, binary_independent_variables) -> tuple[list[float], list[float]]:
    box_plot_x_positions = []
    category_separator_x_positions = []  # Positions of vertical lines that visualize where the next category starts

    _prev_col_category = None
    _next_x_position = -BOX_PLOT_STEP
    for col in _df.columns:
        col_category = None

        if col == 'total':
            # Special case for 'total' column which is not listed in binary_independent_variables dict
            col_category = 'total'
        elif col in {'party status: other', 'other'}:
            col_category = _prev_col_category
        else:
            # Try to find column name in the binary_independent_variables dictionary
            # This gives us the category that this column belongs to
            for var_category, var_values in binary_independent_variables.items():
                if col in var_values:
                    col_category = var_category

        assert col_category is not None, f"Could not find category for column {col}"

        # Create a small gap between box plots if the next boxplot belongs to a different category
        if _prev_col_category is not None and col_category != _prev_col_category:
            category_separator_x_positions.append(_next_x_position + (BOX_PLOT_STEP + GAP_BETWEEN_CATEGORIES) / 2)
            _next_x_position += GAP_BETWEEN_CATEGORIES

        _next_x_position += BOX_PLOT_STEP
        _prev_col_category = col_category
        box_plot_x_positions.append(_next_x_position)

    return box_plot_x_positions, category_separator_x_positions
