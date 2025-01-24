# from lib.pysquared.pysquared import cubesat as c
import lib.pysquared.config as Config
import lib.pysquared.pysquared as Satellite
from lib.pysquared.logger import Logger

config = Config.Config()
logger = Logger()
c = Satellite.Satellite(config, logger)

logger.info(message="Initialized a cubesat object as `c` in the REPL...")
