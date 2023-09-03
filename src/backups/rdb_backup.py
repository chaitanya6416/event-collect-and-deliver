''' one type of redis back is rdb which stores the db instance in a byte format,
    this file helps us in taking rdb snapshots '''

import os
import sys
import shutil
import hashlib
from datetime import datetime
from time import sleep
import redis


redis_client = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)


def file_md5(filename, blocksize=2**20):
    """
    Calculate the MD5 checksum of a file.
    """
    md5 = hashlib.md5()
    with open(filename, 'rb') as fn:
        while True:
            data = fn.read(blocksize)
            if not data:
                break
            md5.update(data)
    return md5.digest()


def rdb_path():
    """
    Get and return the Redis config `dbfilename`.
    """
    dir_config = redis_client.config_get('dir')
    dbfilename_config = redis_client.config_get('dbfilename')
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

    print(f"Copying RDB to: {backup_filepath}")

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    elif not os.path.isdir(backup_dir):
        sys.stderr.write(f'Error: {backup_dir} is not a directory.\n')
        return False
    elif os.path.exists(backup_filepath):
        sys.stderr.write(f'Error: {backup_filepath} already exists.\n')
        return False

    shutil.copy2(rdb, backup_filepath)
    print(
        f'Backup {backup_filepath} created. Size: {os.path.getsize(backup_filepath)} bytes.')
    return True


def rdb_bgsave():
    """
    Perform a background save of the RDB snapshot.
    """
    last_save_time = redis_client.lastsave()

    if redis_client.bgsave():
        while True:
            if redis_client.lastsave() != last_save_time:
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
        copy_rdb(rdb, "/rdb_backups", 6379)
