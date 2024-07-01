import logging as lg
import inspect
import traceback
from typing import TypeVar, Union
from functools import wraps

T = TypeVar('T')
Some = Union[T, None]

class NullException(Exception):
    """Raised when a null value is encountered"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

def expect(generic: Some[T], msg: str = "") -> T:
    if generic is None:
        caller_frame = inspect.currentframe()
        caller_info = caller_frame.f_back.f_code.co_name
        error_msg = f"Value is null at |{caller_info}| fn"
        if msg:
            error_msg += f": {msg}"
        error_msg += traceback.format_exc()
        raise NullException(error_msg)
    return generic

def unwrap(generic: Some[T]) -> T:
    match generic:
        case None:
            lg.warning('Unwrap called on None')
            return 'Null'
        case _:
            return generic

def expected(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is None:
            caller_frame = inspect.currentframe().f_back
            caller_info = caller_frame.f_code.co_name
            error_msg = f"Fn |{caller_info}| returned null"
            raise NullException(error_msg)
        return result
    return wrapper