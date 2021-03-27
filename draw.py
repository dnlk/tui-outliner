
import enums


class Draw:
    def __init__(self, screen, selection, node_edit):
        self.screen = screen
        self.selection = selection
        self.node_edit = node_edit

    def __draw_node(self, node_id, node, left_margin, line_number, mode):


        if self.selection.is_selected(node_id):
            bg_color = self.screen.COLOUR_CYAN
        else:
            bg_color = self.screen.COLOUR_BLACK

        self.screen.print_at(
            ' ' * 70, left_margin, line_number, colour=7, bg=bg_color
        )
        self.screen.print_at(
            ' ' * left_margin, 0, line_number, colour=7, bg=bg_color
        )

        cursor_pos = self.node_edit.cursor_index
        if self.selection.is_selected(node_id) and mode == enums.Mode.EditNode:
            text = self.node_edit.text + ' '
            self.screen.print_at(
                '* ' + text, left_margin, line_number, colour=7, bg=bg_color
            )
            self.screen.print_at(
                text[cursor_pos], left_margin + 2 + cursor_pos, line_number, colour=0, attr=self.screen.A_UNDERLINE, bg=self.screen.COLOUR_WHITE
            )
        else:
            text = node.text
            self.screen.print_at(
                '* ' + text, left_margin, line_number, colour=7, bg=bg_color
            )


    def __draw_node_tree(self, tree, node_id, left_margin, line_number, mode):

        node = tree.get_node(node_id)
        child_ids = tree.tree.get_children(node_id)

        self.__draw_node(node_id, node, left_margin, line_number, mode)
        line_number += 1

        for child_id in child_ids:
            line_number = self.__draw_node_tree(tree, child_id, left_margin + 2, line_number, mode)

        return line_number

    def draw_node_tree(self, tree, node_id, mode):
        line_number = 0

        for child_id in tree.tree.get_children(node_id):
            line_number = self.__draw_node_tree(tree, child_id, 0, line_number, mode)

        self.screen.refresh()
