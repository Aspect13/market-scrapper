import logging
import logging.config

# logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
logging.config.fileConfig('logging.conf')

# create logger
logger = logging.getLogger('main')
