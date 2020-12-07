# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC

import asyncio
import dbussy
import os
import ravel
import threading
import traceback
import xbmc
import xbmcaddon
import xbmcgui

ADDON = xbmcaddon.Addon()
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_NAME = ADDON.getAddonInfo('name')

BUS = ravel.system_bus()

CONFIG_CACHE = os.environ.get('CONFIG_CACHE', '/storage/.cache')

LOG_HEADER = f'{ADDON_NAME}:'
LOG_LEVEL = xbmc.LOGDEBUG


def log_function(function):
    def wrapper(*args, **kwargs):
        header = f'{LOG_HEADER}{function.__qualname__}'
        try:
            xbmc.log(f'{header}<{args}{kwargs}', LOG_LEVEL)
            result = function(*args, **kwargs)
            xbmc.log(f'{header}>{result}', LOG_LEVEL)
            return result
        except Exception as e:
            xbmc.log(f'{header}#{repr(e)}', xbmc.LOGERROR)
            xbmc.log(traceback.format_exc(), xbmc.LOGERROR)
    return wrapper


@log_function
def notification(message, heading=ADDON_NAME, icon=ADDON_ICON):
    xbmcgui.Dialog().notification(heading, message, icon)
