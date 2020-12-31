# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC

import config
import os
import os_tools


def get_hostname():
    return os_tools.read_shell_setting(config.HOSTNAME, config.OS_RELEASE['NAME'])


def set_hostname(hostname):
    with open(config.HOSTNAME, 'w') as output:
        output.write(hostname)
    with open('/proc/sys/kernel/hostname', 'w') as output:
        output.write(hostname)
    with open('/etc/hosts', 'w') as output:
        if os.path.isfile(config.HOSTS_CONF):
            with open(config.HOSTS_CONF) as input:
                output.write(input.read())
        output.write(f'127.0.0.1 localhost {hostname}\n')
        output.write(f'::1 localhost ip6-localhost ip6-loopback {hostname}\n')
