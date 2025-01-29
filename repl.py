import microcontroller

import lib.pysquared.nvm.register as register
from lib.pysquared.config import Config
from lib.pysquared.logger import Logger
from lib.pysquared.nvm.counter import Counter
from lib.pysquared.pysquared import Satellite

logger: Logger = Logger(
    error_counter=Counter(index=register.ERRORCNT, datastore=microcontroller.nvm)
)
config: Config = Config()
logger.info("Initializing a cubesat object as `c` in the REPL...")
c: Satellite = Satellite(config, logger)
