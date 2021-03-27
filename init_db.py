
import os

import consts
import db
from enums import TreeLink
from node import NodeId


def init_if_needed(db_path):
    if not os.path.exists(db_path):
        print('Initializing db')
        conn = db.create_connection(db_path)
        db.initialize_db(conn)
        db.create_node(conn.cursor(), NodeId(None), NodeId(-1), TreeLink.Parent)


if __name__ == '__main__':
    if os.path.exists(consts.DB_PATH):
        print('Removing db')
        os.remove(consts.DB_PATH)

    init_if_needed(consts.DB_PATH)
