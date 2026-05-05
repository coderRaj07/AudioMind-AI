from fastapi import HTTPException


class UnauthorizedException(HTTPException):
    def __init__(self, detail="Unauthorized"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(HTTPException):
    def __init__(self, detail="Forbidden"):
        super().__init__(status_code=403, detail=detail)


class NotFoundException(HTTPException):
    def __init__(self, detail="Not found"):
        super().__init__(status_code=404, detail=detail)


class BadRequestException(HTTPException):
    def __init__(self, detail="Bad request"):
        super().__init__(status_code=400, detail=detail)