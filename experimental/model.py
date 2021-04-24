from experimental import adt


class Node(adt.DataEnum):
    Bullet = {
        'id': int,
        'parent_id': int,
        'previous_sibling_id': (int, None),
        'next_sibling_id': (int, None),
        'text': str,
        'expanded': bool,
        'child_ids': list
    }


DB_ENUMERATIONS = {
    Node.Bullet: 0
}

DB_ENUMERATIONS_LOOKUP = {v: k for k, v in DB_ENUMERATIONS.items()}
