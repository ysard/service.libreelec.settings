# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)
import oe
import log
import modules


class about:

    ENABLED = False
    menu = {'99': {
        'name': 32196,
        'menuLoader': 'menu_loader',
        'listTyp': 'other',
        'InfoText': 705,
    }}

    @log.log_function()
    def __init__(self, oeMain):
        super().__init__()
        self.controls = {}

    @log.log_function()
    def menu_loader(self, menuItem):
        pass

    @log.log_function()
    def exit_addon(self):
        oe.winOeMain.close()

    @log.log_function()
    def init_controls(self):
        pass

    @log.log_function()
    def exit(self):
        for control in self.controls:
            try:
                oe.winOeMain.removeControl(self.controls[control])
            finally:
                self.controls = {}

    @log.log_function()
    def do_wizard(self):
        oe.winOeMain.set_wizard_title(oe._(32317))
        oe.winOeMain.set_wizard_text(oe._(32318))
