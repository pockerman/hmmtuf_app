
class Error(Exception):
    """
    General error class to handle generic errors
    """
    def __init__(self, message) -> None:
        self.message = message


class FullWindowException(Exception):

    """
    Exception to throw when attempting to
    add a new observation to an already full window
    """
    def __init__(self, size) -> None:
        self.message = "The Window size has already been reached. Window size: " + str(size)

    def __str__(self) -> str:
        return self.message


class InvalidGCLimiter(Exception):
    """
    Exception to be thrown when
    invalid GC limiter is specified
    """

    def __init__(self, expression, message) -> None:
        self.expression = expression
        self.message = message

    def __str__(self) -> str:
        return self.message


class InvalidGCLimitType(Exception):
    """
    Exception to be thrown when
    invalid GC limit type is specified
    """

    def __init__(self, expression, message) -> None:
        self.expression = expression
        self.message = message

    def __str__(self) -> str:
        return self.message


class NoDataQuery(Exception):
    """
    Exception to be thrown when a DB query
    returns no results
    """

    def __init__(self, expression, message) -> None:
        self.expression = expression
        self.message = message

    def __str__(self) -> str:
        return self.message

class IndexExists(Exception):
    def  __init__(self, index) -> None:
        self.message = "Index " + str(index) + " already exists"

class InvalidReadingMode(Exception):
    def __init__(self, mode: str, values: list) -> None:
        self.message = "Reading mode " + mode + " not in " + str(values)

class InvalidFileFormat(Exception):
    def __init__(self, filename):
        self.message = f"File {filename} has incorrect format."


