"""
Class for handling errors in config.py.
"""


class ConfigErrorHandlers(Exception):
    def __init__(self):
        pass

    def KeyError(self, key: str) -> str:
        if not isinstance(key, str):
            raise TypeError()


"""
Error handlers for getter functions
"""
# handle errors that might occur:
# value is not found, value type is incorrect
"""
Error handlers for setter functions
"""
# handle errors that might occur:
# key does not match database, value is of different type
"""
Error handlers for saver functions
"""
# handle errors that might occur:
# setter functions returned error, parsing to config returned error
