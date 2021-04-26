
import aiosqlite
import os

import consts
from enums import TreeLink
from nodes.node import NodeId, get_next_available_temp_id

from . import db


async def initialize_db(conn):
    with open(consts.SCHEMA_PATH, 'r') as f:
        schema = f.read()
    cursor = await conn.cursor()
    await cursor.execute(schema)
    await conn.commit()


async def init_if_needed(db_path):
    if not os.path.exists(db_path):
        print('Initializing db')
        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.cursor()
            await initialize_db(conn)
            await db.create_node(cursor, get_next_available_temp_id(), NodeId(-1), TreeLink.Parent)
            await conn.commit()
