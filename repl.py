print("Initializing a cubesat object as `c` in the REPL...")

# from lib.pysquared.pysquared import cubesat as c
from lib.pysquared.Config import Config
from lib.pysquared.pysquared import Satellite

config = Config()
c = Satellite(config)
