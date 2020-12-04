# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)
import config
import oe


class about:

    ENABLED = False
    menu = {'99': {
        'name': 32196,
        'menuLoader': 'menu_loader',
        'listTyp': 'other',
        'InfoText': 705,
    }}

    @config.log_function
    def __init__(self, oeMain):
        self.controls = {}

    @config.log_function
    def menu_loader(self, menuItem):
        pass

    @config.log_function
    def exit_addon(self):
        oe.winOeMain.close()

    @config.log_function
    def init_controls(self):
        pass

    @config.log_function
    def exit(self):
        for control in self.controls:
            try:
                oe.winOeMain.removeControl(self.controls[control])
            finally:
                self.controls = {}

    @config.log_function
    def do_wizard(self):
        oe.winOeMain.set_wizard_title(oe._(32317))
        oe.winOeMain.set_wizard_text(oe._(32318))
