
import os
import sys
from typing import List, Tuple

import consts
from enums import TreeLink
from nodes.node_types import NodeId

from . import db


def export_nodes(root_id, filename):

    conn = db.create_connection(consts.DB_PATH)

    with open(filename, 'w') as f:
        def traverse_callback(_id, text, level):
            f.write(f'{level * "  "}* {text}\n')

        db.depth_first_traversal(conn.cursor(), root_id, traverse_callback)


def import_nodes(filename, output_db_path):
    root_id = consts.ROOT_NODE_ID
    if os.path.exists(output_db_path):
        os.remove(output_db_path)
    conn = db.create_connection(output_db_path)
    db.initialize_db(conn)

    with open(filename, 'r') as f:
        node_trace: List[Tuple[int, int]] = []  # indent : id
        for i, line in enumerate(f, 1):
            node_id = NodeId(None)
            previous_indent, previous_node = node_trace[-1] if node_trace else (-1, root_id)

            parts = line.strip('\n').split('*', 1)
            assert len(parts) == 2
            indent, text = parts
            assert len(indent) % 2 == 0
            assert len(indent) <= previous_indent * 2 + 2
            assert all(c == ' ' for c in indent)

            indent_level = len(indent) // 2

            if indent_level == previous_indent:
                # New sibling of current parent
                db.create_node(conn.cursor(), node_id, previous_node, TreeLink.Sibling, text=text)
                node_trace[-1] = (indent_level, i)
            elif indent_level == previous_indent + 1:
                # New child of current parent
                db.create_node(conn.cursor(), node_id, previous_node, TreeLink.Parent, text=text)
                node_trace.append((indent_level, i))
            elif indent_level < previous_indent:
                # New sibling of ancestor
                node_trace = node_trace[:indent_level + 1]
                old_indent, old_id = node_trace[-1]
                assert old_indent == indent_level
                db.create_node(conn.cursor(), node_id, old_id, TreeLink.Sibling, text=text)
                node_trace[-1] = (indent_level, i)
            else:
                assert False

    conn.commit()


if __name__ == '__main__':
    export_filepath = sys.argv[1]
    # export_nodes(1, export_filepath)
    import_nodes(export_filepath, 'db.sqlite')
