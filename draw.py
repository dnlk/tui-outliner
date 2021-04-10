
import enums
from typing import *

from asciimatics import screen

from edit import Edit
from text_editor import TextFormat
from ui import UIState

BG_COLOR = screen.Screen.COLOUR_BLACK


class Draw:
    def __init__(self, screen, selection, node_edit: Edit, ui_state: UIState, width: int):
        self.screen = screen
        self.selection = selection
        self.node_edit = node_edit
        self.ui_state = ui_state
        self.width = width
        self.previous_line_number = 0

    def draw_blank_line(self, line_number, bg_color):
        self.screen.screen_api.print_at(
            ' ' * self.width, 0, line_number, colour=7, bg=bg_color
        )

    def __draw_node(self, node_id, node, left_margin, line_number, mode, has_children):

        if self.selection.is_selected(node_id):
            bg_color = self.screen.screen_api.COLOUR_CYAN
        else:
            bg_color = self.screen.screen_api.COLOUR_BLACK

        remaining_width = self.width - left_margin - 2

        if self.selection.is_selected(node_id) and mode == enums.Mode.EditNode:
            node_text = self.node_edit.text_editor.get_data()
        else:
            node_text = node.text

        formatted_text = TextFormat(node_text, remaining_width)
        lines = formatted_text.get_lines()

        # Show empty nodes with at least one blank line, with a space for the cursor
        if not lines:
            lines = [' ']

        cursor_pos = None
        if self.selection.is_selected(node_id) and mode == enums.Mode.EditNode:
            cursor_pos = self.node_edit.text_editor.calculate_cursor.get_cursor_coord(remaining_width)
            assert cursor_pos.y <= len(lines)

            # Create an extra space char for the cursor
            if cursor_pos.y == len(lines):
                lines.append(' ')
            else:
                lines[cursor_pos.y] += ' '

        for i, line in enumerate(lines):
            self.draw_blank_line(line_number, bg_color)

            if i == 0:
                if not has_children:
                    left_padding = '* '
                elif node.expanded:
                    left_padding = '- '
                else:
                    left_padding = '+ '
            else:
                left_padding = '  '

            if self.selection.is_selected(node_id) and mode == enums.Mode.EditNode:
                self.screen.screen_api.print_at(
                    left_padding + line, left_margin, line_number, colour=7, bg=bg_color
                )

                if i == cursor_pos.y:
                    cursor_x = left_margin + 2 + cursor_pos.x
                    cursor_text = line[cursor_pos.x]

                    self.screen.screen_api.print_at(
                        cursor_text, cursor_x, line_number, colour=0, attr=self.screen.screen_api.A_UNDERLINE, bg=self.screen.screen_api.COLOUR_WHITE
                    )
            else:
                self.screen.screen_api.print_at(
                    left_padding + line, left_margin, line_number, colour=7, bg=bg_color
                )

            line_number += 1

        return line_number

    def __draw_node_tree(self, tree, node_id, left_margin, line_number, mode):
        node = tree.get_node(node_id)
        children = tree.tree.get_children(node_id)

        line_number = self.__draw_node(node_id, node, left_margin, line_number, mode, bool(children))

        if node.expanded:
            for child_id in children:
                line_number = self.__draw_node_tree(tree, child_id, left_margin + 2, line_number, mode)

        return line_number

    @staticmethod
    def __clamp_breadcrumb_part_text(s):
        if len(s) > 15:
            return s[:15] + '...'
        else:
            return s

    def __get_breadcrumbs_text(self, tree) -> Optional[str]:
        if self.ui_state.node_path.breadcrumbs:
            breadcrumb_nodes = self.ui_state.node_path.get_breadcrumb_path()
            breadcrumb_text = ' > '.join(self.__clamp_breadcrumb_part_text(tree.get_node(bc_id).text) for bc_id in breadcrumb_nodes)

            if len(breadcrumb_text) > self.screen.width:
                num_chars_display = self.screen.width - 3  # 3 for the '...' elipsis
                breadcrumb_text = '...' + breadcrumb_text[-num_chars_display:]

            return breadcrumb_text

    def __draw_divider(self, width: int, line_number) -> int:
        self.draw_blank_line(line_number, BG_COLOR)
        divider_text = '-' * width
        self.screen.screen_api.print_at(
            divider_text, 0, line_number, colour=7, bg=BG_COLOR
        )
        return line_number + 1

    def __draw_breadcrumbs(self, tree, line_number) -> int:
        if header_text := self.__get_breadcrumbs_text(tree):
            self.draw_blank_line(line_number, BG_COLOR)
            self.screen.screen_api.print_at(
                header_text, 0, line_number, colour=7, bg=BG_COLOR
            )
            line_number += 1

            line_number = self.__draw_divider(len(header_text), line_number)
        return line_number

    def __draw_root_node(self, tree, line_number) -> int:
        self.draw_blank_line(line_number, BG_COLOR)
        root_node_text = tree.get_node(tree.root_node).text
        self.screen.screen_api.print_at(
            root_node_text, 0, line_number, colour=7, bg=BG_COLOR
        )
        return line_number + 1

    def __draw_header(self, tree, line_number):
        line_number = self.__draw_breadcrumbs(tree, line_number)
        line_number = self.__draw_root_node(tree, line_number)
        return line_number

    def draw_node_tree(self, tree, node_id, mode):
        line_number = 0

        line_number = self.__draw_header(tree, line_number)

        for child_id in tree.tree.get_children(node_id):
            line_number = self.__draw_node_tree(tree, child_id, 0, line_number, mode)

        # Blank out any lines at the bottom that were previously drawn, as can happen e.g. when nodes are deleted
        blank_line_bg_color = self.screen.screen_api.COLOUR_BLACK
        for excess_line_number in range(line_number, self.previous_line_number):
            self.draw_blank_line(excess_line_number, blank_line_bg_color)
        self.previous_line_number = line_number

        self.screen.screen_api.refresh()
