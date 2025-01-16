# from lib.pysquared.pysquared import cubesat as c
import lib.pysquared.Config as Config
import lib.pysquared.pysquared as Satellite

print("Initializing a cubesat object as `c` in the REPL...")
config = Config.Config()
c = Satellite.Satellite(config)
