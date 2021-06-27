
from typing import *

from enums import NodeType, TreeLink
from nodes.node import NodeData
from nodes.node_tree import NodeContext
from nodes.node_types import NodeId, IdType


SWAP_ID = -12345


new_node_mapping: Dict[NodeId, NodeId] = {}
reverse_new_node_mapping: Dict[NodeId, NodeId] = {}


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


async def run_query(cursor, query: str, args: List[SupportedSqlParameterType]):
    modified_args: List[SqliteBindingType] = [convert_arg(arg) for arg in args]
    result = await cursor.execute(query, modified_args)
    return result


async def create_node(cursor, node_id, previous_node_id, previous_node_link, text='') -> int:

    query = """
        INSERT INTO node
            (previous_node_id, previous_node_link, type, text, expanded)
        VALUES
            (?, ?, 0, ?, 1)
    """
    result = await run_query(
        cursor,
        query,
        [
            previous_node_id,
            previous_node_link,
            text
        ]
    )

    if not node_id.is_none() and node_id.type == IdType.Temp:
        new_node_mapping[node_id] = NodeId(cursor.lastrowid)
        reverse_new_node_mapping[NodeId(cursor.lastrowid)] = node_id

    return cursor.lastrowid


async def _get_previous_linkage(cursor, node_id: NodeId):
    query_get_original_link = """
        SELECT previous_node_id, previous_node_link
        FROM node
        WHERE id=?1
    """

    result = await run_query(
        cursor,
        query_get_original_link,
        [
            node_id
        ]
    )
    return await result.fetchone()


async def _get_next_node_id(cursor, node_id: NodeId, link_type: TreeLink):
    query_get_next_id = f"""
        SELECT id
        FROM node
        WHERE previous_node_id=?1 AND previous_node_link={link_type}
    """

    result = await run_query(
        cursor,
        query_get_next_id,
        args=[
            node_id
        ]
    )
    if row := await result.fetchone():
        return row[0]


async def switch_previous_node(cursor, node_id: NodeId, previous_sibling_id: NodeId, link_type: TreeLink):
    query_switch_previous_node = f"""
        UPDATE node
        SET previous_node_id=?2, previous_node_link={link_type}
        WHERE id=?1
    """

    result = await run_query(
        cursor,
        query_switch_previous_node,
        [
            node_id,
            previous_sibling_id,
        ]
    )
    return


async def create_node_after(cursor, node_id: NodeId, previous_sibling_id: NodeId, link_type: TreeLink):

    await create_node(cursor, node_id, SWAP_ID, link_type)

    if next_id := await _get_next_node_id(cursor, previous_sibling_id, link_type):
        await switch_previous_node(cursor, next_id, node_id, TreeLink.Sibling)

    await switch_previous_node(cursor, node_id, previous_sibling_id, link_type)


async def _splice_node(cursor, node_id: NodeId):

    previous_node_id, previous_node_link = await _get_previous_linkage(cursor, node_id)

    query_remove_link = f"""
        UPDATE node
        SET previous_node_id={SWAP_ID}
        WHERE id=?1
    """
    result1 = await run_query(
        cursor,
        query_remove_link,
        [
            node_id
        ]
    )

    if next_node_id := await _get_next_node_id(cursor, node_id, TreeLink.Sibling):
        await switch_previous_node(cursor, next_node_id, previous_node_id, previous_node_link)


async def _insert_after(cursor, node_id: NodeId, previous_id: NodeId, link_type: TreeLink):

    if next_id := await _get_next_node_id(cursor, previous_id, link_type):
        await switch_previous_node(cursor, next_id, node_id, TreeLink.Sibling)

    await switch_previous_node(cursor, node_id, previous_id, link_type)


async def move_after(cursor, node_id: NodeId, previous_id: NodeId, link_type: TreeLink):
    await _splice_node(cursor, node_id)
    await _insert_after(cursor, node_id, previous_id, link_type)


async def delete_node(cursor, node_id: NodeId):
    await _splice_node(cursor, node_id)

    delete_node_query = """
        DELETE FROM node
        WHERE id=?1
    """
    result = await run_query(
        cursor,
        delete_node_query,
        args=[
            node_id
        ]
    )


async def get_node(cursor, node_id: NodeId) -> NodeContext:
    query_node = """
        SELECT previous_node_id, previous_node_link, type, text, expanded
        FROM node
        WHERE id=?
    """
    result = await run_query(cursor, query_node, [node_id])
    previous_node_id, previous_link_type, node_type_enum, text, expanded = await result.fetchone()
    previous_node_id = NodeId(previous_node_id)
    previous_link_type = TreeLink(previous_link_type)
    node_type_enum = NodeType(node_type_enum)

    node_data = NodeData(type=node_type_enum, text=text, expanded=bool(expanded))
    node_context = NodeContext(node_id, node_data, previous_node_id, previous_link_type)

    return node_context


async def get_all_nodes(cursor):
    query = """
        SELECT (id)
        FROM node
    """

    return [
        await get_node(cursor, NodeId(results[0], IdType.DB))
        async for results
        in await cursor.execute(query)
    ]


async def update_node_text(cursor, node_id, text):
    query = """
        UPDATE node
        SET text=?1
        WHERE id=?2
    """
    result = await run_query(cursor, query, [text, node_id])


async def update_node_expanded(cursor, node_id: NodeId, expanded: bool):
    query = f"""
        UPDATE node
        SET expanded={expanded}
        WHERE id=?1
    """
    result = await run_query(cursor, query, [node_id])


async def depth_first_traversal(cursor, root_id, callback):

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

    result = await run_query(
        cursor,
        traversal_query,
        [
            root_id
        ]
    )

    for _id, text, level in await result.fetchall():
        callback(_id, text, level)


async def get_nodes_matching_text_including_ancestors(cursor, root_id: NodeId, text: str):

    results = set()
    stack = []

    def callback(_id, node_text, level):
        nonlocal stack
        stack = stack[:level - 1]
        stack.append(_id)

        if text in node_text:

            for x in stack:
                node_id = NodeId(x)
                if node_id in reverse_new_node_mapping:
                    node_id = reverse_new_node_mapping[node_id]
                results.add(node_id)

    await depth_first_traversal(cursor, root_id, callback)
    return results


async def get_nodes_matching_text(cursor, root_id: NodeId, text: str):
    results = []

    def callback(_id, node_text, level):
        if text in node_text:
            node_id = NodeId(_id)
            if node_id in reverse_new_node_mapping:
                node_id = reverse_new_node_mapping[node_id]
            results.append(node_id)

    await depth_first_traversal(cursor, root_id, callback)
    return results
