class ApiException(Exception):
    """Base class for exceptions thrown by the API classes
    """
    pass

class ApiNetworkException(ApiException):
    """We couldn't talk to the API because the internet tubes are clogged or
    something
    """
    pass

class ApiBadResponseException(ApiException):
    """We got a response from the API but it didn't make any sense or we don't
    know how to handle it
    """
    pass

class ApiError(ApiException):
    """API gave us an error response (that we know how to parse)
    """
    pass

class ApiLoginFailure(ApiError):
    """Login info wasn't correct
    """
    pass
