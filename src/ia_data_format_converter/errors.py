"""Exceptions raised by conversion operations."""


class ConversionError(Exception):
    """Base class for all conversion failures."""


class InputFileError(ConversionError):
    """The input file is missing, empty, unreadable or malformed."""


class UnknownFormatError(ConversionError):
    """The requested output format is not registered."""


class OutputExistsError(ConversionError):
    """The output file exists and overwriting was not allowed."""


class InvalidOptionError(ConversionError):
    """A conversion option has an unsupported value."""
