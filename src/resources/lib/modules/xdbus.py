# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)
import config
import dbus
import dbus.service
import threading


class xdbus(object):

    ENABLED = False
    menu = {'99': {}}

    @config.log_function
    def __init__(self, oeMain):
        self.oe = oeMain
        self.dbusSystemBus = self.oe.dbusSystemBus

    @config.log_function
    def start_service(self):
        self.dbusMonitor = dbusMonitor(self.oe)
        self.dbusMonitor.start()

    @config.log_function
    def stop_service(self):
        if hasattr(self, 'dbusMonitor'):
            self.dbusMonitor.stop()
            del self.dbusMonitor

    @config.log_function
    def exit(self):
        pass

    @config.log_function
    def restart(self):
        self.stop_service()
        self.start_service()


class dbusMonitor(threading.Thread):

    def __init__(self, oeMain):
        self.monitors = []
        self.oe = oeMain
        self.dbusSystemBus = oeMain.dbusSystemBus
        threading.Thread.__init__(self)

    @config.log_function
    def run(self):
        for strModule in sorted(self.oe.dictModules, key=lambda x: list(self.oe.dictModules[x].menu.keys())):
            module = self.oe.dictModules[strModule]
            if hasattr(module, 'monitor') and module.ENABLED:
                monitor = module.monitor(self.oe, module)
                monitor.add_signal_receivers()
                self.monitors.append(monitor)
        try:
            self.oe.dbg_log('xdbus Monitor started.', '', self.oe.LOGINFO)
            self.mainLoop.run()
            self.oe.dbg_log('xdbus Monitor stopped.', '', self.oe.LOGINFO)
        except:
            pass

    @config.log_function
    def stop(self):
        self.mainLoop.quit()
        for monitor in self.monitors:
            monitor.remove_signal_receivers()
            monitor = None
