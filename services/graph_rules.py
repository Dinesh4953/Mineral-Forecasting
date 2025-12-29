# services/graph_rules.py

GRAPH_RULES = {
    1: [  # single numeric column
        "line",
        "bar",
        "area",
        "hist",
        "box",
        "violin"
    ],
    "multi": [  # multiple numeric columns
        "multi_line",
        "grouped_bar",
        "area_stack",
        "heatmap",
        "pairplot"
    ]
}

def get_valid_graphs(selected_columns):
    """
    Decide valid graph types based on number of selected columns
    """
    if not selected_columns:
        return []

    if len(selected_columns) == 1:
        return GRAPH_RULES[1]

    return GRAPH_RULES["multi"]


# GRAPH_RULES = {
#     "single_numeric": [
#         "line",
#         "bar",
#         "area",
#         "scatter",
#         "histogram",
#         "box",
#         "violin"
#     ],
#     "multi_numeric": [
#         "grouped_bar",
#         "multi_line",
#         "area_stack",
#         "radar",
#         "heatmap",
#         "pairplot"
#     ],
#     "time_series": [
#         "line",
#         "area",
#         "multi_line"
#     ]
# }
