class ValidationError(Exception):
    """
    Exception for cases where the criteria for a certain operation or value is not met
    """

    pass


class InvalidFileError(Exception):
    """
    Exception for cases where the criteria for a certain operation or value is not met
    """

    pass


class InvalidConfigsError(Exception):
    """
    Exception for situation where the file passed as input is not valid
    
    E.g.:
        - non-matching pixel amount
        - special characters
        - missing values (for width, height, etc)
    """

    pass


class InvalidHeaderError(Exception):
    """
    Exception for cases where and unknow header if passed or and invalid header
    for a certain operation is used
    """

    pass


class ImcompatibleImages(Exception):
    """
    Exception for cases where there's attempt to operate in 2 images and they are incompatible
    """

    pass


class UnkownError(Exception):
    """
    Exception for any case where there's no clear cause for a crash
    """

    pass
