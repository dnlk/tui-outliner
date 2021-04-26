
import asyncio
import os
import sys
from typing import List, Tuple

import aiosqlite

import consts
from enums import TreeLink
from nodes.node_types import NodeId

from database import db, init_db


async def export_nodes(root_id, filename, db_name):

    with open(filename, 'w') as f:
        def traverse_callback(_id, text, level):
            f.write(f'{(level - 1) * "  "}* {text}\n')

        async with aiosqlite.connect(db_name) as conn:
            cursor = await conn.cursor()
            await db.depth_first_traversal(cursor, root_id, traverse_callback)


async def import_nodes(filename, output_db_path):
    root_id = consts.ROOT_NODE_ID
    if os.path.exists(output_db_path):
        os.remove(output_db_path)
    async with aiosqlite.connect(output_db_path) as conn:
        await init_db.initialize_db(conn)

        with open(filename, 'r') as f:
            node_trace: List[Tuple[int, int]] = []  # indent : id
            for i, line in enumerate(f, 1):
                node_id = NodeId(None)
                previous_indent, previous_node = node_trace[-1] if node_trace else (-1, root_id)

                parts = line.strip('\n').split('* ', 1)
                assert len(parts) == 2
                indent, text = parts
                assert len(indent) % 2 == 0
                assert len(indent) <= previous_indent * 2 + 2
                assert all(c == ' ' for c in indent)

                indent_level = len(indent) // 2

                cursor = await conn.cursor()

                if indent_level == previous_indent:
                    # New sibling of current parent
                    await db.create_node(cursor, node_id, previous_node, TreeLink.Sibling, text=text)
                    node_trace[-1] = (indent_level, i)
                elif indent_level == previous_indent + 1:
                    # New child of current parent
                    await db.create_node(cursor, node_id, previous_node, TreeLink.Parent, text=text)
                    node_trace.append((indent_level, i))
                elif indent_level < previous_indent:
                    # New sibling of ancestor
                    node_trace = node_trace[:indent_level + 1]
                    old_indent, old_id = node_trace[-1]
                    assert old_indent == indent_level
                    await db.create_node(cursor, node_id, old_id, TreeLink.Sibling, text=text)
                    node_trace[-1] = (indent_level, i)
                else:
                    assert False

            await conn.commit()


if __name__ == '__main__':


    export_filepath = sys.argv[1]
    # asyncio.run(export_nodes(-1, export_filepath, 'database/_db.sqlite'))
    # asyncio.run(import_nodes(export_filepath, 'database/db.sqlite'))
