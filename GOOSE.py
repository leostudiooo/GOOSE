#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GOOSE - GOOSE Opens workOut for SEU undErgraduates
Copyright (C) 2025 GOOSE Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import sys

from src.ui.tui.GOOSEApp import GOOSEApp
from src.ui.cli.handler import CLIHandler, setup_cli_logging

if __name__ == "__main__":
	# Check if running in CLI mode (any command-line arguments provided)
	if len(sys.argv) > 1:
		# CLI mode
		setup_cli_logging()
		cli = CLIHandler()
		exit_code = cli.run()
		sys.exit(exit_code)
	else:
		# TUI mode
		app = GOOSEApp()
		app.run()