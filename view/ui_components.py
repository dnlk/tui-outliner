
from changes.change import ChangeNotifier
from enums import Mode
from view.layout import Height, Layout
from view.components.lines import Lines
from view.components.scrollable_container import ScrollableLines
from view.components.text_editor import TextEditorComponent
from view.components.selectable_list import SelectableListComponent
from view_data_provider.breadcrumbs_data_provider import BreadcrumbsDataProvider
from view_data_provider.node_tree_data_provider import NodeTreeDataProvider


def get_layout(
        width: int,
        height: int,
        breadcrumbs_data_provider: BreadcrumbsDataProvider,
        node_tree_data_provider: NodeTreeDataProvider,
        filter_text_data,
        search_text_data,
        selected_search_item_data,
        search_results_data_provider,
        action_notifier,
        change_notifier: ChangeNotifier,
        ui_state,
):

    return Layout(
        width=width,
        height=height,
        components=[
            Lines(node_tree_data_provider.node_sub_tree_header_data_provider, width=width),
            ScrollableLines(change_notifier, node_tree_data_provider, width=width, height=Height.Fill),
            Lines(breadcrumbs_data_provider, width=width),
            TextEditorComponent(width, Mode.Filter, ui_state, action_notifier, change_notifier)
                .text.bind(filter_text_data),
            TextEditorComponent(width, Mode.Search, ui_state, action_notifier, change_notifier)
                .text.bind(search_text_data),
            SelectableListComponent(
                    width,
                    search_results_data_provider,
                    Mode.Search,
                    ui_state,
                    action_notifier,
                    change_notifier)
                .selected_item.bind(selected_search_item_data)
        ]
    )
