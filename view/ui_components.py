
from changes.change import ChangeNotifier
from view.layout import Height, Layout
from view.components.lines import Lines
from view.components.scrollable_container import ScrollableLines
from view_data_provider.breadcrumbs_data_provider import BreadcrumbsDataProvider
from view_data_provider.filter_data_provider import FilterDataProvider
from view_data_provider.node_tree_data_provider import NodeTreeDataProvider


def get_layout(
        width: int,
        height: int,
        breadcrumbs_data_provider: BreadcrumbsDataProvider,
        node_tree_data_provider: NodeTreeDataProvider,
        filter_data_provider: FilterDataProvider,
        change_notifier: ChangeNotifier
):

    return Layout(
        width=width,
        height=height,
        components=[
            Lines(node_tree_data_provider.node_sub_tree_header_data_provider, width=width),
            ScrollableLines(change_notifier, node_tree_data_provider, width=width, height=Height.Fill),
            Lines(breadcrumbs_data_provider, width=width),
            Lines(filter_data_provider, width=width),
        ]
    )
