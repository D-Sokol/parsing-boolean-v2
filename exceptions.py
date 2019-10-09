class CustomException(Exception):
    """
    Base exception class for lexer and parser
    """


class LexerException(CustomException):
    """
    Raised when lexer finds an unexpected character
    """
    def __str__(self):
        return 'Illegal character: ' + super().__str__()


class ParserException(CustomException):
    """
    Raised when an error occurs during parsing process
    """
    def __str__(self):
        return 'Syntax error at: ' + super().__str__()
