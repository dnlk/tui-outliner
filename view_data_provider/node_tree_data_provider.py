
from dataclasses import dataclass
from typing import *

from asciimatics import screen

import consts

from datastructures.linked_list import LinkedList, DefaultId, DefaultIdFactory
import enums
from ext import func
from ext.geometry import Coord
from nodes.node_tree import NodeTree
from nodes.node_types import NodeId
from ui.selection import Selection
from ui.text_editor import TextFormat
from ui.ui import UIState
from view.color import Color
from view.text import TextSnippet, Line, simple_line

BLACK = screen.Screen.COLOUR_BLACK
CYAN = screen.Screen.COLOUR_CYAN
WHITE = screen.Screen.COLOUR_WHITE
A_UNDERLINE = screen.Screen.A_UNDERLINE


@dataclass
class CachedNode:
    id: NodeId
    num_lines: int
    lines: List[str]
    margin_left: int
    has_children: bool
    is_expanded: bool
    cursor_pos: Optional[Coord]


@dataclass
class FormattedLine:
    relative_line_number: int
    line: str
    node: CachedNode


class FormattedNodeCache(LinkedList[DefaultId, DefaultIdFactory, CachedNode]):

    def __init__(self, selection: Selection, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selection = selection

    @staticmethod
    def _extract_lines(node, start, end):
        if not node:
            return []

        return [
            FormattedLine(i, line, node)
            for i, line
            in enumerate(node.lines)
            if start <= i < end
        ]

    def get_lines(self, start: int, num_rows: int):
        end = start + num_rows
        nodes = self.get_ordered_nodes()
        counted_nodes = func.lazy_accumulate(
            f=lambda node, acc: (node, acc[2], acc[2] + (0 if not node else node.num_lines)),
            acc=(None, 0, 0),
            seq=nodes
        )
        trimmed_text = (
            self._extract_lines(node, start - line_start, end - line_start)
            for node, line_start, line_end
            in counted_nodes
        )
        lines = func.lazy_chain(trimmed_text)
        return lines

    def num_lines(self):
        return sum(node.num_lines for node in self.get_ordered_nodes())


class NodeSubTreeHeaderDataProvider:

    def __init__(self, node_tree: NodeTree):
        self.node_tree = node_tree
        self.width = 0

    def set_width(self, width: int):
        self.width = width

    def get_lines(self) -> List[Line]:
        root_node = self.node_tree.root_node
        if root_node.id == consts.ROOT_NODE_ID:
            return [
                simple_line('Welcome to your happy place. :)', 0, bg_color=Color.Black, fg_color=Color.White),
                simple_line('-' * self.width, 0, bg_color=Color.Black, fg_color=Color.White)
            ]
        else:
            node = self.node_tree.get_node(root_node)
            node_text = node.text or "<empty node text>"
            return [
                simple_line(node_text, 0, bg_color=Color.Black, fg_color=Color.White),
                simple_line('-' * self.width, 0, bg_color=Color.Black, fg_color=Color.White)
            ]

    def num_lines(self) -> int:
        if self.node_tree.root_node.id == consts.ROOT_NODE_ID:
            return 2
        else:
            return 2


class NodeTreeDataProvider:
    def __init__(self, ui_state: UIState):
        self.node_tree: NodeTree = ui_state.node_tree
        self.selection = ui_state.selection
        self.node_edit = ui_state.node_edit
        self.ui_state = ui_state
        self.width = 0
        self.previous_line_number = 0
        self.window_begin = 0
        self.formatted_node_cache: Optional[FormattedNodeCache] = None
        self.node_sub_tree_header_data_provider = NodeSubTreeHeaderDataProvider(self.node_tree)

    def add_node_to_cache(self, node_id, margin_left, has_children):
        node = self.node_tree.get_node(node_id)

        remaining_width = self.width - margin_left - 2

        if self.selection.is_selected(node_id) and self.ui_state.mode == enums.Mode.EditNode:
            node_text = self.node_edit.text_editor.get_data()
        else:
            node_text = node.text

        formatted_text = TextFormat(node_text, remaining_width)
        lines = formatted_text.get_lines()

        # Show empty nodes with at least one blank line, with a space for the cursor
        if not lines:
            lines = [' ']

        cursor_pos = None
        if self.selection.is_selected(node_id) and self.ui_state.mode == enums.Mode.EditNode:
            cursor_pos = self.node_edit.text_editor.calculate_cursor.get_cursor_coord(remaining_width)
            assert cursor_pos.y <= len(lines)

            # Create an extra space char for the cursor
            if cursor_pos.y == len(lines):
                lines.append(' ')
            else:
                lines[cursor_pos.y] += ' '

        # Hack so that we draw the whole line, e.g. for selected background
        lines = [
            line + ' ' * (self.width - len(line))
            for line in lines
        ]

        formatted_node = CachedNode(
            node_id,
            len(lines),
            lines,
            margin_left=margin_left,
            has_children=has_children,
            is_expanded=node.expanded,
            cursor_pos=cursor_pos,
        )

        self.formatted_node_cache.add_to_end(formatted_node)

    def add_tree_to_cache(self, node_id: NodeId, margin_left: int):
        if not self.ui_state.filter.is_visible(node_id):
            return

        node = self.node_tree.get_node(node_id)
        children = self.node_tree.tree.get_children(node_id)

        self.add_node_to_cache(node_id, margin_left, bool(children))

        if node.expanded:
            for child_id in children:
                self.add_tree_to_cache(child_id, margin_left + 2)

    def refresh_cache(self):
        self.formatted_node_cache = FormattedNodeCache(self.selection)

        for child_id in self.node_tree.tree.get_children(self.node_tree.root_node):
            self.add_tree_to_cache(child_id, 0,)

    def refresh(self):
        self.refresh_cache()

    def set_width(self, width: int):
        self.width = width

    def _format_line(self, formatted_line: FormattedLine) -> Line:
        node = formatted_line.node
        line = formatted_line.line
        relative_line_number = formatted_line.relative_line_number
        margin_left = node.margin_left

        if formatted_line.relative_line_number == 0:
            if not node.has_children:
                left_padding = '* '
            elif node.is_expanded:
                left_padding = '- '
            else:
                left_padding = '+ '
        else:
            left_padding = '  '

        bg_color = Color.Cyan if self.selection.is_selected(node.id) else Color.Black

        if self.selection.is_selected(node.id) and self.ui_state.mode == enums.Mode.EditNode:
            if node.cursor_pos is None:
                raise Exception('Cursor unexpectedly None')
            cursor_x = node.cursor_pos.x
            cursor_y = node.cursor_pos.y
            if relative_line_number != cursor_y:
                return Line(
                    [
                        TextSnippet(left_padding + line, bg_color=bg_color, fg_color=Color.White)
                    ],
                    x=margin_left
                )

            else:
                return Line(
                    [
                        TextSnippet(left_padding + line[:cursor_x], bg_color=bg_color, fg_color=Color.White),
                        TextSnippet(line[cursor_x: cursor_x + 1], bg_color=Color.White, fg_color=Color.Black),
                        TextSnippet(line[cursor_x + 1:], bg_color=bg_color, fg_color=Color.White),
                    ],
                    x=margin_left
                )
        else:
            return Line(
                [
                    TextSnippet(left_padding + line, bg_color=bg_color, fg_color=Color.White)
                ],
                x=margin_left
            )

    def get_lines(self, row_begin: int, num_rows: int) -> List[Line]:
        return [
            self._format_line(formatted_line)
            for formatted_line
            in self.formatted_node_cache.get_lines(row_begin, num_rows)
        ]

    def num_lines(self) -> int:
        return self.formatted_node_cache.num_lines()
