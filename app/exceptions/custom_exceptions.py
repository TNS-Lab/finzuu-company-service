from fastapi import HTTPException, status


class BadRequestException(HTTPException):
    """Exception pour 400."""

    def __init__(self, description: str = "Mauvaise requete"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=description,
        )


class UnauthorizedException(HTTPException):
    """Exception pour 401."""

    def __init__(self, description: str = "Authentification requise"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=description,
        )


class ForbiddenException(HTTPException):
    """Exception pour 403."""

    def __init__(self, description: str = "Permissions insuffisantes"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=description,
        )


class NotFoundException(HTTPException):
    """Exception pour 404."""

    def __init__(self, description: str = "Ressource non trouvee"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=description,
        )


class ConflictException(HTTPException):
    """Exception pour 409."""

    def __init__(self, description: str = "Conflit"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=description,
        )


class IntegrationException(HTTPException):
    """Exception pour les erreurs d'integration entre services."""

    def __init__(self, description: str = "Unable to complete request", status_code: int = status.HTTP_502_BAD_GATEWAY):
        super().__init__(
            status_code=status_code,
            detail=description,
        )
        self.message = description
