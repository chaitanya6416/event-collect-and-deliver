import os
import sys

# Adjust this path to point to your project's src directory
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
sys.path.insert(0, src_path)


TEMP_ENV_VARS = {
        'RDB_BACKUPS_INTERVAL': '1',
        'AOF_BACKUPS_INTERVAL': '1'
}

os.environ.update(TEMP_ENV_VARS)
