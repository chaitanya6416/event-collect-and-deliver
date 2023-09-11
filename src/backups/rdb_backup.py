''' one type of redis back is rdb which stores the db instance in a byte format,
    this file helps us in taking rdb snapshots '''

import os
import sys
import shutil
from datetime import datetime
from time import sleep
sys.path.append(os.path.abspath(".."))

from logger import logger
from redis_client import get_redis_instance

redis_client_instance = get_redis_instance()


def rdb_path():
    """
    Get and return the Redis config `dbfilename`.
    """
    dir_config = redis_client_instance.config_get('dir')
    dbfilename_config = redis_client_instance.config_get('dbfilename')
    return os.path.join(dir_config['dir'], dbfilename_config['dbfilename'])


def copy_rdb(rdb, backup_dir, port):
    """
    Copies and renames the RDB file to the backup directory.
    The final backup name is a timestamp + "(port_<port_number>).rdb".
    Returns True when the copy was successful.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_filename = f"{timestamp}(port_{port}).rdb"
    backup_filepath = os.path.join(backup_dir, backup_filename)

    logger.info(f"Copying RDB to: {backup_filepath}")

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    elif not os.path.isdir(backup_dir):
        sys.stderr.write(f'Error: {backup_dir} is not a directory.\n')
        return False
    elif os.path.exists(backup_filepath):
        sys.stderr.write(f'Error: {backup_filepath} already exists.\n')
        return False

    shutil.copy2(rdb, backup_filepath)
    logger.info(
        f'Backup {backup_filepath} created. Size: {os.path.getsize(backup_filepath)} bytes.')
    return True


def rdb_bgsave():
    """
    Perform a background save of the RDB snapshot.
    """
    last_save_time = redis_client_instance.lastsave()

    if redis_client_instance.bgsave():
        while True:
            if redis_client_instance.lastsave() != last_save_time:
                break
            sleep(1)
        return 'ok'
    return 'failed'


def create_redis_rdb_snapshot():
    """
    Create a Redis RDB snapshot and save it to a backup directory.
    """
    if rdb_bgsave() == 'ok':
        rdb = rdb_path()
        print(f"RDB Path: {rdb}")
        copy_rdb(rdb, os.path.join(os.getcwd(), "rdb_backups"), 6379)
