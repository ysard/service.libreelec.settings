# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

import oe
import config
import os
import threading
import socket
import xbmc


class Service_Thread(threading.Thread):

    SOCKET = '/var/run/service.libreelec.settings.sock'

    def __init__(self):
        threading.Thread.__init__(self)
        self.init()

    @config.log_function
    def init(self):
        if os.path.exists(self.SOCKET):
            os.remove(self.SOCKET)
        self.daemon = True
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.setblocking(1)
        self.sock.bind(self.SOCKET)
        self.sock.listen(1)
        self.stopped = False

    @config.log_function
    def run(self):
        if oe.read_setting('libreelec', 'wizard_completed') == None:
            threading.Thread(target=oe.openWizard).start()
        while self.stopped == False:
            oe.dbg_log('_service_::run', 'WAITING:', oe.LOGINFO)
            conn, addr = self.sock.accept()
            message = (conn.recv(1024)).decode('utf-8')
            conn.close()
            oe.dbg_log('_service_::run', f'MESSAGE:{message}', oe.LOGINFO)
            if message == 'openConfigurationWindow':
                if not hasattr(oe, 'winOeMain'):
                    threading.Thread(target=oe.openConfigurationWindow).start()
                else:
                    if oe.winOeMain.visible != True:
                        threading.Thread(
                            target=oe.openConfigurationWindow).start()
            if message == 'exit':
                self.stopped = True

    @config.log_function
    def stop(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.SOCKET)
        sock.send(bytes('exit', 'utf-8'))
        sock.close()
        self.join()
        self.sock.close()


class Monitor(xbmc.Monitor):

    @config.log_function
    def onScreensaverActivated(self):
        if oe.read_setting('bluetooth', 'standby'):
            threading.Thread(target=oe.standby_devices).start()

    @config.log_function
    def onDPMSActivated(self):
        if oe.read_setting('bluetooth', 'standby'):
            threading.Thread(target=oe.standby_devices).start()

    @config.log_function
    def run(self):
        oe.load_modules()
        oe.start_service()
        service_thread = Service_Thread()
        service_thread.start()
        while not self.abortRequested():
            if self.waitForAbort(60):
                break
            if not oe.read_setting('bluetooth', 'standby'):
                continue
            timeout = oe.read_setting('bluetooth', 'idle_timeout')
            if not timeout:
                continue
            try:
                timeout = int(timeout)
            except:
                continue
            if timeout < 1:
                continue
            if xbmc.getGlobalIdleTime() / 60 >= timeout:
                oe.dbg_log('service', 'idle timeout reached', oe.LOGDEBUG)
                oe.standby_devices()
        if hasattr(oe, 'winOeMain') and hasattr(oe.winOeMain, 'visible'):
            if oe.winOeMain.visible == True:
                oe.winOeMain.close()
        oe.stop_service()
        service_thread.stop()


if __name__ == '__main__':
    Monitor().run()
