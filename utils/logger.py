import os, logging

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       datefmt='%Y-%m-%d %H:%M:%S'
   )

logger = logging.getLogger('multi-agent')
logger.setLevel(LOG_LEVEL)