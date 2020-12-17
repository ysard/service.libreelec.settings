# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC
import pprint
import sys
import traceback

DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3
FATAL = 4
NONE = 5

_DEFAULT = DEBUG
_HEADER = 'SETTINGS: '


try:
    import xbmc
    def _log(message, level=_DEFAULT):
        xbmc.log(message, level)
except ModuleNotFoundError:
    def _log(message, level=_DEFAULT):
        print(message)


def log(message, level=_DEFAULT):
    _log(f'{_HEADER}{sys._getframe().f_back.f_code.co_name} # {message}', level)


def log_function(level=_DEFAULT):
    def _log_function_1(function):
        header = f'{_HEADER}{function.__qualname__} '
        def _log_function_2(*args, **kwargs):
            try:
                _log(f'{header}-', level)
                for arg in args:
                    _log(f'{header}< {pprint.pformat(arg)}', level)
                for key, value in kwargs.items():
                    _log(f'{header}< {key}={pprint.pformat(value)}', level)
                result = function(*args, **kwargs)
                _log(f'{header}> {pprint.pformat(result)}', level)
                return result
            except Exception as e:
                _log(f'{header}# {repr(e)}', ERROR)
                _log(traceback.format_exc(), ERROR)
        return _log_function_2
    return _log_function_1
