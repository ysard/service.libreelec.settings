# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC

import os

def read_shell_setting(file, default):
    setting = default
    if os.path.isfile(file):
        with open(file) as input:
            setting = input.readline().strip()
    return setting


def read_shell_settings(file, defaults={}):
    settings = defaults
    if os.path.isfile(file):
        with open(file) as input:
            for line in input:
                name, value = line.strip().split('=', 1)
                if len(value) and value[0] in ['"', '"'] and value[0] == value[-1]:
                    value = value[1:-1]
                settings[name] = value
    return settings
