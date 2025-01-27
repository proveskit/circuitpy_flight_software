"""
Class for hanlding various error types that
could arise in the Config class.
"""


class ConfigErrorHandler(Exception):
    def __init__(self) -> None:
        pass

    """
    Error handler for constructor
    """
    # handle errors that might occur:
    # parsing fails and no values populate the dictionary in config class

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
