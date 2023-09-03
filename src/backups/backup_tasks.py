''' backup_tasks is for periodic creation of  rbd and aof files used
for backups if failure'''

from apscheduler.schedulers.background import BackgroundScheduler
from backups.rdb_backup import create_redis_rdb_snapshot
from backups.aof_backup import create_redis_aof_backup_and_copy


def upload_to_s3():
    ''' do upload to s3 for backups '''


# Create a scheduler and add the jobs
scheduler = BackgroundScheduler()


scheduler.add_job(create_redis_rdb_snapshot, 'interval', minutes=15)
scheduler.add_job(create_redis_aof_backup_and_copy, 'interval', minutes=1)
