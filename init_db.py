
import os

import consts
import db
from enums import TreeLink
from node import NodeId, get_next_available_temp_id


def init_if_needed(db_path):
    if not os.path.exists(db_path):
        print('Initializing db')
        conn = db.create_connection(db_path)
        db.initialize_db(conn)
        db.create_node(conn.cursor(), get_next_available_temp_id(), NodeId(-1), TreeLink.Parent)
        conn.commit()


if __name__ == '__main__':
    if os.path.exists(consts.DB_PATH):
        print('Removing db')
        os.remove(consts.DB_PATH)

    init_if_needed(consts.DB_PATH)
