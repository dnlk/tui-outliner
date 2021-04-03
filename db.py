
import sqlite3
from typing import *

import change
import consts
from enums import NodeType, TreeLink
from node import NodeId, NodeData
from node_tree import NodeContext
from node_types import NodeId, IdType
from transaction import NodeTransaction


SWAP_ID = -12345


new_node_mapping: Dict[NodeId, NodeId] = {}


SupportedSqlParameterType = Union[None, int, str, NodeId]
SqliteBindingType = Union[None, int, str]


def convert_arg(arg: SupportedSqlParameterType) -> SqliteBindingType:
    if arg is None:
        return arg
    elif isinstance(arg, int):
        return arg
    elif isinstance(arg, str):
        return arg
    elif isinstance(arg, NodeId):
        return get_db_nodeid(arg).id
    elif isinstance(arg, TreeLink):
        return arg.value
    else:
        raise NotImplementedError('Unsupported type: {}'.format(arg))


def get_db_nodeid(node_id: NodeId) -> NodeId:
    if node_id.type == IdType.Temp:
        if node_id in new_node_mapping:
            return new_node_mapping[node_id]
        else:
            raise Exception("No db id for temp id: {}".format(node_id))
    else:
        return node_id


def run_query(cursor: sqlite3.Cursor, query: str, args: List[SupportedSqlParameterType]):
    modified_args: List[SqliteBindingType] = [convert_arg(arg) for arg in args]
    return cursor.execute(query, modified_args)


def create_connection(db_path):
    return sqlite3.connect(db_path)


def initialize_db(conn):
    with open(consts.SCHEMA_PATH, 'r') as f:
        schema = f.read()
    conn.cursor().execute(schema)
    conn.commit()


def create_node(cursor, node_id, previous_node_id, previous_node_link, text=None) -> int:

    query = """
        INSERT INTO node 
            (previous_node_id, previous_node_link, type, text, expanded)
        VALUES
            (?, ?, 0, ?, 1)
    """
    result = run_query(
        cursor,
        query,
        [
            previous_node_id,
            previous_node_link,
            '' if next is None else text
        ]
    )

    if not node_id.is_none() and node_id.type == IdType.Temp:
        new_node_mapping[node_id] = NodeId(cursor.lastrowid)

    return cursor.lastrowid

#
# def create_node_under_parent(conn, parent_id, node_type):
#     query = """
#         INSERT INTO node (parent_id, type, expanded) VALUES (?, ?, 1)
#     """
#     # parent_id = get_db_nodeid(parent_id)
#
#     result = run_query(conn.cursor(), query, [parent_id, node_type.value])
#     # result = conn.cursor().execute(query, [parent_id, node_type.value])
#     conn.commit()
#     return result
#
#


def get_next_sibling(cursor, node_id: NodeId):
    query_get_next_sibling = """
        SELECT id
        FROM node
        WHERE previous_sibling_id=?1
    """
    result = run_query(
        cursor,
        query_get_next_sibling,
        [
            node_id
        ]
    )

    if row := result.fetchone():
        return row[0]


def switch_previous_node(cursor, node_id: NodeId, previous_sibling_id: NodeId, link_type: TreeLink):
    query_switch_previous_node = """
        UPDATE node
        SET previous_sibling=?1, link_type=?2
        WHERE id=?3
    """

    result = run_query(
        cursor,
        query_switch_previous_node,
        [
            node_id,
            previous_sibling_id,
            link_type,
        ]
    )
    return


def create_node_after_as_sibling(cursor, node_id: NodeId, previous_sibling_id: NodeId):

    result1 = create_node(cursor, node_id, SWAP_ID, TreeLink.Sibling)
    next_sibling_id = get_next_sibling(cursor, previous_sibling_id)
    result2 = switch_previous_node(cursor, next_sibling_id, node_id, TreeLink.sibling)
    result3 = switch_previous_node(cursor, node_id, previous_sibling_id)
    return


def splice_node(cursor, node_id: NodeId):
    """
        id_to_patch_through = None
        if link_type_to_patch_through:
            id_to_patch_through = self.node_links.lpop((_id, link_type_to_patch_through))
        previous_link = self.node_links.rpop(_id)
        if id_to_patch_through is not None and previous_link is not None:
            previous_id, previous_link_type = previous_link
            self.add_link(previous_id, id_to_patch_through, previous_link_type)
    """

    query_remove_link = """
        UPDATE node
        SET previous_node_id=NULL
        WHERE id=?1
    """

    result1 = run_query(
        cursor,
        query_remove_link,
        [
            node_id
        ]
    )

    query_patch_through = f"""
        UPDATE node
        SET n2.previous_node_id=?1, n2.previous_node_link=n1.previous_node_link
        FROM node as n1, node as n2
        WHERE n1.previous_node_id=?1 AND n2.previous_node_id=n1.id AND n2.previous_node_link={TreeLink.Sibling.value}
    """

    result2 = run_query(
        cursor,
        query_patch_through,
        [
            node_id,
        ]
    )
    return


