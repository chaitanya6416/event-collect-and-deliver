''' all actions performed against redis can be saved to create a point-in-time
    redis state, this file is responsible to create such a backup file of
    redis db '''

from logger import logger
from redis_client import RedisClient
import os
import shutil
from datetime import datetime
import sys
sys.path.append(os.path.abspath(".."))


redis_client = RedisClient().get_client_instance()


def copy_aof(aof_folder_path, backup_dir):
    """
    Copies the AOF folder and its contents to the backup directory.
    The backup folder will be named with a timestamp.
    Returns True when the copy was successful.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_folder_name = f"aof_backups_{timestamp}"
    backup_folder_path = os.path.join(backup_dir, backup_folder_name)

    logger.info(f"Copying AOF folder to: {backup_folder_path}")

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    elif not os.path.isdir(backup_dir):
        sys.stderr.write(f'Error: {backup_dir} is not a directory.\n')
        return False
    elif os.path.exists(backup_folder_path):
        sys.stderr.write(f'Error: {backup_folder_path} already exists.\n')
        return False

    shutil.copytree(aof_folder_path, backup_folder_path)
    logger.info(f'AOF folder backup created at: {backup_folder_path}')
    return True


def create_redis_aof_backup_and_copy():
    ''' Create a Redis AOF backup and copy it to the "aof_backups" folder. '''
    # Create a Redis AOF backup
    redis_client.bgrewriteaof()

    # Get the path to the AOF file
    dir_config = redis_client.config_get('dir')
    appendonlydir_folder = redis_client.config_get('appenddirname')
    aof_folder_path = os.path.join(
        dir_config['dir'], appendonlydir_folder['appenddirname'])

    # Copy the AOF file to the "aof_backups" folder
    copy_aof(aof_folder_path, os.path.join(os.getcwd(), "aof_backups"))
