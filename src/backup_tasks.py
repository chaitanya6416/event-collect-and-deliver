''' backup_tasks is for periodic creation of  rbd and aof files used
for backups if failure'''

import os
from apscheduler.schedulers.background import BackgroundScheduler
import shutil
import datetime
from redis_client import RedisClient
from config import RDB_BACKUP_DIR, AOF_BACKUP_DIR

# Redis connection
redis_client = RedisClient().get_client_instance()


# Create the directories if they don't exist
os.makedirs(RDB_BACKUP_DIR, exist_ok=True)
os.makedirs(AOF_BACKUP_DIR, exist_ok=True)


def upload_to_s3():
    ''' do upload to s3 for backups '''


def create_redis_rdb_snapshot():
    ''' one type of backup is rbd, can be done by redis_client.save() '''
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    snapshot_filename = f'{timestamp}.rdb'
    snapshot_path = os.path.join(RDB_BACKUP_DIR, snapshot_filename)

    # Create a Redis RDB snapshot
    redis_client.save()

    # Move the snapshot to the RDB backup directory
    shutil.move('dump.rdb', snapshot_path)

    # Upload the RDB snapshot to S3
    upload_to_s3()


def create_redis_aof_backup():
    ''' another type of backup is to have a aof file '''
    # Create a Redis AOF backup
    redis_client.bgrewriteaof()


# Create a scheduler and add the jobs
scheduler = BackgroundScheduler()


scheduler.add_job(create_redis_rdb_snapshot, 'interval', hours=1)
scheduler.add_job(create_redis_aof_backup, 'interval', minutes=1)
