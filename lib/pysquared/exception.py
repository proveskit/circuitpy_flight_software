class NotInitializedError(Exception):
    def __init__(self, name, exception=None):
        self._name = name
        self._exception = exception

    def __str__(self):
        if self._exception:
            return f"Failed to initialize: {self._name} - Exception: {self._exception}"
        return self.message
