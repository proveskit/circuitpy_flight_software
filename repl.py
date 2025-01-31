# from lib.pysquared.pysquared import cubesat as c
from lib.pysquared.config import Config
from lib.pysquared.logger import Logger
from lib.pysquared.pysquared import Satellite

config = Config()
logger = Logger()
c = Satellite(config=config, logger=logger)

logger.info("Initialized a cubesat object as `c` in the REPL...")
