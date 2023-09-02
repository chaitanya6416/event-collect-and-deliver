''' defined basic logging format here, files can import and use from here '''
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
