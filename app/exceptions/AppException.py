class AppException(Exception):
    """Basic exception for all service."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
