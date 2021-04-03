
import enums

from edit import Edit


class Draw:
    def __init__(self, screen, selection, node_edit: Edit, width: int):
        self.screen = screen
        self.selection = selection
        self.node_edit = node_edit
        self.width = width

    def __draw_node(self, node_id, node, left_margin, line_number, mode):

        if self.selection.is_selected(node_id):
            bg_color = self.screen.screen_api.COLOUR_CYAN
        else:
            bg_color = self.screen.screen_api.COLOUR_BLACK

        remaining_width = self.width - left_margin - 2

        if self.selection.is_selected(node_id) and mode == enums.Mode.EditNode:
            if self.node_edit.text_editor.calculate_cursor.is_end():
                # One extra space at the end to accommodate a cursor on an empty newline
                node_text = self.node_edit.text_editor.get_data() + ' '
            else:
                node_text = self.node_edit.text_editor.get_data()
        else:
            node_text = node.text

        for i in range(0, max(1, len(node_text)), remaining_width):
            self.screen.screen_api.print_at(
                ' ' * self.width, 0, line_number, colour=7, bg=bg_color
            )

            if i == 0:
                left_padding = '* '
            else:
                left_padding = '  '

            if self.selection.is_selected(node_id) and mode == enums.Mode.EditNode:
                cursor_pos = self.node_edit.text_editor.calculate_cursor.get_cursor_coord(remaining_width)

                text = node_text[i : i + remaining_width]
                self.screen.screen_api.print_at(
                    left_padding + text, left_margin, line_number, colour=7, bg=bg_color
                )

                if i / remaining_width == cursor_pos.y:
                    cursor_x = left_margin + 2 + cursor_pos.x
                    cursor_text = text[cursor_pos.x]

                    self.screen.screen_api.print_at(
                        cursor_text, cursor_x, line_number, colour=0, attr=self.screen.screen_api.A_UNDERLINE, bg=self.screen.screen_api.COLOUR_WHITE
                    )
            else:
                text = node_text[i : i + remaining_width]
                self.screen.screen_api.print_at(
                    left_padding + text, left_margin, line_number, colour=7, bg=bg_color
                )

            line_number += 1

        return line_number

    def __draw_node_tree(self, tree, node_id, left_margin, line_number, mode):

        node = tree.get_node(node_id)
        child_ids = tree.tree.get_children(node_id)

        line_number = self.__draw_node(node_id, node, left_margin, line_number, mode)

        for child_id in child_ids:
            line_number = self.__draw_node_tree(tree, child_id, left_margin + 2, line_number, mode)

        return line_number

    def draw_node_tree(self, tree, node_id, mode):
        line_number = 0

        for child_id in tree.tree.get_children(node_id):
            line_number = self.__draw_node_tree(tree, child_id, 0, line_number, mode)

        self.screen.screen_api.refresh()
