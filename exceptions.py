from fastapi import status


class DomainException(Exception):
    exception_to_status_map = {
        "not_found_exception": status.HTTP_404_NOT_FOUND,
        "already_exists_exception": status.HTTP_400_BAD_REQUEST,
        "bad_request_exception": status.HTTP_400_BAD_REQUEST,
    }

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail: str = detail
        self._exception = None

    @property
    def exception(self):
        return self._exception

    @exception.setter
    def exception(self, value):
        self._exception = value

    def __str__(self):
        return str({"exception": self.exception, "detail": self.detail})


class NotFoundException(DomainException):
    def __init__(self, detail: str):
        super().__init__(detail)
        self.exception = "not_found_exception"


class AlreadyExistsException(DomainException):
    def __init__(self, detail: str):
        super().__init__(detail)
        self.exception = "already_exists_exception"


class BadRequestException(DomainException):
    def __init__(self, detail: str):
        super().__init__(detail)
        self.exception = "bad_request_exception"
