import pprint
import traceback

DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3
FATAL = 4
NONE = 5

_DEFAULT = DEBUG
_HEADER = 'SETTINGS: '


def _format(message):
    return f'{_HEADER}{message}'


try:
    import xbmc
    def log(message, level=_DEFAULT):
        xbmc.log(_format(message), level)
except ModuleNotFoundError:
    def log(message, level=_DEFAULT):
        print(_format(message))


def log_function(level=_DEFAULT):
    def _log_function_1(function):
        name = function.__qualname__
        def _log_function_2(*args, **kwargs):
            try:
                log(f'> {name}', level)
                for arg in args:
                    log(f'>  {pprint.pformat(arg)}', level)
                for key, value in kwargs.items():
                    log(f'>  {key}={pprint.pformat(value)}', level)
                result = function(*args, **kwargs)
                log(f'< {name}', level)
                log(f'<  {pprint.pformat(result)}', level)
                return result
            except Exception as e:
                log(f'# {name} {repr(e)}', ERROR)
                log(traceback.format_exc(), ERROR)
        return _log_function_2
    return _log_function_1
