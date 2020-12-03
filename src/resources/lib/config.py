# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC

import asyncio
import dbussy
import ravel
import threading
import traceback
import xbmc
import xbmcaddon
import xbmcgui

ADDON = xbmcaddon.Addon()
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_NAME = ADDON.getAddonInfo('name')

LOG_HEADER = f'{ADDON_NAME}:'
LOG_LEVEL = xbmc.LOGDEBUG

BUS = ravel.system_bus()
_LOOP = asyncio.get_event_loop()

BUS.attach_asyncio(_LOOP)
threading.Thread(target=_LOOP.run_forever, daemon=True).start()


def convert_dbussy(data):
    if isinstance(data, list):
        return [convert_dbussy(item) for item in data]
    if isinstance(data, dict):
        return {key: convert_dbussy(data[key]) for key in data.keys()}
    if isinstance(data, tuple) and isinstance(data[0], dbussy.DBUS.Signature):
        return convert_dbussy(data[1])
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

@log_function
def notification(message, heading=ADDON_NAME, icon=ADDON_ICON):
    xbmcgui.Dialog().notification(heading, message, icon)
