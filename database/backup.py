import datetime
import os
import shutil

import consts


def backup(source):
    timestamp = datetime.datetime.now().strftime('%Y.%m.%d-%H.%M.%S')

    source_dir, source_name = os.path.split(source)
    name_parts = source_name.rsplit('.', 1)
    name_base = name_parts[0]
    name_ext = name_parts[1] if len(name_parts) > 1 else ''
    dest_name = f'{name_base}-{timestamp}.{name_ext}'
    dest_path = os.path.join(consts.BACKUPS_DIR, dest_name)

    if not os.path.exists(consts.BACKUPS_DIR):
        os.makedirs(consts.BACKUPS_DIR)

    shutil.copy(source, dest_path)
