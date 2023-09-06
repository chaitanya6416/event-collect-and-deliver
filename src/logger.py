''' defined basic logging format here, files can import and use from here '''
# import logging


# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s %(levelname)s - %(message)s"
# )

# logger = logging.getLogger(__name__)

import logging
import threading

# Define a custom log format that includes the thread ID
log_format = "%(asctime)s - %(name)s %(levelname)s - %(message)s"

# Configure the logger with the custom format
logging.basicConfig(
    level=logging.INFO,
    format=log_format
)

# Get the logger instance
logger = logging.getLogger(__name__)

# If you want to log the thread ID as well, you can create a function like this


def log_with_thread_id(msg, *args, **kwargs):
    thread_id = threading.current_thread().name
    logger.info(msg + f" (Thread ID: {thread_id})", *args, **kwargs)
