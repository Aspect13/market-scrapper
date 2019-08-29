# import logging
import logging.config

# logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
from settings import LOG_CONFIG_PATH

logging.config.fileConfig(LOG_CONFIG_PATH)

# create logger
logger = logging.getLogger('main')
