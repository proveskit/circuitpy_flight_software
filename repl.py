import microcontroller

from lib.pysquared.config import Config
from lib.pysquared.logger import Logger
from lib.pysquared.pysquared import Satellite

logger: Logger = Logger(datastore=microcontroller.nvm)
config: Config = Config()
logger.info("Initializing a cubesat object as `c` in the REPL...")
c: Satellite = Satellite(config, logger)
