# from lib.pysquared.pysquared import cubesat as c
import lib.pysquared.config as Config
import lib.pysquared.pysquared as Satellite
from lib.pysquared.logger import Logger

config: Config = Config.Config()
logger: Logger = Logger()
c: Satellite.Satellite = Satellite.Satellite(config, logger)

logger.info("Initialized a cubesat object as `c` in the REPL...")
