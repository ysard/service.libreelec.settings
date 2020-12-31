# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC

import log
import xbmcgui
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_NAME = ADDON.getAddonInfo('name')


@log.log_function()
def notification(message, heading=ADDON_NAME, icon=ADDON_ICON):
    xbmcgui.Dialog().notification(heading, message, icon)
