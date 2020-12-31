# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC

import config
import os_tools


def get_hostname():
    return os_tools.read_shell_setting(config.HOSTNAME, config.OS_RELEASE['NAME'])
