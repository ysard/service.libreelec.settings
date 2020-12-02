import asyncio
import dbussy
import ravel
import threading
import traceback
import xbmc
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo('name')

LOG_HEADER = f'{ADDON_NAME}:'
LOG_LEVEL = xbmc.LOGINFO

BUS = ravel.system_bus()
_LOOP = asyncio.get_event_loop()

BUS.attach_asyncio(_LOOP)
threading.Thread(target=_LOOP.run_forever, daemon=True).start()


def convert_debussy(data):
    if type(data) is list:
        return [convert_debussy(item) for item in data]
    if type(data) is dict:
        return {key: convert_debussy(data[key]) for key in data.keys()}
    if type(data) is tuple and type(data[0]) is dbussy.DBUS.Signature:
        return data[1]
    return data


def log_function(function):
    def wrapper(*args, **kwargs):
        header = f'{LOG_HEADER}{function.__qualname__}'
        try:
            xbmc.log(f'{header}<{args}{kwargs}', LOG_LEVEL)
            result = function(*args, **kwargs)
            return result
            xbmc.log(f'{header}>{result}', LOG_LEVEL)
        except Exception as e:
            xbmc.log(f'{header}#{repr(e)}', xbmc.LOGERROR)
            xbmc.log(traceback.format_exc(), xbmc.LOGERROR)
    return wrapper
