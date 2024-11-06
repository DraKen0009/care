class CeleryTaskError(Exception):
    pass


class ICD11DiagnosisNotFoundError(Exception):
    """Custom exception for ICD11 diagnosis not found."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ICD11RedisConnectionError(Exception):
    """Custom exception for Redis connection issues."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
