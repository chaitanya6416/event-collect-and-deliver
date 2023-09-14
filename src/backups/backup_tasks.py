''' backup_tasks is for periodic creation of  rbd and aof files used
for backups if failure'''

import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from backups.rdb_backup import create_redis_rdb_snapshot
from backups.aof_backup import create_redis_aof_backup_and_copy
sys.path.append(os.path.abspath(".."))
import config

def upload_to_s3():
    ''' do upload to s3 for backups '''


# Create a scheduler and add the jobs
scheduler = BackgroundScheduler()


scheduler.add_job(create_redis_rdb_snapshot, 'interval',
                  minutes=config.RDB_BACKUPS_INTERVAL)
scheduler.add_job(create_redis_aof_backup_and_copy,
                  'interval', seconds=config.AOF_BACKUPS_INTERVAL)
