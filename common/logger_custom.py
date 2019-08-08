import logging
import logging.config
from pathlib import Path

# logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
logging.config.fileConfig(f'{Path(__file__).absolute().parent}/logging.conf')

# create logger
logger = logging.getLogger('main')
