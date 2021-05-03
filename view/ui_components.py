
from view.color import Color
from view.layout import Height, Layout
from view.components.lines import Lines
from view.components.simple_line import SimpleLine
from view.components.scrollable_container import ScrollableLines
from view_data_provider.breadcrumbs_data_provider import BreadcrumbsDataProvider
from view_data_provider.node_tree_data_provider import NodeTreeDataProvider
from view_data_provider.search_data_provider import SearchDataProvider


def get_layout(
        width: int,
        height: int,
        breadcrumbs_data_provider: BreadcrumbsDataProvider,
        node_tree_data_provider: NodeTreeDataProvider,
        search_data_provider: SearchDataProvider,
):

    return Layout(
        width=width,
        height=height,
        components=[
            Lines(node_tree_data_provider.node_sub_tree_header_data_provider, width=width),
            ScrollableLines(node_tree_data_provider, width=width, height=Height.Fill),
            Lines(breadcrumbs_data_provider, width=width),
            Lines(search_data_provider, width=width),
        ]
    )