def _insert_after(self, node_id: NodeId, previous_id: NodeId, link_type: TreeLink):
    """
    next_id = self.node_links.lpop((previous_id, link_type))
    self.add_link(previous_id, _id, link_type)
    if next_id is not None:
        self.add_link(_id, next_id, bumped_link_type)
    """

    query_get_next_id = f"""
        SELECT id
        FROM node
        WHERE previous_node_id={previous_id.id} AND previous_node_link={link_type.value}
    """

    query_


def move_after(cursor, node_id: NodeId, previous_id: NodeId, link: TreeLink):
    """
    self._splice(_id, link_type_to_patch_though)
    self._insert_after(_id, previous_id, link_type, bumped_link_type)
    """


def get_node(cursor, node_id: NodeId) -> NodeContext:
    query_node = """
        SELECT previous_node_id, previous_node_link, type, text, expanded
        FROM node
        WHERE id=?
    """

    # node_id = get_db_nodeid(node_id)

    result = run_query(cursor, query_node, [node_id])
    previous_node_id, previous_link_type, node_type_enum, text, expanded = result.fetchone()
    previous_node_id = NodeId(previous_node_id)
    previous_link_type = TreeLink(previous_link_type)
    node_type_enum = NodeType(node_type_enum)

    node_data = NodeData(type=node_type_enum, text=text, expanded=bool(expanded))
    node_context = NodeContext(node_id, node_data, previous_node_id, previous_link_type)

    return node_context


def get_all_nodes(cursor):
    query = """
        SELECT (id)
        FROM node
    """

    return [
        get_node(cursor, NodeId(results[0], IdType.DB))
        for results
        in cursor.execute(query).fetchall()
    ]


def update_node_text(cursor, node_id, text):
    query = """
        UPDATE node
        SET text=?1
        WHERE id=?2
    """
    result = run_query(cursor, query, [text, node_id])


# def get_parent_id(conn, node_id):
#     query = """
#         SELECT n1.id
#         FROM node n1
#         INNER JOIN node n2
#         WHERE n1.id = n2.parent_id AND n2.id = ?1
#     """
#     # node_id = get_db_nodeid(node_id)
#     result = run_query(conn.cursor(), query, [node_id]).fetchone()
#     # result = conn.cursor().execute(query, [node_id.id]).fetchone()
#     return result[0]

#
# def update_node(conn, node_update: change.NodeChange):
#     accepted_columns = (
#         'parent_id',
#         'previous_sibling_id',
#         'next_sibling_id',
#         'type',
#         'text',
#         'expanded'
#     )
#     for column in node_update.changes:
#         assert column.value in accepted_columns, column
#
#     set_sql = ','.join([column.value + '=?' + str(i) for i, column in enumerate(node_update.changes, 2)])
#
#     query = """
#         UPDATE node
#         SET {set_sql}
#         WHERE id = ?1
#     """.format(set_sql=set_sql)
#
#     node_id = get_db_nodeid(node_update.node_id)
#
#     argument_list = [node_id.id]
#     argument_list.extend(node_update.changes.values())
#
#     result = run_query(conn.cursor(), query, argument_list)
#     # result = conn.cursor().execute(query, argument_list)
#     return

#
# def apply_node_tree_change(conn, node_change: change.Change):
#     if isinstance(node_change, change.NewNode):
#         create_node(conn, node_change)
#     elif isinstance(node_change, change.NodeChange):
#         update_node(conn, node_change)
#
#
# def apply_node_tree_transaction(conn, node_transaction: NodeTransaction):
#     for change_ in node_transaction.changes:
#         apply_node_tree_change(conn, change_)
#
#     conn.commit()


#
# def move_node_after(conn, node_id, previous_sibling_id):
#
#     previous_sibling = get_node(conn, previous_sibling_id)
#     new_parent_id = previous_sibling.parent_id
#     next_sibling_id = previous_sibling.next_sibling_id
#
#     update_node(
#         conn,
#         node_id,
#         parent_id=new_parent_id,
#         previous_sibling_id=previous_sibling_id,
#         next_sibling_id=next_sibling_id
#     )
#
#     update_node(
#         conn,
#         previous_sibling_id,
#         next_sibling_id=node_id
#     )
#
#     update_node(
#         conn,
#         next_sibling_id,
#         previous_sibling_id=node_id,
#     )
#
#     update_node(
#         conn,
#         new_parent_id,
#         expanded=1
#     )
#
#     conn.commit()


def depth_first_traversal(cursor, root_id, callback):

    traversal_query = """
            WITH RECURSIVE
            traverse_nodes(id, text, level) AS (
             SELECT n.id, text, 1 FROM node as n WHERE n.previous_node_id=?1 AND n.previous_node_link=0
             UNION
             SELECT node.id,
                    node.text,
                    CASE node.previous_node_link
                         WHEN 0
                             THEN level+1
                         ELSE level
                    END node_level
             FROM traverse_nodes, node
             WHERE node.previous_node_id=traverse_nodes.id
             ORDER BY 3 DESC
            )
            SELECT id, text, 0 FROM node WHERE id=?1
            UNION ALL
            SELECT id, text, level FROM traverse_nodes;
        """

    result = run_query(
        cursor,
        traversal_query,
        [
            root_id
        ]
    )

    for _id, text, level in result.fetchall():
        callback(_id, text, level)
